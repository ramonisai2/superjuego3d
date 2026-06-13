"""Interaccion y actualizacion runtime de entidades."""

import pygame

from game.entity_update_budget import update_enemy_with_budget, update_npc_with_budget


def handle_npc_interaction(keys, current_time, px, pz, npcs, last_interact_time, distance_sq_func):
    """Actualiza highlights/prompts de NPC y devuelve el estado de dialogo visible."""
    result = {
        "dialog": None,
        "prompt": "",
        "name_label": "",
        "description": "",
        "label_screen": None,
        "last_interact_time": last_interact_time,
    }
    for npc in npcs:
        npc.highlight = False
    for npc in npcs:
        dist2 = distance_sq_func(px, pz, npc.x, npc.z)
        if dist2 < 4.0 * 4.0:
            result["name_label"] = f"{npc.nombre} {npc.titulo}"
            result["description"] = npc.descripcion
            result["prompt"] = f"Pulsa botón E para interactuar con {npc.nombre}"
            npc.highlight = True
            npc.screen_label = None
            if keys[pygame.K_e] and (current_time - last_interact_time) >= 0.35:
                result["dialog"] = npc.interactuar()
                result["last_interact_time"] = current_time
            break
    return result


def update_entities_runtime(
    *,
    dt,
    px,
    pz,
    player,
    npcs,
    enemies,
    slime_remnants,
    admin_hub,
    perf_tracker,
    npc_full_ai_distance,
    npc_far_ai_interval,
    enemy_full_ai_distance,
    enemy_far_ai_interval,
):
    """Actualiza NPCs, enemigos y restos respetando pausa de IA del Admin Hub."""
    ai_active = True
    if admin_hub:
        ai_active = admin_hub.ai_enabled

    with perf_tracker.measure("ai"):
        if ai_active:
            for npc in npcs:
                update_npc_with_budget(
                    npc,
                    dt,
                    px,
                    pz,
                    full_ai_distance=npc_full_ai_distance,
                    far_ai_interval=npc_far_ai_interval,
                )

            for enemy in enemies[:]:
                update_enemy_with_budget(
                    enemy,
                    player,
                    dt,
                    px,
                    pz,
                    full_ai_distance=enemy_full_ai_distance,
                    far_ai_interval=enemy_far_ai_interval,
                )
                if enemy.health <= 0:
                    slime_remnants.append(enemy.create_remnant())
                    enemies.remove(enemy)

        for rem in slime_remnants[:]:
            rem.update(dt)
            if not rem.alive():
                slime_remnants.remove(rem)
