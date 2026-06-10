from motor_juegos.playtest_tuning_advisor import advise_from_playtest_logs, compact_status
from motor_juegos.render_mode_status import print_render_mode_banner

if __name__ == "__main__":
    print_render_mode_banner("recomendar_ajustes_playtest.py")
    stats = advise_from_playtest_logs()
    print("Recomendador de Ajustes Playtest")
    print("Estado:", compact_status(stats))
    print("Accion:", stats.get("action_label", ""))
    print("Sugerencia:", stats.get("suggested_change", ""))
    print("Logs:", stats.get("send_log_hint", ""))
    for k, v in stats.items():
        print(f"{k}: {v}")
