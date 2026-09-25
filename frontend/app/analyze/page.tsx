"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Compass, Sparkles, Loader2, AlertCircle, Clock, BookOpen } from "lucide-react";
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
    // Load recently analyzed repos
    api.listRepos()
      .then((res) => setRecentRepos(res.repositories))
      .catch(() => {}); // silent catch if backend is offline initially

    // Auto-analyze if URL query param is present
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
        setError("Failed to connect to backend server. Make sure the FastAPI backend is running.");
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
        <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
          Analyze GitHub Repository
        </h1>
        <p className="text-gray-400 max-w-xl mx-auto text-sm">
          Enter any public repository link (e.g. <code className="text-cyan-400 font-mono text-xs">https://github.com/fastapi/fastapi</code>) to analyze metadata, languages, and initialize repository dashboard.
        </p>
      </div>

      {/* Input Form Card */}
      <div className="bg-surface border border-border rounded-2xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-300 uppercase tracking-wider flex items-center gap-2">
              <Compass className="w-4 h-4 text-cyan-400" />
              GitHub Repository URL
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
                className="w-full bg-gray-900/90 border border-border focus:border-blue-500 rounded-xl px-4 py-3.5 text-white placeholder-gray-500 focus:outline-none text-sm font-mono transition-colors disabled:opacity-60"
              />
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start gap-3 text-rose-300 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <div className="leading-relaxed">{error}</div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-semibold text-sm transition-all shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>Fetching metadata from GitHub API...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Start Analysis</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Recently Analyzed Repositories */}
      {recentRepos.length > 0 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-white font-semibold text-lg">
              <Clock className="w-5 h-5 text-violet-400" />
              <h2>Recently Analyzed Repositories</h2>
            </div>
            <span className="text-xs text-gray-500">{recentRepos.length} repositories</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
