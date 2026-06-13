"""Combate runtime: ataques, proyectiles y marcado visual de objetivos."""

import pygame

from game.combat import attack_enemy
from game.projectiles import spawn_stone_projectile, update_stone_projectiles


def update_combat_runtime(
    *,
    current_time,
    dt,
    player,
    enemies,
    npcs,
    stone_projectiles,
    z_target,
    z_target_type,
    last_attack_time,
    attack_cooldown,
    audio,
    get_total_height,
    entity_alive,
    distance_sq_func,
    px,
    pz,
):
    """Actualiza combate de jugador y seleccion visual cercana."""
    if pygame.mouse.get_pressed()[0] and (current_time - last_attack_time) >= attack_cooldown:
        if z_target_type == "enemy" and z_target is not None and player.has_items({"piedra": 1}):
            if player.consume_items({"piedra": 1}):
                stone_projectiles.append(spawn_stone_projectile(player, z_target))
                if audio and hasattr(audio, "play_sound"):
                    audio.play_sound("lanzar", volume=0.7)
                last_attack_time = current_time
        else:
            if hasattr(player, "start_attack_swing"):
                player.start_attack_swing()
            locked_enemy = z_target if z_target_type == "enemy" else None
            hit_enemy = attack_enemy(player, enemies, locked_target=locked_enemy, attack_range=3.2)
            last_attack_time = current_time
            if hit_enemy:
                if audio and hasattr(audio, "play_sound"):
                    audio.play_sound("golpe", volume=0.7)
                if z_target_type == "enemy" and z_target is not None and z_target not in enemies:
                    z_target = None
                    z_target_type = None

    stone_projectiles = update_stone_projectiles(stone_projectiles, dt, enemies, get_total_height, entity_alive)
    _update_visual_targeting(enemies, npcs, z_target, z_target_type, distance_sq_func, px, pz)
    return {
        "stone_projectiles": stone_projectiles,
        "z_target": z_target,
        "z_target_type": z_target_type,
        "last_attack_time": last_attack_time,
    }


def _update_visual_targeting(enemies, npcs, z_target, z_target_type, distance_sq_func, px, pz):
    for enemy in enemies:
        enemy.selected = False
        enemy.z_locked = False
    for npc in npcs:
        npc.z_locked = False

    close_enemy = None
    close_enemy_dist2 = 999999999.0
    for enemy in enemies:
        ed2 = distance_sq_func(px, pz, enemy.x, enemy.z)
        if ed2 < 4.0 * 4.0 and ed2 < close_enemy_dist2:
            close_enemy = enemy
            close_enemy_dist2 = ed2
    if close_enemy is not None:
        close_enemy.selected = True

    if z_target is not None:
        if z_target_type == "enemy":
            z_target.selected = True
        z_target.z_locked = True
