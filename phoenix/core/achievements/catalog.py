from __future__ import annotations

"""Catalogo padrao de conquistas do Phoenix 3.0."""

CATALOG: list[dict[str, object]] = [
    {"key": "habit_first", "name": "Ignicao", "description": "Primeiro check de habito", "icon": "H1", "category": "habits", "xp_reward": 10, "rarity": "common"},
    {"key": "habit_week", "name": "Semana de Fogo", "description": "7 dias seguidos em qualquer habito", "icon": "H7", "category": "habits", "xp_reward": 30, "rarity": "common"},
    {"key": "habit_month", "name": "Mes Implacavel", "description": "30 dias de streak", "icon": "H30", "category": "habits", "xp_reward": 100, "rarity": "rare"},
    {"key": "goal_first", "name": "Visionario", "description": "Primeira meta criada", "icon": "G1", "category": "goals", "xp_reward": 10, "rarity": "common"},
    {"key": "goal_complete", "name": "Cumpridor", "description": "Primeira meta concluida", "icon": "GC", "category": "goals", "xp_reward": 100, "rarity": "rare"},
    {"key": "fin_import", "name": "Importador", "description": "Primeiro extrato importado", "icon": "F1", "category": "finances", "xp_reward": 15, "rarity": "common"},
    {"key": "fin_100tx", "name": "Centena", "description": "100 transacoes registradas", "icon": "F100", "category": "finances", "xp_reward": 60, "rarity": "rare"},
    {"key": "focus_first", "name": "Primeiro Flow", "description": "Primeira sessao de 90 minutos", "icon": "P1", "category": "focus", "xp_reward": 30, "rarity": "common"},
    {"key": "focus_100", "name": "Centuriao do Foco", "description": "100 sessoes completas", "icon": "P100", "category": "focus", "xp_reward": 300, "rarity": "epic"},
    {"key": "proj_first", "name": "Gerenciador", "description": "Primeiro projeto criado", "icon": "PR1", "category": "projects", "xp_reward": 10, "rarity": "common"},
    {"key": "lib_first", "name": "Leitor", "description": "Primeiro livro adicionado", "icon": "L1", "category": "library", "xp_reward": 10, "rarity": "common"},
    {"key": "diary_first", "name": "Narrador", "description": "Primeira entrada do diario", "icon": "D1", "category": "diary", "xp_reward": 10, "rarity": "common"},
    {"key": "gen_onboard", "name": "Recem-chegado", "description": "Onboarding completo", "icon": "N", "category": "general", "xp_reward": 20, "rarity": "common"},
    {"key": "gen_explorer", "name": "Explorador", "description": "Visitar todos os modulos em um dia", "icon": "E", "category": "general", "xp_reward": 30, "rarity": "common"},
]
