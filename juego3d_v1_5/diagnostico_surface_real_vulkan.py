from motor_juegos.vulkan_surface_real_probe import run_real_surface_probe, compact_status
from motor_juegos.render_mode_status import write_render_mode_log
from motor_juegos.version_info import full_update_name, UPDATE_SUBTITLE

if __name__ == "__main__":
    write_render_mode_log("diagnostico_surface_real_vulkan.py")
    print(full_update_name())
    print(UPDATE_SUBTITLE)
    stats = run_real_surface_probe(create_window=True, attempt_create_surface=False)
    print("Diagnostico surface real Vulkan:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
