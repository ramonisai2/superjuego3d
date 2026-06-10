from motor_juegos.terrain_noise_experiment import (
    benchmark_terrain_noise,
    benchmark_full_chunk_modes,
    compact_status,
    compact_full_chunk_status,
)
from motor_juegos.render_mode_status import print_render_mode_banner


if __name__ == "__main__":
    print_render_mode_banner("probar_ruido_terreno.py")
    stats = benchmark_terrain_noise()
    print("Prueba de Ruido Economico para Terreno")
    print("Estado:", compact_status(stats))
    print("Puntos:", stats.get("grid_points", 0))
    print("Actual:", f"{stats.get('current_ms', 0):.3f} ms")
    print("Fast noise:", f"{stats.get('fast_noise_ms', 0):.3f} ms")
    print("Ventaja:", f"x{stats.get('speedup', 0):.2f}")
    print("Altura actual:", f"{stats.get('current_height_min', 0):.2f}", "a", f"{stats.get('current_height_max', 0):.2f}")
    print("Altura fast:", f"{stats.get('fast_height_min', 0):.2f}", "a", f"{stats.get('fast_height_max', 0):.2f}")
    print("Nota:", stats.get("notes", ""))
    print("")
    full = benchmark_full_chunk_modes()
    print("Benchmark de Chunk Completo")
    print("Estado:", compact_full_chunk_status(full))
    print("Loops:", full.get("loops", 0), "Subdivisiones:", full.get("subdivisions", 0))
    for item in full.get("results", []):
        speedup = full.get("speedups_vs_current", {}).get(item.get("mode"), 0)
        print(
            "Modo:",
            item.get("mode"),
            "avg=", f"{item.get('avg_ms', 0):.2f} ms",
            "x=", f"{speedup:.2f}",
            "quads=", item.get("quads", 0),
            "water=", item.get("water", 0),
            "grass=", item.get("grass", 0),
            "rocks=", item.get("rocks", 0),
            "deco=", item.get("deco", 0),
        )
    print("Ganador crudo:", full.get("fastest_mode", ""))
