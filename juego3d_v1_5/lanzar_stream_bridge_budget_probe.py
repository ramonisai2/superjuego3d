from motor_juegos.stream_bridge_budget import run_stream_bridge_budget_probe, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner

if __name__ == "__main__":
    print_render_mode_banner("lanzar_stream_bridge_budget_probe.py")
    stats = run_stream_bridge_budget_probe()
    print("Presupuesto Puente Seguro")
    print("Estado:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
