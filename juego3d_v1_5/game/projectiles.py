"""Proyectiles simples del jugador."""

from __future__ import annotations

import math

from game.voxel_models import draw_box


def entity_alive(entity) -> bool:
    return entity is not None and getattr(entity, "health", 1) > 0


class StoneProjectile:
    def __init__(self, x, y, z, vx, vy, vz, damage=2.0, max_distance=34.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.vx = float(vx)
        self.vy = float(vy)
        self.vz = float(vz)
        self.damage = float(damage)
        self.distance_traveled = 0.0
        self.max_distance = float(max_distance)

    def update(self, dt, enemies, ground_height_func, alive_func=entity_alive):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        self.vy -= 24.0 * dt
        self.distance_traveled += math.hypot(self.vx * dt, self.vz * dt)

        if self.y < -16.0 or self.distance_traveled > self.max_distance:
            return False

        ground_y = ground_height_func(self.x, self.z)
        if self.y <= ground_y + 0.05:
            self.y = ground_y + 0.05
            return False

        for enemy in enemies:
            if not alive_func(enemy):
                continue
            dx = enemy.x - self.x
            dz = enemy.z - self.z
            dist2 = dx * dx + dz * dz
            if dist2 <= 0.8 * 0.8:
                if hasattr(enemy, "take_hit"):
                    enemy.take_hit(self.damage, source_x=self.x, source_z=self.z)
                else:
                    enemy.health -= self.damage
                return False

        return True

    def render(self):
        draw_box(self.x, self.y, self.z, 0.18, 0.18, 0.18, (0.40, 0.38, 0.34))


def spawn_stone_projectile(player, target):
    start_x = player.pos_x
    start_y = player.pos_y + getattr(player, "player_height", 1.4) * 0.9
    start_z = player.pos_z
    if target is not None:
        target_y = getattr(target, "y", player.pos_y) + 0.55
        dx = target.x - start_x
        dz = target.z - start_z
        dist = math.hypot(dx, dz)
        if dist < 0.5:
            dist = 0.5
        speed = 18.0
        vx = dx / dist * speed
        vz = dz / dist * speed
        vy = (target_y - start_y) * 0.75 + 5.5
    else:
        yaw = math.radians(player.yaw)
        pitch = math.radians(player.pitch)
        speed = 18.0
        vx = math.cos(yaw) * math.cos(pitch) * speed
        vz = math.sin(yaw) * math.cos(pitch) * speed
        vy = math.sin(pitch) * 12.0 + 4.0
    return StoneProjectile(start_x, start_y, start_z, vx, vy, vz)


def update_stone_projectiles(projectiles, dt, enemies, ground_height_func, alive_func=entity_alive):
    if not projectiles:
        return []
    alive = []
    for proj in projectiles:
        if proj.update(dt, enemies, ground_height_func, alive_func):
            alive.append(proj)
    return alive
