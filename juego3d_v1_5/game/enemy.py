import math
import numpy as np

from motor_juegos import biomes
from game.voxel_models import render_voxel_slime, render_slime_puddle

class SlimeRemnant:
    def __init__(self, x, y, z, color, ttl=7.0, scale=1.0):
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        self.ttl = ttl
        self.max_ttl = ttl
        self.scale = scale

    def update(self, dt):
        self.ttl -= dt

    def alive(self):
        return self.ttl > 0

    def render(self, detail_level="full"):
        alpha = max(0.0, min(0.45, 0.45 * (self.ttl / self.max_ttl)))
        scale = self.scale * (0.85 + 0.15 * (self.ttl / self.max_ttl))
        render_slime_puddle(self.x, self.y, self.z, self.color, alpha=alpha, scale=scale)

class Enemy:
    def __init__(self, x, y, z, terrain_height_func):
        self.x = x
        self.y = y
        self.z = z
        self.ground_y = y
        self.max_health = 2
        self.health = 2
        self.hit_points = 2
        self.speed = 1.7
        self.height = 1.05
        self.body_scale = 1.0
        self.terrain_height_func = terrain_height_func
        self.yaw = 0.0
        self.aggro_range = 18.0
        self.catch_range = 1.25
        self.aggro = 0.0
        self.squish_phase = 0.0
        self.selected = False
        self.world_seed = 0
        self.color = (0.90, 0.10, 0.12)
        self.spawn_biome_color = None
        self.spawn_biome_locked = False
        self.knockback_x = 0.0
        self.knockback_z = 0.0
        self.knockback_timer = 0.0

    def lock_spawn_biome_color(self, seed=None):
        """Fija el color del slime según el bioma donde nació."""
        if seed is not None:
            self.world_seed = seed
        self.spawn_biome_color = self._compute_biome_color_at(self.x, self.z)
        self.color = self.spawn_biome_color
        self.spawn_biome_locked = True

    def _compute_biome_color(self):
        # Compatibilidad: ahora el color real se fija en el spawn.
        if self.spawn_biome_color is not None:
            return self.spawn_biome_color
        return self._compute_biome_color_at(self.x, self.z)

    def _compute_biome_color_at(self, wx, wz):
        x = np.array([wx])
        z = np.array([wz])
        h, m, c, t, r = biomes.calculate_terrain_properties(x, z, self.world_seed)
        h = float(h[0]); m = float(m[0]); c = bool(c[0]); t = float(t[0]); r = float(r[0])

        # Colores mucho más marcados para que el cambio sí sea visible.
        if c:
            return (0.18, 0.95, 1.00)      # cueva/cristal -> cian brillante
        if t > 0.90 and r > 0.70 and h < 18:
            return (1.00, 0.30, 0.05)      # volcánico -> naranja/rojo intenso
        if t < 0.22 and h > 14:
            return (0.55, 0.82, 1.00)      # glaciar -> azul helado
        if t > 0.75 and m < 0.22:
            return (1.00, 0.82, 0.16)      # desierto -> ámbar vivo
        if t > 0.66 and 0.20 < m < 0.55 and r > 0.76:
            return (1.00, 0.48, 0.15)      # terracota caliente
        if m > 0.72 and t < 0.60:
            return (0.56, 0.22, 0.92)      # pantano -> violeta tóxico
        if m > 0.60:
            return (0.10, 0.96, 0.22)      # bosque húmedo -> verde vivo
        if h > 13.0:
            return (0.72, 0.76, 0.86)      # montaña -> gris azulado
        return (0.96, 0.12, 0.18)          # pradera/base -> rojo vivo

    def take_hit(self, damage=1, source_x=None, source_z=None):
        self.hit_points -= damage
        self.health = self.hit_points
        if source_x is not None and source_z is not None:
            dx = self.x - source_x
            dz = self.z - source_z
            dist = math.sqrt(dx*dx + dz*dz) or 1.0
            force = 0.9 if not getattr(self, 'is_boss', False) else 0.55
            self.knockback_x = (dx / dist) * force
            self.knockback_z = (dz / dist) * force
            self.knockback_timer = 0.18

    def create_remnant(self):
        ground_y = self.ground_y
        if self.terrain_height_func:
            try:
                ground_y = self.terrain_height_func(self.x, self.z)
            except Exception:
                ground_y = self.ground_y
        return SlimeRemnant(self.x, ground_y + 0.04, self.z, self.color, ttl=7.0, scale=getattr(self, 'body_scale', 1.0))

    def update(self, player, dt):
        if self.spawn_biome_color is None:
            self.lock_spawn_biome_color(self.world_seed)
        self.color = self.spawn_biome_color
        dx = player.pos_x - self.x
        dz = player.pos_z - self.z
        dist2 = dx*dx + dz*dz
        alerted = dist2 < self.aggro_range * self.aggro_range
        dist = math.sqrt(dist2) if alerted else 0.0
        target_aggro = 1.0 if alerted else 0.0
        self.aggro += (target_aggro - self.aggro) * min(1.0, dt * 4.5)

        # Retroceso al recibir golpes.
        if self.knockback_timer > 0.0:
            self.x += self.knockback_x
            self.z += self.knockback_z
            self.knockback_x *= 0.78
            self.knockback_z *= 0.78
            self.knockback_timer -= dt
            self.squish_phase += dt * 14.0
        elif alerted and dist > 0.001:
            self.yaw = math.degrees(math.atan2(dx, dz))
            if dist > self.catch_range:
                move = self.speed * (0.65 + self.aggro * 0.90) * dt
                step = min(move, max(0.0, dist - self.catch_range * 0.4))
                self.x += (dx / dist) * step
                self.z += (dz / dist) * step
                self.squish_phase += dt * 11.0
            else:
                player.take_damage(0.10 * dt * 60)
                self.squish_phase += dt * 8.0
        else:
            self.squish_phase += dt * 3.0

        if self.terrain_height_func:
            suelo_y = self.terrain_height_func(self.x, self.z)
            self.ground_y = suelo_y
            leg_h = 0.16 + 0.34 * self.aggro
            total_h = leg_h + 0.74 * self.body_scale
            self.y = suelo_y + total_h * 0.5

    def render(self, detail_level="full"):
        base_y = self.ground_y
        if getattr(self, "is_boss", False):
            color = (min(1.0, self.color[0] * 1.05), max(0.08, self.color[1] * 0.65), min(1.0, self.color[2] * 1.10))
            scale = getattr(self, "body_scale", 1.45)
        else:
            color = self.color
            scale = getattr(self, "body_scale", 1.0)
        render_voxel_slime(
            self.x, base_y, self.z,
            yaw=self.yaw,
            body_color=color,
            selected=getattr(self, 'selected', False),
            debug_hitbox=False,
            body_scale=scale,
            aggro=self.aggro,
            squish_phase=self.squish_phase,
            is_boss=bool(getattr(self, 'is_boss', False)),
            detail_level=detail_level,
        )
