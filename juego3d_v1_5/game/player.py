from motor_juegos import FirstPersonCamera
from game.debug_log import log_event, log_exception
import math

WEAPON_DEFS = {
    "mano": {
        "name": "Mano",
        "damage": 1.0,
        "range": 3.2,
        "max_uses": 0,
    },
    "palo": {
        "name": "Palo",
        "damage": 1.2,
        "range": 6.4,
        "max_uses": 20,
    },
    "palo_fibra": {
        "name": "Palo con fibras",
        "damage": 1.2,
        "range": 6.4,
        "max_uses": 50,
    },
    "palo_piedra": {
        "name": "Palo con piedra",
        "damage": 2.0,
        "range": 6.4,
        "max_uses": 70,
    },
}
CRAFT_RECIPES = {
    "mano": {
        "target": "palo",
        "label": "Palo",
        "costs": {"madera": 1},
    },
    "palo": {
        "target": "palo_fibra",
        "label": "Palo con fibras",
        "costs": {"fibra": 2},
    },
    "palo_fibra": {
        "target": "palo_piedra",
        "label": "Palo con piedra",
        "costs": {"piedra": 1},
    },
}

INVENTORY_ITEM_MAX = {
    "piedra": 6,
    "madera": 6,
    "fibra": 6,
}

DEFAULT_ITEM_MAX = 6


