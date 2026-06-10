from motor_juegos.vulkan_swapchain_create_probe import run_swapchain_create_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_swapchain_create.py")
    stats = run_swapchain_create_probe()
    print("Diagnóstico Vulkan VkSwapchainKHR")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
