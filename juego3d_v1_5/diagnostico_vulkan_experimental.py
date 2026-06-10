from motor_juegos.vulkan_experimental_mode import run_vulkan_experimental_mode_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_vulkan_experimental.py")
    stats = run_vulkan_experimental_mode_probe(frames=3)
    print("Diagnóstico Modo Vulkan Experimental")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
