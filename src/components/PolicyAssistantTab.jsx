import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, HelpCircle } from 'lucide-react';
import { sendChatMessage } from '../services/api';

export default function PolicyAssistantTab({ quickQuery, assessmentResult }) {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: `Hello, I am your **Loan-IQ Banking & Policy AI Assistant**. I can help you check loan eligibility criteria, interest rates, CIBIL score rules, and document requirements for **SBI, HDFC Bank, ICICI Bank, IOB, and Canara Bank**.\n\n**Try asking me questions like:**\n• "What is the minimum income for an SBI Personal Loan?"\n• "What are ICICI Bank's CIBIL score requirements for Home Loans?"\n• "Canara Bank Education Loan interest rates and collateral limits"\n• "What is the FOIR limit for HDFC Bank?"\n\nHow can I help you today?`,
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatBottomRef = useRef(null);

  useEffect(() => {
    if (quickQuery) {
      handleSendQuery(quickQuery);
    }
  }, [quickQuery]);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendQuery = async (queryText) => {
    const prompt = (queryText || inputQuery).trim();
    if (!prompt) return;

    setInputQuery('');
    setMessages((prev) => [...prev, { sender: 'user', text: prompt }]);
    setIsLoading(true);

    try {
      // Merge form payload (bank, loan_type, cibil) + API response (approved, violations, foir, ltv, probability)
      // The backend's /api/chat needs ALL of these fields to provide personalised answers
      const contextData = assessmentResult
        ? {
            bank: assessmentResult.payload?.bank,
            loan_type: assessmentResult.payload?.loan_type,
            cibil: assessmentResult.payload?.cibil,
            ...assessmentResult.data,
          }
        : {};
      const resData = await sendChatMessage(prompt, contextData);
      setMessages((prev) => [
        ...prev,
        { sender: 'bot', text: resData.answer || 'No response generated.' },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: 'bot', text: 'Failed to connect to AI Policy server.' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatMarkdown = (text, sender) => {
    if (!text) return '';
    let str = String(text)
      .replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '')
      .trim();

    str = str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');

    const isUser = sender === 'user';
    const textClass = isUser ? 'text-white' : 'text-slate-700';
    const boldClass = isUser ? 'text-white' : 'text-slate-900';

    str = str.replace(/\*\*(.*?)\*\*/g, `<strong class="font-bold ${boldClass}">$1</strong>`);
    str = str.replace(/\*(.*?)\*/g, `<em class="italic ${textClass}">$1</em>`);

    let lines = str.split('\n');
    let out = [];
    let inList = false;

    for (let line of lines) {
      let trimmed = line.trim();
      if (!trimmed) {
        if (inList) {
          out.push('</ul>');
          inList = false;
        }
        out.push('<div class="h-1.5"></div>');
        continue;
      }

      let bulletMatch = trimmed.match(/^[•\*\+\-]\s+(.*)$/);
      if (bulletMatch) {
        if (!inList) {
          out.push(`<ul class="my-1.5 pl-5 list-disc space-y-1 ${textClass}">`);
          inList = true;
        }
        out.push(`<li class="leading-relaxed">${bulletMatch[1]}</li>`);
        continue;
      }

      if (inList) {
        out.push('</ul>');
        inList = false;
      }

      if (trimmed.startsWith('### ')) {
        out.push(`<h4 class="mt-2.5 mb-1 font-heading text-sm font-bold ${boldClass}">${trimmed.substring(4)}</h4>`);
      } else if (trimmed.startsWith('## ')) {
        out.push(`<h3 class="mt-3 mb-1.5 font-heading text-base font-extrabold ${boldClass}">${trimmed.substring(3)}</h3>`);
      } else if (trimmed.endsWith(':') && trimmed.length < 80) {
        out.push(`<div class="font-bold ${boldClass} mt-2 mb-1">${trimmed}</div>`);
      } else if (out.length === 0 && trimmed.length < 80 && !trimmed.endsWith('.')) {
        out.push(`<div class="font-heading font-bold text-sm ${boldClass} mb-1.5 border-b ${isUser ? 'border-white/30' : 'border-slate-200'} pb-1">${trimmed}</div>`);
      } else {
        out.push(`<div class="mb-1 leading-relaxed ${textClass}">${trimmed}</div>`);
      }
    }

    if (inList) {
      out.push('</ul>');
    }

    return out.join('');
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div>
        <h2 className="font-heading text-2xl font-extrabold text-slate-900">
          Policy & AI Banking Assistant
        </h2>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Query Indian commercial banking rules, CIBIL score floors, FOIR caps, and SBI/HDFC/ICICI/IOB/Canara Bank loan policies.
        </p>
      </div>

      <div className="react-bits-glass rounded-3xl p-6 flex flex-col h-[580px] shadow-lg">
        
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto pr-2 space-y-4 mb-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex items-start gap-3 max-w-[88%] ${
                msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''
              }`}
            >
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold shrink-0 ${
                  msg.sender === 'user'
                    ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white'
                    : 'bg-white border border-slate-200 text-slate-700 shadow-2xs'
                }`}
              >
                {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4 text-indigo-600" />}
              </div>

              <div
                className={`p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white font-medium rounded-tr-xs shadow-md'
                    : 'bg-slate-50/90 border border-slate-200 text-slate-800 rounded-tl-xs shadow-2xs'
                }`}
                dangerouslySetInnerHTML={{ __html: formatMarkdown(msg.text, msg.sender) }}
              />
            </div>
          ))}

          {isLoading && (
            <div className="flex items-center gap-3 max-w-[88%]">
              <div className="w-8 h-8 rounded-xl bg-white border border-slate-200 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 text-indigo-600" />
              </div>
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 text-slate-500 text-xs font-medium flex items-center gap-2">
                <span className="w-3.5 h-3.5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                <span>Querying bank policy vector index...</span>
              </div>
            </div>
          )}

          <div ref={chatBottomRef} />
        </div>

        {/* Input Form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendQuery();
          }}
          className="flex items-center gap-3 pt-2"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask about bank policies or eligibility rules..."
            className="flex-1 bg-white/90 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
          />
          <button
            type="submit"
            disabled={isLoading || !inputQuery.trim()}
            className="py-3 px-6 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 text-white font-heading font-bold text-xs shadow-md hover:shadow-indigo-500/25 active:translate-y-0 disabled:opacity-40 transition-all flex items-center gap-2"
          >
            <span>Send Query</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>

      </div>
    </div>
  );
}
