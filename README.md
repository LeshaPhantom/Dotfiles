# Dotfiles

Репозиторий с конфигами и скриптами для синхронизации между машинами через Git.

## Что синхронизируется

В `config.yaml` перечислены пути относительно `$HOME`:

- **Папки:** `~/.tmux`, `~/.config/alacritty`, `~/.config/nvim`, `~/.oh-my-zsh`
- **Файлы:** `~/.tmux.conf`, `~/.zshrc`, `~/.p10k.zsh`

Структура в репозитории повторяет домашнюю (те же имена папок и файлов в корне репо).

## Требования

- Python 3.10+
- [Poetry](https://python-poetry.org/)
- TUI на [Textual](https://textual.textualize.io/)

## Установка

```bash
cd /path/to/Dotfiles
poetry install
```

## Использование

### TUI (основная программа)

```bash
poetry run dotfiles-sync
# или после poetry install:
poetry run python sync.py
```

В меню можно выбрать пункт стрелками + Enter или **нажать цифру 1–5**:
- **1** — Export (дом → репо)
- **2** — Import (репо → дом)
- **3** — Status (diff)
- **4** — Check updates (git pull + применить)
- **5** — Выход

Описания действий: **Export** копирует текущие конфиги из домашней директории в репозиторий (перед коммитом). **Import** — из репо в дом (после клонирования или `git pull`). **Status** — отличия дом ↔ репо. **Check updates** — fetch, при необходимости pull и предложение сделать import.

### Добавить новый конфиг/программу

```bash
poetry run dotfiles-add-program
# или
poetry run python add_program.py
```

Скрипт спросит путь относительно `$HOME` (например `.config/kitty` или `.bashrc`), определит файл или папка, и добавит запись в `config.yaml`. Дальше используйте **Export** в TUI, чтобы скопировать файлы в репо.

## Типичный сценарийf

**ПК 1 (основной):**

1. Меняете конфиги дома.
2. Запускаете `dotfiles-sync` → **Export** → сохраняете файлы в репо.
3. `git add . && git commit -m "..." && git push`

**ПК 2 (другой):**

1. Клонируете репо: `git clone ... Dotfiles && cd Dotfiles && poetry install`
2. Запускаете `dotfiles-sync` → **Import** — конфиги попадают в `~`.
3. При необходимости меняете конфиги, снова **Export**, коммит, push.

**ПК 1 на следующий день:**

1. Запускаете `dotfiles-sync` → **Check updates**.
2. Выполняете pull и по запросу применяете конфиги (import).

## Структура репозитория

```
Dotfiles/
  config.yaml      # список путей и storage_dir (YAML)
  sync.py          # точка входа TUI
  add_program.py   # добавление записи в config.yaml
  dotfiles_sync/   # пакет (логика sync, TUI)
  pyproject.toml   # зависимости и скрипты (Poetry)
  dotfiles/        # папка с копиями конфигов (появляется после Export)
    .tmux/
    .tmux.conf
    .config/
      alacritty/
      nvim/
    .zshrc
    .p10k.zsh
    .oh-my-zsh/    # при необходимости можно исключить из репо (.gitignore)
```

Папку хранения можно сменить в `config.yaml`: параметр `storage_dir` (по умолчанию `dotfiles`).

## Заметки

- **.oh-my-zsh** — большая папка. Если не хотите хранить её в Git, добавьте в `.gitignore`: `dotfiles/.oh-my-zsh/` и уберите запись из `config.yaml` или оставьте только нужные подпапки/файлы через отдельные записи.
- При **Export/Import** папки копируются **без** вложенных `.git` и `.gitmodules`, чтобы Dotfiles-репо видел обычные файлы, а не вложенные репозитории. После Import при необходимости можно снова выполнить `git clone` для oh-my-zsh или плагинов (tmux/nvim) в нужных каталогах.
- Все пути в `config.yaml` задаются относительно домашней директории.
- Проверка обновлений (п. 4 в TUI) делает только `git fetch` и `git pull`; ветка предполагается той, на которой вы находитесь (обычно `main`/`master`).
