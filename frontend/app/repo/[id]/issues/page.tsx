"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  Compass,
  CircleDot,
  Loader2,
  RefreshCw,
  Sparkles,
  FileCode,
  ArrowLeft,
  Filter,
  CheckCircle2,
  ChevronRight,
} from "lucide-react";
import { api, ApiError } from "@/services/api";
import { Repository, RepoIssue } from "@/types/repo";
import { IssueDetailModal } from "@/components/IssueDetailModal";

export default function IssueDiscoveryPage() {
  const params = useParams();
  const repoId = params.id as string;

  const [repo, setRepo] = useState<Repository | null>(null);
  const [issues, setIssues] = useState<RepoIssue[]>([]);
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>("all");
  const [selectedIssue, setSelectedIssue] = useState<RepoIssue | null>(null);

  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadIssues = async (diffFilter?: string) => {
    try {
      const repoData = await api.getRepo(repoId);
      setRepo(repoData);

      const filterVal = diffFilter && diffFilter !== "all" ? diffFilter : undefined;
      const issuesData = await api.getRepoIssues(repoId, filterVal);
      setIssues(issuesData);
      setLoading(false);
    } catch (err) {
      setLoading(false);
      setError("Failed to load repository issues.");
    }
  };

  useEffect(() => {
    if (repoId) {
      loadIssues(selectedDifficulty);
    }
  }, [repoId, selectedDifficulty]);

  const handleSyncIssues = async () => {
    setSyncing(true);
    setError(null);
    try {
      const synced = await api.syncRepoIssues(repoId);
      setIssues(synced);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to sync issues from GitHub.");
      }
    } finally {
      setSyncing(false);
    }
  };

  const difficultyColors = {
    beginner: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    intermediate: "bg-amber-500/10 text-amber-400 border-amber-500/30",
    advanced: "bg-rose-500/10 text-rose-400 border-rose-500/30",
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
        <p className="text-sm text-gray-400">Loading Issue Assistant...</p>
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
              <CircleDot className="w-5 h-5 text-cyan-400" />
              <span>{repo?.owner} / {repo?.name} — Issue Assistant</span>
            </h1>
            <p className="text-xs text-gray-400">
              AI difficulty classification, code context correlation & implementation guides
            </p>
          </div>
        </div>

        <button
          onClick={handleSyncIssues}
          disabled={syncing}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-semibold text-xs transition-all shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2 disabled:opacity-50 shrink-0"
        >
          {syncing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Syncing GitHub Issues...</span>
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4" />
              <span>Sync & Analyze Issues</span>
            </>
          )}
        </button>
      </div>

      {error && <p className="text-xs text-rose-400 pl-2">{error}</p>}

      {/* Difficulty Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-border pb-3 overflow-x-auto">
        {[
          { id: "all", label: "All Issues" },
          { id: "beginner", label: "Beginner Friendly" },
          { id: "intermediate", label: "Intermediate" },
          { id: "advanced", label: "Advanced" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setSelectedDifficulty(tab.id)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              selectedDifficulty === tab.id
                ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                : "bg-surface text-gray-400 hover:text-white border border-border"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Issues Grid / List */}
      {issues.length === 0 ? (
        <div className="bg-surface/60 border border-border/80 rounded-2xl p-16 text-center space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-blue-600/10 border border-blue-500/30 flex items-center justify-center mx-auto text-cyan-400">
            <CircleDot className="w-7 h-7" />
          </div>
          <h2 className="text-xl font-bold text-white">No Issues Analyzed Yet</h2>
          <p className="text-sm text-gray-400 max-w-md mx-auto">
            Click "Sync & Analyze Issues" to fetch open GitHub issues and generate AI implementation guides.
          </p>
          <div>
            <button
              onClick={handleSyncIssues}
              disabled={syncing}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 text-white font-semibold text-sm transition-all"
            >
              {syncing ? "Syncing..." : "Sync Open Issues Now"}
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {issues.map((issue) => (
            <div
              key={issue.id}
              onClick={() => setSelectedIssue(issue)}
              className="bg-surface/90 border border-border hover:border-blue-500/50 p-5 rounded-2xl space-y-4 transition-all hover:shadow-xl hover:shadow-blue-500/5 cursor-pointer group flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-cyan-300 font-mono font-semibold border border-cyan-500/20">
                      #{issue.issue_number}
                    </span>
                    <span
                      className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border capitalize ${
                        difficultyColors[issue.difficulty_level] || "bg-gray-800 text-gray-300 border-border"
                      }`}
                    >
                      {issue.difficulty_level}
                    </span>
                  </div>

                  <span className="text-xs text-cyan-400 font-semibold flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                    <span>Inspect</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </span>
                </div>

                <h3 className="text-base font-bold text-white group-hover:text-cyan-300 transition-colors leading-snug">
                  {issue.title}
                </h3>

                {issue.description && (
                  <p className="text-xs text-gray-400 line-clamp-2 leading-relaxed">
                    {issue.description}
                  </p>
                )}
              </div>

              <div className="pt-3 border-t border-border/50 flex items-center justify-between text-xs text-gray-400">
                <div className="flex items-center gap-1.5 font-mono">
                  <FileCode className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{issue.relevant_files?.length || 0} relevant files</span>
                </div>
                <span className="text-gray-500">AI Analyzed</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Issue Detail Modal */}
      <IssueDetailModal issue={selectedIssue} onClose={() => setSelectedIssue(null)} />
    </div>
  );
}
