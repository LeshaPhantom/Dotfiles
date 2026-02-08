"""TUI for dotfiles sync (Textual): menu, export, import, status, check updates."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import (
    Header,
    Footer,
    OptionList,
    RichLog,
    Static,
    Button,
)
from textual.widgets.option_list import Option
from textual import work

from . import sync_ops


class DotfilesSyncApp(App[None]):
    """Главное приложение Dotfiles Sync."""

    BINDINGS = [
        Binding("1", "do_export", "1 Export", show=True),
        Binding("2", "do_import", "2 Import", show=True),
        Binding("3", "do_status", "3 Status", show=True),
        Binding("4", "do_check", "4 Check", show=True),
        Binding("5", "quit", "5 Выход", show=True),
    ]

    CSS = """
    Screen {
        layout: vertical;
        background: $surface-darken-1;
    }

    Header {
        background: $primary 20%;
        color: $primary-background;
        text-style: bold;
        padding: 0 1;
        height: 3;
    }

    #menu_container {
        width: 42;
        min-width: 36;
        height: auto;
        border: round $primary 80%;
        border-title-align: center;
        padding: 1 2;
        margin: 1 2;
        background: $surface;
        color: $text;
    }

    #menu_container .menu_title {
        text-style: bold;
        color: $primary;
        padding-bottom: 1;
        text-align: center;
    }

    #menu_container OptionList {
        height: auto;
        min-height: 10;
        border: none;
        padding: 0;
        background: transparent;
    }

    #menu_container OptionList > .option-list--option-highlighted {
        background: $primary 30%;
        color: $primary-background;
    }

    #output_container {
        layout: vertical;
        height: 1fr;
        border: round #505050;
        border-title-align: center;
        padding: 1 2;
        margin: 1 2;
        background: $surface;
    }

    #output_container .output_title {
        color: $text-muted;
        padding-bottom: 1;
    }

    #output_container RichLog {
        height: 1fr;
        scrollbar-background: $surface-darken-1;
        scrollbar-color: $primary;
        padding: 0 1;
        border: solid #303030;
        margin: 1 0 0 0;
    }

    #buttons {
        height: auto;
        padding: 0 2 1 2;
        align: center middle;
    }

    #buttons Button {
        margin-right: 2;
        min-width: 12;
    }

    #buttons Button.primary {
        background: $primary;
        color: $primary-background;
    }

    Footer {
        background: $surface-darken-2;
        color: $text-muted;
    }
    """

    TITLE = "Dotfiles Sync"
    SUB_TITLE = "дом ↔ репо"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Container(id="menu_container"):
                yield Static("Выберите пункт или нажмите 1–5", classes="menu_title")
                yield OptionList(
                    Option("1. Export (дом → репо)", id="export"),
                    Option("2. Import (репо → дом)", id="import"),
                    Option("3. Status (diff дом ↔ репо)", id="status"),
                    Option("4. Check updates (git pull + применить)", id="check"),
                    Option("5. Выход", id="quit"),
                    id="menu",
                )
            with Container(id="output_container"):
                yield Static("Результаты операций", classes="output_title")
                yield RichLog(highlight=True, markup=True, id="log")
        with Horizontal(id="buttons"):
            yield Button("Выполнить", variant="primary", id="run")
            yield Button("Очистить лог", id="clear")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#menu", OptionList).focus()

    def action_do_export(self) -> None:
        self._run_menu_action("export")

    def action_do_import(self) -> None:
        self._run_menu_action("import")

    def action_do_status(self) -> None:
        self._run_menu_action("status")

    def action_do_check(self) -> None:
        self._run_menu_action("check")

    def action_quit(self) -> None:
        self.exit()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        opt = event.option_id
        if opt == "quit":
            self.exit()
            return
        if opt:
            self._run_menu_action(opt)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run":
            opt_list = self.query_one("#menu", OptionList)
            try:
                idx = opt_list.highlighted_index
                if idx is not None:
                    opt = opt_list.get_option_at_index(idx)
                    if opt and getattr(opt, "id", None):
                        if opt.id == "quit":
                            self.exit()
                            return
                        self._run_menu_action(opt.id)
            except Exception:
                pass
        elif event.button.id == "clear":
            self.query_one("#log", RichLog).clear()

    def _run_menu_action(self, action_id: str) -> None:
        if action_id == "export":
            self._run_export()
        elif action_id == "import":
            self._run_import()
        elif action_id == "status":
            self._run_status()
        elif action_id == "check":
            self._run_check_updates()

    def _append_log(self, text: str) -> None:
        self.query_one("#log", RichLog).write(text)

    @work(thread=True, exclusive=True)
    def _run_export(self) -> None:
        self.call_from_thread(self._append_log, "\n[bold]Export: дом → репо[/]\n")
        results = sync_ops.export_all()
        lines = []
        for rel, ok, err in results:
            lines.append(f"  [{'green' if ok else 'red'}]{rel}[/] — {'OK' if ok else (err or '—')}")
        self.call_from_thread(self._append_log, "\n".join(lines) + "\n")

    @work(thread=True, exclusive=True)
    def _run_import(self) -> None:
        self.call_from_thread(self._append_log, "\n[bold]Import: репо → дом[/]\n")
        results = sync_ops.import_all()
        lines = []
        for rel, ok, err in results:
            lines.append(f"  [{'green' if ok else 'red'}]{rel}[/] — {'OK' if ok else (err or '—')}")
        self.call_from_thread(self._append_log, "\n".join(lines) + "\n")

    @work(thread=True, exclusive=True)
    def _run_status(self) -> None:
        self.call_from_thread(self._append_log, "\n[bold]Status: diff дом ↔ репо[/]\n")
        diffs = sync_ops.diff_entries()
        for rel, diff_text in diffs:
            if diff_text is None:
                self.call_from_thread(self._append_log, f"  [green]• {rel}[/] — без отличий\n")
            else:
                self.call_from_thread(self._append_log, f"  [yellow]{rel}:[/]\n{diff_text}\n")
        self.call_from_thread(self._append_log, "")

    @work(thread=True, exclusive=True)
    def _run_check_updates(self) -> None:
        log = self.query_one("#log", RichLog)

        def out(msg: str) -> None:
            self.call_from_thread(log.write, msg + "\n")

        out("\n[bold]Check updates[/]\n")
        ok, msg = sync_ops.git_fetch()
        if not ok:
            out(f"[red]Fetch: {msg}[/]")
            return
        out(f"[green]{msg}[/]")
        behind, status_msg = sync_ops.git_status_behind()
        if not behind:
            out(f"[green]Ветка актуальна. {status_msg}[/]")
            return
        out(f"[yellow]Есть обновления: {status_msg}[/]")
        # Дальше нужен интерактивный выбор (pull / import) — делаем по шагам в лог и предлагаем запустить Import вручную
        out("[dim]Выполните в терминале: git pull. Затем выберите «Import» здесь.[/]")
        ok_pull, pull_msg = sync_ops.git_pull()
        if ok_pull:
            out(f"[green]Pull: {pull_msg}[/]")
            out("[bold]Применить конфиги? Выберите «2. Import» в меню.[/]")
        else:
            out(f"[red]Pull: {pull_msg}[/]")

def main() -> None:
    app = DotfilesSyncApp()
    app.run()
