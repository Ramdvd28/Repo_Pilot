"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  Compass,
  Star,
  GitFork,
  CircleDot,
  ExternalLink,
  Loader2,
  AlertCircle,
  FileCode,
  MessageSquare,
  ShieldAlert,
  Sparkles,
  GitPullRequest,
  Network,
  BookOpen,
  CheckCircle2,
  Layers,
  ArrowLeft,
} from "lucide-react";
import { api, ApiError } from "@/services/api";
import { Repository } from "@/types/repo";
import { LanguageBar } from "@/components/LanguageBar";
import { formatNumber } from "@/lib/utils";

export default function RepoDashboardPage() {
  const params = useParams();
  const repoId = params.id as string;

  const [repo, setRepo] = useState<Repository | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>("overview");

  useEffect(() => {
    if (!repoId) return;

    api.getRepo(repoId)
      .then((data) => {
        setRepo(data);
        setLoading(false);
      })
      .catch((err) => {
        setLoading(false);
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError("Failed to load repository details from server.");
        }
      });
  }, [repoId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
        <p className="text-sm text-gray-400">Loading repository dashboard...</p>
      </div>
    );
  }

  if (error || !repo) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-rose-500/10 border border-rose-500/30 flex items-center justify-center mx-auto text-rose-400">
          <AlertCircle className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-white">Repository Not Found</h2>
        <p className="text-gray-400 text-sm max-w-md mx-auto">{error || "Could not retrieve repository data."}</p>
        <Link
          href="/analyze"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-white font-semibold text-sm transition-colors border border-border"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Repository Analysis</span>
        </Link>
      </div>
    );
  }

  const tabs = [
    { id: "overview", label: "Overview", icon: Layers, phase: "Phase 1" },
    { id: "files", label: "File Explorer", icon: FileCode, phase: "Phase 2" },
    { id: "chat", label: "AI RAG Chat", icon: MessageSquare, phase: "Phase 3" },
    { id: "issues", label: "Issue Assistant", icon: CircleDot, phase: "Phase 4" },
    { id: "contribute", label: "Contribute", icon: GitPullRequest, phase: "Phase 5" },
    { id: "security", label: "Security & Quality", icon: ShieldAlert, phase: "Phase 6" },
    { id: "architecture", label: "Architecture", icon: Network, phase: "Phase 7" },
    { id: "docs", label: "Documentation", icon: BookOpen, phase: "Phase 8" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header Banner */}
      <div className="bg-surface/90 border border-border rounded-2xl p-6 sm:p-8 space-y-6 shadow-xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/60 pb-6">
          <div className="space-y-2">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
                <Compass className="w-7 h-7 text-cyan-400" />
                <span>{repo.owner} / <span className="text-cyan-400">{repo.name}</span></span>
              </h1>
              <a
                href={repo.github_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 border border-border transition-colors"
              >
                <span>GitHub</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>

            <p className="text-sm text-gray-300 max-w-3xl leading-relaxed">
              {repo.description || "No description provided for this repository."}
            </p>
          </div>

          {/* Key Quick Stats */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="px-4 py-2 rounded-xl bg-gray-900/80 border border-border text-center">
              <div className="flex items-center gap-1 text-amber-400 text-xs font-semibold">
                <Star className="w-3.5 h-3.5" /> Stars
              </div>
              <div className="text-lg font-bold text-white">{formatNumber(repo.stars)}</div>
            </div>
            <div className="px-4 py-2 rounded-xl bg-gray-900/80 border border-border text-center">
              <div className="flex items-center gap-1 text-violet-400 text-xs font-semibold">
                <GitFork className="w-3.5 h-3.5" /> Forks
              </div>
              <div className="text-lg font-bold text-white">{formatNumber(repo.forks)}</div>
            </div>
            <div className="px-4 py-2 rounded-xl bg-gray-900/80 border border-border text-center">
              <div className="flex items-center gap-1 text-emerald-400 text-xs font-semibold">
                <CircleDot className="w-3.5 h-3.5" /> Issues
              </div>
              <div className="text-lg font-bold text-white">{formatNumber(repo.open_issues)}</div>
            </div>
          </div>
        </div>

        {/* Language Breakdown */}
        <div className="space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wider text-gray-400">
            Language Breakdown
          </div>
          <LanguageBar languages={repo.languages} />
        </div>

        {/* Topics */}
        {repo.topics && repo.topics.length > 0 && (
          <div className="flex flex-wrap gap-2 pt-2">
            {repo.topics.map((topic) => (
              <span
                key={topic}
                className="text-xs px-2.5 py-1 rounded-md bg-gray-800 text-cyan-300 border border-border"
              >
                #{topic}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Feature Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-border overflow-x-auto pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          const href = tab.id === "overview" ? `/repo/${repoId}` : `/repo/${repoId}/${tab.id}`;
          return (
            <Link
              key={tab.id}
              href={href}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-xs whitespace-nowrap transition-all ${
                isActive
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                  : "text-gray-400 hover:text-white hover:bg-surface border border-transparent hover:border-border"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${isActive ? "bg-blue-700 text-blue-100" : "bg-gray-800 text-gray-500"}`}>
                {tab.phase}
              </span>
            </Link>
          );
        })}
      </div>

      {/* Tab Content Display */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Metadata Card */}
          <div className="bg-surface/80 border border-border p-6 rounded-2xl space-y-4">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              Repository Metadata
            </h3>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-2 border-b border-border/50 text-gray-400">
                <span>Default Branch</span>
                <span className="font-mono text-white">{repo.default_branch}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-border/50 text-gray-400">
                <span>Primary Language</span>
                <span className="font-semibold text-cyan-300">{repo.primary_language || "N/A"}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-border/50 text-gray-400">
                <span>Open Issues Count</span>
                <span className="text-white">{repo.open_issues}</span>
              </div>
              <div className="flex justify-between py-2 text-gray-400">
                <span>Last Analyzed</span>
                <span className="text-gray-300">
                  {repo.analyzed_at ? new Date(repo.analyzed_at).toLocaleDateString() : "Just now"}
                </span>
              </div>
            </div>
          </div>

          {/* AI Overview Summary */}
          <div className="md:col-span-2 bg-surface/80 border border-border p-6 rounded-2xl space-y-4">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-violet-400" />
              Repository Quick Insight
            </h3>
            <p className="text-sm text-gray-300 leading-relaxed">
              <strong className="text-white">{repo.name}</strong> is a high-visibility repository owned by{" "}
              <strong className="text-white">{repo.owner}</strong>. It predominantly utilizes{" "}
              <span className="text-cyan-300 font-semibold">{repo.primary_language}</span>.
              Phase 1 repository ingestion and database record registration have completed successfully.
            </p>
            <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-200 flex items-start gap-3">
              <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
              <div>
                <strong>Phase 1 active:</strong> Metadata parsing & database registration ready. Continue to Phase 2 for full file tree cloning and code parsing.
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab !== "overview" && (
        <div className="bg-surface/60 border border-border/80 rounded-2xl p-12 text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-blue-600/10 border border-blue-500/30 flex items-center justify-center mx-auto text-cyan-400">
            <Sparkles className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white capitalize">
            {tabs.find((t) => t.id === activeTab)?.label}
          </h3>
          <p className="text-sm text-gray-400 max-w-md mx-auto">
            This module will be populated in subsequent phases. Phase 1 repository ingestion and dashboard are active and operational.
          </p>
        </div>
      )}
    </div>
  );
}
