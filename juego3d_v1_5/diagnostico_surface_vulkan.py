from motor_juegos.vulkan_surface_readiness import run_surface_readiness_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_surface_vulkan.py")
    stats = run_surface_readiness_probe(create_tiny_window=True)
    print("Diagnóstico SDL/pygame + Vulkan surface readiness")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
