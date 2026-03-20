from __future__ import annotations

"""Workers em QThread para operacoes longas da interface."""

import logging
from collections.abc import Callable
from typing import Any

from PyQt6.QtCore import QObject, QRunnable, QThread, QThreadPool, pyqtSignal

LOGGER = logging.getLogger(__name__)


class WorkerThread(QThread):
    """Executa uma funcao longa em thread separada e publica sinais de resultado."""

    completed = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, task: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self._task = task
        self._args = args
        self._kwargs = kwargs

    def run(self) -> None:
        """Executa a tarefa protegendo contra falhas nao tratadas."""

        try:
            result = self._task(*self._args, **self._kwargs)
            self.completed.emit(result)
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Falha em worker thread")
            self.failed.emit(str(exc))


class WorkerSignals(QObject):
    """Sinais padrao para workers baseados em QRunnable."""

    completed = pyqtSignal(object)
    failed = pyqtSignal(str)


class DbTaskWorker(QRunnable):
    """Executa tarefa em ``QThreadPool`` para evitar bloqueio de UI."""

    def __init__(self, task: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self._task = task
        self._args = args
        self._kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self) -> None:
        """Executa a tarefa e propaga sucesso/falha por sinais Qt."""

        try:
            result = self._task(*self._args, **self._kwargs)
            self.signals.completed.emit(result)
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Falha em worker QRunnable")
            self.signals.failed.emit(str(exc))


class WorkerPool:
    """Gerencia thread pool global para tarefas pesadas da aplicacao."""

    def __init__(self, max_threads: int = 4) -> None:
        self.pool = QThreadPool.globalInstance()
        self.pool.setMaxThreadCount(max(2, max_threads))

    def submit(self, worker: DbTaskWorker) -> None:
        """Agenda um worker para execucao assincrona."""

        self.pool.start(worker)