from motor_juegos.vulkan_multi_chunk_probe import run_vulkan_multi_chunk_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("lanzar_multi_chunk_vulkan.py")
    stats = run_vulkan_multi_chunk_probe(radius=1)
    print("Anillo de Chunks Vulkan Experimental")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
