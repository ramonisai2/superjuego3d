"""Atajos de guardado/carga dentro del loop principal."""

import pygame

from game.save_system import apply_save_to_player, load_game_data, save_game


def handle_save_hotkeys(keys, player, seed, spawn_runtime, log_event):
    """Procesa F5/F9 y reposiciona al jugador en suelo seguro al recargar."""
    if keys[pygame.K_F5]:
        save_game(player, seed)
        print(f"[SAVE] Mundo guardado. Semilla={seed} X={player.pos_x:.1f} Z={player.pos_z:.1f}")
        pygame.time.wait(200)

    if keys[pygame.K_F9]:
        data = load_game_data()
        if data and int(data.get("seed", seed)) == int(seed):
            apply_save_to_player(player, data)
            log_event("F9_RELOAD_RAW", x=player.pos_x, y=player.pos_y, z=player.pos_z, health=player.health)
            safe_x, suelo, safe_z = spawn_runtime.find_safe_player_position(
                player.pos_x,
                player.pos_z,
                reason="f9_reload",
            )
            player.pos_x = safe_x
            player.pos_z = safe_z
            player.pos_y = suelo + player.player_height + 0.08
            player.velocity_y = 0
            player.is_grounded = True
            player._last_safe_x = player.pos_x
            player._last_safe_y = player.pos_y
            player._last_safe_z = player.pos_z
            spawn_runtime.set_player_respawn_point(player, player.pos_x, player.pos_z)
            print(f"[LOAD] Partida recargada. X={player.pos_x:.1f} Z={player.pos_z:.1f}")
        elif data:
            print("[LOAD] La partida guardada usa otra semilla. Reinicia y usa Continuar.")
        else:
            print("[LOAD] No hay partida guardada.")
        pygame.time.wait(200)
