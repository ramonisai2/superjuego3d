from motor_juegos.render_mode_status import write_render_mode_log

if __name__ == "__main__":
    st = write_render_mode_log("diagnostico_render.py")
    print("Modo de render:")
    print(" ", st.compact())
    print("Notas:")
    print(" ", st.notes)
    print("Este diagnostico no inicia el juego; solo verifica la configuracion.")
