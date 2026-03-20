from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from dynaconf import Dynaconf
from sqlalchemy.orm import Session

from dev_tools import seed_demo_data
from phoenix.core.models import Budget, Goal, GoalMilestone, Habit

SETTINGS = Dynaconf(settings_files=[str(Path(__file__).resolve().parents[2] / "settings.toml")])

_HABIT_COLORS = {
    "🏃 Exercício": "#E74C3C",
    "💧 Água": "#3498DB",
    "📚 Leitura": "#E67E22",
    "🧘 Meditação": "#8E44AD",
    "😴 Sono": "#2980B9",
    "💊 Suplementos": "#16A085",
    "✍️ Journaling": "#C0392B",
    "🎯 Foco": "#F39C12",
    "🥗 Alimentação": "#27AE60",
}

_BUDGET_COLORS = {
    "🍔 Alimentação": "#E67E22",
    "🚗 Transporte": "#E74C3C",
    "🏠 Moradia": "#C0392B",
    "🎮 Lazer": "#9B59B6",
    "💪 Saúde": "#16A085",
    "📚 Educação": "#3498DB",
    "👗 Compras": "#D35400",
    "💰 Investimentos": "#F39C12",
}

_FOCUS_TO_CATEGORY = {
    "Carreira e produtividade": "carreira",
    "Saúde e bem-estar": "saude",
    "Aprendizado e crescimento": "aprendizado",
    "Finanças pessoais": "financas",
    "Projetos pessoais": "projetos",
    "Equilíbrio geral": "geral",
}

_INCOME_BASE = {
    "Prefiro não informar": 1800.0,
    "Até R$ 2.000": 2000.0,
    "R$ 2-5k": 5000.0,
    "R$ 5-10k": 10000.0,
    "Acima de R$ 10k": 14000.0,
}


def _suggest_monthly_limit(income_range: str, categories_count: int) -> float:
    base = _INCOME_BASE.get(income_range, 2000.0)
    slots = max(categories_count, 1)
    return round((base * 0.55) / slots, 2)


def run_seed(data: dict, session: Session) -> None:
    """Cria dados iniciais reais a partir das respostas do onboarding.

    Args:
        data: Mapa de respostas coletadas no wizard.
        session: Sessão SQLAlchemy ativa para persistência.
    """

    today = date.today()

    selected_habits = list(data.get("habits", []))
    habit_frequency = int(data.get("habit_frequency", 5))
    for habit_name in selected_habits:
        session.add(
            Habit(
                name=str(habit_name),
                frequency="custom",
                target_days=list(range(habit_frequency)),
                color=_HABIT_COLORS.get(str(habit_name), "#E67E22"),
                description=f"Onboarding seed | icon {habit_name.split(' ')[0]}",
                created_at=today,
                active=True,
            )
        )

    focus = str(data.get("life_focus", "Equilíbrio geral"))
    category = _FOCUS_TO_CATEGORY.get(focus, "geral")

    goals = list(data.get("goals", []))
    for item in goals:
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        offset = int(item.get("deadline_offset", 90))
        target = today + timedelta(days=offset)
        goal = Goal(
            title=title,
            category=category,
            status="active",
            start_date=today,
            target_date=target,
            current_value=0,
            target_value=1,
            color="#E67E22",
        )
        session.add(goal)
        session.flush()

        session.add(
            GoalMilestone(
                goal_id=goal.id,
                title="Planejamento inicial",
                completed=False,
                due_date=today + timedelta(days=14),
            )
        )
        session.add(
            GoalMilestone(
                goal_id=goal.id,
                title="Marco intermediário",
                completed=False,
                due_date=today + timedelta(days=max(offset // 2, 21)),
            )
        )

    categories = list(data.get("budget_categories", []))
    limit = _suggest_monthly_limit(str(data.get("income_range", "Prefiro não informar")), len(categories))
    for category_name in categories:
        session.add(
            Budget(
                category=str(category_name),
                amount=limit,
                period="monthly",
                color=_BUDGET_COLORS.get(str(category_name), "#E67E22"),
                active=True,
            )
        )

    SETTINGS.set("user.name", str(data.get("name", "Usuário")))
    SETTINGS.set("focus.default_duration", int(data.get("focus_duration", 25)))
    SETTINGS.set("focus.daily_goal_hours", int(data.get("daily_goal_hours", 2)))
    SETTINGS.set("focus.peak_time", str(data.get("peak_time", "Manhã (6h-12h)")))
    SETTINGS.set("ui.life_focus", str(data.get("life_focus", "Equilíbrio geral")))

    if bool(data.get("load_demo_data", False)):
        seed_demo_data()
