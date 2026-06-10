from motor_juegos.vulkan_terrain_pipeline_probe import run_vulkan_terrain_pipeline_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("diagnostico_terrain_pipeline_vulkan.py")
    stats = run_vulkan_terrain_pipeline_probe()
    print("Diagnóstico Pipeline Terreno Vulkan")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
