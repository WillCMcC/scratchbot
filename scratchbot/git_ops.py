from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable, Optional


def clone_pr_branch(repo: str, branch: str, dest: str | Path, token: Optional[str] = None) -> None:
    """Clone ``branch`` of ``repo`` into ``dest``.

    ``repo`` may be an ``owner/repo`` string or a full git URL. When provided,
    ``token`` is injected into HTTPS URLs for GitHub App authentication.
    """
    dest = str(dest)
    if repo.startswith("http"):
        url = repo
    elif repo.count("/") == 1:
        url = f"https://github.com/{repo}.git"
    else:
        url = repo

    if token and url.startswith("https://"):
        url = url.replace("https://", f"https://x-access-token:{token}@")

    subprocess.run(["git", "clone", "--branch", branch, url, dest], check=True)


def verify_head_sha(repo_path: str | Path, expected_sha: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    sha = result.stdout.strip()
    if sha != expected_sha:
        raise ValueError(f"Head SHA {sha} does not match expected {expected_sha}")
    return sha


def commit_changes(repo_path: str | Path, files: Iterable[str], message_template: str, mode: str = "per_file") -> None:
    repo_path = str(repo_path)
    files = list(files)
    if mode == "per_file":
        for path in files:
            subprocess.run(["git", "-C", repo_path, "add", path], check=True)
            message = message_template.format(path=path)
            subprocess.run(["git", "-C", repo_path, "commit", "-m", message], check=True)
    else:
        for path in files:
            subprocess.run(["git", "-C", repo_path, "add", path], check=True)
        joined = ", ".join(files)
        message = message_template.format(path=joined)
        subprocess.run(["git", "-C", repo_path, "commit", "-m", message], check=True)
