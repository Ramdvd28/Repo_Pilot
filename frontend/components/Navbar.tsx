"use client";

import Link from "next/link";
import { Command, GitBranch, Terminal, ShieldCheck, ArrowRight } from "lucide-react";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-xl bg-[#090b11]/80 border-b border-white/[0.08] transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Status Badge */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-white/10 flex items-center justify-center text-white group-hover:border-blue-500/50 transition-colors">
            <Command className="w-4 h-4 text-blue-400" />
          </div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-base text-white tracking-tight font-sans">RepoPilot</span>
            <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-white/10">
              v1.0
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-8 text-xs font-medium text-zinc-400">
          <Link href="/analyze" className="hover:text-white transition-colors flex items-center gap-2">
            <Terminal className="w-3.5 h-3.5 text-zinc-400" />
            <span>Repository Analyzer</span>
          </Link>
          <Link href="/#features" className="hover:text-white transition-colors flex items-center gap-2">
            <GitBranch className="w-3.5 h-3.5 text-zinc-400" />
            <span>Architecture & Tools</span>
          </Link>
          <span className="flex items-center gap-1.5 text-[11px] font-mono text-emerald-400/90 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>Engine Ready</span>
          </span>
        </nav>

        {/* Action Button */}
        <div className="flex items-center gap-3">
          <Link
            href="/analyze"
            className="px-3.5 py-2 text-xs font-medium rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-md shadow-blue-600/20 flex items-center gap-1.5 border border-blue-400/30"
          >
            <span>Inspect Repo</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </header>
  );
}
