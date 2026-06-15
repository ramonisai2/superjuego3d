from motor_juegos import r2d
from motor_juegos.render_mode_status import get_render_mode_status
from game.npc_ai_debug import npc_ai_telemetry_lines
import os

# UI 2D para ventana OPENGL.
# Importante: no usamos pygame.display.get_surface().blit() porque en modo OPENGL
# suele no aparecer o queda tapado por el render 3D.

def _panel(x, y, w, h):
    if hasattr(r2d, "draw_rounded_rect_2d"):
        r2d.draw_rounded_rect_2d(x, y, w, h, 8, (0.02, 0.024, 0.030, 0.34))
        r2d.draw_rounded_rect_2d(x + 1, y + 1, w - 2, h - 2, 7, (0.05, 0.060, 0.070, 0.18))
        r2d.draw_rounded_rect_2d(x + 1, y + 1, w - 2, 1, 1, (0.45, 0.58, 0.70, 0.10))
    else:
        r2d.draw_rect_2d(x, y, w, h, (0.01, 0.01, 0.012, 0.34))
        r2d.draw_rect_2d(x + 2, y + 2, w - 4, h - 4, (0.04, 0.045, 0.05, 0.18))


def _clip(text, limit):
    text = str(text)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def draw_bag_status_icon(player, x, y):
    notices = list(getattr(player, "pickup_notices", []))
    free = player.inventory_free() if hasattr(player, "inventory_free") else 1
    active = notices[-1] if notices else None
    active_kind = active.get("kind") if active else None
    collecting = active_kind in ("piedra", "madera", "fibra", "bag")
    full = free <= 0 or active_kind == "full"
    blink = True
    if active:
        ttl = float(active.get("ttl", 0.0))
        blink = int(ttl * 8.0) % 2 == 0

    outer = (0.10, 0.11, 0.12)
    inner = (0.18, 0.20, 0.21)
    flap = (0.12, 0.13, 0.14)
    r2d.draw_rect_2d(x, y + 7, 34, 26, outer)
    r2d.draw_rect_2d(x + 3, y + 10, 28, 20, inner)
    r2d.draw_rect_2d(x + 8, y + 3, 18, 8, outer)
    r2d.draw_rect_2d(x + 11, y + 5, 12, 5, inner)
    r2d.draw_rect_2d(x + 6, y + 12, 22, 7, flap)
    if full:
        if blink or not active:
            r2d.draw_rect_2d(x + 5, y + 25, 24, 4, (1.0, 0.50, 0.16))
    elif collecting and blink:
        r2d.draw_rect_2d(x + 5, y + 25, 24, 4, (0.18, 0.95, 0.30))


def draw_ui(player):
    _panel(14, 14, 316, 228)
    r2d.draw_text_2d(f'Vida {int(player.health)}', 26, 26, (245, 245, 240))
    r2d.draw_text_2d(f'Stamina {int(player.stamina)}', 26, 51, (205, 245, 205))
    r2d.draw_text_2d(f'Hambre {int(player.hunger)}', 26, 76, (255, 225, 170))
    modo = '3ra' if getattr(player, 'camera_mode', 'first') == 'third' else '1ra'
    r2d.draw_text_2d(f'Cam {modo}', 138, 26, (205, 220, 255))
    if hasattr(player, "normalize_inventory"):
        inv = player.normalize_inventory()
        used = player.inventory_used()
        cap = int(getattr(player, "bag_capacity", 0))
        r2d.draw_text_2d(f"Mochila {used}/{cap}", 26, 102, (210, 235, 255))
        draw_bag_status_icon(player, 276, 94)
        piedra_max = player.inventory_item_capacity("piedra") if hasattr(player, "inventory_item_capacity") else 6
        madera_max = player.inventory_item_capacity("madera") if hasattr(player, "inventory_item_capacity") else 6
        fibra_max = player.inventory_item_capacity("fibra") if hasattr(player, "inventory_item_capacity") else 6
        r2d.draw_text_2d(
            f"P:{int(inv.get('piedra', 0))}/{piedra_max} M:{int(inv.get('madera', 0))}/{madera_max} F:{int(inv.get('fibra', 0))}/{fibra_max}",
            26, 127, (230, 230, 210)
        )
        msg = getattr(player, "last_pickup_message", "")
        if msg:
            r2d.draw_text_2d(_clip(msg, 20), 142, 127, (255, 225, 140))
        if hasattr(player, "weapon_info"):
            weapon = player.weapon_info()
            r2d.draw_text_2d(
                _clip(f"Arma {weapon.get('name', 'Mano')}", 28),
                26, 152, (255, 230, 180)
            )
            uses = int(weapon.get("uses", 0) or 0)
            use_text = f"{uses} usos" if uses > 0 else "sin desgaste"
            r2d.draw_text_2d(
                f"D:{float(weapon.get('damage', 1.0)):.1f} R:{float(weapon.get('range', 3.2)):.1f} {use_text}",
                26, 177, (220, 235, 245)
            )
        if hasattr(player, "next_craft_recipe"):
            recipe = player.next_craft_recipe()
            color = (190, 255, 190) if recipe.get("complete") else (255, 215, 140)
            r2d.draw_text_2d(_clip(recipe.get("text", ""), 34), 26, 202, color)
        craft_msg = getattr(player, "last_craft_message", "")
        if craft_msg:
            r2d.draw_text_2d(_clip(f"C {craft_msg}", 24), 144, 102, (255, 235, 150))

    render_mode = get_render_mode_status()
    badge_color = (255, 210, 120) if render_mode.is_vulkan_requested else (150, 235, 170)
    _panel(1010, 14, 256, 36)
    r2d.draw_text_2d(render_mode.hud_label(), 1022, 24, badge_color)
    graphics_preset = os.environ.get("JUEGO_GRAPHICS_PRESET", "balanced").strip().upper() or "BALANCED"
    _panel(1010, 56, 160, 30)
    r2d.draw_text_2d(f"Graf: {graphics_preset}", 1022, 63, (205, 225, 255))
    terrain_mode = os.environ.get("JUEGO_TERRAIN_MODE", "current").strip().lower()
    if terrain_mode and terrain_mode != "current":
        _panel(1010, 92, 256, 32)
        r2d.draw_text_2d(f"Terreno: {terrain_mode.upper()}", 1022, 100, (255, 225, 150))


