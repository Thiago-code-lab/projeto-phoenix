from __future__ import annotations

"""Configuracao central de logging da aplicacao."""

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configura logging padrao da aplicacao uma unica vez."""

    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(level)
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
