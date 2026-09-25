"use client";

import Link from "next/link";
import { Compass, GitPullRequest, ShieldCheck, Sparkles, Terminal } from "lucide-react";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-background/80 border-b border-border/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
            <Compass className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-lg text-white tracking-tight">RepoPilot</span>
            <span className="ml-1 text-xs font-semibold px-1.5 py-0.5 rounded bg-blue-500/10 text-cyan-400 border border-cyan-500/20">AI</span>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-400">
          <Link href="/analyze" className="hover:text-white transition-colors flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            Analyze Repo
          </Link>
          <Link href="/#features" className="hover:text-white transition-colors flex items-center gap-1.5">
            <Terminal className="w-4 h-4 text-violet-400" />
            Capabilities
          </Link>
        </nav>

        <div className="flex items-center gap-3">
          <Link
            href="/analyze"
            className="px-4 py-2 text-sm font-semibold rounded-lg bg-gradient-to-r from-blue-600 to-cyan-500 text-white hover:from-blue-500 hover:to-cyan-400 transition-all shadow-lg shadow-blue-600/25 flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            <span>Analyze Repo</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
