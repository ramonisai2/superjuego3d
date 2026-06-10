from motor_juegos.vulkan_dedicated_window_probe import run_dedicated_window_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_vulkan_ventana.py")
    stats = run_dedicated_window_probe()
    print("Diagnóstico ventana dedicada Vulkan")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
