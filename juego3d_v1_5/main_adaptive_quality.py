"""Reglas de calidad adaptativa y distancias de render."""

from __future__ import annotations

import math


class AdaptiveQualityRuntime:
    def __init__(
        self,
        state,
        *,
        chunk_size,
        radio_vision,
        radio_detalle,
        chunk_render_extra,
        chunk_render_min_extra,
        detail_chunk_render_extra,
        entity_full_detail_distance,
        entity_mid_detail_distance,
        lods_crear_por_tanda,
        fps_low,
        fps_high,
        adaptive_chunk_render_enabled=True,
        adaptive_streaming_enabled=True,
    ):
        self.state = state
        self.chunk_size = float(chunk_size)
        self.radio_vision = float(radio_vision)
        self.radio_detalle = float(radio_detalle)
        self.chunk_render_extra = float(chunk_render_extra)
        self.chunk_render_min_extra = float(chunk_render_min_extra)
        self.detail_chunk_render_extra = float(detail_chunk_render_extra)
        self.entity_full_detail_distance = float(entity_full_detail_distance)
        self.entity_mid_detail_distance = float(entity_mid_detail_distance)
        self.lods_crear_por_tanda = int(lods_crear_por_tanda)
        self.fps_low = float(fps_low)
        self.fps_high = float(fps_high)
        self.adaptive_chunk_render_enabled = bool(adaptive_chunk_render_enabled)
        self.adaptive_streaming_enabled = bool(adaptive_streaming_enabled)

    def update(self, dt, engine):
        if not self.state.get("enabled", True) or not engine or not hasattr(engine, "clock"):
            self.state["state"] = "FIJO"
            self.state["scale"] = 1.0
            return
        fps = float(engine.clock.get_fps() or 0.0)
        if fps <= 1.0:
            return
        previous = float(self.state.get("fps_avg", 0.0) or 0.0)
        fps_avg = fps if previous <= 1.0 else previous + (fps - previous) * 0.08
        self.state["fps_avg"] = fps_avg
        scale = float(self.state.get("scale", 1.0) or 1.0)
        if fps_avg < self.fps_low:
            self.state["low_time"] = float(self.state.get("low_time", 0.0)) + dt
            self.state["high_time"] = 0.0
            if self.state["low_time"] >= 0.65:
                scale = max(0.58, scale - 0.08)
                self.state["low_time"] = 0.0
                self.state["state"] = "AHORRO"
        elif fps_avg > self.fps_high:
            self.state["high_time"] = float(self.state.get("high_time", 0.0)) + dt
            self.state["low_time"] = 0.0
            if self.state["high_time"] >= 1.4:
                scale = min(1.0, scale + 0.04)
                self.state["high_time"] = 0.0
                self.state["state"] = "RECUP" if scale < 0.999 else "OK"
        else:
            self.state["low_time"] = 0.0
            self.state["high_time"] = 0.0
            self.state["state"] = "OK" if scale >= 0.999 else "AHORRO"
        self.state["scale"] = scale

    def distance(self, base_distance, min_scale=0.55):
        if not self.state.get("enabled", True):
            return float(base_distance)
        scale = max(float(min_scale), min(1.0, float(self.state.get("scale", 1.0) or 1.0)))
        return float(base_distance) * scale

    def chunk_render_distance(self):
        extra = max(0.75, float(self.chunk_render_extra))
        min_extra = max(0.75, min(extra, float(self.chunk_render_min_extra)))
        base_distance = self.chunk_size * (self.radio_vision + extra)
        if not self.adaptive_chunk_render_enabled or not self.state.get("enabled", True):
            return float(base_distance)
        min_distance = self.chunk_size * (self.radio_detalle + min_extra)
        scale = max(0.70, min(1.0, float(self.state.get("scale", 1.0) or 1.0)))
        return max(float(min_distance), float(base_distance) * scale)

    def detail_chunk_render_distance(self):
        extra = max(0.60, float(self.detail_chunk_render_extra))
        base_distance = self.chunk_size * (self.radio_detalle + extra)
        if not self.adaptive_chunk_render_enabled or not self.state.get("enabled", True):
            return float(base_distance)
        min_distance = self.chunk_size * (self.radio_detalle + 0.65)
        scale = max(0.72, min(1.0, float(self.state.get("scale", 1.0) or 1.0)))
        return max(float(min_distance), float(base_distance) * scale)

    def fog_range(self):
        chunk_distance = self.chunk_render_distance()
        fog_end = max(115.0, min(220.0, chunk_distance * 0.78))
        fog_start = max(42.0, fog_end * 0.34)
        return fog_start, fog_end

    def stream_interval(self):
        if not self.adaptive_streaming_enabled or not self.state.get("enabled", True):
            return 0.05
        scale = max(0.58, min(1.0, float(self.state.get("scale", 1.0) or 1.0)))
        return 0.05 + (1.0 - scale) * 0.17

    def lod_limit(self):
        base = max(1, int(self.lods_crear_por_tanda))
        if not self.adaptive_streaming_enabled or not self.state.get("enabled", True):
            return base
        scale = max(0.58, min(1.0, float(self.state.get("scale", 1.0) or 1.0)))
        if scale < 0.76:
            return 1
        return base

    def entity_detail_level(self, px, pz, x, z, *, forced_full=False):
        if forced_full:
            return "full"
        dist2 = _entity_distance_sq_2d(px, pz, x, z)
        full_distance = self.distance(self.entity_full_detail_distance, 0.62)
        mid_distance = self.distance(self.entity_mid_detail_distance, 0.58)
        if dist2 <= full_distance * full_distance:
            return "full"
        if dist2 <= mid_distance * mid_distance:
            return "mid"
        return "far"


def _entity_distance_sq_2d(a_x, a_z, b_x, b_z):
    dx = a_x - b_x
    dz = a_z - b_z
    return dx * dx + dz * dz
