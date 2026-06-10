from motor_juegos.vulkan_sdl2_direct_probe import run_sdl2_direct_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_sdl2_direct_vulkan.py")
    stats = run_sdl2_direct_probe()
    print("Diagnóstico SDL2 directo + Vulkan")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
