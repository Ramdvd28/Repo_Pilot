"use client";

import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  Compass,
  MessageSquare,
  Send,
  Loader2,
  Sparkles,
  Bot,
  Trash2,
  ArrowLeft,
  Cpu,
  HelpCircle,
} from "lucide-react";
import { api, ApiError } from "@/services/api";
import { Repository, ChatMessage, ChatSession } from "@/types/repo";
import { ChatMessageItem } from "@/components/ChatMessageItem";

export default function RepositoryChatPage() {
  const params = useParams();
  const repoId = params.id as string;

  const [repo, setRepo] = useState<Repository | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuestion, setInputQuestion] = useState("");
  const [activeSessionId, setActiveSessionId] = useState<string | undefined>(undefined);
  const [provider, setProvider] = useState<string>("openai");
  
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const chatBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!repoId) return;

    api.getRepo(repoId)
      .then((data) => {
        setRepo(data);
        setLoading(false);
      })
      .catch((err) => {
        setLoading(false);
        setError("Failed to load repository details.");
      });
  }, [repoId]);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const handleSendMessage = async (questionText: string) => {
    if (!questionText.trim() || sending) return;

    const userQ = questionText.trim();
    setInputQuestion("");
    setSending(true);
    setError(null);

    // Optimistic user message update
    const optimisticUserMsg: ChatMessage = {
      id: "temp-" + Date.now(),
      session_id: activeSessionId || "",
      role: "user",
      content: userQ,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimisticUserMsg]);

    try {
      const respMsg = await api.sendChatMessage(repoId, {
        question: userQ,
        session_id: activeSessionId,
        provider: provider,
      });

      if (!activeSessionId) {
        setActiveSessionId(respMsg.session_id);
      }

      setMessages((prev) => [...prev, respMsg]);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to generate AI response.");
      }
    } finally {
      setSending(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(inputQuestion);
  };

  const handleClearChat = () => {
    setMessages([]);
    setActiveSessionId(undefined);
  };

  const presetQuestions = [
    "What does this project do?",
    "Explain the authentication flow.",
    "Where is database connection created?",
    "How does this API endpoint work?",
    "Which files should I modify to add a feature?",
  ];

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
        <p className="text-sm text-gray-400">Initializing Repository RAG Chat...</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-surface/80 border border-border p-5 rounded-2xl">
        <div className="flex items-center gap-3">
          <Link
            href={`/repo/${repoId}`}
            className="p-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors border border-border"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-lg font-bold text-white flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-cyan-400" />
              <span>{repo?.owner} / {repo?.name} — Repository RAG Chat</span>
            </h1>
            <p className="text-xs text-gray-400">
              Ask questions grounded strictly in the repository's code context
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          {/* AI Provider Switcher */}
          <div className="flex items-center gap-1.5 bg-gray-900 border border-border rounded-xl p-1 text-xs">
            <Cpu className="w-3.5 h-3.5 text-violet-400 ml-1.5" />
            <button
              onClick={() => setProvider("openai")}
              className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
                provider === "openai"
                  ? "bg-blue-600 text-white shadow"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              OpenAI
            </button>
            <button
              onClick={() => setProvider("gemini")}
              className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
                provider === "gemini"
                  ? "bg-blue-600 text-white shadow"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Gemini
            </button>
          </div>

          {messages.length > 0 && (
            <button
              onClick={handleClearChat}
              className="p-2 rounded-xl bg-gray-800 hover:bg-rose-600/20 text-gray-400 hover:text-rose-300 border border-border transition-colors"
              title="Clear chat session"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Main Chat Stream Area */}
      <div className="bg-surface/60 border border-border rounded-2xl p-4 sm:p-6 min-h-[500px] flex flex-col justify-between shadow-2xl">
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center py-12 text-center space-y-6">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-xl shadow-cyan-500/20">
              <Bot className="w-7 h-7" />
            </div>
            <div className="space-y-2 max-w-md">
              <h2 className="text-xl font-bold text-white">Repository AI Chat</h2>
              <p className="text-sm text-gray-400">
                Ask any question about {repo?.name}'s architecture, authentication, API routes, or database patterns.
              </p>
            </div>

            {/* Preset Query Badges */}
            <div className="w-full max-w-xl space-y-2 pt-2">
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center justify-center gap-1">
                <HelpCircle className="w-3.5 h-3.5 text-cyan-400" />
                <span>Suggested Questions</span>
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                {presetQuestions.map((q) => (
                  <button
                    key={q}
                    onClick={() => handleSendMessage(q)}
                    className="text-xs px-3 py-2 rounded-xl bg-surface hover:bg-gray-800 text-cyan-300 border border-border hover:border-cyan-500/40 transition-all text-left"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4 mb-4 overflow-y-auto max-h-[600px] pr-2">
            {messages.map((msg) => (
              <ChatMessageItem key={msg.id} message={msg} />
            ))}
            {sending && (
              <div className="flex items-center gap-3 p-4 rounded-2xl bg-surface/90 border border-border text-xs text-cyan-400">
                <Loader2 className="w-4 h-4 animate-spin shrink-0" />
                <span>Searching repository code chunks and generating RAG answer...</span>
              </div>
            )}
            <div ref={chatBottomRef} />
          </div>
        )}

        {/* Input Form Box */}
        <form onSubmit={handleFormSubmit} className="pt-4 border-t border-border/80">
          {error && <p className="text-xs text-rose-400 mb-2 pl-2">{error}</p>}
          <div className="flex items-center gap-2 bg-gray-900 border border-border rounded-2xl p-2 focus-within:border-blue-500 transition-colors">
            <input
              type="text"
              value={inputQuestion}
              onChange={(e) => setInputQuestion(e.target.value)}
              disabled={sending}
              placeholder={`Ask a question about ${repo?.name || "repository"} code...`}
              className="flex-1 bg-transparent px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!inputQuestion.trim() || sending}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-semibold text-xs transition-all shadow-lg shadow-blue-600/30 flex items-center gap-1.5 disabled:opacity-40 shrink-0"
            >
              <span>Send</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
