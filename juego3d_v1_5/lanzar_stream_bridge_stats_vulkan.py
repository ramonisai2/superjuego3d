import os

from motor_juegos.stream_bridge_stats_probe import run_stream_bridge_stats_probe, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner

if __name__ == "__main__":
    os.environ["JUEGO_RENDER_BACKEND"] = "vulkan_stream_bridge_stats"
    print_render_mode_banner("lanzar_stream_bridge_stats_vulkan.py")
    stats = run_stream_bridge_stats_probe()
    print("Estadisticas Puente Seguro Vulkan Experimental")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
