"""Medicion ligera de rendimiento en runtime.

Se activa con JUEGO_PERF_LOG=1. Mantiene coste bajo cuando esta apagado.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, Iterator
import os
import time


def _flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class RuntimePerfTracker:
    enabled: bool = field(default_factory=lambda: _flag("JUEGO_PERF_LOG"))
    hud_enabled: bool = field(default_factory=lambda: _flag("JUEGO_PERF_HUD"))
    log_interval: float = 0.5
    elapsed_since_log: float = 0.0
    current: Dict[str, float] = field(default_factory=dict)
    last_snapshot: Dict[str, float] = field(default_factory=dict)

    @contextmanager
    def measure(self, name: str) -> Iterator[None]:
        if not (self.enabled or self.hud_enabled):
            yield
            return
        start = time.perf_counter()
        try:
            yield
        finally:
            self.add(name, (time.perf_counter() - start) * 1000.0)

    def add(self, name: str, elapsed_ms: float) -> None:
        if not (self.enabled or self.hud_enabled):
            return
        self.current[name] = self.current.get(name, 0.0) + float(elapsed_ms)

    def finish_frame(self, dt: float, fps: float) -> None:
        if not (self.enabled or self.hud_enabled):
            self.current.clear()
            return
        frame_ms = max(0.0, float(dt) * 1000.0)
        self.current["frame"] = frame_ms
        self.current["fps"] = float(fps)
        self.last_snapshot = dict(self.current)
        self.elapsed_since_log += float(dt)
        if self.enabled and self.elapsed_since_log >= self.log_interval:
            self.elapsed_since_log = 0.0
            print(self.format_log_line(self.last_snapshot))
        self.current.clear()

    def format_log_line(self, stats: Dict[str, float]) -> str:
        order = [
            "fps",
            "frame",
            "update",
            "chunk_total",
            "chunk_admin",
            "chunk_lod",
            "chunk_comm",
            "chunk_compile",
            "player_move",
            "world_context",
            "ai",
            "render3d",
            "render2d",
            "flip",
        ]
        parts = []
        for key in order:
            if key in stats:
                value = stats[key]
                if key == "fps":
                    parts.append(f"{key}={value:.0f}")
                else:
                    parts.append(f"{key}={value:.2f}ms")
        return "[PERF] " + " ".join(parts)

    def snapshot_for_render(self) -> Dict[str, float]:
        if not (self.enabled or self.hud_enabled):
            return {}
        return dict(self.last_snapshot)


perf_tracker = RuntimePerfTracker()
