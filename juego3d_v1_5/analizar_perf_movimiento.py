from motor_juegos.performance_log_analyzer import analyze_movement_perf_logs, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner


if __name__ == "__main__":
    print_render_mode_banner("analizar_perf_movimiento.py")
    stats = analyze_movement_perf_logs()
    print("Analisis de FPS en Movimiento")
    print("Estado:", compact_status(stats))
    print("Recomendacion:", stats.get("recommendation", ""))
    for item in stats.get("summaries") or []:
        print(
            "Log:",
            item.get("name"),
            "exists=", item.get("exists"),
            "perf=", item.get("perf_lines"),
            "avgFPS=", f"{item.get('avg_fps', 0):.1f}",
            "minFPS=", f"{item.get('min_fps', 0):.1f}",
            "maxFrame=", f"{item.get('max_frame_ms', 0):.1f}ms",
            "chunk=", f"{item.get('max_chunk_ms', 0):.1f}ms",
            "lod=", f"{item.get('max_chunk_lod_ms', 0):.1f}ms",
            "compile=", f"{item.get('max_chunk_compile_ms', 0):.1f}ms",
            "r3d=", f"{item.get('max_render3d_ms', 0):.1f}ms",
            "flip=", f"{item.get('max_flip_ms', 0):.1f}ms",
            "bottleneck=", item.get("likely_bottleneck"),
            "notes=", item.get("notes"),
        )
