import Link from "next/link";
import { Command, Github, Terminal } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-white/[0.08] bg-[#090b11] py-12 mt-20 text-xs font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-6">
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 rounded bg-zinc-900 border border-white/10 flex items-center justify-center text-zinc-400">
            <Command className="w-3.5 h-3.5" />
          </div>
          <span className="font-semibold text-zinc-300">RepoPilot</span>
          <span className="text-zinc-500">— GitHub Repository Intelligence & Contribution System</span>
        </div>

        <div className="flex items-center gap-6 text-zinc-400 font-medium">
          <Link href="/analyze" className="hover:text-white transition-colors">Analyzer</Link>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="flex items-center gap-1.5 hover:text-white transition-colors font-mono">
            <Github className="w-3.5 h-3.5" /> GitHub
          </a>
        </div>
      </div>
    </footer>
  );
}
