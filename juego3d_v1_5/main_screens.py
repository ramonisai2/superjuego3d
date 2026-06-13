"""Pantallas simples de arranque y carga."""

from __future__ import annotations

import random

import pygame

from game.save_system import get_save_summary, load_game_data
from motor_juegos.render_mode_status import get_render_mode_status
from motor_juegos.version_info import full_update_name, UPDATE_CODENAME, UPDATE_SUBTITLE


def draw_simple_screen(engine, render_backend, r2d, width, height, title, lines=None, subtitle=None):
    """Pantalla 2D simple para menu/carga usando el contexto OpenGL ya abierto."""
    if lines is None:
        lines = []
    if render_backend:
        render_backend.clear()
    r2d.begin_2d(width, height)
    r2d.draw_rect_2d(0, 0, width, height, (0.04, 0.07, 0.09))
    r2d.draw_rect_2d(160, 115, width - 320, height - 230, (0.02, 0.025, 0.03))
    r2d.draw_text_2d(title, 205, 155, (240, 240, 220))
    y = 210
    if subtitle:
        r2d.draw_text_2d(subtitle, 205, y, (170, 220, 210))
        y += 48
    for line in lines:
        r2d.draw_text_2d(line, 205, y, (220, 230, 220))
        y += 34
    r2d.end_2d()
    pygame.display.flip()


def show_loading_screen(engine, render_backend, r2d, width, height, message="Cargando mundo..."):
    draw_simple_screen(
        engine,
        render_backend,
        r2d,
        width,
        height,
        "JUEGO 1.6",
        [message, "Generando chunks iniciales y preparando entidades...", f"Actualizacion: {full_update_name()}"],
        UPDATE_SUBTITLE,
    )
    pygame.event.pump()


def show_start_menu(engine, render_backend, r2d, width, height):
    """Menu inicial: continuar mundo guardado o empezar con otra semilla."""
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    typing_seed = False
    seed_text = ""
    selected_seed = None
    save_summary = get_save_summary()

    while True:
        if selected_seed is not None:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
            pygame.mouse.get_rel()
            return {"mode": "new", "seed": selected_seed, "save_data": None}

        lines = [
            get_render_mode_status().hud_label(),
            "",
            f"Actualizacion: {full_update_name()}",
            f"Nombre clave: {UPDATE_CODENAME}",
            UPDATE_SUBTITLE,
            "",
        ]
        if save_summary:
            lines.append(
                f"C - Continuar mundo guardado | Semilla {save_summary['seed']} | "
                f"X {save_summary['x']:.1f} Z {save_summary['z']:.1f}"
            )
            lines.append(f"    Guardado: {save_summary.get('saved_at', 'desconocido')}")
        else:
            lines.append("C - Continuar mundo guardado: no hay partida todavia")
        lines.append("N - Nueva partida con semilla aleatoria")
        lines.append("S - Escribir otra semilla manual")
        lines.append("ESC - Salir")
        if typing_seed:
            lines.append("")
            lines.append("Escribe una semilla numerica y pulsa ENTER:")
            lines.append(seed_text if seed_text else "_")
        else:
            lines.append("")
            lines.append("Controles dentro del juego: F5 guarda, F9 recarga, V camara, Q fijar objetivo")

        draw_simple_screen(
            engine,
            render_backend,
            r2d,
            width,
            height,
            "Menu de Mundo",
            lines,
            f"{full_update_name()} | Continuar o empezar",
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return {"mode": "quit", "seed": None, "save_data": None}
            if event.type == pygame.KEYDOWN:
                if typing_seed:
                    if event.key == pygame.K_RETURN:
                        if seed_text.strip():
                            try:
                                selected_seed = int(seed_text.strip())
                            except ValueError:
                                selected_seed = abs(hash(seed_text.strip())) % 1000000
                        typing_seed = False
                    elif event.key == pygame.K_ESCAPE:
                        typing_seed = False
                        seed_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        seed_text = seed_text[:-1]
                    else:
                        ch = event.unicode
                        if ch and (ch.isdigit() or (ch == "-" and not seed_text)):
                            seed_text += ch
                    continue

                if event.key == pygame.K_ESCAPE:
                    return {"mode": "quit", "seed": None, "save_data": None}
                if event.key == pygame.K_c and save_summary:
                    data = load_game_data()
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    pygame.mouse.get_rel()
                    return {"mode": "continue", "seed": int(data.get("seed", 1)), "save_data": data}
                if event.key == pygame.K_n:
                    selected_seed = random.randint(1, 1000000)
                if event.key == pygame.K_s:
                    typing_seed = True
                    seed_text = ""
        pygame.time.wait(16)
