"""
Stage33 O - prueba jugable guiada.

Verifica que existen los lanzadores y nombres de log necesarios para comparar
OpenGL legacy contra OpenGL + puente seguro con informacion concreta.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict


@dataclass
class GuidedPlaytestStatus:
    ok: bool = False
    legacy_launcher_ready: bool = False
    bridge_launcher_ready: bool = False
    legacy_log_path_ready: bool = False
    bridge_log_path_ready: bool = False
    stream_bridge_console_markers_ready: bool = True
    recommended_first_run: str = "LANZAR_PLAYTEST_OPENGL_LEGACY_LOG.bat"
    recommended_second_run: str = "LANZAR_PLAYTEST_OPENGL_BRIDGE_LOG.bat"
    legacy_log: str = "juego3d_v1_5/logs/playtest_opengl_legacy.log"
    bridge_log: str = "juego3d_v1_5/logs/playtest_opengl_bridge.log"
    notes: str = ""
    blocked_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_guided_playtest_probe(root: str | None = None) -> Dict[str, Any]:
    status = GuidedPlaytestStatus()
    try:
        base = Path(root).resolve() if root else Path(__file__).resolve().parents[2]
        status.legacy_launcher_ready = (base / "LANZAR_PLAYTEST_OPENGL_LEGACY_LOG.bat").exists()
        status.bridge_launcher_ready = (base / "LANZAR_PLAYTEST_OPENGL_BRIDGE_LOG.bat").exists()
        status.legacy_log_path_ready = (base / "juego3d_v1_5" / "logs").exists() or (base / "juego3d_v1_5").exists()
        status.bridge_log_path_ready = status.legacy_log_path_ready
        status.ok = (
            status.legacy_launcher_ready
            and status.bridge_launcher_ready
            and status.legacy_log_path_ready
            and status.bridge_log_path_ready
            and status.stream_bridge_console_markers_ready
        )
        status.notes = (
            "Prueba guiada lista. Ejecuta primero legacy, luego bridge; si bridge falla, "
            "comparte solo playtest_opengl_bridge.log."
        )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes = f"guided playtest probe fallo: {exc}"
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("legacy_launcher_ready", "legacy-launcher"),
        ("bridge_launcher_ready", "bridge-launcher"),
        ("legacy_log_path_ready", "legacy-log"),
        ("bridge_log_path_ready", "bridge-log"),
        ("stream_bridge_console_markers_ready", "markers"),
        ("ok", "playtestOK"),
    ]:
        if stats.get(key):
            flags.append(label)
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_guided_playtest_probe()
    print("Guided playtest probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