def draw_fps_counter(fps, x=1180, y=56):
    try:
        value = int(round(float(fps)))
    except Exception:
        value = 0
    if value >= 50:
        color = (160, 255, 180)
    elif value >= 30:
        color = (255, 225, 130)
    else:
        color = (255, 150, 120)
    _panel(x, y, 86, 30)
    r2d.draw_text_2d(f"FPS {value}", x + 10, y + 7, color)


def draw_adaptive_quality(state, scale, x=1058, y=676):
    state = str(state or "OK").upper()
    try:
        scale_value = max(0.0, min(1.0, float(scale)))
    except Exception:
        scale_value = 1.0
    if state in ("CRIT", "CRITICO"):
        color = (255, 150, 120)
    elif state in ("RESC", "AHORRO"):
        color = (255, 215, 130)
    elif state == "RECUP":
        color = (170, 225, 255)
    else:
        color = (180, 245, 190)
    _panel(x, y, 116, 30)
    r2d.draw_text_2d(f"Auto {state[:5]} {int(scale_value * 100)}", x + 9, y + 7, color)


def draw_pickup_notices(player):
    notices = getattr(player, "pickup_notices", [])
    if not notices:
        return
    visible = list(notices)[-3:]
    x = 342
    y = 18
    w = 188
    h = 18 + len(visible) * 24
    _panel(x, y, w, h)
    colors = {
        "piedra": (210, 215, 220),
        "madera": (225, 180, 115),
        "fibra": (165, 235, 155),
        "bag": (170, 220, 255),
        "full": (255, 170, 130),
        "blocked": (255, 220, 135),
    }
    for idx, notice in enumerate(visible):
        ttl = float(notice.get("ttl", 0.0))
        max_ttl = max(0.01, float(notice.get("max_ttl", 1.0)))
        fade = max(0.35, min(1.0, ttl / max_ttl))
        base = colors.get(notice.get("kind"), (230, 230, 210))
        color = tuple(max(0, min(255, int(c * fade))) for c in base)
        r2d.draw_text_2d(_clip(notice.get("text", ""), 18), x + 12, y + 12 + idx * 24, color)


