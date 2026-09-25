"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Compass,
  Sparkles,
  Bot,
  ShieldCheck,
  GitPullRequest,
  Network,
  Bug,
  BookOpen,
  ArrowRight,
  Code2,
  CheckCircle2,
  Zap,
} from "lucide-react";

export default function LandingPage() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");

  const handleQuickSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      setError("Please enter a valid GitHub repository URL");
      return;
    }
    router.push(`/analyze?url=${encodeURIComponent(url.trim())}`);
  };

  const handleSampleClick = (sampleRepo: string) => {
    router.push(`/analyze?url=${encodeURIComponent(`https://github.com/${sampleRepo}`)}`);
  };

  return (
    <div className="space-y-24 pb-16">
      {/* Hero Section */}
      <section className="relative pt-20 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/30 via-background to-background -z-10" />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-cyan-400 text-xs font-semibold tracking-wide uppercase shadow-inner">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI-Powered GitHub Intelligence Engine</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Navigate, Understand & Contribute to Any Codebase with{" "}
            <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-violet-400 bg-clip-text text-transparent">
              RepoPilot AI
            </span>
          </h1>

          <p className="max-w-3xl mx-auto text-lg text-gray-400 leading-relaxed">
            Enter any public GitHub URL to instantly analyze repository architecture, chat with code via RAG, detect security vulnerabilities, find beginner-friendly issues, and generate production-ready PR descriptions.
          </p>

          {/* Quick URL Input */}
          <div className="max-w-2xl mx-auto pt-4">
            <form onSubmit={handleQuickSubmit} className="relative group">
              <div className="flex flex-col sm:flex-row gap-2 bg-surface/90 border border-border p-2 rounded-2xl shadow-2xl focus-within:border-blue-500 transition-all">
                <div className="flex-1 flex items-center px-4 py-2 gap-3">
                  <Compass className="w-5 h-5 text-cyan-400 shrink-0" />
                  <input
                    type="text"
                    value={url}
                    onChange={(e) => {
                      setUrl(e.target.value);
                      setError("");
                    }}
                    placeholder="https://github.com/owner/repository"
                    className="w-full bg-transparent text-white placeholder-gray-500 focus:outline-none text-sm"
                  />
                </div>
                <button
                  type="submit"
                  className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-semibold text-sm transition-all shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2"
                >
                  <span>Analyze Repo</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
              {error && <p className="text-xs text-rose-400 mt-2 text-left pl-4">{error}</p>}
            </form>

            {/* Example Repos */}
            <div className="mt-4 flex flex-wrap items-center justify-center gap-2 text-xs text-gray-400">
              <span className="font-medium text-gray-500">Try popular repositories:</span>
              {[
                "fastapi/fastapi",
                "pallets/flask",
                "facebook/react",
                "vercel/next.js",
              ].map((sample) => (
                <button
                  key={sample}
                  onClick={() => handleSampleClick(sample)}
                  className="px-2.5 py-1 rounded-lg bg-gray-800/80 hover:bg-gray-700 text-gray-300 border border-border/60 transition-colors"
                >
                  {sample}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl font-bold text-white tracking-tight">Full-Spectrum Repository Intelligence</h2>
          <p className="text-gray-400 max-w-2xl mx-auto text-sm">
            Everything developer teams and open-source contributors need to explore, audit, and contribute to complex codebases.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            {
              icon: Bot,
              color: "text-blue-400",
              title: "Repository RAG Chat",
              description: "Ask questions about auth flows, API handlers, or database connection logic with grounded line-number references.",
            },
            {
              icon: Network,
              color: "text-cyan-400",
              title: "Architecture Visualizer",
              description: "Extract real dependency relationships and import graphs visually using React Flow interactive diagrams.",
            },
            {
              icon: ShieldCheck,
              color: "text-emerald-400",
              title: "Static Security & Quality",
              description: "Run deterministic tools like Semgrep, Bandit, and OSV-Scanner with AI explanations of real findings.",
            },
            {
              icon: Bug,
              color: "text-amber-400",
              title: "Issue Assistant",
              description: "Discover good-first-issues, classify difficulty, and get step-by-step implementation strategies.",
            },
            {
              icon: Code2,
              color: "text-violet-400",
              title: "Smart Code Reviewer",
              description: "Paste git diffs to receive detailed reviews on correctness, safety, performance, and breaking changes.",
            },
            {
              icon: GitPullRequest,
              color: "text-rose-400",
              title: "PR Description Generator",
              description: "Generate structured, professional Pull Request titles, summaries, and testing checklists automatically.",
            },
          ].map((feature, idx) => (
            <div
              key={idx}
              className="bg-surface/60 border border-border/80 hover:border-blue-500/40 p-6 rounded-2xl transition-all hover:shadow-xl hover:shadow-blue-500/5 group"
            >
              <div className="w-12 h-12 rounded-xl bg-gray-800/80 border border-border flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <feature.icon className={`w-6 h-6 ${feature.color}`} />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-r from-blue-900/40 via-surface to-cyan-900/30 border border-blue-500/30 p-10 rounded-3xl text-center space-y-6 shadow-2xl">
          <h2 className="text-3xl font-bold text-white">Ready to inspect your first repository?</h2>
          <p className="text-gray-300 max-w-xl mx-auto text-sm">
            Analyze any repository URL in seconds to inspect language breakdown, open issues, and repository stats.
          </p>
          <div>
            <Link
              href="/analyze"
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-semibold shadow-lg shadow-blue-600/30 transition-all"
            >
              <span>Get Started Now</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
