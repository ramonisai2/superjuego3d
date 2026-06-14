"""Previsualizacion offline de vegetacion por bioma."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np
from PIL import Image, ImageDraw

from motor_juegos import biomes
from motor_juegos.version_info import full_update_name


TREE_COLORS = {
    "arbol_roble": (42, 135, 44),
    "arbol_pino": (34, 98, 76),
    "arbol_abedul": (118, 180, 82),
    "arbol_sauce": (78, 128, 55),
    "arbol_cipres": (22, 70, 38),
    "arbol_seco": (148, 112, 58),
}

UNDERSTORY_COLORS = {
    "arbusto_verde": (34, 116, 42),
    "arbusto_seco": (138, 105, 60),
    "hongo": (210, 74, 66),
    "junco": (156, 178, 76),
    "helecho": (42, 154, 70),
    "hierba_alta": (72, 174, 64),
    "flor_azul": (66, 94, 224),
    "maleza_oscura": (28, 82, 42),
}


def build_vegetation_biome_preview(
    output_dir: str | Path,
    seed: int = 12345,
    size: int = 224,
    world_span: float = 768.0,
) -> Dict[str, object]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    lin = np.linspace(-world_span * 0.5, world_span * 0.5, size)
    gx, gz = np.meshgrid(lin, lin, indexing="ij")
    terrain_props, fields = biomes.calculate_terrain_properties_with_fields(gx, gz, seed)
    h_map, m_map, cave_map, temp_map, rare_map = terrain_props
    water, shore, _level, _depth = biomes.calculate_water_properties(
        gx, gz, h_map, m_map, temp_map, rare_map, seed, terrain_fields=fields
    )

    img = Image.new("RGB", (size, size), (20, 22, 22))
    pix = img.load()
    counts = {key: 0 for key in sorted({**TREE_COLORS, **UNDERSTORY_COLORS})}
    land_pixels = 0
    tree_pixels = 0
    understory_pixels = 0
    for ix in range(size):
        for iz in range(size):
            h = float(h_map[ix, iz])
            moisture = float(m_map[ix, iz])
            temp = float(temp_map[ix, iz])
            rare = float(rare_map[ix, iz])
            cave = bool(cave_map[ix, iz])
            biome_data = biomes.get_biome_color_and_features(h, moisture, cave, temp, rare)
            color, has_grass, _rock_chance, _rock_type, deco_type, deco_chance, _rock_color = biome_data
            base = tuple(max(0, min(255, int(c * 255))) for c in color)
            if water[ix, iz]:
                base = (34, 104, 158)
            elif shore[ix, iz]:
                base = _mix_rgb(base, (185, 170, 100), 0.45)
            else:
                land_pixels += 1
            mark = _vegetation_mark(
                h,
                moisture,
                temp,
                rare,
                has_grass,
                deco_type,
                deco_chance,
                bool(water[ix, iz]),
                bool(shore[ix, iz]),
                ix,
                iz,
                seed,
            )
            if mark:
                counts[mark] = counts.get(mark, 0) + 1
                if mark in TREE_COLORS:
                    tree_pixels += 1
                else:
                    understory_pixels += 1
                mark_color = TREE_COLORS.get(mark) or UNDERSTORY_COLORS.get(mark) or (240, 240, 240)
                base = _mix_rgb(base, mark_color, 0.72)
            pix[iz, ix] = base

    summary = _coverage_summary(land_pixels, tree_pixels, understory_pixels)
    samples = _sample_multi_seed_coverage((seed, 24680, 54321), min(size, 128), world_span)
    panel = _with_legend(img, counts, summary)
    preview_path = out / "vegetation_biomes_preview.png"
    report_path = out / "vegetation_biomes_report.txt"
    panel.save(preview_path)
    _write_report(report_path, counts, summary, samples, seed, size, world_span)
    return {
        "ok": True,
        "preview": str(preview_path),
        "report": str(report_path),
        "output_dir": str(out),
        "counts": counts,
        "summary": summary,
        "multi_seed": samples,
    }


def compact_status(stats: Dict[str, object]) -> str:
    if not stats.get("ok"):
        return "not-ready"
    summary = stats.get("summary", {})
    multi_seed = stats.get("multi_seed", {})
    stability = multi_seed.get("stability", "n/a") if isinstance(multi_seed, dict) else "n/a"
    return f"vegetationPreviewOK cobertura={summary.get('coverage_pct', 0):.1f}% multiseed={stability} {stats.get('preview')}"


def _write_report(
    report_path: Path,
    counts: Dict[str, int],
    summary: Dict[str, object],
    samples: Dict[str, object],
    seed: int,
    size: int,
    world_span: float,
) -> None:
    lines = [
        "JUEGO 1.6 - REPORTE DE VEGETACION POR BIOMA",
        "",
        f"update_stage={full_update_name()}",
        f"seed={seed}",
        f"preview_size={size}x{size}",
        f"world_span={world_span:.1f}",
        "",
        "DIAGNOSTICO",
        f"cobertura_total={summary.get('coverage_pct', 0):.2f}%",
        f"arboles={summary.get('tree_pct', 0):.2f}%",
        f"sotobosque={summary.get('understory_pct', 0):.2f}%",
        f"lectura={summary.get('verdict', 'n/a')}",
        f"land_pixels={summary.get('land_pixels', 0)}",
        "",
        "CONTEOS",
    ]
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"{key}={value}")
    lines.extend([
        "",
        "MUESTRAS_MULTISEED",
        f"stability={samples.get('stability', 'n/a')}",
        f"coverage_min={samples.get('coverage_min', 0):.2f}%",
        f"coverage_avg={samples.get('coverage_avg', 0):.2f}%",
        f"coverage_max={samples.get('coverage_max', 0):.2f}%",
    ])
    for item in samples.get("items", []):
        lines.append(
            "seed_{seed}=cobertura:{coverage:.2f}% arboles:{trees:.2f}% sotobosque:{understory:.2f}% lectura:{verdict}".format(
                seed=item.get("seed", 0),
                coverage=item.get("coverage_pct", 0),
                trees=item.get("tree_pct", 0),
                understory=item.get("understory_pct", 0),
                verdict=item.get("verdict", "n/a"),
            )
        )
    lines.extend([
        "",
        "LECTURA RAPIDA",
        _recommendation(summary, samples),
    ])
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _recommendation(summary: Dict[str, object], samples: Dict[str, object] | None = None) -> str:
    if samples and samples.get("stability") == "revisar":
        return "Una o mas semillas salen fuera del rango sano; revisar reglas antes de subir densidad."
    verdict = summary.get("verdict", "n/a")
    if verdict == "vacio":
        return "Subir detalle de suelo o ampliar reglas de vegetacion antes de agregar mas sistemas."
    if verdict == "saturado":
        return "Bajar probabilidades de sotobosque/arboles antes de agregar nuevas plantas."
    return "Cobertura sana: conviene probar OpenGL y medir FPS antes de tocar densidad."


def _sample_multi_seed_coverage(seeds, size: int, world_span: float) -> Dict[str, object]:
    items = []
    for seed in seeds:
        summary = _coverage_for_seed(int(seed), size, world_span)
        items.append({"seed": int(seed), **summary})
    coverages = [item["coverage_pct"] for item in items]
    stability = "estable" if all(item["verdict"] == "sano" for item in items) else "revisar"
    return {
        "stability": stability,
        "coverage_min": min(coverages) if coverages else 0.0,
        "coverage_avg": sum(coverages) / max(1, len(coverages)),
        "coverage_max": max(coverages) if coverages else 0.0,
        "items": items,
    }


def _coverage_for_seed(seed: int, size: int, world_span: float) -> Dict[str, object]:
    lin = np.linspace(-world_span * 0.5, world_span * 0.5, size)
    gx, gz = np.meshgrid(lin, lin, indexing="ij")
    terrain_props, fields = biomes.calculate_terrain_properties_with_fields(gx, gz, seed)
    h_map, m_map, cave_map, temp_map, rare_map = terrain_props
    water, shore, _level, _depth = biomes.calculate_water_properties(
        gx, gz, h_map, m_map, temp_map, rare_map, seed, terrain_fields=fields
    )
    land_pixels = 0
    tree_pixels = 0
    understory_pixels = 0
    for ix in range(size):
        for iz in range(size):
            if not water[ix, iz] and not shore[ix, iz]:
                land_pixels += 1
            biome_data = biomes.get_biome_color_and_features(
                float(h_map[ix, iz]),
                float(m_map[ix, iz]),
                bool(cave_map[ix, iz]),
                float(temp_map[ix, iz]),
                float(rare_map[ix, iz]),
            )
            _color, has_grass, _rock_chance, _rock_type, deco_type, deco_chance, _rock_color = biome_data
            mark = _vegetation_mark(
                float(h_map[ix, iz]),
                float(m_map[ix, iz]),
                float(temp_map[ix, iz]),
                float(rare_map[ix, iz]),
                has_grass,
                deco_type,
                deco_chance,
                bool(water[ix, iz]),
                bool(shore[ix, iz]),
                ix,
                iz,
                seed,
            )
            if mark in TREE_COLORS:
                tree_pixels += 1
            elif mark in UNDERSTORY_COLORS:
                understory_pixels += 1
    return _coverage_summary(land_pixels, tree_pixels, understory_pixels)


def _vegetation_mark(h, moisture, temp, rare, has_grass, deco_type, deco_chance, water, shore, ix, iz, seed):
    if water:
        return None
    roll = _hash01(ix, iz, seed)
    if deco_type in TREE_COLORS and roll < min(0.58, deco_chance * 38.0):
        return deco_type
    under_roll = _hash01(ix + 917, iz - 431, seed + 19)
    if (shore or (moisture > 0.74 and h < 8.5)) and under_roll < 0.36:
        return "junco"
    if moisture > 0.74 and temp < 0.62 and rare > 0.10 and under_roll < 0.17:
        return "hongo"
    if moisture > 0.70 and temp < 0.72 and under_roll < 0.28:
        return "helecho"
    if moisture > 0.64 and temp < 0.58 and rare < -0.18 and under_roll < 0.22:
        return "maleza_oscura"
    if 0.48 < moisture < 0.78 and temp > 0.28 and rare > 0.24 and under_roll < 0.16:
        return "arbusto_verde"
    if moisture < 0.30 and temp > 0.46 and h < 13.0 and under_roll < 0.13:
        return "arbusto_seco"
    if 0.40 < moisture < 0.72 and temp < 0.66 and rare < 0.18 and under_roll < 0.18:
        return "flor_azul"
    if has_grass and moisture > 0.34 and under_roll < 0.14:
        return "hierba_alta"
    return None


def _hash01(ix: int, iz: int, seed: int) -> float:
    value = (ix * 374761393 + iz * 668265263 + seed * 1442695041) & 0xFFFFFFFF
    value = (value ^ (value >> 13)) * 1274126177
    value = (value ^ (value >> 16)) & 0xFFFFFFFF
    return value / 0xFFFFFFFF


def _coverage_summary(land_pixels: int, tree_pixels: int, understory_pixels: int) -> Dict[str, object]:
    total_marks = tree_pixels + understory_pixels
    safe_land = max(1, land_pixels)
    coverage_pct = total_marks * 100.0 / safe_land
    tree_pct = tree_pixels * 100.0 / safe_land
    understory_pct = understory_pixels * 100.0 / safe_land
    if coverage_pct < 12.0:
        verdict = "vacio"
    elif coverage_pct > 38.0:
        verdict = "saturado"
    else:
        verdict = "sano"
    return {
        "land_pixels": land_pixels,
        "tree_pixels": tree_pixels,
        "understory_pixels": understory_pixels,
        "coverage_pct": coverage_pct,
        "tree_pct": tree_pct,
        "understory_pct": understory_pct,
        "verdict": verdict,
    }


def _with_legend(img: Image.Image, counts: Dict[str, int], summary: Dict[str, object]) -> Image.Image:
    legend_width = 292
    legend_height = 224 + (len(TREE_COLORS) + len(UNDERSTORY_COLORS)) * 18
    panel_height = max(img.height, legend_height)
    panel = Image.new("RGB", (img.width + legend_width, panel_height), (16, 18, 20))
    panel.paste(img, (0, 0))
    draw = ImageDraw.Draw(panel)
    x = img.width + 12
    y = 12
    draw.text((x, y), "VEGETACION POR BIOMA", fill=(235, 240, 230))
    y += 24
    draw.text((x, y), "Arboles", fill=(190, 225, 180))
    y += 18
    for key, color in TREE_COLORS.items():
        _legend_row(draw, x, y, color, key, counts.get(key, 0))
        y += 18
    y += 8
    draw.text((x, y), "Sotobosque", fill=(190, 220, 235))
    y += 18
    for key, color in UNDERSTORY_COLORS.items():
        _legend_row(draw, x, y, color, key, counts.get(key, 0))
        y += 18
    y += 10
    draw.text((x, y), "Azul = agua / orilla", fill=(150, 196, 230))
    y += 22
    draw.text((x, y), "Diagnostico", fill=(235, 220, 170))
    y += 18
    draw.text((x, y), f"cobertura: {summary.get('coverage_pct', 0):.1f}%", fill=(220, 224, 214))
    y += 16
    draw.text((x, y), f"arboles: {summary.get('tree_pct', 0):.1f}%", fill=(190, 225, 180))
    y += 16
    draw.text((x, y), f"sotobosque: {summary.get('understory_pct', 0):.1f}%", fill=(190, 220, 235))
    y += 16
    draw.text((x, y), f"lectura: {summary.get('verdict', 'n/a')}", fill=(235, 220, 170))
    return panel


def _legend_row(draw: ImageDraw.ImageDraw, x: int, y: int, color, label: str, count: int) -> None:
    draw.rectangle((x, y + 3, x + 12, y + 15), fill=color)
    draw.text((x + 18, y), f"{label}: {count}", fill=(220, 224, 214))


def _mix_rgb(a, b, t):
    return tuple(int(a[i] * (1.0 - t) + b[i] * t) for i in range(3))
