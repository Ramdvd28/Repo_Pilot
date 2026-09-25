import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status

# Default max file size to index/chunk (1 MB)
MAX_FILE_SIZE_BYTES = 1 * 1024 * 1024

IGNORED_DIRECTORIES = {
    ".git", ".github", "node_modules", "dist", "build", "target",
    "__pycache__", ".venv", "venv", "env", "ENV", ".idea", ".vscode",
    ".pytest_cache", ".next", "out", "coverage", "vendor", "eggs", "*.egg-info"
}

IGNORED_EXTENSIONS = {
    # Binaries & Media
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".pdf",
    ".zip", ".tar", ".gz", ".7z", ".rar", ".bz2", ".xz",
    ".pyc", ".pyo", ".pyd", ".so", ".dll", ".dylib", ".exe", ".bin",
    ".db", ".sqlite", ".sqlite3", ".woff", ".woff2", ".ttf", ".eot",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".flv", ".lock", ".log",
    ".ds_store"
}

EXTENSION_TO_LANGUAGE = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".cpp": "C++",
    ".cxx": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".json": "JSON",
    ".md": "Markdown",
    ".sql": "SQL",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".toml": "TOML",
    ".xml": "XML",
    ".dockerfile": "Dockerfile",
    "dockerfile": "Dockerfile",
}


class FileScannerService:

    @staticmethod
    def validate_safe_path(base_dir: Path, relative_path: str) -> Path:
        """
        Validates that requested relative path strictly resolves inside base_dir.
        Throws HTTPException(403) on path traversal attempt.
        """
        base_dir_canonical = base_dir.resolve()
        target_path = (base_dir_canonical / relative_path).resolve()

        if not str(target_path).startswith(str(base_dir_canonical)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Security Violation: Path traversal attempt detected for '{relative_path}'."
            )
        return target_path

    @staticmethod
    def detect_language(file_path: Path) -> Optional[str]:
        name_lower = file_path.name.lower()
        if name_lower in EXTENSION_TO_LANGUAGE:
            return EXTENSION_TO_LANGUAGE[name_lower]
        ext = file_path.suffix.lower()
        return EXTENSION_TO_LANGUAGE.get(ext)

    @staticmethod
    def is_binary_or_ignored(file_path: Path) -> bool:
        ext = file_path.suffix.lower()
        if ext in IGNORED_EXTENSIONS:
            return True
        name_lower = file_path.name.lower()
        if name_lower in {".ds_store", "thumbs.db", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"}:
            return True
        return False

    def scan_repository(self, base_dir: Path) -> List[Dict[str, Any]]:
        """
        Scans base_dir recursively and returns metadata dicts for all valid source files.
        """
        base_dir_canonical = base_dir.resolve()
        scanned_files = []

        for root, dirs, files in os.walk(base_dir_canonical):
            # Prune ignored directories in-place
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES and not d.startswith(".")]

            for file_name in files:
                full_path = Path(root) / file_name
                
                # Boundary check
                try:
                    canonical_file_path = full_path.resolve()
                    if not str(canonical_file_path).startswith(str(base_dir_canonical)):
                        continue
                except Exception:
                    continue

                if self.is_binary_or_ignored(canonical_file_path):
                    continue

                try:
                    stat_info = canonical_file_path.stat()
                    file_size = stat_info.st_size

                    # Skip empty or oversized files (>1MB)
                    if file_size == 0 or file_size > MAX_FILE_SIZE_BYTES:
                        continue

                    rel_path = str(canonical_file_path.relative_to(base_dir_canonical)).replace("\\", "/")
                    language = self.detect_language(canonical_file_path)

                    # Calculate total lines count safely
                    total_lines = 0
                    try:
                        with open(canonical_file_path, "r", encoding="utf-8", errors="ignore") as f:
                            total_lines = sum(1 for _ in f)
                    except Exception:
                        pass

                    scanned_files.append({
                        "file_path": rel_path,
                        "full_path": canonical_file_path,
                        "language": language or "Plain Text",
                        "size_bytes": file_size,
                        "total_lines": total_lines
                    })
                except Exception:
                    continue

        return scanned_files
