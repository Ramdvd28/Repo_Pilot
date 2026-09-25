"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  Compass,
  GitPullRequest,
  Code2,
  Sparkles,
  Loader2,
  Check,
  Copy,
  ArrowLeft,
  FileText,
  ShieldCheck,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import { api, ApiError } from "@/services/api";
import { CodeReviewResponse, PrGenerateResponse } from "@/types/repo";
import { CodeReviewCard } from "@/components/CodeReviewCard";

const SAMPLE_GIT_DIFF = `diff --git a/backend/app/api/v1/endpoints/repos.py b/backend/app/api/v1/endpoints/repos.py
index a1b2c3d..e5f6a7b 100644
--- a/backend/app/api/v1/endpoints/repos.py
+++ b/backend/app/api/v1/endpoints/repos.py
@@ -25,6 +25,12 @@ async def analyze_repository(payload: RepoAnalyzeRequest):
+    # Sanitize incoming GitHub URL
+    if ".." in payload.github_url:
+        raise HTTPException(status_code=400, detail="Invalid URL")
+
     meta = await github_service.fetch_repository_metadata(payload.github_url)
     repo = await repo_service.create_or_update_repo(meta)
     return repo
`;

export default function ContributionWorkspacePage() {
  const params = useParams();
  const repoId = params.id as string;

  const [gitDiff, setGitDiff] = useState<string>("");
  const [testResults, setTestResults] = useState<string>("");
  const [issueNumber, setIssueNumber] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"review" | "pr">("review");

  const [reviewResult, setReviewResult] = useState<CodeReviewResponse | null>(null);
  const [prResult, setPrResult] = useState<PrGenerateResponse | null>(null);

  const [loadingReview, setLoadingReview] = useState(false);
  const [loadingPr, setLoadingPr] = useState(false);
  const [copiedPr, setCopiedPr] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLoadSample = () => {
    setGitDiff(SAMPLE_GIT_DIFF);
    setTestResults("pytest - 19 passed in 0.85s");
    setIssueNumber("1");
  };

  const handleRunReview = async () => {
    if (!gitDiff.trim()) {
      setError("Please paste a valid git diff.");
      return;
    }

    setLoadingReview(true);
    setError(null);
    setActiveTab("review");

    try {
      const issueNum = issueNumber ? parseInt(issueNumber, 10) : undefined;
      const res = await api.reviewCodeDiff(repoId, gitDiff, issueNum);
      setReviewResult(res);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to run code review.");
      }
    } finally {
      setLoadingReview(false);
    }
  };

  const handleGeneratePr = async () => {
    if (!gitDiff.trim()) {
      setError("Please paste a valid git diff.");
      return;
    }

    setLoadingPr(true);
    setError(null);
    setActiveTab("pr");

    try {
      const issueNum = issueNumber ? parseInt(issueNumber, 10) : undefined;
      const res = await api.generatePrDescription(repoId, gitDiff, issueNum, testResults);
      setPrResult(res);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to generate PR description.");
      }
    } finally {
      setLoadingPr(false);
    }
  };

  const handleCopyPr = () => {
    if (!prResult) return;
    const fullText = `# ${prResult.title}\n\n${prResult.markdown_description}`;
    navigator.clipboard.writeText(fullText);
    setCopiedPr(true);
    setTimeout(() => setCopiedPr(false), 2000);
  };

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
              <GitPullRequest className="w-5 h-5 text-cyan-400" />
              <span>Contribution Workspace — Code Review & PR Generator</span>
            </h1>
            <p className="text-xs text-gray-400">
              Analyze proposed git diffs for correctness & security, and generate GitHub PR descriptions
            </p>
          </div>
        </div>

        <button
          onClick={handleLoadSample}
          className="px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-cyan-300 border border-border text-xs font-semibold transition-colors shrink-0 flex items-center gap-1.5"
        >
          <Code2 className="w-3.5 h-3.5" />
          <span>Load Sample Diff</span>
        </button>
      </div>

      {error && <p className="text-xs text-rose-400 pl-2">{error}</p>}

      {/* Workspace Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Git Diff Input & Configuration */}
        <div className="bg-surface/90 border border-border p-6 rounded-2xl space-y-5 shadow-xl flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-gray-300 uppercase tracking-wider flex items-center gap-1.5">
                <Code2 className="w-4 h-4 text-cyan-400" />
                Git Diff Payload
              </label>
              <span className="text-[11px] text-gray-500 font-mono">paste output from git diff</span>
            </div>

            <textarea
              rows={12}
              value={gitDiff}
              onChange={(e) => setGitDiff(e.target.value)}
              placeholder="Paste git diff output here (e.g. diff --git a/file b/file ...)"
              className="w-full bg-gray-900 border border-border focus:border-blue-500 rounded-xl p-4 text-xs font-mono text-gray-200 placeholder-gray-600 focus:outline-none transition-colors"
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                  Linked Issue Number (Optional)
                </label>
                <input
                  type="text"
                  value={issueNumber}
                  onChange={(e) => setIssueNumber(e.target.value)}
                  placeholder="e.g. 42"
                  className="w-full bg-gray-900 border border-border rounded-xl px-3 py-2 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                  Test Results (Optional)
                </label>
                <input
                  type="text"
                  value={testResults}
                  onChange={(e) => setTestResults(e.target.value)}
                  placeholder="e.g. pytest 12 passed"
                  className="w-full bg-gray-900 border border-border rounded-xl px-3 py-2 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-border/80">
            <button
              onClick={handleRunReview}
              disabled={loadingReview || !gitDiff.trim()}
              className="flex-1 py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-semibold text-xs transition-all shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loadingReview ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Evaluating Code Diff...</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  <span>Run AI Code Review</span>
                </>
              )}
            </button>

            <button
              onClick={handleGeneratePr}
              disabled={loadingPr || !gitDiff.trim()}
              className="flex-1 py-3 px-4 rounded-xl bg-gray-800 hover:bg-gray-700 text-cyan-300 border border-border font-semibold text-xs transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loadingPr ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Generating PR...</span>
                </>
              ) : (
                <>
                  <GitPullRequest className="w-4 h-4 text-violet-400" />
                  <span>Generate PR Description</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Review Findings / PR Generator Output Tabs */}
        <div className="bg-surface/90 border border-border p-6 rounded-2xl space-y-4 shadow-xl flex flex-col h-full min-h-[550px]">
          {/* Tab Selection */}
          <div className="flex items-center justify-between border-b border-border/80 pb-3">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveTab("review")}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === "review"
                    ? "bg-blue-600 text-white shadow"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                Code Review ({reviewResult?.findings.length || 0})
              </button>
              <button
                onClick={() => setActiveTab("pr")}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === "pr"
                    ? "bg-blue-600 text-white shadow"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                PR Generator
              </button>
            </div>

            {activeTab === "pr" && prResult && (
              <button
                onClick={handleCopyPr}
                className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-xs font-semibold text-gray-300 hover:text-white transition-colors flex items-center gap-1.5 border border-border"
              >
                {copiedPr ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy Markdown</span>
                  </>
                )}
              </button>
            )}
          </div>

          {/* Tab 1: Code Review Output */}
          {activeTab === "review" && (
            <div className="flex-1 overflow-y-auto space-y-4 pr-1 custom-scrollbar">
              {!reviewResult ? (
                <div className="flex flex-col items-center justify-center h-full text-center space-y-3 py-16 text-gray-400">
                  <ShieldCheck className="w-10 h-10 text-gray-600" />
                  <p className="text-sm">Paste a git diff and click "Run AI Code Review" to inspect findings.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Score & Summary Banner */}
                  <div className="p-4 rounded-2xl bg-gray-900 border border-border flex items-center justify-between gap-4">
                    <div>
                      <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                        Overall Review Score
                      </div>
                      <div className="text-2xl font-bold text-white mt-0.5">
                        <span className={reviewResult.score >= 80 ? "text-emerald-400" : "text-amber-400"}>
                          {reviewResult.score}
                        </span>
                        <span className="text-gray-500 text-sm"> / 100</span>
                      </div>
                    </div>
                    <p className="text-xs text-gray-300 flex-1 leading-relaxed border-l border-border/80 pl-4">
                      {reviewResult.summary}
                    </p>
                  </div>

                  {/* Findings Cards */}
                  <div className="space-y-3">
                    {reviewResult.findings.map((f, idx) => (
                      <CodeReviewCard key={idx} finding={f} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Tab 2: PR Generator Output */}
          {activeTab === "pr" && (
            <div className="flex-1 overflow-y-auto space-y-4 pr-1 custom-scrollbar">
              {!prResult ? (
                <div className="flex flex-col items-center justify-center h-full text-center space-y-3 py-16 text-gray-400">
                  <GitPullRequest className="w-10 h-10 text-gray-600" />
                  <p className="text-sm">Paste a git diff and click "Generate PR Description" to create Markdown.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="p-4 rounded-2xl bg-gray-900 border border-border space-y-2">
                    <div className="text-[11px] uppercase font-semibold text-gray-400 tracking-wider">
                      Generated PR Title
                    </div>
                    <div className="text-base font-bold text-cyan-300 font-mono">
                      {prResult.title}
                    </div>
                  </div>

                  <div className="p-5 rounded-2xl bg-gray-900 border border-border space-y-2">
                    <div className="text-[11px] uppercase font-semibold text-gray-400 tracking-wider">
                      Generated Markdown Description
                    </div>
                    <pre className="text-xs font-sans text-gray-200 whitespace-pre-wrap leading-relaxed">
                      {prResult.markdown_description}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
