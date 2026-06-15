# npc_manager.py
# Define la clase NPC principal, integrando identidad, memoria, necesidades, rutinas y pistas.
import math
import random
from typing import List, Tuple, Dict, Any, Optional, Callable
from game.npc_identity import (
FIRST_NAMES, TITLES, HUMAN_PROFESSIONS, HUMAN_PROFESSION_PROFILES,
Rango, Cultura, asignar_cultura_y_rango, build_npc_id,
profile_for_profession, visible_tool_name, profession_identity,
stable_offset, stable_float01
)
from game.npc_memory import npc_memory_for, remember_npc_event, npc_memory_snapshot
from game.npc_ai_runtime import mood_for_npc, dialogue_tone_prefix, contextual_dialogue_line

# ============================================================================
# Clase NPC
# ============================================================================
class NPC:
    def __init__(self, seed: int, x: float = 0, z: float = 0, y: float = 0,
                 id_source: str = "world", id_slot: int = 0, npc_id: str = None,
                 bioma: str = None):
        # ---------- Identidad permanente ----------
        self.id = npc_id or build_npc_id(seed, x, z, id_source, id_slot)
        self.seed = seed
        self.nombre = self._generar_nombre(seed)
        self.titulo = self._generar_titulo(seed)
        self.apodo = self._generar_apodo(seed)
        self.muletilla = self._generar_muletilla(seed)
        # Profesión, cultura y rango
        self.profession = self._elegir_profesion(seed)
        self.cultura, self.rango = asignar_cultura_y_rango(seed, self.profession, bioma)
        # Atributos físicos y de combate
        self.x = x
        self.y = y
        self.z = z
        self.spawn_x = x
        self.spawn_z = z
        self.yaw = 0.0
        self.health = 100.0
        self.max_health = 100.0
        self.daño = random.Random(seed).randint(8, 18)
        self.hostilidad = random.Random(seed).randint(0, 100)
        self.speed = 1.2 + random.Random(seed).random() * 0.8
        self.wander_radius = 10.0
        # ---------- Necesidades ----------
        needs_r = random.Random(seed ^ 0x4E454544)
        self.needs = {
            "food": 72.0 + needs_r.random() * 18.0,
            "water": 70.0 + needs_r.random() * 20.0,
            "energy": 68.0 + needs_r.random() * 24.0,
            "security": 62.0 + needs_r.random() * 28.0,
            "social": 45.0 + needs_r.random() * 35.0,
        }
        self.need_rates = {
            "food": 0.008 + needs_r.random() * 0.006,
            "water": 0.011 + needs_r.random() * 0.008,
            "energy": 0.006 + needs_r.random() * 0.005,
            "social": 0.003 + needs_r.random() * 0.004,
        }
        self.stress = 0.0
        self.current_need = "calm"
        self.intent = "wander"
        self.activity = "wander"
        self.activity_detail = "explorar cerca"
        self.activity_progress = 0.0
        self.mood = "calmado"
        self.stance = "abierto"
        # ---------- Rutinas día/noche ----------
        self.rutina_dia = self._definir_rutina_dia()
        self.rutina_noche = self._definir_rutina_noche()
        # ---------- Anclas de actividad ----------
        work_dx, work_dz = stable_offset(self.id, f"work_{self.profession}", 2.5, 7.5)
        rest_dx, rest_dz = stable_offset(self.id, "rest", 1.5, 4.0)
        social_dx, social_dz = stable_offset(self.id, "social", 3.0, 6.0)
        self.work_anchor = (self.spawn_x + work_dx, self.spawn_z + work_dz)
        self.rest_anchor = (self.spawn_x + rest_dx, self.spawn_z + rest_dz)
        self.social_anchor = (self.spawn_x + social_dx, self.spawn_z + social_dz)
        # ---------- Pistas de crafteo y secretos ----------
        self.pistas = self._generar_pistas()
        # ---------- Memoria y diálogo ----------
        self.memory = npc_memory_for(self)
        self.memoria = self.memory.get("encounters", 0)
        self.update_mood()
        # ---------- Datos visuales (profesión, herramientas, etc.) ----------
        profile = profile_for_profession(self.profession)
        self.tool_label = profile["tool_label"]
        self.workplace = profile["workplace"]
        self.work_material = profile["material"]
        self.work_action = profile["action"]
        self.temper = profile["temper"]
        self.back_tool = visible_tool_name(profile["tool"])
        self.profession_color = profile["color"]
        # Variables de movimiento y animación
        self.target_x = x
        self.target_z = z

