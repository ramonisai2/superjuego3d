from motor_juegos.vulkan_visible_clear_runner import run_visible_clear_runner, compact_status
from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    write_render_mode_log("lanzar_vulkan_clear_visible.py")
    stats = run_visible_clear_runner()
    print("Vulkan Clear Visible Experimental")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
