from motor_juegos.playtest_guided_probe import run_guided_playtest_probe, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner

if __name__ == "__main__":
    print_render_mode_banner("lanzar_guided_playtest_probe.py")
    stats = run_guided_playtest_probe()
    print("Prueba Jugable Guiada")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
