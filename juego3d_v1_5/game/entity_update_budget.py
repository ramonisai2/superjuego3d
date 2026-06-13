"""Actualizacion de entidades con presupuesto por distancia."""

from __future__ import annotations


def update_npc_with_budget(npc, dt, px, pz, *, full_ai_distance, far_ai_interval):
    if getattr(npc, "highlight", False) or getattr(npc, "z_locked", False):
        npc._ai_far_accum = 0.0
        npc.update(dt)
        return True
    dist2 = _distance_sq_2d(px, pz, npc.x, npc.z)
    if dist2 <= full_ai_distance * full_ai_distance:
        npc._ai_far_accum = 0.0
        npc.update(dt)
        return True
    return _run_throttled_entity_update(
        npc,
        dt,
        far_ai_interval,
        "_ai_far_accum",
        lambda step_dt: npc.update(step_dt),
    )


def update_enemy_with_budget(enemy, player, dt, px, pz, *, full_ai_distance, far_ai_interval):
    if getattr(enemy, "selected", False) or getattr(enemy, "z_locked", False):
        enemy._ai_far_accum = 0.0
        enemy.update(player, dt)
        return True
    dist2 = _distance_sq_2d(px, pz, enemy.x, enemy.z)
    active_distance = max(float(full_ai_distance), float(getattr(enemy, "aggro_range", 0.0)) + 8.0)
    if dist2 <= active_distance * active_distance:
        enemy._ai_far_accum = 0.0
        enemy.update(player, dt)
        return True
    return _run_throttled_entity_update(
        enemy,
        dt,
        far_ai_interval,
        "_ai_far_accum",
        lambda step_dt: enemy.update(player, step_dt),
    )


def _run_throttled_entity_update(entity, dt, interval, attr_name, update_fn):
    accumulated = float(getattr(entity, attr_name, 0.0)) + float(dt)
    if accumulated < interval:
        setattr(entity, attr_name, accumulated)
        return False
    setattr(entity, attr_name, 0.0)
    update_fn(accumulated)
    return True


def _distance_sq_2d(a_x, a_z, b_x, b_z):
    dx = a_x - b_x
    dz = a_z - b_z
    return dx * dx + dz * dz
