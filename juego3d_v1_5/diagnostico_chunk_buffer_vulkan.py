from motor_juegos.vulkan_chunk_buffer_upload_probe import run_vulkan_chunk_buffer_upload_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_chunk_buffer_vulkan.py")
    stats = run_vulkan_chunk_buffer_upload_probe()
    print("Diagnóstico Chunk Buffer Vulkan")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
