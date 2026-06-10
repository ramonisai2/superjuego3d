from motor_juegos.terrain_method_advisor import advise_terrain_method, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner


if __name__ == "__main__":
    print_render_mode_banner("elegir_metodo_terreno.py")
    advice = advise_terrain_method()
    print("Recomendador de Metodo de Terreno")
    print("Estado:", compact_status(advice))
    print("Accion:", advice.get("action_label", ""))
    print("Default recomendado:", advice.get("recommended_default", "current"))
    print("Candidato a probar:", advice.get("test_candidate", ""))
    print("Notas:", advice.get("notes", ""))
    bench = advice.get("benchmark") or {}
    for item in bench.get("results", []):
        speedup = bench.get("speedups_vs_current", {}).get(item.get("mode"), 0)
        print(
            "Modo:",
            item.get("mode"),
            "avg=", f"{item.get('avg_ms', 0):.2f} ms",
            "x=", f"{speedup:.2f}",
            "water=", item.get("water", 0),
            "grass=", item.get("grass", 0),
            "rocks=", item.get("rocks", 0),
            "deco=", item.get("deco", 0),
        )
