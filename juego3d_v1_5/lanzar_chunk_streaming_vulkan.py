import os

from motor_juegos.vulkan_chunk_streaming_probe import run_vulkan_chunk_streaming_probe, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner

if __name__ == "__main__":
    os.environ["JUEGO_RENDER_BACKEND"] = "vulkan_chunk_streaming"
    print_render_mode_banner("lanzar_chunk_streaming_vulkan.py")
    stats = run_vulkan_chunk_streaming_probe(radius=1)
    print("Streaming de Chunks Vulkan Experimental")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
