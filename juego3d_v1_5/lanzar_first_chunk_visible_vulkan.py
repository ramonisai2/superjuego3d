from motor_juegos.vulkan_first_chunk_visible_probe import run_vulkan_first_chunk_visible_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("lanzar_first_chunk_visible_vulkan.py")
    stats = run_vulkan_first_chunk_visible_probe()
    print("Primer Chunk Visible Vulkan Experimental")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
