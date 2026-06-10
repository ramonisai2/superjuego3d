from motor_juegos.stream_bridge_preset_comparison import (
    compare_stream_bridge_presets,
    compact_status,
)
from motor_juegos.render_mode_status import print_render_mode_banner


if __name__ == "__main__":
    print_render_mode_banner("comparar_presets_stream_bridge.py")
    stats = compare_stream_bridge_presets()
    print("Comparador de Presets del Puente")
    print("Estado:", compact_status(stats))
    print("Accion:", stats.get("action_label", ""))
    print("Recomendacion:", stats.get("recommendation", ""))
    for item in stats.get("preset_summaries") or []:
        print(
            "Preset:",
            item.get("preset"),
            "exists=", item.get("exists"),
            "errors=", item.get("error_count"),
            "stream=", item.get("stream_bridge_count"),
            "score=", item.get("score"),
            "notes=", item.get("notes"),
        )
