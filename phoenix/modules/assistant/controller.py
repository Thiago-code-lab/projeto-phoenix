from __future__ import annotations

import json
import logging
from datetime import date

from PyQt6.QtCore import QObject, QThread, pyqtSignal

logger = logging.getLogger(__name__)


class AssistantWorker(QThread):
    """Executa chamadas de backend do assistant fora da thread UI.

    Args:
        backend_fn: Funcao que executa a tarefa.
        *args: Argumentos da funcao.
    """

    response_ready = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, backend_fn, *args):
        super().__init__()
        self._fn = backend_fn
        self._args = args

    def run(self) -> None:
        """Executa a funcao e publica resposta ou erro."""

        try:
            result = self._fn(*self._args)
            self.response_ready.emit(result)
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))


class AssistantController(QObject):
    """Controlador do Phoenix Assistant com fallback local.

    Detecta backends disponiveis e opera de modo assincorno.
    """

    response_ready = pyqtSignal(str)
    insight_ready = pyqtSignal(list)
    intent_parsed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._backend = self._detect_backend()
        self._history: list[dict[str, str]] = []
        self._workers: list[AssistantWorker] = []
        logger.info("AssistantController backend: %s", self._backend)

    def backend_name(self) -> str:
        """Retorna nome do backend ativo."""

        return self._backend

    def _detect_backend(self) -> str:
        try:
            import urllib.request

            urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
            return "ollama"
        except Exception:
            pass
        try:
            import transformers  # noqa: F401

            return "transformers"
        except ImportError:
            pass
        return "rule_based"

    def chat(self, message: str, context: dict) -> None:
        """Gera resposta de chat sem bloquear a UI."""

        from phoenix.modules.assistant.prompts import SYSTEM_PROMPT

        system = SYSTEM_PROMPT.format(context=json.dumps(context, ensure_ascii=False, indent=2))
        worker = AssistantWorker(self._call_backend, system, message, self._history.copy())
        worker.response_ready.connect(self._on_response)
        worker.error.connect(lambda err: self.response_ready.emit(f"Erro: {err}"))
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        worker.start()
        self._workers.append(worker)
        self._history.append({"role": "user", "content": message})

    def _cleanup_worker(self, worker: AssistantWorker) -> None:
        if worker in self._workers:
            self._workers.remove(worker)

    def _on_response(self, text: str) -> None:
        self._history.append({"role": "assistant", "content": text})
        if len(self._history) > 20:
            self._history = self._history[-20:]
        self.response_ready.emit(text)

    def _call_backend(self, system: str, message: str, history: list[dict[str, str]]) -> str:
        if self._backend == "ollama":
            return self._ollama(system, message, history)
        if self._backend == "transformers":
            return self._transformers(system, message)
        return self._rule_based(message)

    def _ollama(self, system: str, message: str, history: list[dict[str, str]]) -> str:
        import urllib.request

        messages = [{"role": "system", "content": system}]
        messages += history[-6:]
        messages.append({"role": "user", "content": message})
        payload = json.dumps({"model": "llama3", "messages": messages, "stream": False}).encode()
        req = urllib.request.Request(
            "http://localhost:11434/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
            return str(data.get("message", {}).get("content", "Sem resposta"))

    def _transformers(self, system: str, message: str) -> str:
        from transformers import pipeline

        pipe = pipeline("text-generation", model="microsoft/phi-2", max_new_tokens=150)
        prompt = f"{system}\n\nUsuario: {message}\nAssistente:"
        result = pipe(prompt)[0]["generated_text"]
        return result.split("Assistente:")[-1].strip()

    def _rule_based(self, message: str) -> str:
        msg = message.lower()
        if any(token in msg for token in ["habito", "streak", "check"]):
            return "Continue com seus habitos. Consistencia diaria gera resultado composto."
        if any(token in msg for token in ["gasto", "dinheiro", "saldo", "financ"]):
            return "Revise suas categorias de gasto do mes e ajuste o limite da categoria mais critica."
        if any(token in msg for token in ["foco", "pomodoro", "sessao"]):
            return "Escolha uma tarefa unica e rode um ciclo de foco de 25 ou 50 minutos agora."
        if any(token in msg for token in ["meta", "goal", "objetivo"]):
            return "Quebre sua meta em marcos menores e defina o proximo passo executavel de hoje."
        return "Estou pronto para ajudar com habitos, metas, foco e financas no Phoenix."

    def parse_intent(self, text: str) -> None:
        """Executa parse de intencao em background."""

        worker = AssistantWorker(self._parse_intent_sync, text)
        worker.response_ready.connect(lambda raw: self.intent_parsed.emit(json.loads(raw)))
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        worker.start()
        self._workers.append(worker)

    def _parse_intent_sync(self, text: str) -> str:
        from phoenix.modules.assistant.prompts import INTENT_PROMPT

        prompt = INTENT_PROMPT.format(command=text)
        try:
            raw = self._call_backend("", prompt, [])
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return raw[start:end] if start >= 0 else '{"intent": "unknown", "entities": {}}'
        except Exception:
            return '{"intent": "unknown", "entities": {}}'

    def analyze_patterns(self, all_data: dict) -> None:
        """Gera insights semanais em segundo plano."""

        worker = AssistantWorker(self._analyze_sync, all_data)
        worker.response_ready.connect(lambda raw: self.insight_ready.emit(json.loads(raw) if raw.startswith("[") else []))
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        worker.start()
        self._workers.append(worker)

    def _analyze_sync(self, data: dict) -> str:
        from phoenix.modules.assistant.prompts import INSIGHT_PROMPT

        prompt = INSIGHT_PROMPT.format(data=json.dumps(data, ensure_ascii=False))
        try:
            raw = self._call_backend("", prompt, [])
            start = raw.find("[")
            end = raw.rfind("]") + 1
            return raw[start:end] if start >= 0 else "[]"
        except Exception:
            return "[]"

    def get_context(self, session) -> dict:
        """Coleta contexto resumido de habitos, metas e financas."""

        from phoenix.core.models import Goal, Habit, HabitLog, Transaction
        from phoenix.core.native_bridge import calculate_streak

        context: dict[str, object] = {}
        try:
            today = date.today()
            habits = session.query(Habit).filter_by(active=True).all()
            context["habits_active"] = len(habits)
            all_logs: list[str] = []
            for habit in habits:
                logs = session.query(HabitLog).filter_by(habit_id=habit.id).all()
                all_logs.extend([str(log.date) for log in logs])
            context["streak_global"] = calculate_streak(all_logs)
            context["goals_active"] = session.query(Goal).filter_by(status="active").count()
            month_start = today.replace(day=1)
            txs = session.query(Transaction).filter(Transaction.date >= month_start).all()
            context["income_month"] = sum(tx.amount for tx in txs if tx.type == "income")
            context["expense_month"] = sum(tx.amount for tx in txs if tx.type == "expense")
            context["today"] = today.isoformat()
        except Exception as exc:  # noqa: BLE001
            logger.warning("get_context error: %s", exc)
        return context
