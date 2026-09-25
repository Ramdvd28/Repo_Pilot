"use client";

import Link from "next/link";
import { GitFork, Star, CircleDot, ArrowRight, BookOpen } from "lucide-react";
import { Repository } from "@/types/repo";
import { formatNumber } from "@/lib/utils";

interface RepoCardProps {
  repo: Repository;
}

export function RepoCard({ repo }: RepoCardProps) {
  return (
    <div className="bg-surface/80 border border-border/80 hover:border-blue-500/50 rounded-xl p-5 transition-all hover:shadow-xl hover:shadow-blue-500/5 flex flex-col justify-between group">
      <div>
        <div className="flex items-start justify-between gap-3 mb-2">
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-blue-400 shrink-0" />
            <span className="font-semibold text-white group-hover:text-blue-400 transition-colors truncate">
              {repo.owner}/{repo.name}
            </span>
          </div>
          {repo.primary_language && (
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-cyan-300 border border-cyan-500/20 shrink-0">
              {repo.primary_language}
            </span>
          )}
        </div>

        <p className="text-xs text-gray-400 line-clamp-2 mb-4 leading-relaxed">
          {repo.description || "No description provided for this repository."}
        </p>
      </div>

      <div>
        <div className="flex items-center gap-4 text-xs text-gray-400 border-t border-border/50 pt-3 mb-3">
          <div className="flex items-center gap-1">
            <Star className="w-3.5 h-3.5 text-amber-400" />
            <span>{formatNumber(repo.stars)}</span>
          </div>
          <div className="flex items-center gap-1">
            <GitFork className="w-3.5 h-3.5 text-violet-400" />
            <span>{formatNumber(repo.forks)}</span>
          </div>
          <div className="flex items-center gap-1">
            <CircleDot className="w-3.5 h-3.5 text-emerald-400" />
            <span>{formatNumber(repo.open_issues)} issues</span>
          </div>
        </div>

        <Link
          href={`/repo/${repo.id}`}
          className="w-full text-xs font-semibold py-2 px-3 rounded-lg bg-gray-800 hover:bg-blue-600 text-gray-300 hover:text-white transition-all flex items-center justify-center gap-1.5"
        >
          <span>Open Dashboard</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
