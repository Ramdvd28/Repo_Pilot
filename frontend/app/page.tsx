"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Terminal,
  Search,
  ArrowRight,
  GitBranch,
  ShieldCheck,
  MessageSquareCode,
  CheckCircle2,
  Cpu,
  Layers,
  FileCode2,
  GitPullRequest,
  Bug,
  CornerDownLeft
} from "lucide-react";

export default function LandingPage() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");

  const handleQuickSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      setError("Enter a valid GitHub repository URL (e.g. https://github.com/fastapi/fastapi)");
      return;
    }
    router.push(`/analyze?url=${encodeURIComponent(url.trim())}`);
  };

  const handleSampleClick = (sampleRepo: string) => {
    router.push(`/analyze?url=${encodeURIComponent(`https://github.com/${sampleRepo}`)}`);
  };

  return (
    <div className="space-y-24 pb-20 pt-8">
      {/* Hero Section */}
      <section className="relative pt-12 pb-12 overflow-hidden bg-grid-pattern">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
          
          {/* Status Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900/90 border border-white/10 text-zinc-300 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            <span>RepoPilot Core Engine v1.0</span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-[1.15] font-sans">
            Deep Repository Intelligence & Codebase Navigation
          </h1>

          <p className="max-w-2xl mx-auto text-base text-zinc-400 leading-relaxed font-sans">
            Instant AST file tree parsing, grounded RAG semantic code search, deterministic vulnerability scanning, and automated PR generation for engineering teams.
          </p>

          {/* Developer Command / Input Bar */}
          <div className="max-w-2xl mx-auto pt-2">
            <form onSubmit={handleQuickSubmit} className="relative">
              <div className="flex flex-col sm:flex-row items-stretch gap-2 p-2 rounded-xl bg-zinc-900/90 border border-white/15 shadow-2xl focus-within:border-blue-500/80 transition-all backdrop-blur-xl">
                <div className="flex-1 flex items-center px-3 py-2 gap-3 text-zinc-400 font-mono text-xs">
                  <Terminal className="w-4 h-4 text-zinc-400 shrink-0" />
                  <input
                    type="text"
                    value={url}
                    onChange={(e) => {
                      setUrl(e.target.value);
                      setError("");
                    }}
                    placeholder="https://github.com/owner/repository"
                    className="w-full bg-transparent text-white placeholder-zinc-500 focus:outline-none font-mono text-xs"
                  />
                </div>
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs transition-all shadow-md shadow-blue-600/20 flex items-center justify-center gap-2 border border-blue-400/30 shrink-0"
                >
                  <span>Inspect Repo</span>
                  <CornerDownLeft className="w-3.5 h-3.5 opacity-80" />
                </button>
              </div>
              {error && <p className="text-xs text-rose-400 mt-2 text-left pl-3 font-mono">{error}</p>}
            </form>

            {/* Pre-filled Sample Repositories */}
            <div className="mt-5 flex flex-wrap items-center justify-center gap-2 text-xs font-mono">
              <span className="text-zinc-500 font-sans text-xs">Popular target repos:</span>
              {[
                "fastapi/fastapi",
                "pallets/flask",
                "facebook/react",
                "vercel/next.js",
              ].map((sample) => (
                <button
                  key={sample}
                  onClick={() => handleSampleClick(sample)}
                  className="px-2.5 py-1 rounded bg-zinc-900/90 hover:bg-zinc-800 text-zinc-300 border border-white/10 hover:border-white/20 transition-all text-[11px]"
                >
                  {sample}
                </button>
              ))}
            </div>
          </div>

          {/* Precision Metrics Row */}
          <div className="pt-6 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto font-mono">
            <div className="p-3.5 rounded-xl dev-card text-left space-y-1">
              <div className="text-[10px] text-zinc-500 uppercase tracking-wider">Semantic RAG</div>
              <div className="text-sm font-bold text-white flex items-center gap-1.5">
                <MessageSquareCode className="w-4 h-4 text-blue-400" /> Grounded Citations
              </div>
            </div>

            <div className="p-3.5 rounded-xl dev-card text-left space-y-1">
              <div className="text-[10px] text-zinc-500 uppercase tracking-wider">Security Audit</div>
              <div className="text-sm font-bold text-white flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400" /> Semgrep & Bandit
              </div>
            </div>

            <div className="p-3.5 rounded-xl dev-card text-left space-y-1">
              <div className="text-[10px] text-zinc-500 uppercase tracking-wider">Dependency Graph</div>
              <div className="text-sm font-bold text-white flex items-center gap-1.5">
                <GitBranch className="w-4 h-4 text-cyan-400" /> React Flow Canvas
              </div>
            </div>

            <div className="p-3.5 rounded-xl dev-card text-left space-y-1">
              <div className="text-[10px] text-zinc-500 uppercase tracking-wider">Contribution</div>
              <div className="text-sm font-bold text-white flex items-center gap-1.5">
                <GitPullRequest className="w-4 h-4 text-violet-400" /> PR & Diff Review
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* Feature Capabilities Grid */}
      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-white/[0.08] pb-6 gap-4">
          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-blue-400">Developer Tools</span>
            <h2 className="text-2xl font-bold text-white tracking-tight mt-1">Full-Stack Codebase Inspection</h2>
          </div>
          <p className="text-xs text-zinc-400 max-w-md font-sans">
            Deterministic AST parsing, vector RAG embeddings, and static analysis compiled into a single developer dashboard.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[
            {
              icon: MessageSquareCode,
              accent: "text-blue-400",
              title: "Codebase RAG & Citation Engine",
              description: "Ask technical questions regarding authentication flows, API handlers, or database models. Returns exact file path & line number citations.",
              badge: "RAG / Vector DB"
            },
            {
              icon: GitBranch,
              accent: "text-cyan-400",
              title: "System Topology & Import Graph",
              description: "Extract module boundaries, microservice endpoints, database relations, and external integrations in an interactive visual canvas.",
              badge: "React Flow Topology"
            },
            {
              icon: ShieldCheck,
              accent: "text-emerald-400",
              title: "Static Security & Secret Audit",
              description: "Audit hardcoded secrets, shell command injections, SQL vectors, and vulnerable dependencies using Bandit, Semgrep, and OSV-Scanner rules.",
              badge: "Semgrep + Bandit"
            },
            {
              icon: Bug,
              accent: "text-amber-400",
              title: "Good-First-Issue Radar",
              description: "Categorize open GitHub issues by difficulty level, identify relevant source code files, and synthesize step-by-step implementation strategies.",
              badge: "GitHub REST API"
            },
            {
              icon: FileCode2,
              accent: "text-violet-400",
              title: "Git Diff AI Code Reviewer",
              description: "Evaluate proposed git diffs for correctness, security flaws, performance degradation, and breaking changes with line-by-line replacement fixes.",
              badge: "Code Review Engine"
            },
            {
              icon: GitPullRequest,
              accent: "text-rose-400",
              title: "PR Description Generator",
              description: "Auto-generate GitHub-ready Pull Request titles, key changes lists, testing checklists, and issue references without manual copy-pasting.",
              badge: "PR Automation"
            },
          ].map((item, idx) => (
            <div key={idx} className="dev-card p-6 rounded-2xl space-y-4 relative group">
              <div className="flex items-center justify-between">
                <div className="p-2.5 rounded-lg bg-zinc-900 border border-white/10 text-white">
                  <item.icon className={`w-5 h-5 ${item.accent}`} />
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-900 text-zinc-400 border border-white/10">
                  {item.badge}
                </span>
              </div>
              <h3 className="text-base font-bold text-white tracking-tight">{item.title}</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">{item.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Box */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="dev-card p-8 sm:p-12 rounded-3xl text-center space-y-6 border border-white/10 relative overflow-hidden">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">Inspect Any Repository in Seconds</h2>
          <p className="text-xs sm:text-sm text-zinc-400 max-w-lg mx-auto font-sans">
            Paste a public GitHub repository link to parse stargazers, directory structures, dependencies, open issues, and codebase architecture.
          </p>
          <div>
            <Link
              href="/analyze"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs transition-all shadow-md shadow-blue-600/20 border border-blue-400/30"
            >
              <span>Analyze Repository Now</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
