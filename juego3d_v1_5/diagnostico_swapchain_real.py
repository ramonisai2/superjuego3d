from motor_juegos.vulkan_swapchain_real_probe import run_swapchain_real_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_swapchain_real.py")
    stats = run_swapchain_real_probe()
    print("Diagnóstico Vulkan Swapchain Real")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
