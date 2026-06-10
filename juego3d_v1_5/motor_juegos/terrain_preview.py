"""Previsualizacion 2D de metodos de terreno."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from PIL import Image, ImageDraw

from motor_juegos import biomes
from motor_juegos.terrain_noise_experiment import (
    calculate_fast_noise_terrain_properties,
    calculate_fast_noise_water_properties,
)


MODES = ("current", "fast_noise", "fast_noise_lite")


def _grid(size: int, world_span: float):
    lin = np.linspace(-world_span * 0.5, world_span * 0.5, size)
    return np.meshgrid(lin, lin, indexing="ij")


def _mode_properties(mode: str, gx, gz, seed):
    if mode == "current":
        props, fields = biomes.calculate_terrain_properties_with_fields(gx, gz, seed)
        h, m, cave, temp, rare = props
        water, shore, level, depth = biomes.calculate_water_properties(gx, gz, h, m, temp, rare, seed, terrain_fields=fields)
    elif mode == "fast_noise":
        h, m, cave, temp, rare = calculate_fast_noise_terrain_properties(gx, gz, seed)
        water, shore, level, depth = biomes.calculate_water_properties(gx, gz, h, m, temp, rare, seed)
    else:
        h, m, cave, temp, rare = calculate_fast_noise_terrain_properties(gx, gz, seed)
        water, shore, level, depth = calculate_fast_noise_water_properties(gx, gz, h, m, temp, rare, seed)
    return h, m, temp, rare, water, shore, depth


def _lerp(a, b, t):
    return a * (1.0 - t) + b * t


def _colorize(h, m, temp, water, shore, depth):
    h_norm = np.clip((h - 3.0) / 15.0, 0.0, 1.0)
    low = np.dstack([
        75 + m * 40,
        130 + m * 88,
        62 + m * 35,
    ])
    mid = np.dstack([
        132 + h_norm * 55,
        118 + h_norm * 42,
        78 + h_norm * 32,
    ])
    high = np.dstack([
        205 + temp * 20,
        214 + temp * 22,
        214 + temp * 35,
    ])
    t_mid = np.clip((h_norm - 0.20) / 0.48, 0.0, 1.0)[..., None]
    t_high = np.clip((h_norm - 0.62) / 0.30, 0.0, 1.0)[..., None]
    col = _lerp(low, mid, t_mid)
    col = _lerp(col, high, t_high)

    shore_col = np.array([184, 180, 118], dtype=float)
    col = np.where(shore[..., None], _lerp(col, shore_col, 0.45), col)

    water_depth = np.clip(depth / 3.5, 0.0, 1.0)[..., None]
    water_col = np.dstack([
        35 + water_depth[..., 0] * 18,
        92 + water_depth[..., 0] * 48,
        132 + water_depth[..., 0] * 72,
    ])
    col = np.where(water[..., None], water_col, col)
    return np.clip(col, 0, 255).astype(np.uint8)


def _water_debug_image(water, shore):
    img = np.zeros((water.shape[0], water.shape[1], 3), dtype=np.uint8)
    img[:, :, :] = [28, 32, 34]
    img[shore] = [176, 155, 88]
    img[water] = [35, 142, 220]
    return img


def _add_label(img: Image.Image, text: str, stats: Dict[str, float]) -> Image.Image:
    labeled = Image.new("RGB", (img.width, img.height + 44), (18, 20, 22))
    labeled.paste(img, (0, 44))
    draw = ImageDraw.Draw(labeled)
    draw.text((10, 8), text, fill=(235, 240, 230))
    draw.text(
        (10, 25),
        f"h {stats['h_min']:.1f}-{stats['h_max']:.1f} agua {stats['water_pct']:.1f}%",
        fill=(178, 214, 230),
    )
    return labeled


def build_terrain_method_previews(
    output_dir: str | Path,
    seed: int = 12345,
    size: int = 192,
    world_span: float = 768.0,
) -> Dict[str, object]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    gx, gz = _grid(size, world_span)

    panels = []
    water_panels = []
    summaries = []
    for mode in MODES:
        h, m, temp, rare, water, shore, depth = _mode_properties(mode, gx, gz, seed)
        img = Image.fromarray(_colorize(h, m, temp, water, shore, depth).transpose(1, 0, 2), "RGB")
        stats = {
            "mode": mode,
            "h_min": float(np.min(h)),
            "h_max": float(np.max(h)),
            "water_pct": float(np.mean(water) * 100.0),
        }
        summaries.append(stats)
        labeled = _add_label(img, mode, stats)
        path = out / f"terrain_{mode}.png"
        labeled.save(path)
        panels.append(labeled)

        water_img = Image.fromarray(_water_debug_image(water, shore).transpose(1, 0, 2), "RGB")
        water_labeled = _add_label(water_img, f"{mode} agua", stats)
        water_labeled.save(out / f"terrain_{mode}_water_debug.png")
        water_panels.append(water_labeled)

    gap = 10
    combined = Image.new("RGB", (sum(p.width for p in panels) + gap * (len(panels) - 1), panels[0].height), (10, 12, 14))
    x = 0
    for panel in panels:
        combined.paste(panel, (x, 0))
        x += panel.width + gap
    combined_path = out / "terrain_methods_preview.png"
    combined.save(combined_path)
    water_combined = Image.new("RGB", (combined.width, combined.height), (10, 12, 14))
    x = 0
    for panel in water_panels:
        water_combined.paste(panel, (x, 0))
        x += panel.width + gap
    water_debug_path = out / "terrain_water_debug_preview.png"
    water_combined.save(water_debug_path)
    return {
        "ok": True,
        "combined": str(combined_path),
        "water_debug": str(water_debug_path),
        "output_dir": str(out),
        "summaries": summaries,
    }


def compact_status(stats: Dict[str, object]) -> str:
    if not stats.get("ok"):
        return "not-ready"
    return f"previewOK {stats.get('combined')}"
