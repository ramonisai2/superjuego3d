from motor_juegos.vulkan_sdl_surface_bridge import run_sdl_surface_bridge_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_surface_bridge.py")
    stats = run_sdl_surface_bridge_probe()
    print("Diagnóstico puente SDL/Vulkan Surface")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
