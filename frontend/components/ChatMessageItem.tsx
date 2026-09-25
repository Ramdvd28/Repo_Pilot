"use client";

import { useState } from "react";
import { Bot, User, ChevronDown, ChevronUp, FileCode, Layers } from "lucide-react";
import { ChatMessage, ChunkSource } from "@/types/repo";

interface ChatMessageItemProps {
  message: ChatMessage;
}

export function ChatMessageItem({ message }: ChatMessageItemProps) {
  const [showSources, setShowSources] = useState(false);
  const isUser = message.role === "user";

  return (
    <div
      className={`flex gap-4 p-4 sm:p-5 rounded-2xl transition-all ${
        isUser
          ? "bg-blue-600/10 border border-blue-500/20 ml-8 sm:ml-16"
          : "bg-surface/90 border border-border mr-8 sm:mr-16 shadow-xl"
      }`}
    >
      {/* Avatar */}
      <div
        className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-gradient-to-tr from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/20"
        }`}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      {/* Message Body */}
      <div className="flex-1 space-y-3 overflow-hidden">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span className="font-semibold text-gray-200">{isUser ? "You" : "RepoPilot Assistant"}</span>
          <span className="text-[10px] text-gray-500">
            {new Date(message.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </span>
        </div>

        <div className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap font-sans">
          {message.content}
        </div>

        {/* Source Citations Accordion (Assistant Only) */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="pt-2 border-t border-border/60">
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 font-semibold transition-colors"
            >
              <FileCode className="w-3.5 h-3.5" />
              <span>{message.sources.length} Code Sources Cited</span>
              {showSources ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>

            {showSources && (
              <div className="mt-3 space-y-2">
                {message.sources.map((src: ChunkSource, idx: number) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-gray-900/90 border border-border text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between text-gray-300 font-mono">
                      <span className="font-semibold text-cyan-300 flex items-center gap-1">
                        <FileCode className="w-3 h-3 text-cyan-400" />
                        {src.file_path}
                      </span>
                      <span className="text-gray-500">
                        Lines {src.start_line}-{src.end_line}
                      </span>
                    </div>
                    {src.symbol_name && (
                      <div className="text-[10px] font-mono text-violet-300">
                        Symbol: {src.symbol_name}
                      </div>
                    )}
                    {src.snippet && (
                      <pre className="p-2 rounded bg-black/50 text-[11px] font-mono text-gray-400 overflow-x-auto border border-border/40 max-h-24">
                        {src.snippet}
                      </pre>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
