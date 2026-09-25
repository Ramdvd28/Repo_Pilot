"use client";

import { useState, useMemo } from "react";
import { Folder, FolderOpen, FileCode, ChevronRight, ChevronDown, Search, FileText } from "lucide-react";
import { RepoFile } from "@/types/repo";

interface TreeNode {
  name: string;
  path: string;
  isFolder: boolean;
  fileData?: RepoFile;
  children: Record<string, TreeNode>;
}

interface FileTreeProps {
  files: RepoFile[];
  selectedPath?: string;
  onSelectFile: (file: RepoFile) => void;
}

export function FileTree({ files, selectedPath, onSelectFile }: FileTreeProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedFolders, setExpandedFolders] = useState<Record<string, boolean>>({});

  // Filter files by search query
  const filteredFiles = useMemo(() => {
    if (!searchQuery.trim()) return files;
    const query = searchQuery.toLowerCase();
    return files.filter((f) => f.file_path.toLowerCase().includes(query));
  }, [files, searchQuery]);

  // Build hierarchical folder tree structure from file list
  const treeRoot = useMemo(() => {
    const root: TreeNode = {
      name: "root",
      path: "",
      isFolder: true,
      children: {},
    };

    for (const file of filteredFiles) {
      const parts = file.file_path.split("/");
      let current = root;
      let currentPath = "";

      for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        currentPath = currentPath ? `${currentPath}/${part}` : part;
        const isLast = i === parts.length - 1;

        if (isLast) {
          current.children[part] = {
            name: part,
            path: currentPath,
            isFolder: false,
            fileData: file,
            children: {},
          };
        } else {
          if (!current.children[part]) {
            current.children[part] = {
              name: part,
              path: currentPath,
              isFolder: true,
              children: {},
            };
          }
          current = current.children[part];
        }
      }
    }
    return root;
  }, [filteredFiles]);

  const toggleFolder = (folderPath: string) => {
    setExpandedFolders((prev) => ({
      ...prev,
      [folderPath]: !prev[folderPath],
    }));
  };

  const renderNode = (node: TreeNode, depth: number = 0) => {
    if (node.isFolder) {
      // Sort children: folders first, then files
      const childrenList = Object.values(node.children).sort((a, b) => {
        if (a.isFolder === b.isFolder) return a.name.localeCompare(b.name);
        return a.isFolder ? -1 : 1;
      });

      // Default expand root-level folders if not manually toggled
      const isExpanded = expandedFolders[node.path] ?? (depth < 1 || searchQuery.length > 0);

      return (
        <div key={node.path || "root"}>
          {node.name !== "root" && (
            <button
              onClick={() => toggleFolder(node.path)}
              style={{ paddingLeft: `${depth * 12 + 8}px` }}
              className="w-full text-left py-1.5 px-2 rounded-lg hover:bg-gray-800/60 flex items-center gap-1.5 text-xs text-gray-300 font-medium group transition-colors"
            >
              {isExpanded ? (
                <ChevronDown className="w-3.5 h-3.5 text-gray-400" />
              ) : (
                <ChevronRight className="w-3.5 h-3.5 text-gray-400" />
              )}
              {isExpanded ? (
                <FolderOpen className="w-4 h-4 text-cyan-400 shrink-0" />
              ) : (
                <Folder className="w-4 h-4 text-blue-400 shrink-0" />
              )}
              <span className="truncate group-hover:text-white">{node.name}</span>
            </button>
          )}

          {isExpanded && (
            <div>
              {childrenList.map((child) => renderNode(child, node.name === "root" ? 0 : depth + 1))}
            </div>
          )}
        </div>
      );
    }

    // File item node
    const isSelected = selectedPath === node.path;
    const file = node.fileData!;

    return (
      <button
        key={node.path}
        onClick={() => onSelectFile(file)}
        style={{ paddingLeft: `${depth * 12 + 20}px` }}
        className={`w-full text-left py-1.5 px-2 rounded-lg flex items-center justify-between gap-2 text-xs transition-colors ${
          isSelected
            ? "bg-blue-600/20 text-cyan-300 border border-cyan-500/30 font-medium"
            : "text-gray-400 hover:text-white hover:bg-gray-800/40"
        }`}
      >
        <div className="flex items-center gap-2 truncate">
          <FileCode className={`w-3.5 h-3.5 shrink-0 ${isSelected ? "text-cyan-400" : "text-gray-400"}`} />
          <span className="truncate">{node.name}</span>
        </div>
        {file.language && (
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400 shrink-0 font-mono">
            {file.language}
          </span>
        )}
      </button>
    );
  };

  return (
    <div className="flex flex-col h-full space-y-3">
      {/* File Search Filter */}
      <div className="relative">
        <Search className="w-3.5 h-3.5 text-gray-500 absolute left-3 top-2.5" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Filter files..."
          className="w-full bg-gray-900 border border-border rounded-xl pl-8 pr-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-colors"
        />
      </div>

      {/* Tree Content Container */}
      <div className="flex-1 overflow-y-auto pr-1 space-y-0.5 custom-scrollbar">
        {files.length === 0 ? (
          <div className="text-center py-8 text-xs text-gray-500 italic">No files indexed yet</div>
        ) : (
          renderNode(treeRoot)
        )}
      </div>
    </div>
  );
}
