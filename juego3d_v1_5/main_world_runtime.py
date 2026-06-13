"""Consultas runtime de mundo: altura, agua y contexto del jugador."""

from __future__ import annotations

import math


class WorldRuntime:
    def __init__(
        self,
        *,
        env,
        resource_runtime,
        seed,
        chunk_size,
        subdivisions,
        water_query_grid,
        total_height_query_grid,
        world_context_interval,
        world_context_move_step,
        log_event,
        log_exception,
        log_throttled,
    ):
        self.env = env
        self.resource_runtime = resource_runtime
        self.seed = seed
        self.chunk_size = int(chunk_size)
        self.subdivisions = int(subdivisions)
        self.water_query_grid = float(water_query_grid)
        self.total_height_query_grid = float(total_height_query_grid)
        self.world_context_interval = float(world_context_interval)
        self.world_context_move_step = float(world_context_move_step)
        self.log_event = log_event
        self.log_exception = log_exception
        self.log_throttled = log_throttled
        self.water_surface_cache = {}
        self.total_height_query_cache = {}
        self.total_height_query_frame = 0
        self.last_context_x = None
        self.last_context_z = None
        self.context_elapsed = self.world_context_interval

    def player_chunk_coord(self, pos):
        return int(math.floor(pos / float(self.chunk_size)))

    def get_terrain_only(self, x, z):
        try:
            return self.env.get_cached_height_at(
                x,
                z,
                size=self.chunk_size,
                subdivisions=self.subdivisions,
                seed=self.seed,
            )
        except Exception:
            return self.env.get_terrain_height_at(x, z, seed=self.seed)

    def get_water_surface_cached(self, x, z):
        grid = max(0.25, float(self.water_query_grid))
        key = (
            int(round(float(x) / grid)),
            int(round(float(z) / grid)),
            int(self.seed),
            int(self.chunk_size),
            int(self.subdivisions),
        )
        cached = self.water_surface_cache.get(key)
        if cached is not None:
            return cached
        value = self.env.get_water_surface_at(
            x,
            z,
            seed=self.seed,
            size=self.chunk_size,
            subdivisions=self.subdivisions,
        )
        if len(self.water_surface_cache) > 4096:
            self.water_surface_cache.clear()
        self.water_surface_cache[key] = value
        return value

    def clear_total_height_query_cache(self):
        self.total_height_query_cache.clear()

    def begin_total_height_query_frame(self):
        self.total_height_query_frame += 1
        self.clear_total_height_query_cache()

    def get_total_height(self, x, z):
        key = self._total_height_cache_key(x, z)
        cached = self.total_height_query_cache.get(key)
        if cached is not None:
            return cached

        h = self.get_terrain_only(x, z)
        if not math.isfinite(h):
            self.log_event("HEIGHT_NOT_FINITE", x=x, z=z, h=h)
        try:
            hay_agua, nivel_agua = self.get_water_surface_cached(x, z)
            if hay_agua and nivel_agua > h:
                self.log_throttled("HEIGHT_WATER_SURFACE_USED", 2.0, x=x, z=z, terrain_h=h, water_level=nivel_agua)
                h = nivel_agua + 0.03
        except Exception as exc:
            self.log_exception("HEIGHT_WATER_CHECK_ERROR", exc)

        for rock in self.resource_runtime.nearby_rock_colliders(x, z):
            rx, ry, rz, sx, sy, sz = rock[:6]
            is_tall_skinny = sy > 1.4 and max(sx, sz) < 1.15
            is_tiny_bush = sy < 0.45 and max(sx, sz) < 0.75
            if is_tall_skinny or is_tiny_bush:
                continue
            if abs(x - rx) <= sx / 2 and abs(z - rz) <= sz / 2:
                h = max(h, ry + sy)

        if len(self.total_height_query_cache) > 512:
            self.total_height_query_cache.clear()
        self.total_height_query_cache[key] = h
        return h

    def is_water_position(self, x, z):
        try:
            hay_agua, _ = self.get_water_surface_cached(x, z)
            return bool(hay_agua)
        except Exception:
            return False

    def update_player_world_context(self, player, dt):
        elapsed = self.context_elapsed + float(dt)
        moved_far = (
            self.last_context_x is None
            or self.last_context_z is None
            or ((player.pos_x - self.last_context_x) ** 2 + (player.pos_z - self.last_context_z) ** 2)
            >= self.world_context_move_step ** 2
        )
        ctx = getattr(player, "world_context", None)
        if ctx is None or elapsed >= self.world_context_interval or moved_far:
            try:
                ctx = self.env.get_world_context_at(
                    player.pos_x,
                    player.pos_z,
                    seed=self.seed,
                    size=self.chunk_size,
                    subdivisions=self.subdivisions,
                )
            except Exception as exc:
                self.log_exception("WORLD_CONTEXT_ERROR", exc)
                ctx = {"biome": "Desconocido", "feature": "Sin datos", "layer": "?", "in_water": False}
            self.last_context_x = player.pos_x
            self.last_context_z = player.pos_z
            elapsed = 0.0
        self.context_elapsed = elapsed

        player.world_context = ctx
        in_water = bool(ctx.get("in_water", False))
        player.is_swimming = in_water

        if in_water:
            phase = getattr(player, "swim_phase", 0.0) + dt * 3.2
            player.swim_phase = phase
            bob = math.sin(phase) * 0.08
            player.surface_offset = 0.82 + bob
            player.speed = min(player.speed, 3.2)
            player.velocity_y = 0.0
        else:
            player.surface_offset = player.player_height

    def _total_height_cache_key(self, x, z):
        grid = max(0.05, float(self.total_height_query_grid))
        return (
            int(round(float(x) / grid)),
            int(round(float(z) / grid)),
            int(self.total_height_query_frame),
        )
