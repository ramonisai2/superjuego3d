from motor_juegos.vulkan_swapchain_frame_probe import run_swapchain_frame_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_swapchain_frame.py")
    stats = run_swapchain_frame_probe()
    print("Diagnóstico Vulkan Swapchain Frames")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
