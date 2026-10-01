"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Terminal, Loader2, AlertCircle, Clock, Search, ArrowRight, GitBranch } from "lucide-react";
import { api, ApiError } from "@/services/api";
import { Repository } from "@/types/repo";
import { RepoCard } from "@/components/RepoCard";

function AnalyzeContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialUrl = searchParams.get("url") || "";

  const [githubUrl, setGithubUrl] = useState(initialUrl);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recentRepos, setRecentRepos] = useState<Repository[]>([]);

  useEffect(() => {
    api.listRepos()
      .then((res) => setRecentRepos(res.repositories))
      .catch(() => {});

    if (initialUrl) {
      handleAnalyze(initialUrl);
    }
  }, [initialUrl]);

  const handleAnalyze = async (targetUrl: string) => {
    if (!targetUrl.trim()) {
      setError("Please enter a valid GitHub repository URL.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const repo = await api.analyzeRepo(targetUrl.trim());
      router.push(`/repo/${repo.id}`);
    } catch (err) {
      setLoading(false);
      if (err instanceof ApiError) {
        setError(err.message);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to connect to backend server. Ensure the FastAPI backend is running.");
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleAnalyze(githubUrl);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
      {/* Header */}
      <div className="text-center space-y-3">
        <span className="text-xs font-mono uppercase tracking-wider text-blue-400">REST API & AST Parsing</span>
        <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
          Repository Analysis Engine
        </h1>
        <p className="text-zinc-400 max-w-xl mx-auto text-xs sm:text-sm font-sans">
          Enter any public GitHub repository URL to analyze metadata, languages, dependencies, and initialize the intelligence dashboard.
        </p>
      </div>

      {/* Input Form Card */}
      <div className="dev-card rounded-2xl p-6 sm:p-8 space-y-5 border border-white/10 shadow-2xl">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="text-xs font-mono font-medium text-zinc-300 uppercase tracking-wider flex items-center gap-2">
              <Terminal className="w-4 h-4 text-blue-400" />
              <span>Target Repository URL</span>
            </label>
            <div className="relative">
              <input
                type="text"
                value={githubUrl}
                onChange={(e) => {
                  setGithubUrl(e.target.value);
                  setError(null);
                }}
                disabled={loading}
                placeholder="https://github.com/owner/repository"
                className="w-full bg-zinc-900/90 border border-white/15 focus:border-blue-500 rounded-xl px-4 py-3.5 text-white placeholder-zinc-500 focus:outline-none text-xs font-mono transition-colors disabled:opacity-60"
              />
            </div>
          </div>

          {error && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start gap-3 text-rose-300 text-xs font-mono">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <div className="leading-relaxed">{error}</div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-6 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs transition-all shadow-md shadow-blue-600/20 flex items-center justify-center gap-2 disabled:opacity-50 border border-blue-400/30"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>Fetching Metadata & Parsing Structure...</span>
              </>
            ) : (
              <>
                <span>Execute Analysis</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>
      </div>

      {/* Recently Analyzed Repositories */}
      {recentRepos.length > 0 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <div className="flex items-center gap-2 text-white font-semibold text-sm">
              <Clock className="w-4 h-4 text-zinc-400" />
              <span>Previously Analyzed Repositories</span>
            </div>
            <span className="text-xs font-mono text-zinc-500">{recentRepos.length} indexed</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {recentRepos.map((repo) => (
              <RepoCard key={repo.id} repo={repo} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function AnalyzePage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    }>
      <AnalyzeContent />
    </Suspense>
  );
}
