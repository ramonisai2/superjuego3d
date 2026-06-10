from motor_juegos.vulkan_present_clear_probe import run_present_clear_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_present_clear.py")
    stats = run_present_clear_probe()
    print("Diagnóstico Vulkan Acquire / Clear / Present")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
