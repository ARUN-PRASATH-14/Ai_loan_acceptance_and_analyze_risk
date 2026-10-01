import os
import sys
import pickle
import re

# Configure UTF-8 output encoding for Windows terminal compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from rank_bm25 import BM25Okapi

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_BASE_DIR = os.path.join(BASE_DIR, "knowledge_base")
RAG_INDEX_DIR = os.path.join(BASE_DIR, "rag_index")
os.makedirs(RAG_INDEX_DIR, exist_ok=True)

FAISS_INDEX_DIR = os.path.join(RAG_INDEX_DIR, "faiss_index")
BM25_INDEX_FILE = os.path.join(RAG_INDEX_DIR, "bm25_index.pkl")

print(f"Scanning '{KNOWLEDGE_BASE_DIR}' for bank policy documents...")

# Load text files with explicit UTF-8 encoding loader
txt_loader = DirectoryLoader(
    KNOWLEDGE_BASE_DIR, 
    glob="**/*.txt", 
    loader_cls=TextLoader, 
    loader_kwargs={'encoding': 'utf-8'}
)
txt_docs = txt_loader.load()

# Load PDF files (if any exist)
try:
    pdf_loader = DirectoryLoader(KNOWLEDGE_BASE_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader)
    pdf_docs = pdf_loader.load()
except Exception as e:
    print(f"No PDFs found or error loading PDFs: {e}")
    pdf_docs = []

all_docs = txt_docs + pdf_docs

if not all_docs:
    print(f"[ERROR] No documents found in '{KNOWLEDGE_BASE_DIR}'. Please add text or PDF policy files.")
    exit(1)

print(f"[OK] Loaded {len(all_docs)} bank policy documents.")
for doc in all_docs:
    src = doc.metadata.get('source', 'Unknown')
    print(f"  - Document: {os.path.basename(src)} ({len(doc.page_content)} characters)")

# Split documents into semantic chunks
print("Splitting policy documents into semantic chunks with structural headers...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=750,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
    separators=["\n\nCHAPTER ", "\n\nSECTION ", "\n\n", "\n", " "]
)
raw_chunks = text_splitter.split_documents(all_docs)

# Add Header-Aware Context to every chunk
chunks = []
for chunk in raw_chunks:
    src_file = os.path.basename(chunk.metadata.get('source', 'Policy'))
    bank_tag = "GENERAL REGULATORY"
    if "sbi" in src_file.lower(): bank_tag = "SBI"
    elif "hdfc" in src_file.lower(): bank_tag = "HDFC BANK"
    elif "icici" in src_file.lower(): bank_tag = "ICICI BANK"
    elif "iob" in src_file.lower(): bank_tag = "IOB"
    elif "canara" in src_file.lower(): bank_tag = "CANARA BANK"
    elif "rbi" in src_file.lower(): bank_tag = "RBI MASTER DIRECTION"

    header_prefix = f"[INSTITUTION: {bank_tag}] [FILE: {src_file}]\n"
    if not chunk.page_content.startswith("[INSTITUTION:"):
        chunk.page_content = header_prefix + chunk.page_content
    
    chunk.metadata['bank'] = bank_tag
    chunks.append(chunk)

print(f"[OK] Created {len(chunks)} header-aware semantic chunks for Hybrid RAG.")

# 1. Build FAISS Vector Database (Dense Retrieval)
print("Loading all-MiniLM-L6-v2 embedding model...")
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

print("Building FAISS Vector Database index...")
vectorstore = FAISS.from_documents(chunks, embeddings)
vectorstore.save_local(FAISS_INDEX_DIR)
print(f"[SUCCESS] Built and saved FAISS index to '{FAISS_INDEX_DIR}'")

# 2. Build BM25 Index (Sparse Retrieval)
def SimpleTokenizer(text):
    return re.findall(r'\w+', text.lower())

print("Building BM25 Sparse Keyword index...")
tokenized_corpus = [SimpleTokenizer(doc.page_content) for doc in chunks]
bm25 = BM25Okapi(tokenized_corpus)

bm25_data = {
    "bm25": bm25,
    "chunks": chunks
}

with open(BM25_INDEX_FILE, "wb") as f:
    pickle.dump(bm25_data, f)

print(f"[SUCCESS] Built and saved BM25 index to '{BM25_INDEX_FILE}'")
print("🚀 Hybrid RAG Indexing complete!")



