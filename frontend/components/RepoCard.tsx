"use client";

import Link from "next/link";
import { GitFork, Star, CircleDot, ArrowRight, FolderGit2 } from "lucide-react";
import { Repository } from "@/types/repo";
import { formatNumber } from "@/lib/utils";

interface RepoCardProps {
  repo: Repository;
}

export function RepoCard({ repo }: RepoCardProps) {
  return (
    <div className="dev-card p-5 rounded-xl border border-white/10 flex flex-col justify-between group transition-all">
      <div>
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex items-center gap-2 min-w-0">
            <FolderGit2 className="w-4 h-4 text-blue-400 shrink-0" />
            <span className="font-semibold text-xs text-white group-hover:text-blue-400 transition-colors truncate font-mono">
              {repo.owner}/{repo.name}
            </span>
          </div>
          {repo.primary_language && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-900 text-zinc-300 border border-white/10 shrink-0">
              {repo.primary_language}
            </span>
          )}
        </div>

        <p className="text-xs text-zinc-400 line-clamp-2 mb-4 leading-relaxed font-sans">
          {repo.description || "No description provided for this repository."}
        </p>
      </div>

      <div>
        <div className="flex items-center gap-4 text-[11px] font-mono text-zinc-400 border-t border-white/[0.08] pt-3 mb-3">
          <div className="flex items-center gap-1">
            <Star className="w-3 h-3 text-amber-400" />
            <span>{formatNumber(repo.stars)}</span>
          </div>
          <div className="flex items-center gap-1">
            <GitFork className="w-3 h-3 text-zinc-400" />
            <span>{formatNumber(repo.forks)}</span>
          </div>
          <div className="flex items-center gap-1">
            <CircleDot className="w-3 h-3 text-emerald-400" />
            <span>{formatNumber(repo.open_issues)} issues</span>
          </div>
        </div>

        <Link
          href={`/repo/${repo.id}`}
          className="w-full text-xs font-medium py-2 px-3 rounded-lg bg-zinc-900 hover:bg-blue-600 text-zinc-200 hover:text-white transition-all flex items-center justify-center gap-1.5 border border-white/10 hover:border-blue-400/30"
        >
          <span>Open Dashboard</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
