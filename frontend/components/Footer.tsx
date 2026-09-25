import Link from "next/link";
import { Compass, Github, Heart } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border/60 bg-background/50 py-12 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-6">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center">
            <Compass className="w-4 h-4 text-cyan-400" />
          </div>
          <span className="text-sm font-semibold text-gray-300">RepoPilot AI</span>
          <span className="text-xs text-gray-500">— GitHub Repository Intelligence Assistant</span>
        </div>

        <div className="flex items-center gap-6 text-xs text-gray-400">
          <Link href="/docs/architecture.md" className="hover:text-white transition-colors">Architecture</Link>
          <Link href="/docs/api.md" className="hover:text-white transition-colors">API Docs</Link>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-white transition-colors">
            <Github className="w-4 h-4" /> GitHub
          </a>
        </div>
      </div>
    </footer>
  );
}
