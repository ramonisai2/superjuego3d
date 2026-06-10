from motor_juegos.vulkan_persistent_clear_backend import run_persistent_clear_backend_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_backend_vulkan_persistente.py")
    stats = run_persistent_clear_backend_probe()
    print("Diagnóstico Backend Vulkan Persistente")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
