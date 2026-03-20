from __future__ import annotations

"""Rotinas de backup local sem dependencia de servidor."""

import json
import logging
from datetime import datetime, timedelta
from shutil import copy2
import zipfile
from pathlib import Path

from cryptography.fernet import Fernet

from .database import DATABASE_PATH
from phoenix.utils.constants import BackupDefaults

LOGGER = logging.getLogger(__name__)


def _settings_path() -> Path:
    return DATABASE_PATH.parent / "settings.toml"


def export_database(destination: Path) -> Path:
    """Exporta somente o arquivo SQLite bruto."""

    destination.write_bytes(DATABASE_PATH.read_bytes())
    return destination


def import_database(source: Path) -> None:
    """Importa um arquivo SQLite bruto para o banco local."""

    DATABASE_PATH.write_bytes(source.read_bytes())


def generate_backup_key() -> bytes:
    """Gera uma chave simetrica para backup criptografado."""

    return Fernet.generate_key()


def export_encrypted_database(destination: Path, key: bytes) -> Path:
    """Exporta o banco criptografado com Fernet."""

    cipher = Fernet(key)
    encrypted = cipher.encrypt(DATABASE_PATH.read_bytes())
    destination.write_bytes(encrypted)
    return destination


def import_encrypted_database(source: Path, key: bytes) -> None:
    """Importa um banco criptografado com Fernet."""

    cipher = Fernet(key)
    DATABASE_PATH.write_bytes(cipher.decrypt(source.read_bytes()))


def export_backup_bundle(destination: Path) -> Path:
    """Exporta um arquivo .phoenix.bak com SQLite comprimido e configuracoes."""

    if destination.suffix != BackupDefaults.EXTENSION:
        destination = destination.with_suffix(BackupDefaults.EXTENSION)

    settings_payload = {
        "settings_toml": _settings_path().read_text(encoding="utf-8") if _settings_path().exists() else "",
    }
    with zipfile.ZipFile(destination, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(BackupDefaults.SQLITE_ENTRY, DATABASE_PATH.read_bytes())
        archive.writestr(BackupDefaults.SETTINGS_ENTRY, json.dumps(settings_payload, ensure_ascii=True, indent=2))
    LOGGER.info("Backup exportado para %s", destination)
    return destination


def import_backup_bundle(source: Path) -> None:
    """Restaura um arquivo .phoenix.bak para o banco e configuracoes locais."""

    with zipfile.ZipFile(source, mode="r") as archive:
        DATABASE_PATH.write_bytes(archive.read(BackupDefaults.SQLITE_ENTRY))
        settings_payload = json.loads(archive.read(BackupDefaults.SETTINGS_ENTRY).decode("utf-8"))
        _settings_path().write_text(settings_payload.get("settings_toml", ""), encoding="utf-8")
    LOGGER.info("Backup restaurado de %s", source)


def auto_backup_if_due(interval_hours: int = 24, keep_last: int = 7) -> Path | None:
    """Executa backup automatico do SQLite quando o intervalo expira.

    Args:
        interval_hours: Intervalo minimo entre backups consecutivos.
        keep_last: Quantidade maxima de arquivos de backup preservados.

    Returns:
        Caminho do backup criado, quando houver; senao ``None``.
    """

    base_dir = DATABASE_PATH.parent
    backup_dir = base_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    marker_file = backup_dir / ".last_backup"

    now = datetime.now()
    last_iso = ""
    if marker_file.exists():
        last_iso = marker_file.read_text(encoding="utf-8").strip()

    if last_iso:
        try:
            last = datetime.fromisoformat(last_iso)
            if now - last < timedelta(hours=interval_hours):
                return None
        except ValueError:
            LOGGER.warning("Timestamp de backup invalido em settings.toml")

    destination = backup_dir / f"phoenix-{now.strftime('%Y%m%d-%H%M%S')}.db"
    copy2(DATABASE_PATH, destination)
    LOGGER.info("Backup automatico gerado em %s", destination)

    backups = sorted(backup_dir.glob("phoenix-*.db"), key=lambda item: item.stat().st_mtime, reverse=True)
    for stale in backups[keep_last:]:
        stale.unlink(missing_ok=True)

    marker_file.write_text(now.isoformat(), encoding="utf-8")
    return destination
