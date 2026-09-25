"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  Compass,
  ShieldAlert,
  Loader2,
  RefreshCw,
  Sparkles,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  Info,
  Shield,
  Layers,
} from "lucide-react";
import { api, ApiError } from "@/services/api";
import { Repository, SecurityFinding, SecurityScanSummaryResponse } from "@/types/repo";
import { SecurityFindingCard } from "@/components/SecurityFindingCard";

export default function SecurityAnalysisPage() {
  const params = useParams();
  const repoId = params.id as string;

  const [repo, setRepo] = useState<Repository | null>(null);
  const [findings, setFindings] = useState<SecurityFinding[]>([]);
  const [counts, setCounts] = useState({ critical: 0, high: 0, medium: 0, low: 0 });
  const [selectedSeverity, setSelectedSeverity] = useState<string>("all");

  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSecurityData = async (severityFilter?: string) => {
    try {
      const repoData = await api.getRepo(repoId);
      setRepo(repoData);

      const filterVal = severityFilter && severityFilter !== "all" ? severityFilter : undefined;
      const findingsData = await api.getSecurityFindings(repoId, filterVal);
      setFindings(findingsData);

      // Calculate counts
      const c = { critical: 0, high: 0, medium: 0, low: 0 };
      findingsData.forEach((f) => {
        const s = f.severity.toLowerCase() as keyof typeof c;
        if (s in c) c[s]++;
      });
      setCounts(c);

      setLoading(false);
    } catch (err) {
      setLoading(false);
      setError("Failed to load security analysis data.");
    }
  };

  useEffect(() => {
    if (repoId) {
      loadSecurityData(selectedSeverity);
    }
  }, [repoId, selectedSeverity]);

  const handleRunScan = async () => {
    setScanning(true);
    setError(null);
    try {
      const scanSummary = await api.runSecurityScan(repoId);
      setFindings(scanSummary.findings);
      setCounts(scanSummary.counts);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Security scan failed to complete.");
      }
    } finally {
      setScanning(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
        <p className="text-sm text-gray-400">Loading Static Security Dashboard...</p>
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
              <ShieldAlert className="w-5 h-5 text-rose-400" />
              <span>{repo?.owner} / {repo?.name} — Security & Code-Quality Analysis</span>
            </h1>
            <p className="text-xs text-gray-400">
              Deterministic static security rules (Semgrep, Bandit, OSV-Scanner) with AI vulnerability explanations
            </p>
          </div>
        </div>

        <button
          onClick={handleRunScan}
          disabled={scanning}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-rose-600 to-amber-500 hover:from-rose-500 hover:to-amber-400 text-white font-semibold text-xs transition-all shadow-lg shadow-rose-600/20 flex items-center justify-center gap-2 disabled:opacity-50 shrink-0"
        >
          {scanning ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Running Security Rules...</span>
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4" />
              <span>Run Security Scan</span>
            </>
          )}
        </button>
      </div>

      {error && <p className="text-xs text-rose-400 pl-2">{error}</p>}

      {/* Severity Counters & Tool Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-surface/90 border border-rose-500/30 p-4 rounded-2xl space-y-1">
          <div className="text-xs font-semibold text-rose-400 flex items-center gap-1.5">
            <AlertCircle className="w-4 h-4" /> Critical Vulnerabilities
          </div>
          <div className="text-2xl font-extrabold text-white">{counts.critical}</div>
        </div>

        <div className="bg-surface/90 border border-orange-500/30 p-4 rounded-2xl space-y-1">
          <div className="text-xs font-semibold text-orange-400 flex items-center gap-1.5">
            <AlertCircle className="w-4 h-4" /> High Severity
          </div>
          <div className="text-2xl font-extrabold text-white">{counts.high}</div>
        </div>

        <div className="bg-surface/90 border border-amber-500/30 p-4 rounded-2xl space-y-1">
          <div className="text-xs font-semibold text-amber-400 flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4" /> Medium Severity
          </div>
          <div className="text-2xl font-extrabold text-white">{counts.medium}</div>
        </div>

        <div className="bg-surface/90 border border-cyan-500/30 p-4 rounded-2xl space-y-1">
          <div className="text-xs font-semibold text-cyan-400 flex items-center gap-1.5">
            <Info className="w-4 h-4" /> Low / Info Alerts
          </div>
          <div className="text-2xl font-extrabold text-white">{counts.low}</div>
        </div>
      </div>

      {/* Static Tools Integrated Row */}
      <div className="flex items-center gap-3 p-3.5 rounded-xl bg-gray-900/80 border border-border text-xs text-gray-400">
        <span className="font-semibold text-gray-300 uppercase tracking-wider">Integrated Static Tools:</span>
        <span className="px-2.5 py-0.5 rounded bg-blue-500/10 text-cyan-300 border border-cyan-500/20 font-mono">Semgrep</span>
        <span className="px-2.5 py-0.5 rounded bg-violet-500/10 text-violet-300 border border-violet-500/20 font-mono">Bandit</span>
        <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-mono">OSV-Scanner</span>
      </div>

      {/* Severity Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-border pb-3 overflow-x-auto">
        {[
          { id: "all", label: "All Findings" },
          { id: "critical", label: "Critical" },
          { id: "high", label: "High" },
          { id: "medium", label: "Medium" },
          { id: "low", label: "Low" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setSelectedSeverity(tab.id)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              selectedSeverity === tab.id
                ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                : "bg-surface text-gray-400 hover:text-white border border-border"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Findings List */}
      {findings.length === 0 ? (
        <div className="bg-surface/60 border border-border/80 rounded-2xl p-16 text-center space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-rose-600/10 border border-rose-500/30 flex items-center justify-center mx-auto text-rose-400">
            <Shield className="w-7 h-7" />
          </div>
          <h2 className="text-xl font-bold text-white">No Security Scan Performed Yet</h2>
          <p className="text-sm text-gray-400 max-w-md mx-auto">
            Click "Run Security Scan" to audit hardcoded secrets, shell command injections, SQL vectors, and vulnerable dependencies.
          </p>
          <div>
            <button
              onClick={handleRunScan}
              disabled={scanning}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-rose-600 to-amber-500 hover:from-rose-500 text-white font-semibold text-sm transition-all"
            >
              {scanning ? "Scanning Codebase..." : "Run Security Scan Now"}
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {findings.map((f, idx) => (
            <SecurityFindingCard key={f.id || idx} finding={f} />
          ))}
        </div>
      )}
    </div>
  );
}
