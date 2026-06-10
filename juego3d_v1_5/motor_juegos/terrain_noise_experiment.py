"""Experimento de terreno con ruido economico tipo Perlin/value noise.

No reemplaza el terreno principal. Sirve para comparar costo y probar una ruta
mas barata activable con JUEGO_TERRAIN_MODE=fast_noise.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List
import time

import numpy as np


def _smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _hash_grid(ix, iz, seed):
    # Hash determinista vectorizado. Es mas barato que recrear toda la logica
    # del terreno actual, aunque no pretende ser Perlin perfecto.
    v = ix * 127.1 + iz * 311.7 + seed * 0.013
    return np.mod(np.sin(v) * 43758.5453, 1.0)


def value_noise_2d(x_array, z_array, seed, scale):
    x = x_array / float(scale)
    z = z_array / float(scale)
    x0 = np.floor(x)
    z0 = np.floor(z)
    tx = _smoothstep(x - x0)
    tz = _smoothstep(z - z0)

    n00 = _hash_grid(x0, z0, seed)
    n10 = _hash_grid(x0 + 1.0, z0, seed)
    n01 = _hash_grid(x0, z0 + 1.0, seed)
    n11 = _hash_grid(x0 + 1.0, z0 + 1.0, seed)

    nx0 = n00 * (1.0 - tx) + n10 * tx
    nx1 = n01 * (1.0 - tx) + n11 * tx
    return nx0 * (1.0 - tz) + nx1 * tz


def fbm_noise_2d(x_array, z_array, seed):
    n1 = value_noise_2d(x_array, z_array, seed + 11, 420.0)
    n2 = value_noise_2d(x_array, z_array, seed + 23, 165.0)
    n3 = value_noise_2d(x_array, z_array, seed + 37, 52.0)
    n4 = value_noise_2d(x_array, z_array, seed + 53, 24.0)
    return np.clip(n1 * 0.38 + n2 * 0.27 + n3 * 0.22 + n4 * 0.13, 0.0, 1.0)


def calculate_fast_noise_terrain_properties(x_array, z_array, seed):
    from . import biomes

    base = fbm_noise_2d(x_array, z_array, seed)
    macro = value_noise_2d(x_array, z_array, seed + 101, 760.0)
    moisture = value_noise_2d(x_array, z_array, seed + 211, 310.0)
    rare_noise = value_noise_2d(x_array, z_array, seed + 307, 118.0)
    lake_basin = biomes._lake_basin_field(x_array, z_array, seed)
    high_lake_basin = biomes._high_lake_basin_field(x_array, z_array, seed)
    mesa_strength, _ = biomes._mesa_field(x_array, z_array, seed)

    hills = _smoothstep((macro - 0.47) / 0.30)
    peaks = _smoothstep((base - 0.66) / 0.26) * _smoothstep((macro - 0.55) / 0.22)
    lowlands = 1.0 - _smoothstep((macro - 0.25) / 0.22)

    elevation = (
        3.9
        + base * 8.4
        + hills * 5.8
        + peaks * 5.2
        - lowlands * 1.8
    )

    lake_curve = _smoothstep((lake_basin - 0.34) / 0.52)
    lake_inner = _smoothstep((lake_basin - 0.56) / 0.34)
    high_lake_gate = _smoothstep((elevation - 9.0) / 3.0) * (1.0 - _smoothstep((elevation - 15.4) / 2.0))
    high_lake_curve = _smoothstep((high_lake_basin - 0.38) / 0.42) * high_lake_gate
    mesa_edge = _smoothstep((mesa_strength - 0.16) / 0.26) * (1.0 - _smoothstep((mesa_strength - 0.70) / 0.22))
    runoff_wave = (
        np.sin(x_array * 0.027 + z_array * 0.011 + seed * 0.037)
        + 0.42 * np.sin(x_array * 0.053 - z_array * 0.041 + seed * 0.019)
    )
    runoff_line = np.clip((0.092 - np.abs(runoff_wave)) / 0.092, 0.0, 1.0)
    runoff_carve = mesa_edge * runoff_line * _smoothstep((moisture - 0.34) / 0.30) * high_lake_gate * 0.52
    elevation = elevation - lake_curve * 1.15 - lake_inner * 1.85 - high_lake_curve * 1.25 - runoff_carve
    elevation = np.clip(elevation, 0.25, 32.0)

    rareza = rare_noise * 2.0 - 1.0
    cave = (rareza > 0.74) & (elevation > 10.0) & (elevation < 24.0)
    elevation = np.where(cave, elevation - 2.5, elevation)
    elevation = np.clip(elevation, 0.25, 32.0)

    temperatura = np.clip(0.88 - elevation / 34.0 + (1.0 - moisture) * 0.16 + rareza * 0.08, 0.0, 1.0)
    return elevation, moisture, cave, temperatura, rareza


def calculate_fast_noise_water_properties(x_array, z_array, elevation, moisture, temperatura, rareza, seed):
    basin = value_noise_2d(x_array, z_array, seed + 701, 260.0)
    basin_detail = value_noise_2d(x_array, z_array, seed + 719, 92.0)
    basin = np.clip(basin * 0.72 + basin_detail * 0.28, 0.0, 1.0)

    low_gate = (basin > 0.70) & (elevation < 7.2)
    high_gate = (basin > 0.78) & (elevation > 10.0) & (elevation < 15.5) & (temperatura > 0.12)
    low_level = 5.85 + np.floor((basin - 0.70) * 8.0) * 0.08
    high_level = 13.10 + np.floor((basin - 0.78) * 7.0) * 0.07
    water_level = np.where(high_gate, high_level, low_level)
    depth = np.clip(water_level - elevation, 0.0, 5.0)
    water_mask = (low_gate | high_gate) & (depth > 0.16)

    shore = (~water_mask) & (basin > 0.58) & (depth > -1.10) & (depth < 0.28)
    return water_mask, shore, water_level, depth


@dataclass
class TerrainNoiseBenchmark:
    ok: bool = False
    grid_points: int = 0
    current_ms: float = 0.0
    fast_noise_ms: float = 0.0
    speedup: float = 0.0
    current_height_min: float = 0.0
    current_height_max: float = 0.0
    fast_height_min: float = 0.0
    fast_height_max: float = 0.0
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def benchmark_terrain_noise(seed=12345, subdivisions=48, loops=30) -> Dict[str, Any]:
    from . import biomes

    size = 64.0
    step = size / float(subdivisions)
    pad = 6
    lin = np.arange(-pad, subdivisions + 1 + pad) * step
    gx, gz = np.meshgrid(lin, lin, indexing="ij")

    current_last = None
    t0 = time.perf_counter()
    for _ in range(int(loops)):
        current_last = biomes.calculate_terrain_properties(gx, gz, seed)
    current_ms = ((time.perf_counter() - t0) * 1000.0) / max(1, int(loops))

    fast_last = None
    t1 = time.perf_counter()
    for _ in range(int(loops)):
        fast_last = calculate_fast_noise_terrain_properties(gx, gz, seed)
    fast_ms = ((time.perf_counter() - t1) * 1000.0) / max(1, int(loops))

    current_h = current_last[0]
    fast_h = fast_last[0]
    speedup = current_ms / fast_ms if fast_ms > 0.0 else 0.0
    notes = "fast_noise parece mas barato." if speedup >= 1.15 else "La diferencia no justifica cambiar todavia."
    return TerrainNoiseBenchmark(
        ok=True,
        grid_points=int(gx.size),
        current_ms=float(current_ms),
        fast_noise_ms=float(fast_ms),
        speedup=float(speedup),
        current_height_min=float(np.min(current_h)),
        current_height_max=float(np.max(current_h)),
        fast_height_min=float(np.min(fast_h)),
        fast_height_max=float(np.max(fast_h)),
        notes=notes,
    ).to_dict()


def _summarize_chunk_result(result) -> Dict[str, int]:
    _, _, quads, grass, rocks, deco, water, _ = result
    return {
        "quads": len(quads),
        "grass": len(grass),
        "rocks": len(rocks),
        "deco": len(deco),
        "water": len(water),
    }


def benchmark_full_chunk_modes(seed=12345, subdivisions=48, loops=3) -> Dict[str, Any]:
    from . import environment as env
    import os

    modes = ["current", "fast_noise", "fast_noise_lite"]
    previous_mode = os.environ.get("JUEGO_TERRAIN_MODE")
    results: List[Dict[str, Any]] = []
    try:
        for mode in modes:
            os.environ["JUEGO_TERRAIN_MODE"] = mode
            elapsed_total = 0.0
            last = None
            for index in range(int(loops)):
                coord = (index % 2, index // 2)
                env._height_cache.pop(coord, None)
                start = time.perf_counter()
                last = env.calculate_chunk_data_background(coord[0], coord[1], 64, subdivisions, seed)
                elapsed_total += (time.perf_counter() - start) * 1000.0
            avg_ms = elapsed_total / max(1, int(loops))
            summary = _summarize_chunk_result(last)
            results.append({
                "mode": mode,
                "avg_ms": float(avg_ms),
                **summary,
            })
    finally:
        if previous_mode is None:
            os.environ.pop("JUEGO_TERRAIN_MODE", None)
        else:
            os.environ["JUEGO_TERRAIN_MODE"] = previous_mode

    fastest = min(results, key=lambda item: item["avg_ms"]) if results else {"mode": ""}
    current = next((item for item in results if item["mode"] == "current"), None)
    speedups = {}
    if current:
        for item in results:
            speedups[item["mode"]] = (current["avg_ms"] / item["avg_ms"]) if item["avg_ms"] > 0 else 0.0

    return {
        "ok": bool(results),
        "loops": int(loops),
        "subdivisions": int(subdivisions),
        "fastest_mode": fastest.get("mode", ""),
        "results": results,
        "speedups_vs_current": speedups,
        "notes": "Usar el mas rapido solo si visualmente conserva identidad suficiente.",
    }


def compact_status(stats: Dict[str, Any]) -> str:
    if not stats.get("ok"):
        return "not-ready"
    return (
        f"noiseBench current={stats.get('current_ms', 0):.2f}ms "
        f"fast={stats.get('fast_noise_ms', 0):.2f}ms "
        f"x{stats.get('speedup', 0):.2f}"
    )


def compact_full_chunk_status(stats: Dict[str, Any]) -> str:
    if not stats.get("ok"):
        return "not-ready"
    parts = [f"fullChunk best={stats.get('fastest_mode', '')}"]
    for item in stats.get("results", []):
        parts.append(f"{item.get('mode')}={item.get('avg_ms', 0):.1f}ms")
    return " ".join(parts)
