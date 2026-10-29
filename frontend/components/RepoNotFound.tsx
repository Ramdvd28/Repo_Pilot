"use client";

import Link from "next/link";
import { AlertCircle, ArrowLeft, Database, RefreshCw, Sparkles, Terminal } from "lucide-react";

interface RepoNotFoundProps {
  repoId: string;
  message?: string | null;
  onRetry?: () => void;
}

export function RepoNotFound({ repoId, message, onRetry }: RepoNotFoundProps) {
  return (
    <div className="max-w-2xl mx-auto px-4 py-16 text-center space-y-6">
      {/* Icon Badge */}
      <div className="w-20 h-20 rounded-3xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mx-auto text-rose-400 shadow-xl shadow-rose-500/5">
        <AlertCircle className="w-10 h-10" />
      </div>

      {/* Main Title & ID */}
      <div className="space-y-3">
        <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Repository Not Found
        </h2>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-gray-900/90 border border-border text-xs font-mono text-gray-300">
          <Terminal className="w-3.5 h-3.5 text-cyan-400" />
          <span>ID: {repoId}</span>
        </div>
        <p className="text-gray-400 text-sm max-w-lg mx-auto leading-relaxed">
          {message || "The requested repository record could not be found in the database."}
        </p>
      </div>

      {/* Serverless Persistence Notice */}
      <div className="bg-surface/90 border border-amber-500/20 rounded-2xl p-5 text-left space-y-2 shadow-lg">
        <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs tracking-wide uppercase">
          <Database className="w-4 h-4 shrink-0" />
          <span>Why does this happen in serverless deployments?</span>
        </div>
        <p className="text-xs text-gray-300 leading-relaxed">
          On serverless platforms like Vercel, function containers are ephemeral and isolated. If a managed PostgreSQL database (
          <code className="px-1.5 py-0.5 rounded bg-gray-900 border border-border text-cyan-300 font-mono text-[11px]">DATABASE_URL</code>
          {" or "}
          <code className="px-1.5 py-0.5 rounded bg-gray-900 border border-border text-cyan-300 font-mono text-[11px]">POSTGRES_URL</code>
          ) is not configured, repository records stored in temporary instance storage do not persist across separate function instances or cold starts.
        </p>
        <p className="text-xs text-gray-400 leading-relaxed pt-1">
          To resolve this in production, add a persistent PostgreSQL database (such as Neon, Supabase, or Vercel Postgres) in your Vercel Project Settings &gt; Environment Variables.
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
        {onRetry && (
          <button
            onClick={onRetry}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-white font-medium text-sm transition-all border border-border shadow"
          >
            <RefreshCw className="w-4 h-4 text-cyan-400" />
            <span>Try Again</span>
          </button>
        )}
        <Link
          href="/analyze"
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-semibold text-sm transition-all shadow-lg shadow-blue-500/20"
        >
          <Sparkles className="w-4 h-4" />
          <span>Analyze Repository</span>
        </Link>
        <Link
          href="/"
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-surface hover:bg-gray-800 text-gray-300 hover:text-white font-medium text-sm transition-colors border border-border"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>All Repositories</span>
        </Link>
      </div>
    </div>
  );
}
