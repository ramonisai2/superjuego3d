"""Indices de recursos del mundo y recoleccion basica."""

from __future__ import annotations

import math


class WorldResourceRuntime:
    def __init__(
        self,
        *,
        resource_cell_size,
        rock_collision_cell_size,
        resource_amount_func,
        clear_height_cache,
    ):
        self.resource_cell_size = float(resource_cell_size)
        self.rock_collision_cell_size = float(rock_collision_cell_size)
        self.resource_amount_func = resource_amount_func
        self.clear_height_cache = clear_height_cache
        self.rocks = {}
        self.grass = {}
        self.trees = {}
        self.resource_cells = {}
        self.rock_collision_cells = {}
        self.pickup_cooldowns = {}

    def nearby_rock_colliders(self, x, z):
        cell = self._world_cell_coord(x, z, self.rock_collision_cell_size)
        return self.rock_collision_cells.get(cell, ())

    def try_gather_basic_resource(self, player, now, log_throttled):
        if player is None:
            return None
        if player.inventory_free() <= 0:
            player.last_pickup_message = f"{getattr(player, 'bag_name', 'mochila')} llena"
            player.last_pickup_time = float(now)
            return None

        px, pz = float(player.pos_x), float(player.pos_z)
        best = None
        best_dist2 = 999999999.0
        for kind, x, z, cx, cz, amount, radius2 in self._nearby_resource_entries(px, pz):
            dist2 = self._distance_sq_2d(px, pz, x, z)
            if dist2 <= radius2 and dist2 < best_dist2:
                best = (kind, x, z, cx, cz, amount)
                best_dist2 = dist2

        if not best:
            return None
        item, x, z, cx, cz, amount = best
        key = self._resource_node_key(item, x, z, cx, cz)
        if not self._resource_ready(key, now):
            return None
        added = player.add_item(item, amount)
        player.last_pickup_time = float(now)
        if added > 0:
            self._mark_resource_taken(key, now)
            log_throttled(
                "RESOURCE_PICKUP",
                0.2,
                item=item,
                amount=added,
                used=player.inventory_used(),
                cap=player.bag_capacity,
            )
            return item
        return None

    def add_rocks_for_chunk(self, rock_data, cx, cz):
        self.clear_height_cache()
        coord = (int(cx), int(cz))
        stone_amount = self.resource_amount_func("piedra")
        self._clear_resource_index_for_chunk(coord, kinds=("piedra",))
        self._clear_rock_collision_index_for_chunk(coord)
        self.rocks[coord] = []
        for rock in rock_data or []:
            try:
                indexed_rock = tuple(rock[:6]) + coord
                rx, _, rz, sx, sy, sz = indexed_rock[:6]
            except Exception:
                continue
            self.rocks[coord].append(indexed_rock)
            is_tall_skinny = sy > 1.4 and max(sx, sz) < 1.15
            is_tiny_bush = sy < 0.45 and max(sx, sz) < 0.75
            if not is_tall_skinny and not is_tiny_bush:
                self._index_rock_collider(indexed_rock)
            if not is_tall_skinny:
                radius = max(0.85, min(2.0, max(sx, sz) * 0.70))
                self._index_resource_entry("piedra", rx, rz, coord[0], coord[1], amount=stone_amount, radius=radius)

    def add_resources_for_chunk(self, grass_data, deco_data, cx, cz):
        coord = (int(cx), int(cz))
        fiber_amount = self.resource_amount_func("fibra")
        wood_amount = self.resource_amount_func("madera")
        self._clear_resource_index_for_chunk(coord, kinds=("fibra", "madera"))
        self.grass[coord] = []
        for grass in grass_data or []:
            try:
                _, gx, gy, gz, gh = grass[:5]
                entry = (float(gx), float(gy), float(gz), float(gh), coord[0], coord[1])
                self.grass[coord].append(entry)
                if entry[3] >= 0.16:
                    self._index_resource_entry("fibra", entry[0], entry[2], coord[0], coord[1], amount=fiber_amount, radius=1.15)
            except Exception:
                continue
        self.trees[coord] = []
        for deco in deco_data or []:
            try:
                dtype, tx, ty, tz, variant = deco[:5]
            except Exception:
                continue
            if str(dtype).startswith("arbol_"):
                entry = (str(dtype), float(tx), float(ty), float(tz), str(variant), coord[0], coord[1])
                self.trees[coord].append(entry)
                self._index_resource_entry("madera", entry[1], entry[3], coord[0], coord[1], amount=wood_amount, radius=2.15)

    def remove_rocks_for_chunk(self, cx, cz):
        self.clear_height_cache()
        coord = (int(cx), int(cz))
        self.rocks.pop(coord, None)
        self._clear_resource_index_for_chunk(coord, kinds=("piedra",))
        self._clear_rock_collision_index_for_chunk(coord)
        self.remove_resources_for_chunk(cx, cz)

    def remove_resources_for_chunk(self, cx, cz):
        coord = (int(cx), int(cz))
        self.grass.pop(coord, None)
        self.trees.pop(coord, None)
        self._clear_resource_index_for_chunk(coord, kinds=("fibra", "madera"))

    def _world_cell_coord(self, x, z, size):
        size = max(0.5, float(size))
        return (int(math.floor(float(x) / size)), int(math.floor(float(z) / size)))

    def _nearby_cells(self, x, z, size, radius=1):
        cx, cz = self._world_cell_coord(x, z, size)
        radius = max(0, int(radius))
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                yield (cx + dx, cz + dz)

    def _resource_entry(self, kind, x, z, cx, cz, amount, radius):
        return (
            str(kind),
            float(x),
            float(z),
            int(cx),
            int(cz),
            int(amount),
            float(radius) * float(radius),
        )

    def _index_resource_entry(self, kind, x, z, cx, cz, amount=1, radius=1.0):
        cell = self._world_cell_coord(x, z, self.resource_cell_size)
        self.resource_cells.setdefault(cell, []).append(
            self._resource_entry(kind, x, z, cx, cz, amount, radius)
        )

    def _clear_resource_index_for_chunk(self, coord, kinds=None):
        coord = (int(coord[0]), int(coord[1]))
        kind_set = {str(kind) for kind in kinds} if kinds else None
        for cell, entries in list(self.resource_cells.items()):
            kept = [
                entry
                for entry in entries
                if (entry[3], entry[4]) != coord or (kind_set is not None and entry[0] not in kind_set)
            ]
            if kept:
                self.resource_cells[cell] = kept
            else:
                self.resource_cells.pop(cell, None)

    def _nearby_resource_entries(self, x, z):
        for cell in self._nearby_cells(x, z, self.resource_cell_size, radius=1):
            for entry in self.resource_cells.get(cell, ()):
                yield entry

    def _index_rock_collider(self, rock):
        try:
            rx, _, rz, sx, _, sz = rock[:6]
        except Exception:
            return
        half_x = max(0.1, float(sx) * 0.5)
        half_z = max(0.1, float(sz) * 0.5)
        min_cell = self._world_cell_coord(float(rx) - half_x, float(rz) - half_z, self.rock_collision_cell_size)
        max_cell = self._world_cell_coord(float(rx) + half_x, float(rz) + half_z, self.rock_collision_cell_size)
        for cell_x in range(min_cell[0], max_cell[0] + 1):
            for cell_z in range(min_cell[1], max_cell[1] + 1):
                self.rock_collision_cells.setdefault((cell_x, cell_z), []).append(rock)

    def _clear_rock_collision_index_for_chunk(self, coord):
        coord = (int(coord[0]), int(coord[1]))
        for cell, rocks in list(self.rock_collision_cells.items()):
            kept = [rock for rock in rocks if len(rock) < 8 or (int(rock[6]), int(rock[7])) != coord]
            if kept:
                self.rock_collision_cells[cell] = kept
            else:
                self.rock_collision_cells.pop(cell, None)

    def _resource_node_key(self, kind, x, z, cx, cz):
        return (str(kind), int(cx), int(cz), int(round(float(x) * 2.0)), int(round(float(z) * 2.0)))

    def _resource_ready(self, key, now, cooldown=3.5):
        last = self.pickup_cooldowns.get(key, -9999.0)
        return (float(now) - float(last)) >= float(cooldown)

    def _mark_resource_taken(self, key, now):
        self.pickup_cooldowns[key] = float(now)
        if len(self.pickup_cooldowns) > 2048:
            cutoff = float(now) - 120.0
            for old_key, last in list(self.pickup_cooldowns.items()):
                if last < cutoff:
                    self.pickup_cooldowns.pop(old_key, None)

    def _distance_sq_2d(self, a_x, a_z, b_x, b_z):
        dx = a_x - b_x
        dz = a_z - b_z
        return dx * dx + dz * dz
