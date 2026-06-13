"""Identidad, profesiones y presets visuales de NPCs."""

from __future__ import annotations

import math
import random


FIRST_NAMES = ["Roy", "Bolvo", "Runia", "Tergul", "Aldor", "Rokkan", "Mork"]
TITLES = ["El Calvo", "Rompepiedras", "El Ocupado", "El Errante"]
HUMAN_PROFESSIONS = [
    "carpintero",
    "herrero",
    "granjero",
    "cazador",
    "minero",
    "mercader",
    "guardia",
    "curandero",
]

SKIN_ZONE_PRESETS = {
    "base": {
        "head": None,
        "torso": None,
        "pants": None,
        "visual_profession": None,
        "face_type": "neutral",
        "torso_type": "neutral",
        "nose_style": "human",
        "ear_style": "human",
    },
    "carpintero_viejo": {
        "head": "carpintero_viejo",
        "torso": "carpintero_viejo",
        "pants": "carpintero_viejo",
        "visual_profession": "carpintero",
        "face_type": "masculino",
        "torso_type": "masculino",
        "nose_style": "human",
        "ear_style": "human",
    },
    "ropa_carpintero": {
        "head": None,
        "torso": "carpintero_viejo",
        "pants": "carpintero_viejo",
        "visual_profession": "carpintero",
        "face_type": "neutral",
        "torso_type": "masculino",
        "nose_style": "human",
        "ear_style": "human",
    },
}

HUMAN_PROFESSION_PROFILES = {
    "carpintero": {
        "skin": "humano_carpintero_joven",
        "color": (0.42, 0.25, 0.12),
        "shape": "sturdy",
        "tool": "hammer_reserved",
        "tool_label": "martillo",
        "workplace": "taller",
        "material": "madera",
        "action": "reparar estructuras",
        "temper": "practico",
    },
    "herrero": {
        "skin": "humano_herrero",
        "color": (0.30, 0.31, 0.32),
        "shape": "broad",
        "tool": "hammer_reserved",
        "tool_label": "martillo de forja",
        "workplace": "forja",
        "material": "metal",
        "action": "mantener herramientas",
        "temper": "duro",
    },
    "granjero": {
        "skin": "humano_granjero",
        "color": (0.34, 0.48, 0.18),
        "shape": "standard",
        "tool": "hoe_reserved",
        "tool_label": "azada",
        "workplace": "cultivo",
        "material": "semillas",
        "action": "cuidar comida",
        "temper": "paciente",
    },
    "cazador": {
        "skin": "humano_cazador",
        "color": (0.16, 0.35, 0.18),
        "shape": "slim",
        "tool": "bow_reserved",
        "tool_label": "arco",
        "workplace": "bosque",
        "material": "pieles",
        "action": "rastrear presas",
        "temper": "alerta",
    },
    "minero": {
        "skin": "humano_minero",
        "color": (0.34, 0.34, 0.40),
        "shape": "compact",
        "tool": "pickaxe_reserved",
        "tool_label": "pico",
        "workplace": "mina",
        "material": "piedra",
        "action": "buscar mineral",
        "temper": "terco",
    },
    "mercader": {
        "skin": "humano_mercader",
        "color": (0.35, 0.22, 0.55),
        "shape": "refined",
        "tool": "satchel_reserved",
        "tool_label": "bolsa",
        "workplace": "mercado",
        "material": "mercancia",
        "action": "negociar rutas",
        "temper": "calculador",
    },
    "guardia": {
        "skin": "humano_guardia",
        "color": (0.55, 0.16, 0.14),
        "shape": "broad",
        "tool": "sword_reserved",
        "tool_label": "espada",
        "workplace": "puesto",
        "material": "acero",
        "action": "vigilar caminos",
        "temper": "disciplinado",
    },
    "curandero": {
        "skin": "humano_curandero",
        "color": (0.18, 0.56, 0.52),
        "shape": "slim",
        "tool": "staff_reserved",
        "tool_label": "baston",
        "workplace": "refugio",
        "material": "hierbas",
        "action": "atender heridas",
        "temper": "sereno",
    },
}


def stable_digest(*parts):
    text = "|".join(str(p) for p in parts)
    value = 1469598103934665603
    for ch in text:
        value ^= ord(ch)
        value = (value * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return f"{value:016x}"


def build_npc_id(seed, x=0, z=0, source="world", slot=0):
    source_key = str(source).replace(":", "_").replace(" ", "_")
    digest = stable_digest("npc", int(seed), _coord_key(x), _coord_key(z), source_key, int(slot))
    return f"npc_{source_key}_{digest[:12]}"


def choose_skin_zone_preset(seed, profession=None):
    visual_r = random.Random(int(seed) ^ 0x534B494E)
    if profession in HUMAN_PROFESSION_PROFILES:
        if profession == "carpintero" and visual_r.random() < 0.28:
            return "carpintero_viejo"
        return f"prof_{profession}"
    roll = visual_r.random()
    if roll < 0.18:
        return "carpintero_viejo"
    if roll < 0.34:
        return "ropa_carpintero"
    return "base"


def skin_zones_for_preset(preset_name, profession):
    if preset_name in SKIN_ZONE_PRESETS:
        preset = SKIN_ZONE_PRESETS[preset_name]
        return {
            "head": preset["head"],
            "torso": preset["torso"],
            "pants": preset["pants"],
        }
    profile = HUMAN_PROFESSION_PROFILES.get(profession, HUMAN_PROFESSION_PROFILES["granjero"])
    return {
        "head": None,
        "torso": profile["skin"],
        "pants": profile["skin"],
    }


def profile_for_profession(profession):
    return HUMAN_PROFESSION_PROFILES.get(profession, HUMAN_PROFESSION_PROFILES["granjero"])


def visible_tool_name(favorite_tool):
    if not favorite_tool:
        return None
    return str(favorite_tool).replace("_reserved", "")


def profession_identity(profile):
    return {
        "tool_label": profile.get("tool_label", "herramienta"),
        "workplace": profile.get("workplace", "camino"),
        "material": profile.get("material", "suministros"),
        "action": profile.get("action", "trabajar"),
        "temper": profile.get("temper", "neutral"),
    }


def stable_float01(*parts):
    return int(stable_digest(*parts)[:12], 16) / float(0xFFFFFFFFFFFF)


def stable_offset(seed, tag, min_radius, max_radius):
    angle = stable_float01(seed, tag, "angle") * math.pi * 2.0
    radius = min_radius + stable_float01(seed, tag, "radius") * (max_radius - min_radius)
    return math.cos(angle) * radius, math.sin(angle) * radius


def _coord_key(value):
    return int(round(float(value) * 100.0))
