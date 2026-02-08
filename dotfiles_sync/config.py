"""Load and resolve paths from config.yaml."""

from pathlib import Path
from typing import Any

import yaml

# Repo root = directory containing config.yaml
REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config.yaml"
HOME = Path.home()


def load_config() -> dict[str, Any]:
    """Load config.yaml from repo root."""
    if not CONFIG_PATH.exists():
        return {"entries": []}
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {"entries": []}


def get_storage_dir() -> str:
    """Папка в репо для хранения dotfiles (не корень)."""
    return load_config().get("storage_dir", "dotfiles").strip("/") or "dotfiles"


def get_entries() -> list[dict[str, Any]]:
    """Return list of entries (home path relative to HOME, type: file|dir)."""
    cfg = load_config()
    return cfg.get("entries", [])


def home_path(rel: str) -> Path:
    """Absolute path in home. rel is like .tmux or .config/nvim."""
    return HOME / rel.lstrip("/")


def repo_path(rel: str) -> Path:
    """Path in repo: storage_dir / rel (mirroring home). rel is like .tmux or .config/nvim."""
    return REPO_ROOT / get_storage_dir() / rel.lstrip("/")
