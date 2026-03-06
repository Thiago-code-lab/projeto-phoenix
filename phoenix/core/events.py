from __future__ import annotations

"""Barramento de eventos baseado em sinais Qt para desacoplar modulos."""

from collections import defaultdict
from typing import Any, Callable

from PyQt6.QtCore import QObject, pyqtSignal

EventCallback = Callable[[dict[str, Any]], None]


class EventBus(QObject):
    """Coordena comunicacao entre componentes sem chamadas diretas entre modulos."""

    event_emitted = pyqtSignal(str, dict)

    def __init__(self) -> None:
        super().__init__()
        self._subscribers: dict[str, list[EventCallback]] = defaultdict(list)
        self.event_emitted.connect(self._dispatch)

    def subscribe(self, event_name: str, callback: EventCallback) -> None:
        """Registra um callback para um evento nomeado."""

        self._subscribers[event_name].append(callback)

    def publish(self, event_name: str, payload: dict[str, Any] | None = None) -> None:
        """Publica um evento para os assinantes registrados."""

        self.event_emitted.emit(event_name, payload or {})

    def _dispatch(self, event_name: str, payload: dict[str, Any]) -> None:
        """Despacha o evento recebido do sinal Qt para os callbacks."""

        data = payload or {}
        for callback in self._subscribers.get(event_name, []):
            callback(data)
