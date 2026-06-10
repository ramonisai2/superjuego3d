import os

from motor_juegos.vulkan_player_chunk_ring_probe import run_vulkan_player_chunk_ring_probe, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner

if __name__ == "__main__":
    os.environ["JUEGO_RENDER_BACKEND"] = "vulkan_player_chunk_ring"
    print_render_mode_banner("lanzar_player_chunk_ring_vulkan.py")
    stats = run_vulkan_player_chunk_ring_probe(player_x=96.0, player_z=32.0, camera_x=96.0, camera_z=32.0)
    print("Anillo Centrado en Jugador Vulkan Experimental")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
