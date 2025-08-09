import subprocess
from pathlib import Path

from scratchbot import commit_changes, clone_pr_branch, verify_head_sha


def init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True)
    (path / "README.md").write_text("init", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True)


def test_commit_per_file(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    (repo / "a.md").write_text("A", encoding="utf-8")
    (repo / "b.md").write_text("B", encoding="utf-8")
    commit_changes(repo, ["a.md", "b.md"], "docs: add {path} (ScratchBot)", mode="per_file")
    log = subprocess.run([
        "git", "-C", repo, "log", "--format=%s"
    ], capture_output=True, text=True, check=True).stdout.strip().splitlines()
    assert log[0] == "docs: add b.md (ScratchBot)"
    assert log[1] == "docs: add a.md (ScratchBot)"


def test_commit_batch(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    (repo / "a.md").write_text("A", encoding="utf-8")
    (repo / "b.md").write_text("B", encoding="utf-8")
    commit_changes(repo, ["a.md", "b.md"], "docs: add {path} (ScratchBot)", mode="batch")
    log = subprocess.run([
        "git", "-C", repo, "log", "--format=%s"
    ], capture_output=True, text=True, check=True).stdout.strip().splitlines()
    assert log[0] == "docs: add a.md, b.md (ScratchBot)"


def test_clone_and_verify(tmp_path):
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "--bare", origin], check=True)

    work = tmp_path / "work"
    subprocess.run(["git", "clone", origin, work], check=True)
    (work / "readme.txt").write_text("hello", encoding="utf-8")
    subprocess.run(["git", "-C", work, "add", "readme.txt"], check=True)
    subprocess.run(["git", "-C", work, "commit", "-m", "base"], check=True)
    sha = subprocess.run(["git", "-C", work, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    subprocess.run(["git", "-C", work, "push", "origin", "HEAD:feature"], check=True)

    dest = tmp_path / "clone"
    clone_pr_branch(str(origin), "feature", dest)
    assert verify_head_sha(dest, sha) == sha
