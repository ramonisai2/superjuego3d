import os

from motor_juegos.vulkan_multi_chunk_visible_probe import run_vulkan_multi_chunk_visible_probe, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner

if __name__ == "__main__":
    os.environ["JUEGO_RENDER_BACKEND"] = "vulkan_multi_chunk_visible"
    print_render_mode_banner("lanzar_multi_chunk_visible_vulkan.py")
    stats = run_vulkan_multi_chunk_visible_probe(radius=1)
    print("Varios Chunks Visibles Vulkan Experimental")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
