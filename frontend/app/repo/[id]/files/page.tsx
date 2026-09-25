"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  Compass,
  FileCode,
  FolderTree,
  Loader2,
  RefreshCw,
  Sparkles,
  Layers,
  ArrowLeft,
  CheckCircle2,
  Code2,
} from "lucide-react";
import { api, ApiError } from "@/services/api";
import { Repository, RepoFile, IngestionSummary, CodeChunk } from "@/types/repo";
import { FileTree } from "@/components/FileTree";
import { CodeViewer } from "@/components/CodeViewer";

export default function FileExplorerPage() {
  const params = useParams();
  const repoId = params.id as string;

  const [repo, setRepo] = useState<Repository | null>(null);
  const [files, setFiles] = useState<RepoFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<RepoFile | null>(null);
  const [fileContent, setFileContent] = useState<string>("");
  const [chunks, setChunks] = useState<CodeChunk[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [ingesting, setIngesting] = useState(false);
  const [loadingContent, setLoadingContent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ingestionResult, setIngestionResult] = useState<IngestionSummary | null>(null);

  const loadData = async () => {
    try {
      const repoData = await api.getRepo(repoId);
      setRepo(repoData);

      const filesData = await api.getRepoFiles(repoId);
      setFiles(filesData);

      // Auto-select first file if available and none selected
      if (filesData.length > 0 && !selectedFile) {
        handleSelectFile(filesData[0]);
      }
      setLoading(false);
    } catch (err) {
      setLoading(false);
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to load repository files.");
      }
    }
  };

  useEffect(() => {
    if (repoId) {
      loadData();
    }
  }, [repoId]);

  const handleSelectFile = async (file: RepoFile) => {
    setSelectedFile(file);
    setLoadingContent(true);
    try {
      const resp = await api.getFileContent(repoId, file.file_path);
      setFileContent(resp.content);

      // Fetch chunks for selected file
      const chunkData = await api.getRepoChunks(repoId, file.file_path);
      setChunks(chunkData);
    } catch (err) {
      setFileContent(`// Error loading file content for ${file.file_path}`);
    } finally {
      setLoadingContent(false);
    }
  };

  const handleIngest = async () => {
    setIngesting(true);
    setError(null);
    try {
      const summary = await api.ingestRepo(repoId);
      setIngestionResult(summary);
      await loadData();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Repository ingestion failed.");
      }
    } finally {
      setIngesting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
        <p className="text-sm text-gray-400">Loading File Explorer...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Top Header Bar */}
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
              <FolderTree className="w-5 h-5 text-cyan-400" />
              <span>{repo?.owner} / {repo?.name} — File Explorer</span>
            </h1>
            <p className="text-xs text-gray-400">
              {files.length > 0
                ? `${files.length} indexed files available in repository knowledge base`
                : "Repository has not been ingested yet. Click 'Ingest Repository' below to start scanning."}
            </p>
          </div>
        </div>

        <button
          onClick={handleIngest}
          disabled={ingesting}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-semibold text-xs transition-all shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2 disabled:opacity-50 shrink-0"
        >
          {ingesting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Cloning & Parsing Code...</span>
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4" />
              <span>{files.length > 0 ? "Re-Ingest Repository" : "Ingest Repository"}</span>
            </>
          )}
        </button>
      </div>

      {/* Ingestion Result Summary Banner */}
      {ingestionResult && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-200 flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-white">Ingestion Complete!</strong> Indexed{" "}
              <span className="font-semibold text-cyan-300">{ingestionResult.files_indexed}</span> files and generated{" "}
              <span className="font-semibold text-violet-300">{ingestionResult.chunks_created}</span> code chunks in{" "}
              {ingestionResult.ingestion_time_seconds}s.
            </div>
          </div>
          <button onClick={() => setIngestionResult(null)} className="text-gray-400 hover:text-white">
            ×
          </button>
        </div>
      )}

      {/* Main Workspace Layout */}
      {files.length === 0 ? (
        <div className="bg-surface/60 border border-border/80 rounded-2xl p-16 text-center space-y-4">
          <div className="w-14 h-14 rounded-full bg-blue-600/10 border border-blue-500/30 flex items-center justify-center mx-auto text-cyan-400">
            <Sparkles className="w-7 h-7" />
          </div>
          <h2 className="text-xl font-bold text-white">Repository Not Ingested Yet</h2>
          <p className="text-sm text-gray-400 max-w-md mx-auto">
            Run the ingestion pipeline to clone source files, filter binaries, and build structured code chunks for RAG.
          </p>
          <div>
            <button
              onClick={handleIngest}
              disabled={ingesting}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 text-white font-semibold text-sm transition-all"
            >
              {ingesting ? "Ingesting..." : "Ingest Repository Now"}
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[750px]">
          {/* File Tree Sidebar */}
          <div className="lg:col-span-1 bg-surface/90 border border-border rounded-2xl p-4 flex flex-col h-full overflow-hidden shadow-xl">
            <div className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3 flex items-center gap-2">
              <FolderTree className="w-4 h-4 text-cyan-400" />
              <span>Files Tree</span>
            </div>
            <FileTree
              files={files}
              selectedPath={selectedFile?.file_path}
              onSelectFile={handleSelectFile}
            />
          </div>

          {/* Code Viewer & Chunks Area */}
          <div className="lg:col-span-3 flex flex-col h-full space-y-4 overflow-hidden">
            {selectedFile ? (
              <div className="flex-1 flex flex-col h-full overflow-hidden">
                {loadingContent ? (
                  <div className="flex-1 flex items-center justify-center bg-surface/90 border border-border rounded-2xl">
                    <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
                  </div>
                ) : (
                  <CodeViewer
                    filePath={selectedFile.file_path}
                    language={selectedFile.language}
                    content={fileContent}
                  />
                )}
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center bg-surface/90 border border-border rounded-2xl p-8 text-center text-gray-400 text-sm">
                <FileCode className="w-10 h-10 text-gray-600 mb-2" />
                <span>Select a file from the sidebar to view code</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
