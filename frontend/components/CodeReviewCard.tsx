"use client";

import { AlertCircle, AlertTriangle, Info, FileCode, Check } from "lucide-react";
import { CodeReviewFinding } from "@/types/repo";

interface CodeReviewCardProps {
  finding: CodeReviewFinding;
}

export function CodeReviewCard({ finding }: CodeReviewCardProps) {
  const severityConfig = {
    error: {
      icon: AlertCircle,
      color: "text-rose-400",
      bg: "bg-rose-500/10 border-rose-500/30",
      badge: "bg-rose-500/20 text-rose-300 border-rose-500/40",
    },
    warning: {
      icon: AlertTriangle,
      color: "text-amber-400",
      bg: "bg-amber-500/10 border-amber-500/30",
      badge: "bg-amber-500/20 text-amber-300 border-amber-500/40",
    },
    info: {
      icon: Info,
      color: "text-cyan-400",
      bg: "bg-cyan-500/10 border-cyan-500/30",
      badge: "bg-cyan-500/20 text-cyan-300 border-cyan-500/40",
    },
  };

  const config = severityConfig[finding.severity] || severityConfig.info;
  const Icon = config.icon;

  return (
    <div className={`p-4 rounded-2xl border ${config.bg} space-y-3 shadow-lg`}>
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className={`text-[11px] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider border ${config.badge}`}>
            {finding.severity}
          </span>
          <div className="flex items-center gap-1.5 text-xs text-gray-200 font-mono">
            <FileCode className="w-3.5 h-3.5 text-cyan-400" />
            <span className="font-semibold text-white">{finding.file_path}</span>
            {finding.line_number && <span className="text-gray-500">:L{finding.line_number}</span>}
          </div>
        </div>
        <Icon className={`w-4 h-4 ${config.color}`} />
      </div>

      <p className="text-xs text-gray-300 leading-relaxed font-sans">
        {finding.explanation}
      </p>

      {finding.suggested_fix && (
        <div className="space-y-1.5 pt-1">
          <div className="text-[10px] uppercase font-semibold text-gray-400 tracking-wider flex items-center gap-1">
            <Check className="w-3 h-3 text-emerald-400" />
            <span>Suggested Code Fix</span>
          </div>
          <pre className="p-3 rounded-xl bg-black/60 font-mono text-xs text-emerald-300 overflow-x-auto border border-border/50 leading-relaxed">
            {finding.suggested_fix}
          </pre>
        </div>
      )}
    </div>
  );
}
