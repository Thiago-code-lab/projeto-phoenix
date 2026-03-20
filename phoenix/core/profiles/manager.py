from __future__ import annotations

import json
import hashlib
from datetime import datetime
from pathlib import Path


class ProfileManager:
    """Gerencia perfis locais e troca de banco por perfil."""

    PROFILES_DIR = Path("phoenix/data/profiles")
    REGISTRY = Path("phoenix/data/profiles/registry.json")

    def list_profiles(self) -> list[dict]:
        if not self.REGISTRY.exists():
            return []
        return json.loads(self.REGISTRY.read_text(encoding="utf-8"))

    def create_profile(self, name: str, color: str = "#E67E22") -> dict:
        profiles = self.list_profiles()
        pid = len(profiles) + 1
        profile = {
            "id": pid,
            "name": name,
            "color": color,
            "db_path": str(self.PROFILES_DIR / f"{name.lower().replace(' ', '_')}.db"),
            "pin_hash": None,
            "created_at": datetime.now().isoformat(),
        }
        profiles.append(profile)
        self.PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        self.REGISTRY.write_text(json.dumps(profiles, ensure_ascii=True, indent=2), encoding="utf-8")
        return profile

    def switch_profile(self, profile: dict) -> bool:
        from phoenix.core.database import switch_database

        switch_database(profile["db_path"])
        return True

    def set_pin(self, profile: dict, pin: str) -> None:
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        profiles = self.list_profiles()
        for existing in profiles:
            if existing["id"] == profile["id"]:
                existing["pin_hash"] = pin_hash
        self.REGISTRY.write_text(json.dumps(profiles, ensure_ascii=True, indent=2), encoding="utf-8")

    def verify_pin(self, profile: dict, pin: str) -> bool:
        if not profile.get("pin_hash"):
            return True
        return hashlib.sha256(pin.encode()).hexdigest() == profile["pin_hash"]
