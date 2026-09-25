"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  BookOpen,
  Loader2,
  RefreshCw,
  ArrowLeft,
  Sparkles,
  Copy,
  Check,
  FileText,
  Layers,
  Terminal,
  Download
} from "lucide-react";
import { api, ApiError } from "@/services/api";
import { Repository, TechDocsResponse } from "@/types/repo";

export default function TechnicalDocsPage() {
  const params = useParams();
  const repoId = params.id as string;

  const [repo, setRepo] = useState<Repository | null>(null);
  const [docs, setDocs] = useState<TechDocsResponse | null>(null);
  const [copied, setCopied] = useState(false);

  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDocs = async () => {
    try {
      const repoData = await api.getRepo(repoId);
      setRepo(repoData);

      const docsData = await api.getTechnicalDocs(repoId);
      setDocs(docsData);
      setLoading(false);
    } catch (err) {
      setLoading(false);
      setError("Failed to load technical documentation.");
    }
  };

  useEffect(() => {
    if (repoId) loadDocs();
  }, [repoId]);

  const handleGenerateDocs = async () => {
    setGenerating(true);
    setError(null);
    try {
      const freshDocs = await api.generateTechnicalDocs(repoId);
      setDocs(freshDocs);
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
      else setError("Failed to synthesize technical documentation suite.");
    } finally {
      setGenerating(false);
    }
  };

  const handleCopyMarkdown = () => {
    if (!docs?.documentation) return;
    navigator.clipboard.writeText(docs.documentation);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
        <p className="text-sm text-gray-400">Loading Technical Documentation Suite...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
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
              <BookOpen className="w-5 h-5 text-violet-400" />
              <span>{repo?.owner} / {repo?.name} — Technical Documentation Suite</span>
            </h1>
            <p className="text-xs text-gray-400">
              GitHub-ready developer docs, architecture specs, API reference, and deployment setup guide
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {docs?.documentation && (
            <button
              onClick={handleCopyMarkdown}
              className="px-4 py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-200 border border-border text-xs font-semibold flex items-center gap-2 transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-emerald-400" />
                  <span>Copied Markdown!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span>Copy Markdown</span>
                </>
              )}
            </button>
          )}

          <button
            onClick={handleGenerateDocs}
            disabled={generating}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold text-xs transition-all shadow-lg shadow-violet-600/20 flex items-center justify-center gap-2 disabled:opacity-50 shrink-0"
          >
            {generating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Generating Technical Docs...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate Full Docs</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && <p className="text-xs text-rose-400 pl-2">{error}</p>}

      {/* Documentation Preview Container */}
      <div className="bg-surface/90 border border-border rounded-2xl p-6 sm:p-8 space-y-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-border pb-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-violet-300">
            <FileText className="w-4 h-4" />
            <span>TECHNICAL_DOCUMENTATION.md</span>
          </div>
          <span className="text-xs text-gray-400 font-mono">Synthesized by RepoPilot AI</span>
        </div>

        {docs?.documentation ? (
          <div className="prose prose-invert max-w-none text-xs text-gray-200 leading-relaxed font-sans whitespace-pre-wrap">
            {docs.documentation}
          </div>
        ) : (
          <div className="text-center py-12 space-y-4">
            <BookOpen className="w-10 h-10 text-violet-400 mx-auto" />
            <h3 className="text-lg font-bold text-white">No Technical Documentation Generated Yet</h3>
            <p className="text-xs text-gray-400 max-w-md mx-auto">
              Click "Generate Full Docs" to synthesize an architecture guide, API spec, database model summary, and deployment guide for this repository.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
