import re
from pathlib import Path
from typing import List, Dict, Any


class DependencyAnalyzer:
    """
    OSV-Scanner inspired static package dependency security auditor.
    Inspects requirements.txt, package.json, etc. for known vulnerable package versions.
    """

    KNOWN_VULNERABLE_PACKAGES = [
        {
            "package": "requests",
            "version_regex": r"requests\s*(?:==|<|<=)\s*(?:2\.(?:[0-2][0-9]\.|3[0-1]\.))",
            "rule_id": "OSV-CVE-2023-32681",
            "severity": "high",
            "description": "Requests package version < 2.31.0 leaks Proxy-Authorization header during HTTPS redirects."
        },
        {
            "package": "pyyaml",
            "version_regex": r"pyyaml\s*(?:==|<|<=)\s*(?:[0-4]\.|5\.[0-3])",
            "rule_id": "OSV-CVE-2020-14343",
            "severity": "critical",
            "description": "PyYAML version < 5.4 vulnerable to arbitrary code execution via unsafe yaml.load()."
        },
        {
            "package": "axios",
            "version_regex": r"\"axios\"\s*:\s*\"(?:\^|~)?(?:0\.|1\.[0-6]\.)",
            "rule_id": "OSV-CVE-2023-45857",
            "severity": "high",
            "description": "Axios package version < 1.7.4 vulnerable to Server-Side Request Forgery (SSRF)."
        },
        {
            "package": "express",
            "version_regex": r"\"express\"\s*:\s*\"(?:\^|~)?(?:[0-3]\.|4\.(?:[0-1][0-8]\.))",
            "rule_id": "OSV-CVE-2024-21536",
            "severity": "high",
            "description": "Express version < 4.19.2 vulnerable to path traversal and open redirect via malformed URLs."
        }
    ]

    def audit_dependencies(self, repo_dir: Path) -> List[Dict[str, Any]]:
        findings = []

        manifest_files = ["requirements.txt", "package.json", "Pipfile", "poetry.lock"]

        for manifest_name in manifest_files:
            file_path = repo_dir / manifest_name
            if not file_path.exists() or not file_path.is_file():
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for vuln in self.KNOWN_VULNERABLE_PACKAGES:
                    if re.search(vuln["version_regex"], content, re.IGNORECASE):
                        findings.append({
                            "rule_id": vuln["rule_id"],
                            "tool_name": "OSV-Scanner",
                            "severity": vuln["severity"],
                            "file_path": manifest_name,
                            "line_number": 1,
                            "description": vuln["description"],
                            "matched_line": f"Vulnerable dependency package '{vuln['package']}' found in {manifest_name}"
                        })
            except Exception:
                continue

        return findings
