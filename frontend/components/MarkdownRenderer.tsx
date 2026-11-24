"use client";

import React, { memo } from "react";
import ReactMarkdown, { Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeRaw from "rehype-raw";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { MermaidDiagram } from "./MermaidDiagram";

interface MarkdownRendererProps {
  content: string;
  /** Extra CSS classes on the outermost wrapper */
  className?: string;
  /** Compact mode reduces heading sizes (useful for chat bubbles) */
  compact?: boolean;
}

/* ---------- custom components for react-markdown ---------- */
function buildComponents(compact: boolean): Components {
  return {
    /* ---- Headings ---- */
    h1: ({ children }) => (
      <h1
        className={`${
          compact ? "text-xl" : "text-2xl sm:text-3xl"
        } font-extrabold text-white mt-10 mb-4 pb-2 border-b border-border`}
      >
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2
        className={`${
          compact ? "text-lg" : "text-xl sm:text-2xl"
        } font-bold text-white mt-8 mb-3 pb-1.5 border-b border-border/60`}
      >
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3
        className={`${
          compact ? "text-base" : "text-lg sm:text-xl"
        } font-semibold text-gray-100 mt-6 mb-2`}
      >
        {children}
      </h3>
    ),
    h4: ({ children }) => (
      <h4 className="text-base font-semibold text-gray-200 mt-5 mb-1.5">
        {children}
      </h4>
    ),
    h5: ({ children }) => (
      <h5 className="text-sm font-semibold text-gray-300 mt-4 mb-1">
        {children}
      </h5>
    ),
    h6: ({ children }) => (
      <h6 className="text-sm font-medium text-gray-400 mt-3 mb-1">
        {children}
      </h6>
    ),

    /* ---- Text ---- */
    p: ({ children }) => (
      <p className="text-sm text-gray-300 leading-relaxed my-3">{children}</p>
    ),
    strong: ({ children }) => (
      <strong className="font-semibold text-gray-100">{children}</strong>
    ),
    em: ({ children }) => <em className="italic text-gray-300">{children}</em>,
    del: ({ children }) => (
      <del className="line-through text-gray-500">{children}</del>
    ),
    hr: () => <hr className="border-border my-8" />,

    /* ---- Lists ---- */
    ul: ({ children }) => (
      <ul className="list-disc list-outside pl-6 my-3 space-y-1 text-sm text-gray-300">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="list-decimal list-outside pl-6 my-3 space-y-1 text-sm text-gray-300">
        {children}
      </ol>
    ),
    li: ({ children }) => (
      <li className="leading-relaxed pl-1">{children}</li>
    ),

    /* ---- Blockquote ---- */
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-violet-500/60 bg-violet-500/5 rounded-r-xl pl-4 pr-3 py-2 my-4 text-sm text-gray-300 italic">
        {children}
      </blockquote>
    ),

    /* ---- Links & Images ---- */
    a: ({ href, children }) => (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-cyan-400 hover:text-cyan-300 underline underline-offset-2 decoration-cyan-500/40 transition-colors"
      >
        {children}
      </a>
    ),
    img: ({ src, alt }) => (
      <span className="block my-4">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={src}
          alt={alt || ""}
          loading="lazy"
          className="rounded-xl border border-border max-w-full h-auto"
        />
      </span>
    ),

    /* ---- Tables ---- */
    table: ({ children }) => (
      <div className="my-4 overflow-x-auto rounded-xl border border-border">
        <table className="min-w-full text-sm">{children}</table>
      </div>
    ),
    thead: ({ children }) => (
      <thead className="bg-surface/90 border-b border-border">{children}</thead>
    ),
    tbody: ({ children }) => <tbody className="divide-y divide-border/50">{children}</tbody>,
    tr: ({ children }) => (
      <tr className="hover:bg-surface-hover/40 transition-colors">{children}</tr>
    ),
    th: ({ children }) => (
      <th className="px-4 py-2.5 text-left text-xs font-semibold text-gray-200 whitespace-nowrap">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="px-4 py-2 text-xs text-gray-300 whitespace-nowrap">
        {children}
      </td>
    ),

    /* ---- Inline code ---- */
    code: ({ className, children, ...props }) => {
      const match = /language-(\w+)/.exec(className || "");
      const lang = match ? match[1] : "";
      const codeStr = String(children).replace(/\n$/, "");

      /* Detect inline vs block – react-markdown v9 no longer passes `inline` */
      const isInline = !className && !codeStr.includes("\n");

      if (isInline) {
        return (
          <code className="px-1.5 py-0.5 rounded-md bg-gray-800 border border-border text-cyan-300 text-[13px] font-mono">
            {children}
          </code>
        );
      }

      /* Mermaid code blocks → render as diagram */
      if (lang === "mermaid") {
        return <MermaidDiagram chart={codeStr} />;
      }

      return (
        <SyntaxHighlighter
          style={vscDarkPlus}
          language={lang || "text"}
          PreTag="div"
          customStyle={{
            margin: 0,
            borderRadius: "0.75rem",
            fontSize: "13px",
            background: "#0d1117",
            border: "1px solid rgba(255,255,255,0.08)",
          }}
          showLineNumbers={codeStr.split("\n").length > 3}
          lineNumberStyle={{ color: "#475569", fontSize: "11px" }}
        >
          {codeStr}
        </SyntaxHighlighter>
      );
    },

    /* Wrap fenced code blocks in a container with a copy header */
    pre: ({ children }) => {
      return <div className="my-4 relative group">{children}</div>;
    },
  };
}

export const MarkdownRenderer = memo(function MarkdownRenderer({
  content,
  className = "",
  compact = false,
}: MarkdownRendererProps) {
  const components = React.useMemo(() => buildComponents(compact), [compact]);

  return (
    <div className={`markdown-body ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex, rehypeRaw]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
});

