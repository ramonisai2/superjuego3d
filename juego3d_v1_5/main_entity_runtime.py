"""Interaccion y actualizacion runtime de entidades."""

from __future__ import annotations

import pygame

from game.debug_log import log_throttled
from game.entity_update_budget import update_enemy_with_budget, update_npc_with_budget


def update_entities_runtime(
    *,
    dt: float,
    px: float,
    pz: float,
    player,
    npcs: list,
    enemies: list,
    slime_remnants: list,
    admin_hub,
    perf_tracker,
    npc_full_ai_distance: float,
    npc_far_ai_interval: float,
    enemy_full_ai_distance: float,
    enemy_far_ai_interval: float,
) -> None:
    """Actualiza NPCs, enemigos y restos respetando pausa y presupuesto."""
    ai_active = True
    if admin_hub:
        ai_active = bool(admin_hub.ai_enabled)
    if not ai_active:
        return

    if admin_hub and admin_hub.visible:
        with perf_tracker.measure("ai_npc"):
            for npc in npcs:
                npc.update(dt)
        with perf_tracker.measure("ai_enemy"):
            for enemy in enemies[:]:
                enemy.update(player, dt)
                if enemy.health <= 0:
                    slime_remnants.append(enemy.create_remnant())
                    enemies.remove(enemy)
        with perf_tracker.measure("ai_remnant"):
            for rem in slime_remnants[:]:
                rem.update(dt)
                if not rem.alive():
                    slime_remnants.remove(rem)
        return

    with perf_tracker.measure("ai_npc"):
        for npc in npcs:
            update_npc_with_budget(
                npc,
                dt,
                px,
                pz,
                full_ai_distance=npc_full_ai_distance,
                far_ai_interval=npc_far_ai_interval,
            )

    with perf_tracker.measure("ai_enemy"):
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

    with perf_tracker.measure("ai_remnant"):
        for rem in slime_remnants[:]:
            rem.update(dt)
            if not rem.alive():
                slime_remnants.remove(rem)


def handle_npc_interaction(
    keys,
    current_time: float,
    px: float,
    pz: float,
    npcs: list,
    last_interact_time: float,
    distance_sq_func,
) -> dict:
    """Actualiza highlight/prompt de NPC y devuelve el dialogo visible."""
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

    nearest_npc = None
    nearest_dist_sq = 4.0 * 4.0
    for npc in npcs:
        dist_sq = distance_sq_func(px, pz, npc.x, npc.z)
        if dist_sq < nearest_dist_sq:
            nearest_dist_sq = dist_sq
            nearest_npc = npc

    if nearest_npc is None:
        return result

    npc_name = getattr(nearest_npc, "nombre", "Desconocido")
    npc_title = getattr(nearest_npc, "titulo", "")
    result["name_label"] = f"{npc_name} {npc_title}".strip()
    result["description"] = getattr(nearest_npc, "descripcion", "Un habitante del mundo")
    result["prompt"] = f"Pulsa E para interactuar con {npc_name}"
    nearest_npc.highlight = True
    nearest_npc.screen_label = None

    if keys[pygame.K_e] and (current_time - last_interact_time) >= 0.35:
        dialog = nearest_npc.interactuar()
        if dialog:
            result["dialog"] = dialog
            log_throttled("NPC_INTERACT", 0.2, npc=npc_name, dialog=str(dialog)[:50])
        result["last_interact_time"] = current_time

    return result
