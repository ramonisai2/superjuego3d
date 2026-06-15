"""Combate runtime: ataques, proyectiles y marcado visual de objetivos."""

import pygame

from game.combat import attack_enemy
from game.projectiles import spawn_stone_projectile, update_stone_projectiles

MAX_ACTIVE_STONE_PROJECTILES = 12


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
    mouse_buttons = pygame.mouse.get_pressed()
    wants_melee = bool(mouse_buttons[0])
    wants_throw = len(mouse_buttons) > 2 and bool(mouse_buttons[2])
    if (wants_melee or wants_throw) and (current_time - last_attack_time) >= attack_cooldown:
        if wants_throw and player.has_items({"piedra": 1}):
            target = z_target if z_target_type == "enemy" else None
            if player.consume_items({"piedra": 1}):
                if hasattr(player, "start_attack_swing"):
                    player.start_attack_swing("throw")
                stone_projectiles.append(spawn_stone_projectile(player, target))
                if len(stone_projectiles) > MAX_ACTIVE_STONE_PROJECTILES:
                    del stone_projectiles[:len(stone_projectiles) - MAX_ACTIVE_STONE_PROJECTILES]
                _push_stone_ammo_notice(player, current_time)
                if audio and hasattr(audio, "play_sound"):
                    audio.play_sound("lanzar", volume=0.7)
                last_attack_time = current_time
        elif wants_throw and not wants_melee:
            player.last_pickup_message = "Sin piedras"
            player.last_pickup_time = float(current_time)
            if hasattr(player, "push_pickup_notice"):
                player.push_pickup_notice("Sin piedras", kind="piedra", ttl=1.1)
            last_attack_time = current_time
        elif wants_melee:
            if hasattr(player, "start_attack_swing"):
                player.start_attack_swing("melee")
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
    z_target, z_target_type = _normalize_target_reference(
        z_target,
        z_target_type,
        enemies,
        npcs,
        entity_alive,
    )
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


def _normalize_target_reference(z_target, z_target_type, enemies, npcs, entity_alive):
    if z_target is None:
        return None, None
    if z_target_type == "enemy":
        if z_target not in enemies or not entity_alive(z_target):
            return None, None
        return z_target, z_target_type
    if z_target_type == "npc":
        if z_target not in npcs:
            return None, None
        return z_target, z_target_type
    return None, None


def _push_stone_ammo_notice(player, current_time):
    try:
        inv = player.normalize_inventory() if hasattr(player, "normalize_inventory") else getattr(player, "inventory", {})
        stones = int(inv.get("piedra", 0))
    except Exception:
        stones = 0
    text = f"Piedras: {stones}"
    if hasattr(player, "push_combat_notice"):
        player.push_combat_notice(text, kind="piedra", ttl=0.75)
    elif hasattr(player, "push_pickup_notice"):
        player.last_pickup_message = text
        player.last_pickup_time = float(current_time)
        player.push_pickup_notice(text, kind="piedra", ttl=0.75)
