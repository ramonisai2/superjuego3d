from motor_juegos.vulkan_first_chunk_renderpass_probe import run_vulkan_first_chunk_renderpass_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_first_chunk_renderpass_vulkan.py")
    stats = run_vulkan_first_chunk_renderpass_probe()
    print("Diagnóstico RenderPass Primer Chunk Vulkan")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
