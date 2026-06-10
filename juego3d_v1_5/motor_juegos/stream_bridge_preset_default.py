"""
Stage33 T - selector seguro de preset por defecto.

No cambia el juego a balanced automaticamente salvo que:
- JUEGO_STREAM_BRIDGE_AUTO_PRESET=1 este activo.
- El comparador tenga logs suficientes.
- Balanced sea el mejor candidato limpio.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict
import os

from motor_juegos.stream_bridge_preset_comparison import compare_stream_bridge_presets


@dataclass
class PresetDefaultDecision:
    ok: bool = False
    auto_enabled: bool = False
    selected_preset: str = "safe"
    reason_code: str = "SAFE_DEFAULT"
    reason_label: str = "Safe sigue como default"
    comparison_checked: bool = False
    comparison_action: str = ""
    comparison_best: str = ""
    notes: str = ""
    comparison: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on", "auto"}


def decide_stream_bridge_default_preset(root: str | None = None) -> Dict[str, Any]:
    decision = PresetDefaultDecision()
    decision.auto_enabled = _env_flag("JUEGO_STREAM_BRIDGE_AUTO_PRESET")

    explicit = os.environ.get("JUEGO_STREAM_BRIDGE_PRESET", "").strip().lower()
    if explicit in {"safe", "balanced", "aggressive"}:
        decision.ok = True
        decision.selected_preset = explicit
        decision.reason_code = "EXPLICIT_ENV"
        decision.reason_label = "Preset elegido manualmente"
        decision.notes = "JUEGO_STREAM_BRIDGE_PRESET tiene prioridad sobre el modo auto."
        return decision.to_dict()

    if not decision.auto_enabled:
        decision.ok = True
        decision.notes = "Modo auto apagado; default conservador."
        return decision.to_dict()

    comparison = compare_stream_bridge_presets(root=root)
    decision.comparison_checked = True
    decision.comparison = comparison
    decision.comparison_action = str(comparison.get("action_code") or "")
    decision.comparison_best = str(comparison.get("best_preset") or "")

    if (
        comparison.get("ok")
        and comparison.get("action_code") == "CANDIDATE_BALANCED"
        and comparison.get("best_preset") == "balanced"
    ):
        decision.ok = True
        decision.selected_preset = "balanced"
        decision.reason_code = "BALANCED_CLEAN_WIN"
        decision.reason_label = "Balanced gana limpio"
        decision.notes = "Modo auto activo y balanced es el mejor candidato limpio."
        return decision.to_dict()

    decision.ok = True
    decision.notes = "Modo auto activo, pero aun no hay victoria limpia de balanced."
    return decision.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = [str(stats.get("selected_preset") or "safe"), str(stats.get("reason_code") or "SAFE_DEFAULT")]
    if stats.get("auto_enabled"):
        flags.append("auto")
    if stats.get("comparison_checked"):
        flags.append("checked")
    if stats.get("ok"):
        flags.append("defaultOK")
    return " ".join(flags)


if __name__ == "__main__":
    stats = decide_stream_bridge_default_preset()
    print("Stream bridge default:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
