import re
from typing import List, Dict, Any, Optional


class CodeChunkerService:
    def __init__(self, max_chunk_lines: int = 60, overlap_lines: int = 15):
        self.max_chunk_lines = max_chunk_lines
        self.overlap_lines = overlap_lines

    @staticmethod
    def extract_symbol_name(lines: List[str], language: Optional[str]) -> Optional[str]:
        """
        Regex-based symbol extractor for common programming language declarations.
        """
        if not lines:
            return None

        # Regex patterns for Python, JS/TS, Java, Go, Rust, C++
        patterns = [
            r"^\s*class\s+([A-Za-z0-9_]+)",
            r"^\s*def\s+([A-Za-z0-9_]+)",
            r"^\s*function\s+([A-Za-z0-9_]+)",
            r"^\s*export\s+(?:default\s+)?(?:class|function|const)\s+([A-Za-z0-9_]+)",
            r"^\s*func\s+(?:\([^\)]+\)\s+)?([A-Za-z0-9_]+)",
            r"^\s*pub\s+(?:fn|struct|enum|trait)\s+([A-Za-z0-9_]+)",
            r"^\s*interface\s+([A-Za-z0-9_]+)",
            r"^\s*type\s+([A-Za-z0-9_]+)"
        ]

        for line in lines[:10]:  # Look in initial lines of chunk
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1)
        return None

    def chunk_file_content(
        self,
        content: str,
        file_path: str,
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Splits source text content into overlapping line-based code chunks.
        """
        lines = content.splitlines()
        if not lines:
            return []

        chunks = []
        total_lines = len(lines)
        start_idx = 0

        while start_idx < total_lines:
            end_idx = min(start_idx + self.max_chunk_lines, total_lines)
            chunk_lines = lines[start_idx:end_idx]

            chunk_content = "\n".join(chunk_lines)
            symbol_name = self.extract_symbol_name(chunk_lines, language)

            chunks.append({
                "file_path": file_path,
                "language": language or "Plain Text",
                "start_line": start_idx + 1,  # 1-indexed
                "end_line": end_idx,          # 1-indexed inclusive
                "symbol_name": symbol_name,
                "content": chunk_content
            })

            if end_idx >= total_lines:
                break

            # Move start_idx forward by (max_chunk_lines - overlap_lines)
            step = max(1, self.max_chunk_lines - self.overlap_lines)
            start_idx += step

        return chunks
