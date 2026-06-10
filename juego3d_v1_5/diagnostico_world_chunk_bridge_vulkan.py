import os

from motor_juegos.world_chunk_stream_bridge import run_world_chunk_stream_bridge_probe, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner

if __name__ == "__main__":
    os.environ["JUEGO_RENDER_BACKEND"] = "vulkan_world_chunk_bridge"
    print_render_mode_banner("diagnostico_world_chunk_bridge_vulkan.py")
    stats = run_world_chunk_stream_bridge_probe()
    print("Diagnostico Puente Streaming Mundo Vulkan")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
