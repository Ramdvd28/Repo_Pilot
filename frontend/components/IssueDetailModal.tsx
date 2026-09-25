"use client";

import { X, CircleDot, FileCode, Sparkles, CheckCircle2, AlertTriangle, Lightbulb } from "lucide-react";
import { RepoIssue } from "@/types/repo";

interface IssueDetailModalProps {
  issue: RepoIssue | null;
  onClose: () => void;
}

export function IssueDetailModal({ issue, onClose }: IssueDetailModalProps) {
  if (!issue) return null;

  const difficultyColors = {
    beginner: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    intermediate: "bg-amber-500/10 text-amber-400 border-amber-500/30",
    advanced: "bg-rose-500/10 text-rose-400 border-rose-500/30",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-surface border border-border rounded-3xl max-w-3xl w-full max-h-[85vh] flex flex-col overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        {/* Modal Header */}
        <div className="flex items-start justify-between p-6 border-b border-border/80 bg-gray-900/60">
          <div className="space-y-2 pr-4">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-cyan-300 font-mono font-semibold border border-cyan-500/20">
                Issue #{issue.issue_number}
              </span>
              <span
                className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border capitalize ${
                  difficultyColors[issue.difficulty_level] || "bg-gray-800 text-gray-300 border-border"
                }`}
              >
                {issue.difficulty_level} Difficulty
              </span>
            </div>
            <h2 className="text-xl font-bold text-white leading-snug">{issue.title}</h2>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition-colors shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-sm text-gray-300 custom-scrollbar">
          {/* Issue Description */}
          {issue.description && (
            <div className="space-y-2 bg-gray-900/50 p-4 rounded-2xl border border-border/60">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                <CircleDot className="w-4 h-4 text-cyan-400" />
                Original Issue Description
              </h3>
              <p className="text-xs text-gray-300 leading-relaxed whitespace-pre-wrap">
                {issue.description}
              </p>
            </div>
          )}

          {/* Relevant Files */}
          {issue.relevant_files && issue.relevant_files.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider flex items-center gap-1.5">
                <FileCode className="w-4 h-4 text-cyan-400" />
                Relevant Code Files to Modify ({issue.relevant_files.length})
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {issue.relevant_files.map((file) => (
                  <div
                    key={file}
                    className="p-3 rounded-xl bg-gray-900 border border-border flex items-center gap-2 text-xs font-mono text-cyan-300"
                  >
                    <FileCode className="w-4 h-4 text-cyan-400 shrink-0" />
                    <span className="truncate">{file}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Suggested Implementation Plan */}
          {issue.suggested_approach && (
            <div className="space-y-3 pt-2">
              <h3 className="text-xs font-semibold text-white uppercase tracking-wider flex items-center gap-1.5">
                <Lightbulb className="w-4 h-4 text-amber-400" />
                AI Implementation Strategy & Guidelines
              </h3>
              <div className="p-5 rounded-2xl bg-gray-900/90 border border-border text-xs text-gray-300 leading-relaxed whitespace-pre-wrap font-sans">
                {issue.suggested_approach}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-border/80 bg-gray-900/60 flex items-center justify-between">
          <span className="text-xs text-gray-500">RepoPilot Issue Intelligence</span>
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-white font-semibold text-xs transition-colors border border-border"
          >
            Close Analysis
          </button>
        </div>
      </div>
    </div>
  );
}
