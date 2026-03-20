from __future__ import annotations

"""Constantes compartilhadas do aplicativo Phoenix."""

from enum import StrEnum


class AppDefaults(StrEnum):
    """Valores padrao de configuracao visual e operacional."""

    APP_NAME = "Phoenix"
    ORGANIZATION = "phoenix-personal"
    VERSION = "3.0.0"
    THEME_DARK = "dark"
    THEME_LIGHT = "light"


DEFAULT_THEME: dict[str, str | int] = {
    "name": "dark",
    "PRIMARY": "#C0392B",
    "SECONDARY": "#E67E22",
    "ACCENT": "#F39C12",
    "BG_ROOT": "#0D0D0D",
    "BG_SURFACE": "#161616",
    "BG_ELEVATED": "#1E1E1E",
    "BORDER": "#2A2A2A",
    "BORDER_HOVER": "#444444",
    "TEXT_PRIMARY": "#F0F0F0",
    "TEXT_SECONDARY": "#AAAAAA",
    "TEXT_HINT": "#555555",
    "RADIUS_SM": "6px",
    "RADIUS_MD": "8px",
    "RADIUS_LG": "12px",
    "SPACING_SM": "6px 10px",
    "SPACING_MD": "9px 14px",
    "SPACING_LG": "13px 18px",
    "SUCCESS": "#10B981",
    "WARNING": "#F59E0B",
    "ERROR": "#EF4444",
    "font_family": "Segoe UI",
    "font_size": 13,
}


LIGHT_THEME: dict[str, str | int] = {
    **DEFAULT_THEME,
    "name": "light",
    "PRIMARY": "#B23A48",
    "SECONDARY": "#D97706",
    "ACCENT": "#B45309",
    "BG_ROOT": "#F7F7F7",
    "BG_SURFACE": "#FFFFFF",
    "BG_ELEVATED": "#F2F2F2",
    "BORDER": "#D8D8D8",
    "BORDER_HOVER": "#BDBDBD",
    "TEXT_PRIMARY": "#1B1B1B",
    "TEXT_SECONDARY": "#4F4F4F",
    "TEXT_HINT": "#777777",
}


THEME_PRESETS: dict[str, dict[str, str | int]] = {
    "dark": DEFAULT_THEME,
    "light": LIGHT_THEME,
}


class UiLimits:
    """Constantes numericas reutilizadas pela interface."""

    SIDEBAR_WIDTH = 220
    HEADER_HEIGHT = 52
    DEFAULT_FONT_SIZE = 13
    DEFAULT_PAGE_SIZE = 50
    TOAST_TIMEOUT_MS = 3000
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
