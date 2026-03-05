from pathlib import Path

APP_NAME = "Projeto Phoenix"
APP_ICON = "🔥"
APP_LAYOUT = "wide"

ROOT_DIR = Path(__file__).resolve().parent
DB_PATH = ROOT_DIR / "phoenix.db"
STYLE_PATH = ROOT_DIR / "styles" / "theme.css"
MIGRATIONS_DIR = ROOT_DIR / "database" / "migrations"

DEFAULT_SETTINGS = {
    "user_name": "Thiago",
    "avatar": "🔥",
    "theme": "dark",
    "currency": "R$",
    "week_start": "Segunda",
    "notifications": "0",
}

MODULES = {
    "dashboard": "🏠 Dashboard",
    "goals": "🎯 Metas",
    "habits": "✅ Hábitos",
    "finances": "💰 Finanças",
    "library": "📚 Biblioteca",
    "health": "🏋️ Saúde",
    "journal": "📝 Diário",
    "projects": "📋 Projetos",
    "settings": "⚙️ Configurações",
}
