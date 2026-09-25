import pytest
from pathlib import Path
from fastapi import HTTPException
from app.services.file_scanner_service import FileScannerService


def test_detect_language():
    assert FileScannerService.detect_language(Path("main.py")) == "Python"
    assert FileScannerService.detect_language(Path("App.tsx")) == "TypeScript"
    assert FileScannerService.detect_language(Path("server.go")) == "Go"
    assert FileScannerService.detect_language(Path("Dockerfile")) == "Dockerfile"
    assert FileScannerService.detect_language(Path("unknown.xyz")) is None


def test_is_binary_or_ignored():
    assert FileScannerService.is_binary_or_ignored(Path("image.png")) is True
    assert FileScannerService.is_binary_or_ignored(Path("archive.zip")) is True
    assert FileScannerService.is_binary_or_ignored(Path("app.exe")) is True
    assert FileScannerService.is_binary_or_ignored(Path("code.py")) is False


def test_validate_safe_path_security(tmp_path):
    base_dir = tmp_path / "repo"
    base_dir.mkdir()

    valid_file = base_dir / "src" / "index.js"
    valid_file.parent.mkdir()
    valid_file.write_text("console.log('hello');")

    # Safe path access
    safe_resolved = FileScannerService.validate_safe_path(base_dir, "src/index.js")
    assert safe_resolved.exists()

    # Path traversal attack attempts
    with pytest.raises(HTTPException) as exc:
        FileScannerService.validate_safe_path(base_dir, "../../../etc/passwd")
    assert exc.value.status_code == 403

    with pytest.raises(HTTPException) as exc:
        FileScannerService.validate_safe_path(base_dir, "..\\..\\windows\\system32")
    assert exc.value.status_code == 403
