from __future__ import annotations

"""Constantes compartilhadas do aplicativo Phoenix."""

from enum import StrEnum


class AppDefaults(StrEnum):
    """Valores padrao de configuracao visual e operacional."""

    APP_NAME = "Phoenix"
    ORGANIZATION = "phoenix-personal"
    VERSION = "2.0.0"
    THEME_DARK = "dark"
    THEME_LIGHT = "light"


class UiLimits:
    """Constantes numericas reutilizadas pela interface."""

    SIDEBAR_WIDTH = 220
    HEADER_HEIGHT = 52
    DEFAULT_FONT_SIZE = 13
    DEFAULT_PAGE_SIZE = 50
    TOAST_TIMEOUT_MS = 2500
    AUTO_SAVE_INTERVAL_MS = 2000


class Events(StrEnum):
    """Canais de eventos aplicacionais."""

    NAVIGATE = "app.navigate"
    SHOW_TOAST = "app.toast"
    SHOW_SHORTCUTS = "app.shortcuts"
    DATA_CHANGED = "app.data_changed"


class BackupDefaults(StrEnum):
    """Convencoes de backup local."""

    EXTENSION = ".phoenix.bak"
    SQLITE_ENTRY = "database.sqlite3"
    SETTINGS_ENTRY = "settings.json"
