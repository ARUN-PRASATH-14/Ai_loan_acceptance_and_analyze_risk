import os
import sys
import pickle
import re
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAG_INDEX_DIR = os.path.join(BASE_DIR, "rag_index")
FAISS_INDEX_DIR = os.path.join(RAG_INDEX_DIR, "faiss_index")
BM25_INDEX_FILE = os.path.join(RAG_INDEX_DIR, "bm25_index.pkl")

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

vectorstore = FAISS.load_local(FAISS_INDEX_DIR, embeddings, allow_dangerous_deserialization=True)

with open(BM25_INDEX_FILE, "rb") as f:
    bm25_data = pickle.load(f)

bm25 = bm25_data["bm25"]
chunks = bm25_data["chunks"]

def expand_user_query(query: str) -> str:
    q_lower = query.lower()
    expansions = []
    
    if "sbi" in q_lower: expansions.append("State Bank of India SBI")
    if "hdfc" in q_lower: expansions.append("HDFC Bank")
    if "icici" in q_lower: expansions.append("ICICI Bank")
    if "iob" in q_lower: expansions.append("Indian Overseas Bank IOB")
    if "canara" in q_lower: expansions.append("Canara Bank")
    
    if "home" in q_lower or "house" in q_lower: expansions.append("Home Loan Housing Mortgage LTV FOIR Property")
    if "personal" in q_lower or "salary" in q_lower: expansions.append("Personal Loan Net Income Monthly Salary FOIR")
    if "kcc" in q_lower or "farm" in q_lower or "agri" in q_lower: expansions.append("Kisan Credit Card KCC Agriculture Scale of Finance Collateral Free Subvention Prompt Repayment")
    if "edu" in q_lower or "student" in q_lower or "college" in q_lower: expansions.append("Education Loan Student Moratorium Premier Institute Vidya Scholar")
    if "kyc" in q_lower or "doc" in q_lower or "ovd" in q_lower: expansions.append("KYC Officially Valid Documents Aadhaar PAN V-CIP Periodic Updation 2025 2026")
    if "cibil" in q_lower or "score" in q_lower: expansions.append("CIBIL score threshold credit score bureau")
    if "ntc" in q_lower or "no credit" in q_lower or "new to credit" in q_lower: expansions.append("New To Credit NTC first time borrower zero history")
    if "age" in q_lower: expansions.append("minimum entry age maximum exit age threshold years mature")
    
    return f"{query} {' '.join(expansions)}" if expansions else query

def hybrid_rrf_search_boosted(query: str, top_k=5):
    enriched_query = expand_user_query(query)
    q_lower = query.lower()
    
    target_banks = []
    if "sbi" in q_lower: target_banks.append("SBI")
    if "hdfc" in q_lower: target_banks.append("HDFC BANK")
    if "icici" in q_lower: target_banks.append("ICICI BANK")
    if "iob" in q_lower: target_banks.append("IOB")
    if "canara" in q_lower: target_banks.append("CANARA BANK")
    if "rbi" in q_lower: target_banks.append("RBI MASTER DIRECTION")

    # 1. Dense Vector Search (FAISS)
    dense_docs_with_scores = vectorstore.similarity_search_with_relevance_scores(enriched_query, k=10)
    
    # 2. Sparse BM25 Search
    tokens = re.findall(r'\w+', enriched_query.lower())
    sparse_docs = []
    if tokens:
        bm25_scores = bm25.get_scores(tokens)
        top_indices = np.argsort(bm25_scores)[::-1][:10]
        sparse_docs = [chunks[idx] for idx in top_indices if bm25_scores[idx] > 0]

    # 3. RRF Re-Ranking with Institution Boost
    rrf_scores = {}
    doc_map = {}
    dense_score_map = {}
    
    for rank, (doc, sim_score) in enumerate(dense_docs_with_scores):
        doc_key = doc.page_content[:150]
        doc_map[doc_key] = doc
        dense_score_map[doc_key] = sim_score
        
        bank_tag = doc.metadata.get('bank', '')
        boost = 1.5 if any(tb in bank_tag.upper() for tb in target_banks) else 1.0
        rrf_scores[doc_key] = rrf_scores.get(doc_key, 0.0) + (1.0 / (60 + rank + 1)) * boost
        
    for rank, doc in enumerate(sparse_docs):
        doc_key = doc.page_content[:150]
        doc_map[doc_key] = doc
        
        bank_tag = doc.metadata.get('bank', '')
        boost = 1.5 if any(tb in bank_tag.upper() for tb in target_banks) else 1.0
        rrf_scores[doc_key] = rrf_scores.get(doc_key, 0.0) + (1.0 / (60 + rank + 1)) * boost
        
    sorted_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)
    
    results = []
    for k in sorted_keys[:top_k]:
        results.append((doc_map[k], rrf_scores[k], dense_score_map.get(k, 0.0)))
        
    return results

test_cases = [
    {"query": "What is the minimum CIBIL score required for SBI Home Loan?", "expected_bank": "SBI"},
    {"query": "What are the HDFC personal loan eligibility rules for salaried employees?", "expected_bank": "HDFC"},
    {"query": "ICICI maximum LTV ratio for housing loans", "expected_bank": "ICICI"},
    {"query": "IOB agriculture Kisan Credit Card KCC scale of finance and limit", "expected_bank": "IOB"},
    {"query": "Canara bank education loan moratorium period and approved course", "expected_bank": "CANARA"},
    {"query": "RBI Master Direction on KYC officially valid documents OVD and V-CIP", "expected_bank": "RBI"},
    {"query": "What is the minimum age for SBI personal loan?", "expected_bank": "SBI"},
    {"query": "What is the FOIR limit for HDFC NTC borrowers?", "expected_bank": "HDFC"},
    {"query": "What are the periodic updation KYC rules under RBI 2025 guidelines?", "expected_bank": "RBI"},
    {"query": "Does ICICI allow NTC for home loans?", "expected_bank": "ICICI"},
]

hits = 0
total = len(test_cases)
mrr_sum = 0.0

print("=== BOOSTED RAG RETRIEVAL EVALUATION REPORT ===\n")

for idx, tc in enumerate(test_cases, 1):
    results = hybrid_rrf_search_boosted(tc["query"], top_k=5)
    query_hit = False
    rank_found = 0
    
    print(f"Query {idx}: '{tc['query']}'")
    
    for rank, (doc, rrf_score, sim_score) in enumerate(results, 1):
        bank = doc.metadata.get('bank', '')
        is_match = (tc['expected_bank'].upper() in bank.upper() or tc['expected_bank'].upper() in doc.metadata.get('source', '').upper())
        
        if is_match and not query_hit:
            query_hit = True
            rank_found = rank
            
        mark = "✓ MATCH" if is_match else " "
        print(f"  [{rank}] RRF: {rrf_score:.4f} | CosineSim: {sim_score:.4f} | Bank: {bank} | {mark}")
        
    if query_hit:
        hits += 1
        mrr_sum += 1.0 / rank_found
        print(f"  Result: HIT at Rank {rank_found} (MRR: {1.0/rank_found:.3f})\n")

hit_rate = (hits / total) * 100
mrr = mrr_sum / total

print(f"==========================================")
print(f"TOTAL EVALUATED: {total}")
print(f"HIT RATE @ Top-5: {hit_rate:.1f}%")
print(f"MEAN RECIPROCAL RANK (MRR): {mrr:.3f}")
print(f"==========================================")
