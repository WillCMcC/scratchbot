"""Minimal GitHub API helpers used by ScratchBot."""

from __future__ import annotations

import requests
from typing import Optional

API_ROOT = "https://api.github.com"


def _headers(token: str) -> dict:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "scratchbot",
    }


def upsert_comment(repo: str, pr_number: int, body: str, token: str) -> None:
    """Create or update the sticky Docs Plan comment on ``pr_number``."""
    url = f"{API_ROOT}/repos/{repo}/issues/{pr_number}/comments"
    headers = _headers(token)
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    existing = None
    for comment in resp.json():
        if comment.get("body", "").startswith("## \ud83d\udcda Docs Plan"):
            existing = comment
            break
    if existing:
        patch = requests.patch(
            existing["url"], json={"body": body}, headers=headers, timeout=10
        )
        patch.raise_for_status()
    else:
        post = requests.post(url, json={"body": body}, headers=headers, timeout=10)
        post.raise_for_status()


def set_plan_status(repo: str, sha: str, state: str, token: str, description: Optional[str] = None, target_url: Optional[str] = None) -> None:
    """Set ``scratchbot/plan`` status on ``sha``."""
    url = f"{API_ROOT}/repos/{repo}/statuses/{sha}"
    payload = {
        "state": state,
        "context": "scratchbot/plan",
    }
    if description:
        payload["description"] = description
    if target_url:
        payload["target_url"] = target_url
    resp = requests.post(url, json=payload, headers=_headers(token), timeout=10)
    resp.raise_for_status()
