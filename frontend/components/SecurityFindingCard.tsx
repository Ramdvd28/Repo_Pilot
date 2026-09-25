"use client";

import { useState } from "react";
import { ShieldAlert, FileCode, ChevronDown, ChevronUp, Sparkles, AlertCircle, AlertTriangle, Info } from "lucide-react";
import { SecurityFinding } from "@/types/repo";

interface SecurityFindingCardProps {
  finding: SecurityFinding;
}

export function SecurityFindingCard({ finding }: SecurityFindingCardProps) {
  const [showAiExp, setShowAiExp] = useState(false);

  const severityConfig = {
    critical: {
      color: "text-rose-400",
      bg: "bg-rose-500/10 border-rose-500/30",
      badge: "bg-rose-500/20 text-rose-300 border-rose-500/40",
      icon: AlertCircle,
    },
    high: {
      color: "text-orange-400",
      bg: "bg-orange-500/10 border-orange-500/30",
      badge: "bg-orange-500/20 text-orange-300 border-orange-500/40",
      icon: AlertCircle,
    },
    medium: {
      color: "text-amber-400",
      bg: "bg-amber-500/10 border-amber-500/30",
      badge: "bg-amber-500/20 text-amber-300 border-amber-500/40",
      icon: AlertTriangle,
    },
    low: {
      color: "text-cyan-400",
      bg: "bg-cyan-500/10 border-cyan-500/30",
      badge: "bg-cyan-500/20 text-cyan-300 border-cyan-500/40",
      icon: Info,
    },
  };

  const config = severityConfig[finding.severity] || severityConfig.medium;
  const Icon = config.icon;

  return (
    <div className={`p-5 rounded-2xl border ${config.bg} space-y-3 shadow-lg`}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className={`text-[11px] px-2.5 py-0.5 rounded-full font-extrabold uppercase tracking-wider border ${config.badge}`}>
            {finding.severity}
          </span>
          <span className="text-[11px] px-2 py-0.5 rounded bg-gray-800 text-gray-300 border border-border font-mono">
            {finding.tool_name}
          </span>
          <span className="text-[11px] px-2 py-0.5 rounded bg-gray-900 text-cyan-300 border border-border font-mono">
            {finding.rule_id}
          </span>
        </div>

        <div className="flex items-center gap-1 text-xs font-mono text-gray-300">
          <FileCode className="w-3.5 h-3.5 text-cyan-400" />
          <span className="font-semibold text-white">{finding.file_path}</span>
          {finding.line_number && <span className="text-gray-500">:L{finding.line_number}</span>}
        </div>
      </div>

      <p className="text-xs text-gray-200 leading-relaxed font-sans font-medium">
        {finding.description}
      </p>

      {finding.ai_explanation && (
        <div className="pt-2 border-t border-border/50">
          <button
            onClick={() => setShowAiExp(!showAiExp)}
            className="flex items-center gap-1.5 text-xs text-violet-400 hover:text-violet-300 font-semibold transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Remediation & Explanation</span>
            {showAiExp ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showAiExp && (
            <div className="mt-2 p-3.5 rounded-xl bg-black/60 border border-violet-500/20 text-xs text-violet-200 leading-relaxed whitespace-pre-wrap font-sans">
              {finding.ai_explanation}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
