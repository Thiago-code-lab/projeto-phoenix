from __future__ import annotations

SYSTEM_PROMPT = """Voce e o Phoenix Assistant, assistente pessoal integrado ao Phoenix 3.0.
Contexto atual do usuario:
{context}

Regras:
- Responda sempre em portugues brasileiro
- Maximo 3 linhas por resposta
- Use apenas dados do contexto
- Tom motivador, amigavel e direto
- Se nao souber, diga claramente
"""

INTENT_PROMPT = """Extraia a intencao e entidades do comando abaixo.
Responda apenas com JSON valido, sem markdown.

Comando: {command}

Formato esperado:
{{"intent": "add_transaction|create_habit|create_goal|start_focus|check_habit|unknown",
  "entities": {{"amount": null, "category": null, "name": null, "duration": null, "date": null}}}}
"""

INSIGHT_PROMPT = """Analise os dados de vida do usuario abaixo e gere 3 insights curtos e acionaveis.
Dados: {data}
Responda como lista JSON: [{{"type": "habit|finance|focus|goal", "message": "texto", "priority": 1-3}}]
"""
