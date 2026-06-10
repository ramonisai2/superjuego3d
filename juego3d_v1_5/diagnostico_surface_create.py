from motor_juegos.vulkan_sdl_surface_create_probe import run_sdl_surface_create_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_surface_create.py")
    stats = run_sdl_surface_create_probe()
    print("Diagnóstico SDL_Vulkan_CreateSurface")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
