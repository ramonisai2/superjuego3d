from motor_juegos.vulkan_chunk_drawindexed_probe import run_vulkan_chunk_drawindexed_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_chunk_drawindexed_vulkan.py")
    stats = run_vulkan_chunk_drawindexed_probe()
    print("Diagnóstico Chunk drawIndexed Vulkan")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
