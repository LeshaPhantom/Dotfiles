---@type LazySpec
return {
  "AstroNvim/astrocore",
  ---@type AstroCoreOpts
  opts = {
    -- Configure core features of AstroNvim
    features = {
      large_buf = { size = 1024 * 256, lines = 10000 }, -- set global limits for large files for disabling features like treesitter
      autopairs = true, -- enable autopairs at start
      cmp = true, -- enable completion at start
      diagnostics_mode = 3, -- diagnostic mode on start (0 = off, 1 = no signs/virtual text, 2 = no virtual text, 3 = on)
      highlighturl = true, -- highlight URLs at start
      notifications = true, -- enable notifications at start
    },
    -- Diagnostics configuration (for vim.diagnostics.config({...})) when diagnostics are on
    diagnostics = {
      virtual_text = true,
      underline = true,
    },
    -- vim options can be configured here
    options = {
      opt = { -- Все параметры через vim.opt.<key>
        -- ===== Настройки нумерации строк =====
        relativenumber = true, -- Показывать относительные номера строк (расстояние до курсора)
        number = true, -- Показывать абсолютные номера строк

        -- ===== Настройки текста =====
        wrap = false, -- Не переносить длинные строки (горизонтальный скролл)
        linebreak = true, -- Если wrap=true, переносить только по словам

        -- ===== Настройки интерфейса =====
        signcolumn = "yes", -- Всегда показывать колонку для значков (ошибки, git и т.д.)
        termguicolors = true, -- Включить true-color поддержку (24-битные цвета)
        cursorline = true, -- Подсвечивать текущую строку
        scrolloff = 8, -- Минимальное число строк над/под курсором при скролле
        sidescrolloff = 8, -- То же самое для горизонтального скролла

        -- ===== Настройки файлов =====
        swapfile = false, -- Не создавать .swp файлы (осторожно - риск потери данных)
        backup = false, -- Не создавать резервные копии (~ файлы)
        undofile = true, -- Сохранять историю изменений между сеансами

        -- ===== Настройки табуляции =====
        tabstop = 4, -- 1 таб = 4 пробела
        shiftwidth = 4, -- Размер автоотступа = 4 пробела
        expandtab = true, -- Преобразовывать табы в пробелы
        smartindent = true, -- "Умные" отступы для кода

        -- ===== Настройки поиска =====
        ignorecase = true, -- Игнорировать регистр при поиске
        smartcase = true, -- Учитывать регистр если есть заглавные буквы
        hlsearch = true, -- Подсвечивать результаты поиска
        incsearch = true, -- Инкрементальный поиск (по мере ввода)

        -- ===== Дополнительные настройки =====
        mouse = "a", -- Включить мышь во всех режимах
        guicursor = "",
        splitright = true, -- Новые вертикальные окна справа
        splitbelow = true, -- Новые горизонтальные окна снизу
        timeoutlen = 300, -- Таймаут для комбинаций клавиш (мс)
        updatetime = 250, -- Частота автосохранения и CursorHold событий
        completeopt = "menuone,noselect", -- Настройки автодополнения
        conceallevel = 0, -- Показывать разметку (например, в Markdown)
      },
      g = { -- vim.g.<key>
        -- configure global vim variables (vim.g)
        -- NOTE: `mapleader` and `maplocalleader` must be set in the AstroNvim opts or before `lazy.setup`
        -- This can be found in the `lua/lazy_setup.lua` file
        python3_host_prog = "/usr/bin/python3",
      },
    },
    -- Mappings can be configured through AstroCore as well.
    -- NOTE: keycodes follow the casing in the vimdocs. For example, `<Leader>` must be capitalized
    mappings = {
      -- first key is the mode
      n = {
        -- second key is the lefthand side of the map

        -- navigate buffer tabs
        ["]b"] = { function() require("astrocore.buffer").nav(vim.v.count1) end, desc = "Next buffer" },
        ["[b"] = { function() require("astrocore.buffer").nav(-vim.v.count1) end, desc = "Previous buffer" },

        -- mappings seen under group name "Buffer"
        ["<Leader>bd"] = {
          function()
            require("astroui.status.heirline").buffer_picker(
              function(bufnr) require("astrocore.buffer").close(bufnr) end
            )
          end,
          desc = "Close buffer from tabline",
        },

        -- tables with just a `desc` key will be registered with which-key if it's installed
        -- this is useful for naming menus
        -- ["<Leader>b"] = { desc = "Buffers" },

        -- setting a mapping to false will disable it
        -- ["<C-S>"] = false,
      },
    },
  },
}
