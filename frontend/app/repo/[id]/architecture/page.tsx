"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  Network,
  Loader2,
  RefreshCw,
  ArrowLeft,
  Layers,
  Server,
  Database,
  Sparkles,
  Github,
  Folder,
  Layout,
  Info,
  ChevronRight
} from "lucide-react";
import { api, ApiError } from "@/services/api";
import { Repository, ArchitectureGraphResponse, ArchNode } from "@/types/repo";

export default function ArchitectureVisualizationPage() {
  const params = useParams();
  const repoId = params.id as string;

  const [repo, setRepo] = useState<Repository | null>(null);
  const [graph, setGraph] = useState<ArchitectureGraphResponse | null>(null);
  const [selectedNode, setSelectedNode] = useState<ArchNode | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>("all");

  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadGraph = async () => {
    try {
      const repoData = await api.getRepo(repoId);
      setRepo(repoData);

      const graphData = await api.getArchitectureGraph(repoId);
      setGraph(graphData);
      if (graphData.nodes.length > 0) {
        setSelectedNode(graphData.nodes[0]);
      }
      setLoading(false);
    } catch (err) {
      setLoading(false);
      setError("Failed to load architecture graph.");
    }
  };

  useEffect(() => {
    if (repoId) loadGraph();
  }, [repoId]);

  const handleRegenerate = async () => {
    setGenerating(true);
    setError(null);
    try {
      const freshGraph = await api.generateArchitectureGraph(repoId);
      setGraph(freshGraph);
      if (freshGraph.nodes.length > 0) {
        setSelectedNode(freshGraph.nodes[0]);
      }
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
      else setError("Failed to re-analyze repository architecture.");
    } finally {
      setGenerating(false);
    }
  };

  const categoryIcons: Record<string, any> = {
    core: Layers,
    frontend: Layout,
    backend: Server,
    database: Database,
    ai: Sparkles,
    external: Github,
    module: Folder,
  };

  const filteredNodes = graph?.nodes.filter((node) => {
    if (activeCategory === "all") return true;
    return node.data.category === activeCategory;
  }) || [];

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
        <p className="text-sm text-gray-400">Loading Repository Architecture Visualization...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-surface/80 border border-border p-5 rounded-2xl">
        <div className="flex items-center gap-3">
          <Link
            href={`/repo/${repoId}`}
            className="p-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors border border-border"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-lg font-bold text-white flex items-center gap-2">
              <Network className="w-5 h-5 text-cyan-400" />
              <span>{repo?.owner} / {repo?.name} — System Architecture Map</span>
            </h1>
            <p className="text-xs text-gray-400">
              Extracted component topology, module boundaries, database relations, and API endpoints
            </p>
          </div>
        </div>

        <button
          onClick={handleRegenerate}
          disabled={generating}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold text-xs transition-all shadow-lg shadow-cyan-600/20 flex items-center justify-center gap-2 disabled:opacity-50 shrink-0"
        >
          {generating ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Analyzing Architecture...</span>
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4" />
              <span>Re-analyze Graph</span>
            </>
          )}
        </button>
      </div>

      {error && <p className="text-xs text-rose-400 pl-2">{error}</p>}

      {/* Category Filter Bar */}
      <div className="flex items-center gap-2 border-b border-border pb-3 overflow-x-auto">
        {[
          { id: "all", label: `All Components (${graph?.nodes.length || 0})` },
          { id: "core", label: "Core App" },
          { id: "frontend", label: "Frontend Layer" },
          { id: "backend", label: "Backend Microservice" },
          { id: "database", label: "Database Store" },
          { id: "ai", label: "AI Abstraction" },
          { id: "external", label: "External Integrations" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveCategory(tab.id)}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              activeCategory === tab.id
                ? "bg-cyan-600 text-white shadow-lg shadow-cyan-600/20"
                : "bg-surface text-gray-400 hover:text-white border border-border"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Interactive Visual Graph Canvas Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Component Canvas Cards Grid */}
        <div className="lg:col-span-2 bg-gray-950/90 border border-border/80 rounded-2xl p-6 min-h-[500px] space-y-6 relative overflow-hidden shadow-2xl">
          <div className="flex items-center justify-between border-b border-border/40 pb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-cyan-400 flex items-center gap-2">
              <Layers className="w-4 h-4" /> Dynamic Component Nodes ({filteredNodes.length})
            </span>
            <span className="text-[11px] text-gray-400 font-mono">Total Edges: {graph?.total_edges || 0}</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {filteredNodes.map((node) => {
              const IconComp = categoryIcons[node.data.category] || Layers;
              const isSelected = selectedNode?.id === node.id;
              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`p-5 rounded-2xl border transition-all cursor-pointer space-y-3 relative group ${
                    isSelected
                      ? "bg-cyan-950/40 border-cyan-400 shadow-xl shadow-cyan-500/10 ring-1 ring-cyan-400"
                      : "bg-surface/80 border-border hover:border-cyan-500/50 hover:bg-surface"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className={`p-2 rounded-xl border ${isSelected ? "bg-cyan-500/20 text-cyan-300 border-cyan-400/50" : "bg-gray-800 text-cyan-400 border-border"}`}>
                        <IconComp className="w-4 h-4" />
                      </div>
                      <span className="text-xs font-bold text-white tracking-wide">{node.data.label}</span>
                    </div>

                    <span className="text-[10px] px-2 py-0.5 rounded-full font-mono uppercase bg-gray-800 text-gray-300 border border-border">
                      {node.data.category}
                    </span>
                  </div>

                  <p className="text-xs text-gray-400 leading-relaxed font-sans line-clamp-2">
                    {node.data.description}
                  </p>

                  <div className="flex items-center justify-between text-[11px] text-cyan-400 pt-1 font-semibold">
                    <span>Inspect Details</span>
                    <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Connection Edges Overview Table */}
          <div className="pt-4 border-t border-border/40 space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400">Architectural Relations & Edges</h4>
            <div className="space-y-2">
              {graph?.edges.map((edge) => (
                <div key={edge.id} className="flex items-center justify-between p-2.5 rounded-xl bg-gray-900/60 border border-border/50 text-xs font-mono">
                  <div className="flex items-center gap-2 text-cyan-300">
                    <span>{edge.source}</span>
                    <span className="text-gray-500">→</span>
                    <span className="text-violet-300">{edge.target}</span>
                  </div>
                  <span className="text-[11px] px-2 py-0.5 rounded bg-gray-800 text-gray-400 border border-border">
                    {edge.label || "connects"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Node Inspector Side Panel */}
        <div className="bg-surface/90 border border-border rounded-2xl p-6 space-y-5 shadow-xl">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 border-b border-border pb-3">
            <Info className="w-4 h-4 text-cyan-400" />
            <span>Component Inspector</span>
          </h3>

          {selectedNode ? (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/30 space-y-2">
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-900 text-cyan-200 border border-cyan-400/30">
                  {selectedNode.data.category}
                </span>
                <h4 className="text-base font-bold text-white">{selectedNode.data.label}</h4>
                <p className="text-xs text-cyan-100 leading-relaxed font-sans">
                  {selectedNode.data.description}
                </p>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-2 border-b border-border/50 text-gray-400">
                  <span>Node Identifier</span>
                  <span className="font-mono text-gray-200">{selectedNode.id}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border/50 text-gray-400">
                  <span>Category Type</span>
                  <span className="font-semibold text-cyan-300 uppercase">{selectedNode.data.category}</span>
                </div>
                <div className="flex justify-between py-2 text-gray-400">
                  <span>Canvas Position</span>
                  <span className="font-mono text-gray-200">X: {selectedNode.position.x}, Y: {selectedNode.position.y}</span>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-xs text-gray-400 italic">Select a component node on the canvas to inspect details.</p>
          )}
        </div>
      </div>
    </div>
  );
}
