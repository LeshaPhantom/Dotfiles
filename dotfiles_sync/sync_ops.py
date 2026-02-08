"""Export, import, and diff between home and repo."""

import shutil
import subprocess
from pathlib import Path

from .config import get_entries, home_path, repo_path, REPO_ROOT


def export_all() -> list[tuple[str, bool, str | None]]:
    """Copy from home to repo. Returns list of (entry_name, success, error_message)."""
    results = []
    for entry in get_entries():
        rel = entry["home"]
        kind = entry.get("type", "file")
        src = home_path(rel)
        dst = repo_path(rel)
        try:
            if kind == "dir":
                if src.exists():
                    if dst.exists():
                        shutil.rmtree(dst)
                    # Не копируем .git — иначе родительский репо не отслеживает файлы
                    shutil.copytree(
                        src, dst,
                        symlinks=True,
                        ignore=shutil.ignore_patterns(".git", ".gitmodules"),
                    )
                    results.append((rel, True, None))
                else:
                    results.append((rel, False, "не найден"))
            else:
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    results.append((rel, True, None))
                else:
                    results.append((rel, False, "не найден"))
        except Exception as e:
            results.append((rel, False, str(e)))
    return results


def import_all() -> list[tuple[str, bool, str | None]]:
    """Copy from repo to home. Returns list of (entry_name, success, error_message)."""
    results = []
    for entry in get_entries():
        rel = entry["home"]
        kind = entry.get("type", "file")
        src = repo_path(rel)
        dst = home_path(rel)
        try:
            if kind == "dir":
                if src.exists():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(
                        src, dst,
                        symlinks=True,
                        ignore=shutil.ignore_patterns(".git", ".gitmodules"),
                    )
                    results.append((rel, True, None))
                else:
                    results.append((rel, False, "нет в репо"))
            else:
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    results.append((rel, True, None))
                else:
                    results.append((rel, False, "нет в репо"))
        except Exception as e:
            results.append((rel, False, str(e)))
    return results


def diff_entries() -> list[tuple[str, str | None]]:
    """Run diff for each entry. Returns list of (entry_name, diff_output or None if same/missing)."""
    out = []
    for entry in get_entries():
        rel = entry["home"]
        kind = entry.get("type", "file")
        a = home_path(rel)
        b = repo_path(rel)
        if kind == "dir":
            try:
                r = subprocess.run(
                    ["diff", "-rq", str(a), str(b)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if r.returncode == 0 and not r.stdout:
                    out.append((rel, None))
                else:
                    out.append((rel, (r.stdout or "") + (r.stderr or "")))
            except Exception as e:
                out.append((rel, str(e)))
        else:
            if not a.exists() and not b.exists():
                out.append((rel, None))
            elif not a.exists():
                out.append((rel, f"Только в репо: {b}"))
            elif not b.exists():
                out.append((rel, f"Только дома: {a}"))
            else:
                try:
                    r = subprocess.run(
                        ["diff", "-u", str(b), str(a)],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    out.append((rel, r.stdout if r.returncode != 0 else None))
                except Exception as e:
                    out.append((rel, str(e)))
    return out


def git_fetch() -> tuple[bool, str]:
    """Run git fetch in repo. Returns (success, message)."""
    try:
        r = subprocess.run(
            ["git", "fetch", "origin"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if r.returncode != 0:
            return False, r.stderr or r.stdout or "git fetch failed"
        return True, "Fetch выполнен"
    except Exception as e:
        return False, str(e)


def git_status_behind() -> tuple[bool, str]:
    """Check if local branch is behind origin. Returns (behind, message)."""
    try:
        r = subprocess.run(
            ["git", "status", "-sb"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode != 0:
            return False, r.stderr or "git status failed"
        # e.g. "## master...origin/master [ahead 1]" or "## master...origin/master [behind 2]"
        line = (r.stdout or "").strip().split("\n")[0]
        if "behind" in line:
            return True, line
        return False, line
    except Exception as e:
        return False, str(e)


def git_pull() -> tuple[bool, str]:
    """Run git pull in repo. Returns (success, message)."""
    try:
        r = subprocess.run(
            ["git", "pull", "origin"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        msg = (r.stdout or "") + (r.stderr or "")
        return r.returncode == 0, msg or "Pull выполнен"
    except Exception as e:
        return False, str(e)
