from pathlib import Path

from motor_juegos.terrain_preview import build_terrain_method_previews, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner


if __name__ == "__main__":
    print_render_mode_banner("previsualizar_metodos_terreno.py")
    output_dir = Path(__file__).resolve().parent / "previews"
    stats = build_terrain_method_previews(output_dir)
    print("Previsualizacion de Metodos de Terreno")
    print("Estado:", compact_status(stats))
    print("Imagen:", stats.get("combined", ""))
    print("Agua debug:", stats.get("water_debug", ""))
    for item in stats.get("summaries", []):
        print(
            "Modo:",
            item.get("mode"),
            "altura=",
            f"{item.get('h_min', 0):.2f}-{item.get('h_max', 0):.2f}",
            "agua=",
            f"{item.get('water_pct', 0):.2f}%",
        )
