import os

from motor_juegos.vulkan_player_chunk_ring_probe import run_vulkan_player_chunk_ring_probe, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner

if __name__ == "__main__":
    os.environ["JUEGO_RENDER_BACKEND"] = "vulkan_player_chunk_ring"
    print_render_mode_banner("diagnostico_player_chunk_ring_vulkan.py")
    stats = run_vulkan_player_chunk_ring_probe(player_x=160.0, player_z=-72.0, camera_x=160.0, camera_z=-72.0, radius=2, frames=3)
    print("Diagnostico Anillo Centrado en Jugador Vulkan")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
