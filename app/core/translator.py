"""Runtime translation helper."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


class Translator:
    """Simple JSON based translator supporting runtime updates."""

    def __init__(self, base_path: Path, language: str = "en") -> None:
        self._base_path = base_path
        self._cache: Dict[str, Dict[str, str]] = {}
        self._language = language
        self.load(language)

    @property
    def language(self) -> str:
        return self._language

    def load(self, language: str) -> None:
        path = self._base_path / f"{language}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self._cache[language] = data
        self._language = language

    def translate(self, key: str) -> str:
        return self._cache.get(self._language, {}).get(key, key)

    def available_languages(self) -> Dict[str, str]:
        return {path.stem: path.stem for path in sorted(self._base_path.glob("*.json"))}

