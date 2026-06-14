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
        frame_rescue_enabled=True,
        rescue_fps=34.0,
        emergency_fps=24.0,
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
        self.frame_rescue_enabled = bool(frame_rescue_enabled)
        self.rescue_fps = float(rescue_fps)
        self.emergency_fps = float(emergency_fps)

    def update(self, dt, engine):
        if not self.state.get("enabled", True) or not engine or not hasattr(engine, "clock"):
            self.state["state"] = "FIJO"
            self.state["scale"] = 1.0
            self.state["rescue_level"] = 0
            return
        self.state["frame_index"] = int(self.state.get("frame_index", 0) or 0) + 1
        fps = float(engine.clock.get_fps() or 0.0)
        self.state["fps_now"] = fps
        if fps <= 1.0:
            return
        previous = float(self.state.get("fps_avg", 0.0) or 0.0)
        fps_avg = fps if previous <= 1.0 else previous + (fps - previous) * 0.08
        self.state["fps_avg"] = fps_avg
        scale = float(self.state.get("scale", 1.0) or 1.0)
        raw_rescue_level = self._rescue_level(fps_avg)
        rescue_level = self._stable_rescue_level(raw_rescue_level, dt)
        if fps_avg < self.fps_low:
            self.state["low_time"] = float(self.state.get("low_time", 0.0)) + dt
            self.state["high_time"] = 0.0
            if self.state["low_time"] >= 0.65:
                min_scale = 0.50 if rescue_level >= 2 else 0.58
                scale = max(min_scale, scale - 0.08)
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
        if rescue_level >= 3:
            self.state["state"] = "CRIT"
        elif rescue_level >= 1:
            self.state["state"] = "RESC"
        self.state["scale"] = scale
        self.state["rescue_level"] = int(rescue_level)
        self.state["rescue_label"] = self._rescue_label(rescue_level)
        self.state["rescue_raw_level"] = int(raw_rescue_level)

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
        fog_end = max(125.0, min(240.0, chunk_distance * 0.88))
        fog_start = max(52.0, fog_end * 0.46)
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
        if int(self.state.get("rescue_level", 0) or 0) >= 2:
            return 0
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

    def rescue_settings(self):
        level = int(self.state.get("rescue_level", 0) or 0)
        if level <= 0:
            return {
                "level": 0,
                "label": "OK",
                "far_radius_scale": 1.0,
                "far_max_visible_scale": 1.0,
                "far_build_scale": 1.0,
                "far_softness": 0.18,
                "forest_radius_scale": 1.0,
                "forest_build_scale": 1.0,
                "forest_max_visible_scale": 1.0,
                "forest_softness": 0.12,
                "sky_cloud_scale": 1.0,
            }
        if level == 1:
            return {
                "level": 1,
                "label": "SUAVE",
                "far_radius_scale": 0.68,
                "far_max_visible_scale": 0.52,
                "far_build_scale": 0.0,
                "far_softness": 0.30,
                "forest_radius_scale": 0.62,
                "forest_build_scale": 0.0,
                "forest_max_visible_scale": 0.48,
                "forest_softness": 0.24,
                "sky_cloud_scale": 0.62,
            }
        if level == 2:
            return {
                "level": 2,
                "label": "FUERTE",
                "far_radius_scale": 0.52,
                "far_max_visible_scale": 0.34,
                "far_build_scale": 0.0,
                "far_softness": 0.42,
                "forest_radius_scale": 0.48,
                "forest_build_scale": 0.0,
                "forest_max_visible_scale": 0.32,
                "forest_softness": 0.38,
                "sky_cloud_scale": 0.38,
            }
        return {
            "level": 3,
            "label": "CRITICO",
            "far_radius_scale": 0.36,
            "far_max_visible_scale": 0.22,
            "far_build_scale": 0.0,
            "far_softness": 0.55,
            "forest_radius_scale": 0.32,
            "forest_build_scale": 0.0,
            "forest_max_visible_scale": 0.18,
            "forest_softness": 0.52,
            "sky_cloud_scale": 0.18,
        }

    def _rescue_level(self, fps_avg):
        if not self.frame_rescue_enabled:
            return 0
        fps_avg = float(fps_avg)
        if fps_avg < self.emergency_fps:
            return 3
        if fps_avg < self.rescue_fps:
            return 2
        if fps_avg < max(self.rescue_fps + 10.0, self.fps_low + 6.0):
            return 1
        return 0

    @staticmethod
    def _rescue_label(level):
        return ("OK", "SUAVE", "FUERTE", "CRITICO")[max(0, min(3, int(level)))]

    def _stable_rescue_level(self, raw_level, dt):
        stable = int(self.state.get("rescue_level", 0) or 0)
        raw_level = int(max(0, min(3, raw_level)))
        if raw_level > stable:
            self.state["rescue_up_time"] = float(self.state.get("rescue_up_time", 0.0) or 0.0) + float(dt)
            self.state["rescue_down_time"] = 0.0
            if self.state["rescue_up_time"] >= 0.35:
                stable = raw_level
                self.state["rescue_up_time"] = 0.0
        elif raw_level < stable:
            self.state["rescue_down_time"] = float(self.state.get("rescue_down_time", 0.0) or 0.0) + float(dt)
            self.state["rescue_up_time"] = 0.0
            if self.state["rescue_down_time"] >= 2.4:
                stable = raw_level
                self.state["rescue_down_time"] = 0.0
        else:
            self.state["rescue_up_time"] = 0.0
            self.state["rescue_down_time"] = 0.0
        return stable


def _entity_distance_sq_2d(a_x, a_z, b_x, b_z):
    dx = a_x - b_x
    dz = a_z - b_z
    return dx * dx + dz * dz
