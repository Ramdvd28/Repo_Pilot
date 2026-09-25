import os
import shutil
import asyncio
from pathlib import Path
import httpx
import zipfile
import io
from fastapi import HTTPException, status
from app.core.config import settings

STORAGE_DIR = Path("storage/cloned_repos").resolve()


class CloneService:
    def __init__(self, storage_dir: Path = STORAGE_DIR):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def get_repo_dir(self, repo_id: str) -> Path:
        repo_dir = (self.storage_dir / repo_id).resolve()
        # Ensure path stays strictly inside storage_dir
        if not str(repo_dir).startswith(str(self.storage_dir)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Security Violation: Invalid repository directory path."
            )
        return repo_dir

    async def clone_repository(self, repo_id: str, github_url: str, default_branch: str = "main") -> Path:
        """
        Clones or downloads a repository securely into storage/cloned_repos/{repo_id}.
        Uses shallow git clone if git binary is available, otherwise falls back to ZIP archive download.
        """
        target_dir = self.get_repo_dir(repo_id)

        # Clean existing directory if it exists
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)

        target_dir.mkdir(parents=True, exist_ok=True)

        # Try git clone --depth 1 first
        git_path = shutil.which("git")
        if git_path:
            try:
                cmd = [
                    git_path, "clone", "--depth", "1",
                    "--single-branch", "--branch", default_branch,
                    github_url, str(target_dir)
                ]
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()

                if proc.returncode == 0 and target_dir.exists() and any(target_dir.iterdir()):
                    # Remove .git folder inside cloned repo to save space and prevent git conflicts
                    git_folder = target_dir / ".git"
                    if git_folder.exists():
                        shutil.rmtree(git_folder, ignore_errors=True)
                    return target_dir
            except Exception as e:
                print(f"[CloneService] Git clone failed: {e}. Falling back to ZIP archive download...")

        # Fallback: Download repo ZIP archive from GitHub API
        # Extract owner/repo from URL
        parts = github_url.rstrip("/").split("/")
        if len(parts) < 2:
            raise HTTPException(status_code=400, detail="Invalid GitHub URL structure")
        
        owner, repo = parts[-2], parts[-1]
        zip_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{default_branch}"

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "RepoPilot-AI"
        }
        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(zip_url, headers=headers)
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"Failed to download repository archive from GitHub: {resp.text}"
                )

            try:
                with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                    # Extract contents, skipping top-level wrapper directory
                    members = z.namelist()
                    if not members:
                        raise HTTPException(status_code=400, detail="Downloaded archive is empty")
                    
                    root_prefix = members[0].split("/")[0] + "/"
                    
                    for member in members:
                        if member == root_prefix:
                            continue
                        rel_name = member[len(root_prefix):] if member.startswith(root_prefix) else member
                        if not rel_name:
                            continue
                        
                        target_file_path = (target_dir / rel_name).resolve()
                        
                        # Prevent Zip Slip vulnerability
                        if not str(target_file_path).startswith(str(target_dir)):
                            continue

                        if member.endswith("/"):
                            target_file_path.mkdir(parents=True, exist_ok=True)
                        else:
                            target_file_path.parent.mkdir(parents=True, exist_ok=True)
                            with z.open(member) as src, open(target_file_path, "wb") as dst:
                                shutil.copyfileobj(src, dst)
            except zipfile.BadZipFile:
                raise HTTPException(status_code=400, detail="Invalid ZIP archive returned by GitHub")

        return target_dir
