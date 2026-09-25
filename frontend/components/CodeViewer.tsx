"use client";

import { useState } from "react";
import Editor from "@monaco-editor/react";
import { Check, Copy, FileCode, Layers } from "lucide-react";

interface CodeViewerProps {
  filePath: string;
  language?: string;
  content: string;
  readOnly?: boolean;
}

const MONACO_LANGUAGE_MAP: Record<string, string> = {
  Python: "python",
  TypeScript: "typescript",
  JavaScript: "javascript",
  Go: "go",
  Rust: "rust",
  Java: "java",
  "C++": "cpp",
  C: "c",
  "C#": "csharp",
  HTML: "html",
  CSS: "css",
  JSON: "json",
  Markdown: "markdown",
  SQL: "sql",
  Shell: "shell",
  YAML: "yaml",
  Dockerfile: "dockerfile",
};

export function CodeViewer({ filePath, language, content }: CodeViewerProps) {
  const [copied, setCopied] = useState(false);

  const monacoLang = (language && MONACO_LANGUAGE_MAP[language]) || "plaintext";
  const lineCount = content ? content.split("\n").length : 0;

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col h-full bg-surface/90 border border-border rounded-2xl overflow-hidden shadow-xl">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-900/90 border-b border-border/80 text-xs">
        <div className="flex items-center gap-2 text-gray-300 font-mono truncate">
          <FileCode className="w-4 h-4 text-cyan-400 shrink-0" />
          <span className="font-semibold text-white truncate">{filePath}</span>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          {language && (
            <span className="px-2 py-0.5 rounded bg-blue-500/10 text-cyan-300 border border-cyan-500/20 font-mono font-medium">
              {language}
            </span>
          )}
          <span className="text-gray-500 font-mono">{lineCount} lines</span>
          <button
            onClick={handleCopy}
            className="p-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white transition-colors flex items-center gap-1 text-xs"
            title="Copy code"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Editor Body */}
      <div className="flex-1 min-h-[500px]">
        <Editor
          height="100%"
          language={monacoLang}
          value={content}
          theme="vs-dark"
          options={{
            readOnly: true,
            minimap: { enabled: true },
            fontSize: 13,
            lineNumbers: "on",
            scrollBeyondLastLine: false,
            wordWrap: "on",
            automaticLayout: true,
            padding: { top: 12, bottom: 12 },
            fontFamily: "Fira Code, Menlo, Monaco, 'Courier New', monospace",
          }}
        />
      </div>
    </div>
  );
}
