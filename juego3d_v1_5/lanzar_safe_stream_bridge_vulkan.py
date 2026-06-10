import os

from motor_juegos.world_chunk_stream_safe_apply import inspect_safe_apply_plan, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner

if __name__ == "__main__":
    os.environ["JUEGO_RENDER_BACKEND"] = "vulkan_safe_stream_bridge"
    print_render_mode_banner("lanzar_safe_stream_bridge_vulkan.py")
    stats = inspect_safe_apply_plan()
    print("Puente Seguro de Chunks Vulkan Experimental")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
