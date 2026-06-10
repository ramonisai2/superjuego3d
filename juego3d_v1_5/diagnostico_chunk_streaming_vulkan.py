import os

from motor_juegos.vulkan_chunk_streaming_probe import run_vulkan_chunk_streaming_probe, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner

if __name__ == "__main__":
    os.environ["JUEGO_RENDER_BACKEND"] = "vulkan_chunk_streaming"
    print_render_mode_banner("diagnostico_chunk_streaming_vulkan.py")
    path = [(32.0, 32.0), (96.0, 32.0), (160.0, 96.0), (224.0, 96.0)]
    stats = run_vulkan_chunk_streaming_probe(path=path, radius=2, frames=3)
    print("Diagnostico Streaming de Chunks Vulkan")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
