import os
import re
from pathlib import Path
from typing import List, Dict, Any
from app.services.file_scanner_service import FileScannerService


class SecurityAnalyzer:
    """
    Deterministic static security scanner inspecting codebase for hardcoded secrets,
    command injection, SQL injection, weak cryptography, and unsafe CORS rules.
    Inspired by Semgrep and Bandit security rule sets.
    """

    PATTERNS = [
        {
            "rule_id": "SEMGREP-SECRET-HARDCODED-KEY",
            "tool_name": "Semgrep",
            "severity": "critical",
            "regex": r"(?:api_key|apikey|secret|private_key|token|password)\s*=\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
            "description": "Hardcoded API Key, Secret, or Password detected in source code."
        },
        {
            "rule_id": "BANDIT-B105-HARDCODED-PASSWORD",
            "tool_name": "Bandit",
            "severity": "high",
            "regex": r"(?:password|passwd|pwd)\s*=\s*['\"][^'\"]+['\"]",
            "description": "Possible hardcoded password string variable assignment."
        },
        {
            "rule_id": "BANDIT-B602-SHELL-COMMAND-INJECTION",
            "tool_name": "Bandit",
            "severity": "high",
            "regex": r"(?:subprocess\.(?:call|Popen|run)\s*\(.*shell\s*=\s*True|os\.system\s*\()",
            "description": "Unsafe command execution with os.system() or shell=True creates shell injection vulnerability."
        },
        {
            "rule_id": "BANDIT-B102-UNSAFE-EXEC-EVAL",
            "tool_name": "Bandit",
            "severity": "critical",
            "regex": r"\b(?:eval|exec)\s*\(",
            "description": "Use of eval() or exec() can allow dynamic arbitrary code execution."
        },
        {
            "rule_id": "BANDIT-B608-SQL-INJECTION",
            "tool_name": "Bandit",
            "severity": "high",
            "regex": r"(?:SELECT|INSERT|UPDATE|DELETE)\s+.*?\+\s*[A-Za-z_]|f['\"](?:SELECT|INSERT|UPDATE|DELETE)\s+.*?\{",
            "description": "Possible SQL injection vector using string concatenation or f-strings in database query."
        },
        {
            "rule_id": "BANDIT-B303-WEAK-CRYPTO-MD5-SHA1",
            "tool_name": "Bandit",
            "severity": "medium",
            "regex": r"hashlib\.(?:md5|sha1)\s*\(",
            "description": "Use of weak cryptographic hash function (MD5 / SHA1) vulnerable to collision attacks."
        },
        {
            "rule_id": "SEMGREP-CORS-WILDCARD-ORIGIN",
            "tool_name": "Semgrep",
            "severity": "medium",
            "regex": r"allow_origins\s*=\s*\[\s*['\"]\*['\"]\s*\]",
            "description": "Wildcard CORS origin allow_origins=['*'] exposes API to arbitrary cross-origin requests."
        }
    ]

    def scan_directory(self, repo_dir: Path) -> List[Dict[str, Any]]:
        scanner = FileScannerService()
        scanned_files = scanner.scan_repository(repo_dir)

        findings = []

        for file_info in scanned_files:
            full_path = file_info["full_path"]
            rel_path = file_info["file_path"]

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
            except Exception:
                continue

            for line_idx, line in enumerate(lines, 1):
                # Ignore comment lines
                stripped = line.strip()
                if stripped.startswith("#") or stripped.startswith("//"):
                    continue

                for pattern_def in self.PATTERNS:
                    if re.search(pattern_def["regex"], line, re.IGNORECASE):
                        findings.append({
                            "rule_id": pattern_def["rule_id"],
                            "tool_name": pattern_def["tool_name"],
                            "severity": pattern_def["severity"],
                            "file_path": rel_path,
                            "line_number": line_idx,
                            "description": pattern_def["description"],
                            "matched_line": line.strip()[:150]
                        })

        return findings
