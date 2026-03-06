from __future__ import annotations

"""Rotinas de backup local sem dependencia de servidor."""

import json
import logging
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
