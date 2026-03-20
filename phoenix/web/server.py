from __future__ import annotations

import json
from datetime import date
from datetime import timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from phoenix.core.database import get_session
from phoenix.core.models import FocusSession, Goal, Habit, Transaction


def detect_backend() -> str:
    """Retorna backend web disponivel: fastapi ou stdlib."""

    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401

        return "fastapi"
    except Exception:
        return "stdlib"


def build_payload() -> dict[str, Any]:
    """Monta payload consolidado para endpoints de status."""

    today = date.today()
    month_start = today.replace(day=1)
    with get_session() as session:
        goals_total = session.query(Goal).count()
        habits_total = session.query(Habit).filter(Habit.active.is_(True)).count()
        tx_month = session.query(Transaction).filter(Transaction.date >= month_start).count()
        focus_week = session.query(FocusSession).filter(FocusSession.date >= (today - timedelta(days=6))).count()

    return {
        "status": "ok",
        "backend": detect_backend(),
        "summary": {
            "goals_total": int(goals_total),
            "habits_active": int(habits_total),
            "transactions_month": int(tx_month),
            "focus_sessions_recent": int(focus_week),
        },
    }


def _build_stdlib_handler() -> type[BaseHTTPRequestHandler]:
    class PhoenixHandler(BaseHTTPRequestHandler):
        def _send_json(self, status_code: int, payload: dict[str, Any]) -> None:
            data = json.dumps(payload, ensure_ascii=True).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                self._send_json(200, {"status": "ok", "backend": "stdlib"})
                return
            if self.path == "/summary":
                self._send_json(200, build_payload())
                return
            self._send_json(404, {"status": "not_found"})

        def log_message(self, format: str, *args: object) -> None:
            del format, args

    return PhoenixHandler


def _run_stdlib(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), _build_stdlib_handler())
    print(f"Servidor web (stdlib) ativo em http://{host}:{port}")
    print("Endpoints: /health e /summary")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _run_fastapi(host: str, port: int) -> None:
    from fastapi import FastAPI
    import uvicorn

    app = FastAPI(title="Phoenix Local API", version="3.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "backend": "fastapi"}

    @app.get("/summary")
    def summary() -> dict[str, Any]:
        payload = build_payload()
        payload["backend"] = "fastapi"
        return payload

    print(f"Servidor web (fastapi) ativo em http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Inicializa servidor web local com fallback transparente."""

    if detect_backend() == "fastapi":
        _run_fastapi(host=host, port=port)
        return
    _run_stdlib(host=host, port=port)
