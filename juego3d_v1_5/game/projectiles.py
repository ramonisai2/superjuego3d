"""Proyectiles simples del jugador."""

from __future__ import annotations

import math

from game.voxel_models import BOXEL_UNIT, draw_boxel

STONE_THROW_DAMAGE = 1.0
STONE_THROW_SPEED = 18.0
STONE_THROW_MAX_DISTANCE = 30.0
STONE_THROW_GRAVITY = 24.0


def entity_alive(entity) -> bool:
    return entity is not None and getattr(entity, "health", 1) > 0


class StoneProjectile:
    def __init__(self, x, y, z, vx, vy, vz, damage=STONE_THROW_DAMAGE, max_distance=STONE_THROW_MAX_DISTANCE):
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
        self.vy -= STONE_THROW_GRAVITY * dt
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
            if self._hits_enemy(enemy):
                if hasattr(enemy, "take_hit"):
                    enemy.take_hit(self.damage, source_x=self.x, source_z=self.z)
                else:
                    enemy.health -= self.damage
                return False

        return True

    def render(self):
        phase = int(self.distance_traveled * 10.0) & 3
        col = (0.40, 0.38, 0.34)
        draw_boxel(self.x, self.y, self.z, 3, 3, 3, col)
        if phase in (0, 2):
            draw_boxel(self.x + BOXEL_UNIT * 1.4, self.y, self.z - BOXEL_UNIT * 0.7, 1, 2, 1, col)
        else:
            draw_boxel(self.x - BOXEL_UNIT * 1.1, self.y + BOXEL_UNIT * 0.5, self.z + BOXEL_UNIT * 0.9, 1, 1, 2, col)

    def _hits_enemy(self, enemy):
        dx = float(getattr(enemy, "x", 0.0)) - self.x
        dz = float(getattr(enemy, "z", 0.0)) - self.z
        body_scale = max(0.5, float(getattr(enemy, "body_scale", 1.0)))
        radius = 0.45 + body_scale * 0.34
        if dx * dx + dz * dz > radius * radius:
            return False

        center_y = float(getattr(enemy, "y", getattr(enemy, "ground_y", self.y)))
        height = max(0.75, float(getattr(enemy, "height", 1.05)) * body_scale)
        bottom = center_y - height * 0.55
        top = center_y + height * 0.65
        return (bottom - 0.16) <= self.y <= (top + 0.16)


def spawn_stone_projectile(player, target):
    start_x = player.pos_x
    player_height = float(getattr(player, "player_height", 1.8))
    start_y = player.pos_y - player_height * 0.22
    start_z = player.pos_z
    if target is not None:
        target_y = getattr(target, "y", player.pos_y) + 0.18
        dx = target.x - start_x
        dz = target.z - start_z
        dist = math.hypot(dx, dz)
        if dist < 0.5:
            dist = 0.5
        speed = STONE_THROW_SPEED
        vx = dx / dist * speed
        vz = dz / dist * speed
        vy = (target_y - start_y) * 0.72 + 4.7
    else:
        yaw = math.radians(player.yaw)
        pitch = math.radians(player.pitch)
        speed = STONE_THROW_SPEED
        vx = math.cos(yaw) * math.cos(pitch) * speed
        vz = math.sin(yaw) * math.cos(pitch) * speed
        vy = math.sin(pitch) * 11.0 + 3.6
    return StoneProjectile(start_x, start_y, start_z, vx, vy, vz)


def update_stone_projectiles(projectiles, dt, enemies, ground_height_func, alive_func=entity_alive):
    if not projectiles:
        return []
    alive = []
    for proj in projectiles:
        if proj.update(dt, enemies, ground_height_func, alive_func):
            alive.append(proj)
    return alive
