from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional


@dataclass(frozen=True)
class CalibrationProfile:
    provider: str
    model: str
    question_type: str
    version: str
    temperature: float
    samples: int = 0
    ece_before: Optional[float] = None
    ece_after: Optional[float] = None


class CalibrationProfileStore:
    def __init__(self, path: Optional[str] = None) -> None:
        self.path = Path(
            path
            or os.getenv(
                "SYSTEMONE_CALIBRATION_PROFILES",
                str(Path(__file__).resolve().parent / "data" / "calibration_profiles.json"),
            )
        )

    def load(self) -> Dict[str, CalibrationProfile]:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text())
        except (OSError, json.JSONDecodeError):
            return {}
        out: Dict[str, CalibrationProfile] = {}
        for item in data:
            try:
                profile = CalibrationProfile(**item)
            except TypeError:
                continue
            out[self.key(profile.provider, profile.model, profile.question_type, profile.version)] = profile
        return out

    def save(self, profiles: Iterable[CalibrationProfile]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps([asdict(p) for p in profiles], indent=2, sort_keys=True))
        tmp.replace(self.path)

    def upsert(self, profile: CalibrationProfile) -> None:
        profiles = self.load()
        profiles[self.key(profile.provider, profile.model, profile.question_type, profile.version)] = profile
        self.save(profiles.values())

    def get(
        self,
        provider: str,
        model: str,
        question_type: str,
        version: str = "latest",
    ) -> Optional[CalibrationProfile]:
        profiles = self.load()
        if version != "latest":
            return profiles.get(self.key(provider, model, question_type, version))
        matches = [
            p for p in profiles.values()
            if p.provider == provider
            and p.model == model
            and p.question_type == question_type
        ]
        if not matches:
            return None
        return sorted(matches, key=lambda p: p.version)[-1]

    @staticmethod
    def key(provider: str, model: str, question_type: str, version: str) -> str:
        return f"{provider}:{model}:{question_type}:{version}"
