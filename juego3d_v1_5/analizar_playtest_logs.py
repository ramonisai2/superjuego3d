from motor_juegos.playtest_log_analyzer import analyze_playtest_logs, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner

if __name__ == "__main__":
    print_render_mode_banner("analizar_playtest_logs.py")
    stats = analyze_playtest_logs()
    print("Analisis de Logs de Playtest")
    print("Estado:", compact_status(stats))
    print("Recomendacion:", stats.get("recommendation", ""))
    for k, v in stats.items():
        print(f"{k}: {v}")
