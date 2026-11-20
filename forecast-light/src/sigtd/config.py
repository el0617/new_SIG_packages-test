"""Load config.yaml into a read-only mapping. Every model parameter lives in config.yaml."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Config:
    raw: Mapping[str, Any]
    path: Path

    def __getitem__(self, key: str) -> Any:
        return self.raw[key]

    def get(self, dotted: str, default: Any = None) -> Any:
        """Nested lookup: cfg.get("mandate.limits.active_weight_pp")."""
        node: Any = self.raw
        for part in dotted.split("."):
            if not isinstance(node, Mapping) or part not in node:
                return default
            node = node[part]
        return node

    @property
    def sectors(self) -> list[str]:
        return list(self.raw["mandate"]["instruments"].keys())


def _freeze(obj: Any) -> Any:
    if isinstance(obj, dict):
        return MappingProxyType({k: _freeze(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return tuple(_freeze(v) for v in obj)
    return obj


def load_config(path: str | Path | None = None) -> Config:
    p = Path(path) if path else ROOT / "config.yaml"
    with p.open() as fh:
        raw = yaml.safe_load(fh)
    return Config(raw=_freeze(raw), path=p)
