"""Interactive add of a new dotfile/dir to config.yaml."""

import sys
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from dotfiles_sync.config import CONFIG_PATH, REPO_ROOT, HOME, load_config

console = Console()


def main() -> None:
    # Чтение ввода в UTF-8, чтобы не падать при другой кодировке терминала (CP1251 и т.д.)
    if hasattr(sys.stdin, "reconfigure"):
        try:
            sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, AttributeError):
            pass

    console.print(Panel("[bold cyan]Добавить программу/конфиг в Dotfiles[/]", border_style="cyan"))
    console.print("\nУкажите путь относительно домашней директории.")
    console.print("Примеры: .tmux  .tmux.conf  .config/nvim  .zshrc\n")
    raw = Prompt.ask("Путь", default="").strip()
    if not raw:
        console.print("[yellow]Путь не задан.[/]")
        return
    # normalize: no leading slash, but allow .config/...
    rel = raw.lstrip("/")
    if not rel.startswith(".") and "/" not in rel:
        rel = "." + rel if not rel.startswith(".") else rel
    abs_path = HOME / rel
    if not abs_path.exists():
        console.print(f"[yellow]Внимание: путь не существует: {abs_path}[/]")
        create = Prompt.ask("Всё равно добавить в конфиг?", choices=["y", "n", "да", "нет"], default="n")
        if create.lower() in ("n", "нет"):
            return
    kind = "dir" if abs_path.is_dir() else "file"
    console.print(f"Определён тип: [cyan]{kind}[/]")
    override = Prompt.ask("Изменить тип? (file/dir/нет)", default="нет")
    if override.lower() in ("file", "dir"):
        kind = override.lower()
    cfg = load_config()
    entries = cfg.get("entries", [])
    for e in entries:
        if e.get("home") == rel:
            console.print(f"[yellow]Запись для {rel} уже есть в конфиге.[/]")
            return
    entries.append({"home": rel, "type": kind})
    cfg["entries"] = entries
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    console.print(f"[green]Добавлено: {rel} ({kind})[/]")


if __name__ == "__main__":
    main()
