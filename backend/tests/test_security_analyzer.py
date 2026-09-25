import pytest
from pathlib import Path
from app.analyzers.security_analyzer import SecurityAnalyzer
from app.analyzers.dependency_analyzer import DependencyAnalyzer


def test_security_analyzer_detects_vulnerabilities(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    # Create file with hardcoded secret and command injection
    vuln_file = repo_dir / "vuln.py"
    vuln_file.write_text(
        'api_key = "AKIA1234567890SECRETKEY"\n'
        'import os\n'
        'os.system("rm -rf " + user_input)\n'
        'eval("print(1)")\n'
    )

    analyzer = SecurityAnalyzer()
    findings = analyzer.scan_directory(repo_dir)

    assert len(findings) >= 3
    rule_ids = [f["rule_id"] for f in findings]
    assert "SEMGREP-SECRET-HARDCODED-KEY" in rule_ids
    assert "BANDIT-B102-UNSAFE-EXEC-EVAL" in rule_ids


def test_dependency_analyzer_detects_outdated_package(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    req_file = repo_dir / "requirements.txt"
    req_file.write_text("requests==2.28.1\npyyaml==5.3.1\n")

    auditor = DependencyAnalyzer()
    findings = auditor.audit_dependencies(repo_dir)

    assert len(findings) >= 2
    rule_ids = [f["rule_id"] for f in findings]
    assert "OSV-CVE-2023-32681" in rule_ids
    assert "OSV-CVE-2020-14343" in rule_ids
