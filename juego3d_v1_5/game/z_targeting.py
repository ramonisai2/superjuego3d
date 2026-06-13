"""Seleccion y camara lock-on para objetivos."""

from __future__ import annotations

from dataclasses import dataclass
import math


def _entity_distance_sq_2d(a_x, a_z, b_x, b_z):
    dx = a_x - b_x
    dz = a_z - b_z
    return dx * dx + dz * dz


def find_z_target(player, enemies, npcs, max_distance=22.0, max_angle_deg=85.0):
    px = player.pos_x
    pz = player.pos_z
    yaw = math.radians(player.yaw)
    fx = math.cos(yaw)
    fz = math.sin(yaw)

    candidates = []
    for enemy in enemies:
        candidates.append(("enemy", enemy, 0.0))
    for npc in npcs:
        candidates.append(("npc", npc, 2.5))

    best = None
    best_score = 999999.0
    max_distance2 = max_distance * max_distance

    for kind, ent, penalty in candidates:
        dx = ent.x - px
        dz = ent.z - pz
        dist2 = dx * dx + dz * dz
        if dist2 <= 0.01 * 0.01 or dist2 > max_distance2:
            continue

        dist = math.sqrt(dist2)
        dot = (dx / dist) * fx + (dz / dist) * fz
        dot = max(-1.0, min(1.0, dot))
        angle = math.degrees(math.acos(dot))
        if angle > max_angle_deg:
            continue

        score = angle * 1.8 + dist * 0.55 + penalty
        if score < best_score:
            best_score = score
            best = (kind, ent)

    return best


def z_target_candidates(player, enemies, npcs, max_distance=26.0, max_angle_deg=110.0):
    px = player.pos_x
    pz = player.pos_z
    yaw = math.radians(player.yaw)
    fx = math.cos(yaw)
    fz = math.sin(yaw)
    result = []
    max_distance2 = max_distance * max_distance

    for kind, collection, penalty in (("enemy", enemies, 0.0), ("npc", npcs, 3.5)):
        for ent in collection:
            dx = ent.x - px
            dz = ent.z - pz
            dist2 = dx * dx + dz * dz
            if dist2 <= 0.01 * 0.01 or dist2 > max_distance2:
                continue
            dist = math.sqrt(dist2)
            dot = (dx / dist) * fx + (dz / dist) * fz
            dot = max(-1.0, min(1.0, dot))
            angle = math.degrees(math.acos(dot))
            if angle > max_angle_deg:
                continue
            score = angle * 1.4 + dist * 0.45 + penalty
            result.append((score, kind, ent))

    result.sort(key=lambda item: item[0])
    return result


@dataclass
class ZTargetState:
    target: object | None = None
    target_type: str | None = None
    q_down: bool = False
    cycle_down: bool = False

    def update_lock(self, q_down: bool, player, enemies, npcs, alive_func) -> None:
        if q_down and not self.q_down:
            if self.target is not None:
                self.target = None
                self.target_type = None
            else:
                found = find_z_target(player, enemies, npcs)
                if found:
                    self.target_type, self.target = found
        self.q_down = bool(q_down)
        self.validate(player, enemies, npcs, alive_func)

    def cycle(self, player, enemies, npcs) -> None:
        candidates = z_target_candidates(player, enemies, npcs)
        if not candidates:
            self.target = None
            self.target_type = None
            return

        if self.target is None:
            _, self.target_type, self.target = candidates[0]
            return

        current_index = -1
        for i, (_, kind, ent) in enumerate(candidates):
            if ent is self.target:
                current_index = i
                break

        next_index = (current_index + 1) % len(candidates)
        _, self.target_type, self.target = candidates[next_index]

    def validate(self, player, enemies, npcs, alive_func) -> None:
        if self.target is None:
            return

        if self.target_type == "enemy":
            valid = self.target in enemies and alive_func(self.target)
        else:
            valid = self.target in npcs

        if not valid:
            self.target = None
            self.target_type = None
            return

        dist2 = _entity_distance_sq_2d(player.pos_x, player.pos_z, self.target.x, self.target.z)
        if dist2 > 28.0 * 28.0:
            self.target = None
            self.target_type = None

    def apply_camera(self, player, dt) -> None:
        if self.target is None:
            return

        dx = self.target.x - player.pos_x
        dz = self.target.z - player.pos_z
        dist = math.hypot(dx, dz)
        if dist <= 0.01:
            return

        target_y = getattr(self.target, "y", player.pos_y)
        dy = (target_y + 0.45) - player.pos_y

        desired_yaw = math.degrees(math.atan2(dz, dx))
        desired_pitch = math.degrees(math.atan2(dy, max(0.1, dist)))

        yaw_diff = (desired_yaw - player.yaw + 180.0) % 360.0 - 180.0
        player.yaw += yaw_diff * min(1.0, dt * 5.8)
        player.pitch += (desired_pitch - player.pitch) * min(1.0, dt * 4.2)
        player.pitch = max(-38.0, min(38.0, player.pitch))
