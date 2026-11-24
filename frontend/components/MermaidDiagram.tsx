"use client";

import { useEffect, useRef, useState, useId } from "react";

interface MermaidDiagramProps {
  chart: string;
}

export function MermaidDiagram({ chart }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const uniqueId = useId().replace(/:/g, "_");

  useEffect(() => {
    let cancelled = false;

    const renderChart = async () => {
      try {
        const mermaid = (await import("mermaid")).default;
        mermaid.initialize({
          startOnLoad: false,
          theme: "dark",
          themeVariables: {
            darkMode: true,
            background: "#0f141f",
            primaryColor: "#6366f1",
            primaryTextColor: "#e2e8f0",
            primaryBorderColor: "#4f46e5",
            secondaryColor: "#1e293b",
            secondaryTextColor: "#cbd5e1",
            secondaryBorderColor: "#334155",
            tertiaryColor: "#0f172a",
            tertiaryTextColor: "#94a3b8",
            tertiaryBorderColor: "#1e293b",
            lineColor: "#64748b",
            textColor: "#e2e8f0",
            mainBkg: "#1e293b",
            nodeBkg: "#1e293b",
            nodeBorder: "#4f46e5",
            clusterBkg: "#0f172a",
            clusterBorder: "#334155",
            titleColor: "#e2e8f0",
            edgeLabelBackground: "#0f141f",
            nodeTextColor: "#e2e8f0",
          },
          fontFamily: "Inter, system-ui, sans-serif",
          fontSize: 14,
          flowchart: { curve: "basis", padding: 15 },
          sequence: { actorMargin: 50 },
        });

        const id = `mermaid_${uniqueId}_${Date.now()}`;
        const { svg: renderedSvg } = await mermaid.render(id, chart.trim());

        if (!cancelled) {
          setSvg(renderedSvg);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to render diagram"
          );
          setSvg("");
        }
      }
    };

    renderChart();
    return () => {
      cancelled = true;
    };
  }, [chart, uniqueId]);

  if (error) {
    return (
      <div className="my-4 rounded-xl border border-amber-500/30 bg-amber-500/5 p-4">
        <div className="flex items-center gap-2 text-xs font-semibold text-amber-400 mb-2">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Diagram could not be rendered
        </div>
        <pre className="text-xs text-gray-400 font-mono whitespace-pre-wrap overflow-x-auto">{chart}</pre>
      </div>
    );
  }

  if (!svg) {
    return (
      <div className="my-4 flex items-center justify-center p-8 rounded-xl border border-border bg-surface/50">
        <div className="w-5 h-5 border-2 border-violet-400 border-t-transparent rounded-full animate-spin" />
        <span className="ml-3 text-xs text-gray-400">Rendering diagram…</span>
      </div>
    );
  }

  return (
    <div className="my-4 overflow-x-auto rounded-xl border border-border bg-[#0d1117] p-4">
      <div
        ref={containerRef}
        className="flex justify-center [&_svg]:max-w-full"
        dangerouslySetInnerHTML={{ __html: svg }}
      />
    </div>
  );
}