def draw_combat_notices(player, ancho=1280, alto=720):
    notices = getattr(player, "combat_notices", [])
    if not notices:
        return
    visible = list(notices)[-2:]
    w = 168
    h = 16 + len(visible) * 22
    x = int(ancho // 2 - w // 2)
    y = int(alto - 118 - len(visible) * 10)
    _panel(x, y, w, h)
    colors = {
        "piedra": (220, 225, 230),
        "combat": (255, 220, 150),
    }
    for idx, notice in enumerate(visible):
        ttl = float(notice.get("ttl", 0.0))
        max_ttl = max(0.01, float(notice.get("max_ttl", 1.0)))
        fade = max(0.35, min(1.0, ttl / max_ttl))
        base = colors.get(notice.get("kind"), (235, 230, 210))
        color = tuple(max(0, min(255, int(c * fade))) for c in base)
        r2d.draw_text_2d(_clip(notice.get("text", ""), 18), x + 12, y + 10 + idx * 22, color)


def draw_npc_ai_telemetry():
    enabled = os.environ.get("JUEGO_DEBUG_NPC_AI", "0").strip().lower() in ("1", "true", "yes", "on")
    if not enabled:
        return
    lines = npc_ai_telemetry_lines()
    x = 820
    y = 584
    w = 446
    h = 118
    _panel(x, y, w, h)
    r2d.draw_text_2d("IA NPC", x + 14, y + 10, (180, 235, 255))
    for idx, line in enumerate(lines):
        color = (210, 245, 220) if idx != 3 else (255, 225, 170)
        r2d.draw_text_2d(_clip(line, 54), x + 14, y + 34 + idx * 20, color)


def draw_npc_label(name):
    if not name:
        return
    _panel(14, 548, 300, 32)
    r2d.draw_text_2d(_clip(name, 28), 24, 556, (200, 255, 200))


def draw_npc_prompt(prompt):
    if not prompt:
        return
    _panel(14, 586, 320, 32)
    r2d.draw_text_2d(_clip(prompt, 34), 24, 594, (255, 255, 200))


def draw_npc_description(description):
    if not description:
        return
    _panel(14, 624, 360, 32)
    r2d.draw_text_2d(_clip(description, 42), 24, 632, (200, 240, 255))


def draw_npc_dialog(dialog):
    if not dialog:
        return
    _panel(14, 662, 420, 32)
    r2d.draw_text_2d(_clip(dialog, 50), 24, 670, (200, 255, 200))


def draw_npc_world_label(name, x, y):
    if not name or x is None or y is None:
        return
    # Etiqueta aproximada centrada. Evitamos medir texto para mantenerlo simple.
    w = max(120, min(360, len(name) * 11))
    h = 30
    _panel(int(x - w // 2), int(y - h - 8), w, h)
    r2d.draw_text_2d(name, int(x - w // 2 + 8), int(y - h), (180, 255, 180))



def draw_z_target_ui(target, target_type, player=None):
    if target is None:
        return

    if target_type == "enemy":
        name = "SLIME FIJADO"
        hp = max(0, getattr(target, "health", 0))
        max_hp = max(1, getattr(target, "max_health", 2))
        stones = 0
        if player is not None:
            try:
                inv = player.normalize_inventory() if hasattr(player, "normalize_inventory") else getattr(player, "inventory", {})
                stones = int(inv.get("piedra", 0))
            except Exception:
                stones = 0
        subtitle = f"Vida: {hp}/{max_hp}   Piedras: {stones}"
        color = (255, 120, 120)
        ratio = max(0.0, min(1.0, hp / max_hp))
    else:
        name = "NPC FIJADO"
        subtitle = getattr(target, "nombre", "Objetivo")
        color = (180, 255, 180)
        ratio = 1.0

    w = 360
    h = 68
    x = 1280 // 2 - w // 2
    y = 22
    _panel(x, y, w, h)
    r2d.draw_text_2d("Q soltar   TAB cambiar", x + 16, y + 8, (255, 235, 130))
    r2d.draw_text_2d(f"{name}  {subtitle}", x + 16, y + 30, color)

    bar_x = x + 16
    bar_y = y + 54
    bar_w = w - 32
    r2d.draw_rect_2d(bar_x, bar_y, bar_w, 6, (0.10, 0.05, 0.05))
    if target_type == "enemy":
        r2d.draw_rect_2d(bar_x, bar_y, int(bar_w * ratio), 6, (0.95, 0.12, 0.10))
    else:
        r2d.draw_rect_2d(bar_x, bar_y, int(bar_w * ratio), 6, (0.25, 0.85, 0.35))

def draw_z_target_marker(screen_pos):
    if not screen_pos:
        return
    x, y = int(screen_pos[0]), int(screen_pos[1])
    size = 44
    col = (1.0, 0.82, 0.12)

    r2d.draw_rect_2d(x - size, y - size, 18, 3, col)
    r2d.draw_rect_2d(x - size, y - size, 3, 18, col)
    r2d.draw_rect_2d(x + size - 18, y - size, 18, 3, col)
    r2d.draw_rect_2d(x + size - 3, y - size, 3, 18, col)
    r2d.draw_rect_2d(x - size, y + size - 3, 18, 3, col)
    r2d.draw_rect_2d(x - size, y + size - 18, 3, 18, col)
    r2d.draw_rect_2d(x + size - 18, y + size - 3, 18, 3, col)
    r2d.draw_rect_2d(x + size - 3, y + size - 18, 3, 18, col)


def draw_world_context(player):
    ctx = getattr(player, "world_context", None)
    if not ctx:
        return
    y = 256
    _panel(14, y, 318, 84)
    swim = "  |  NADANDO" if getattr(player, "is_swimming", False) else ""
    r2d.draw_text_2d(_clip(f"Zona {ctx.get('feature','?')}{swim}", 31), 24, y + 8, (180, 235, 255))
    r2d.draw_text_2d(_clip(f"Bioma {ctx.get('biome','?')}", 31), 24, y + 32, (210, 255, 210))
    r2d.draw_text_2d(_clip(f"Altura {ctx.get('layer','?')}", 31), 24, y + 56, (255, 235, 170))
    if ctx.get('in_water'):
        pass
    else:
        pass