class Player(FirstPersonCamera):
    def __init__(self, x, y, z, terrain_height_func):
        super().__init__(x, y, z)
        self.health = 100
        self.hunger = 100
        self.stamina = 100
        self.inventory = {"piedra": 0, "madera": 0, "fibra": 0}
        self.bag_name = "mochila basica"
        self.bag_capacity = 18
        self.last_pickup_message = ""
        self.last_pickup_time = 0.0
        self.pickup_notices = []
        self.active_weapon = None
        self.last_craft_message = ""
        self.last_craft_time = 0.0
        self.attack_swing_timer = 0.0
        self.attack_swing_duration = 0.26
        self.terrain_func = terrain_height_func
        self.respawn_x = x
        self.respawn_z = z

    def normalize_inventory(self):
        if isinstance(self.inventory, dict):
            clean = {}
            for item, amount in self.inventory.items():
                try:
                    value = int(amount)
                except Exception:
                    value = 0
                if value > 0:
                    clean[str(item)] = value
            for item in ("piedra", "madera", "fibra"):
                clean.setdefault(item, 0)
            self.inventory = clean
            return self.inventory
        clean = {"piedra": 0, "madera": 0, "fibra": 0}
        if isinstance(self.inventory, list):
            for item in self.inventory:
                key = str(item)
                clean[key] = clean.get(key, 0) + 1
        self.inventory = clean
        return self.inventory

    def inventory_item_capacity(self, item):
        return int(INVENTORY_ITEM_MAX.get(str(item), DEFAULT_ITEM_MAX))

    def inventory_used(self):
        self.normalize_inventory()
        return sum(max(0, int(amount)) for amount in self.inventory.values())

    def inventory_free(self):
        return max(0, int(self.bag_capacity) - self.inventory_used())

    def push_pickup_notice(self, text, kind="resource", ttl=1.8):
        notice = {
            "text": str(text),
            "kind": str(kind),
            "ttl": float(ttl),
            "max_ttl": float(ttl),
        }
        self.pickup_notices.append(notice)
        if len(self.pickup_notices) > 4:
            del self.pickup_notices[:-4]
        return notice

    def update_pickup_notices(self, dt):
        dt = max(0.0, float(dt))
        for notice in self.pickup_notices:
            notice["ttl"] = max(0.0, float(notice.get("ttl", 0.0)) - dt)
        self.pickup_notices = [notice for notice in self.pickup_notices if notice.get("ttl", 0.0) > 0.0]

    def add_item(self, item, amount=1):
        self.normalize_inventory()
        item = str(item)
        amount = max(0, int(amount))
        if amount <= 0:
            return 0
        free = self.inventory_free()
        item_limit = self.inventory_item_capacity(item)
        current_amount = int(self.inventory.get(item, 0))
        available_for_item = max(0, item_limit - current_amount)
        if available_for_item <= 0:
            self.last_pickup_message = f"{item} lleno"
            self.push_pickup_notice(self.last_pickup_message, kind=item, ttl=1.6)
            return 0
        if free <= 0:
            self.last_pickup_message = f"{self.bag_name} llena"
            self.push_pickup_notice(self.last_pickup_message, kind="full", ttl=1.6)
            return 0
        added = min(amount, free, available_for_item)
        if added <= 0:
            self.last_pickup_message = f"No hay espacio para {item}"
            self.push_pickup_notice(self.last_pickup_message, kind=item, ttl=1.6)
            return 0
        self.inventory[item] = int(self.inventory.get(item, 0)) + added
        self.last_pickup_message = f"+{added} {item}"
        self.push_pickup_notice(self.last_pickup_message, kind=item, ttl=1.8)
        return added

    def has_items(self, costs):
        self.normalize_inventory()
        for item, amount in costs.items():
            if int(self.inventory.get(item, 0)) < int(amount):
                return False
        return True

    def consume_items(self, costs):
        if not self.has_items(costs):
            return False
        for item, amount in costs.items():
            self.inventory[item] = int(self.inventory.get(item, 0)) - int(amount)
            if self.inventory[item] <= 0:
                self.inventory[item] = 0
        return True

    def weapon_key(self):
        weapon = self.active_weapon if isinstance(self.active_weapon, dict) else None
        return weapon.get("key") if weapon else "mano"

    def normalize_active_weapon(self):
        if not isinstance(self.active_weapon, dict):
            self.active_weapon = None
            return self.active_weapon
        key = str(self.active_weapon.get("key", ""))
        if key not in WEAPON_DEFS or key == "mano":
            self.active_weapon = None
            return self.active_weapon
        max_uses = int(WEAPON_DEFS[key]["max_uses"])
        try:
            uses = int(self.active_weapon.get("uses", max_uses))
        except Exception:
            uses = max_uses
        if uses <= 0:
            self.active_weapon = None
        else:
            self.active_weapon = {"key": key, "uses": min(uses, max_uses)}
        return self.active_weapon

    def weapon_info(self):
        self.normalize_active_weapon()
        key = self.weapon_key()
        data = dict(WEAPON_DEFS.get(key, WEAPON_DEFS["mano"]))
        uses = 0
        if isinstance(self.active_weapon, dict):
            uses = int(self.active_weapon.get("uses", data.get("max_uses", 0)))
        data["key"] = key
        data["uses"] = uses
        return data

    def equip_weapon(self, key):
        data = WEAPON_DEFS.get(key)
        if not data or key == "mano":
            self.active_weapon = None
            return self.weapon_info()
        self.active_weapon = {
            "key": key,
            "uses": int(data["max_uses"]),
        }
        return self.weapon_info()

    def craft_best_weapon(self):
        self.normalize_inventory()
        current = self.weapon_key()
        recipe = CRAFT_RECIPES.get(current)
        if recipe and self.has_items(recipe["costs"]):
            self.consume_items(recipe["costs"])
            info = self.equip_weapon(recipe["target"])
            self.last_craft_message = f"Creaste {recipe['label']}"
            return True, self.last_craft_message, info
        if not recipe:
            self.last_craft_message = "Ya tienes palo con piedra"
        else:
            missing = self.missing_items_for(recipe["costs"])
            self.last_craft_message = "Falta " + ", ".join(missing) if missing else "Faltan materiales"
        return False, self.last_craft_message, self.weapon_info()

    def missing_items_for(self, costs):
        self.normalize_inventory()
        missing = []
        for item, amount in costs.items():
            have = int(self.inventory.get(item, 0))
            need = int(amount)
            if have < need:
                missing.append(f"{item} {have}/{need}")
        return missing

    def next_craft_recipe(self):
        self.normalize_inventory()
        current = self.weapon_key()
        recipe = CRAFT_RECIPES.get(current)
        if not recipe:
            return {
                "available": False,
                "complete": False,
                "label": "Maximo",
                "target": current,
                "costs": {},
                "missing": [],
                "text": "Crafteo maximo",
            }
        missing = self.missing_items_for(recipe["costs"])
        parts = []
        short = {"madera": "M", "fibra": "F", "piedra": "P"}
        for item, amount in recipe["costs"].items():
            parts.append(f"{short.get(item, item)}:{int(self.inventory.get(item, 0))}/{int(amount)}")
        return {
            "available": True,
            "complete": not missing,
            "label": recipe["label"],
            "target": recipe["target"],
            "costs": dict(recipe["costs"]),
            "missing": missing,
            "text": f"C {recipe['label']} " + " ".join(parts),
        }

    def current_attack_damage(self):
        return float(self.weapon_info().get("damage", 1.0))

    def current_attack_range(self):
        return float(self.weapon_info().get("range", 3.2))

    def use_weapon_once(self):
        if not isinstance(self.active_weapon, dict):
            return self.weapon_info()
        uses = int(self.active_weapon.get("uses", 0)) - 1
        if uses <= 0:
            broken_name = self.weapon_info().get("name", "arma")
            self.active_weapon = None
            self.last_craft_message = f"{broken_name} se rompio"
            return self.weapon_info()
        self.active_weapon["uses"] = uses
        return self.weapon_info()

    def start_attack_swing(self):
        self.attack_swing_timer = float(self.attack_swing_duration)

    def update_attack_animation(self, dt):
        self.attack_swing_timer = max(0.0, float(self.attack_swing_timer) - max(0.0, float(dt)))

    def attack_swing_value(self):
        duration = max(0.01, float(self.attack_swing_duration))
        progress = 1.0 - max(0.0, min(1.0, float(self.attack_swing_timer) / duration))
        if progress <= 0.0 or progress >= 1.0:
            return 0.0
        return max(0.0, math.sin(progress * math.pi))

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.respawn()

    def respawn(self):
        rx = float(getattr(self, "respawn_x", self.pos_x))
        rz = float(getattr(self, "respawn_z", self.pos_z))
        try:
            suelo = self.terrain_func(rx, rz)
        except Exception as exc:
            log_exception("PLAYER_RESPAWN_TERRAIN_ERROR", exc)
            rx, rz = 0.0, 0.0
            suelo = self.terrain_func(0, 0)
        self.pos_x = rx
        self.pos_z = rz
        self.pos_y = suelo + self.player_height + 0.08
        self.health = 100
        self.stamina = 100
        self.hunger = 100
        self.velocity_y = 0
        self.is_grounded = True
        self._last_safe_x = self.pos_x
        self._last_safe_y = self.pos_y
        self._last_safe_z = self.pos_z
        log_event("PLAYER_RESPAWN_DONE", x=self.pos_x, y=self.pos_y, z=self.pos_z)
        print("[RESPAWN] Jugador ha revivido.")
