from pathlib import Path

from motor_juegos.render_mode_status import print_render_mode_banner
from motor_juegos.vegetation_preview import build_vegetation_biome_preview, compact_status


if __name__ == "__main__":
    print_render_mode_banner("previsualizar_vegetacion_biomas.py")
    output_dir = Path(__file__).resolve().parent / "previews"
    stats = build_vegetation_biome_preview(output_dir)
    print("Previsualizacion de Vegetacion por Bioma")
    print("Estado:", compact_status(stats))
    print("Imagen:", stats.get("preview", ""))
    print("Reporte:", stats.get("report", ""))
    summary = stats.get("summary", {})
    if summary:
        print("Cobertura:", f"{summary.get('coverage_pct', 0):.2f}%")
        print("Arboles:", f"{summary.get('tree_pct', 0):.2f}%")
        print("Sotobosque:", f"{summary.get('understory_pct', 0):.2f}%")
        print("Lectura:", summary.get("verdict", "n/a"))
    multi_seed = stats.get("multi_seed", {})
    if multi_seed:
        print("Multiseed:", multi_seed.get("stability", "n/a"))
        print(
            "Rango cobertura:",
            f"{multi_seed.get('coverage_min', 0):.2f}%",
            "-",
            f"{multi_seed.get('coverage_max', 0):.2f}%",
        )
    for key, count in stats.get("counts", {}).items():
        if count:
            print(f"{key}: {count}")
