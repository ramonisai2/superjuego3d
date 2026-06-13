"""Busqueda de spawn seco y puntos seguros de reaparicion."""

from __future__ import annotations

import math
import random


class SpawnRuntime:
    def __init__(self, *, seed, get_total_height, is_water_position, log_event, log_exception):
        self.seed = seed
        self.get_total_height = get_total_height
        self.is_water_position = is_water_position
        self.log_event = log_event
        self.log_exception = log_exception

    def find_dry_position(self, base_x, base_z, min_radius, max_radius, attempts=40):
        """Busca una posicion seca alrededor del jugador para NPCs/enemigos terrestres."""
        best = None
        for _ in range(attempts):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(min_radius, max_radius)
            x = base_x + math.cos(angle) * radius
            z = base_z + math.sin(angle) * radius
            if self.is_water_position(x, z):
                continue
            y = self.get_total_height(x, z)
            best = (x, y, z)
            break
        if best is None:
            x = base_x + min_radius
            z = base_z
            y = self.get_total_height(x, z)
            best = (x, y, z)
        return best

    def find_safe_player_position(self, base_x, base_z, attempts=72, reason="unknown"):
        self.log_event(
            "SAFE_SEARCH_START",
            reason=reason,
            base_x=base_x,
            base_z=base_z,
            attempts=attempts,
            seed=self.seed,
        )
        try:
            base_water = self.is_water_position(base_x, base_z)
            base_y = self.get_total_height(base_x, base_z)
            self.log_event("SAFE_BASE_CHECK", x=base_x, z=base_z, water=base_water, y=base_y, finite=math.isfinite(base_y))
            if (not base_water) and math.isfinite(base_y) and -20.0 < base_y < 160.0:
                self.log_event("SAFE_BASE_ACCEPTED", x=base_x, y=base_y, z=base_z)
                return base_x, base_y, base_z
        except Exception as exc:
            self.log_exception("SAFE_BASE_ERROR", exc)

        checked = 0
        for radius in (3.0, 6.0, 10.0, 16.0, 24.0, 36.0, 55.0):
            for i in range(attempts):
                checked += 1
                angle = (i / float(attempts)) * math.pi * 2.0 + random.uniform(-0.03, 0.03)
                x = base_x + math.cos(angle) * radius
                z = base_z + math.sin(angle) * radius
                water = self.is_water_position(x, z)
                if water:
                    if checked <= 8 or checked % 40 == 0:
                        self.log_event("SAFE_CANDIDATE_REJECT_WATER", radius=radius, x=x, z=z)
                    continue
                y = self.get_total_height(x, z)
                if not math.isfinite(y) or y < -20.0 or y > 160.0:
                    if checked <= 8 or checked % 40 == 0:
                        self.log_event("SAFE_CANDIDATE_REJECT_HEIGHT", radius=radius, x=x, z=z, y=y)
                    continue
                self.log_event("SAFE_CANDIDATE_ACCEPTED", checked=checked, radius=radius, x=x, y=y, z=z)
                return x, y, z

        self.log_event("SAFE_SEARCH_FALLBACK_ORIGIN", checked=checked)
        return self.find_dry_position(0.0, 0.0, 0.0, 18.0, attempts=80)

    def set_player_respawn_point(self, player, x=None, z=None):
        old_x = getattr(player, "respawn_x", None)
        old_z = getattr(player, "respawn_z", None)
        player.respawn_x = float(player.pos_x if x is None else x)
        player.respawn_z = float(player.pos_z if z is None else z)
        player._last_safe_x = player.respawn_x
        player._last_safe_z = player.respawn_z
        try:
            player._last_safe_y = self.get_total_height(player.respawn_x, player.respawn_z) + player.player_height
        except Exception:
            player._last_safe_y = getattr(player, "pos_y", 10.0)
        self.log_event(
            "RESPAWN_POINT_SET",
            old_x=old_x,
            old_z=old_z,
            new_x=player.respawn_x,
            new_z=player.respawn_z,
            safe_y=player._last_safe_y,
        )
