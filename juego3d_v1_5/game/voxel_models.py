
from OpenGL.GL import *
import math
import os

try:
    import pygame
except Exception:
    pygame = None

_PLAYER_SKIN_TEX_ID = None
_PLAYER_SKIN_TEX_W = 1
_PLAYER_SKIN_TEX_H = 1
_SKIN_TEX_CACHE = {}
_SKIN_SURFACE_CACHE = {}
BOXEL_UNIT = 0.055

# Rectangulos (x0, y0, x1, y1) dentro del atlas generado.
# Son aproximados pero estan ajustados a la plantilla creada para este personaje.
PLAYER_SKIN_RECTS = {
    "head": {
        "top": (0, 0, 31, 31),
        "bottom": (34, 0, 65, 31),
        "front": (68, 0, 99, 31),
        "back": (102, 0, 133, 31),
        "left": (136, 0, 167, 31),
        "right": (170, 0, 201, 31),
    },
    "torso": {
        "top": (0, 36, 39, 59),
        "bottom": (42, 36, 81, 59),
        "front": (84, 36, 123, 99),
        "back": (126, 36, 165, 99),
        "left": (168, 36, 199, 99),
        "right": (202, 36, 233, 99),
    },
    "right_arm": {
        "top": (0, 104, 23, 127),
        "bottom": (26, 104, 49, 127),
        "front": (52, 104, 75, 159),
        "back": (78, 104, 101, 159),
        "left": (104, 104, 127, 159),
        "right": (130, 104, 153, 159),
    },
    "left_arm": {
        "top": (0, 104, 23, 127),
        "bottom": (26, 104, 49, 127),
        "front": (156, 104, 179, 159),
        "back": (182, 104, 205, 159),
        "left": (208, 104, 231, 159),
        "right": (232, 104, 255, 159),
    },
    "right_leg": {
        "top": (0, 164, 23, 187),
        "bottom": (26, 164, 49, 187),
        "front": (52, 164, 75, 239),
        "back": (78, 164, 101, 239),
        "left": (104, 164, 127, 239),
        "right": (130, 164, 153, 239),
    },
    "left_leg": {
        "top": (0, 164, 23, 187),
        "bottom": (26, 164, 49, 187),
        "front": (156, 164, 179, 239),
        "back": (182, 164, 205, 239),
        "left": (208, 164, 231, 239),
        "right": (232, 164, 255, 239),
    },
}

def _find_player_skin_path():
    here = os.path.dirname(__file__)
    candidates = [
        os.path.join(here, '..', 'player_skin_texture_atlas.png'),
        os.path.join(os.path.dirname(here), 'player_skin_texture_atlas.png'),
        '/mnt/data/minecraft_character_skin_texture_atlas.png',
    ]
    for path in candidates:
        path = os.path.abspath(path)
        if os.path.exists(path):
            return path
    return None

def _find_named_skin_path(skin_path=None):
    if not skin_path or skin_path == "player":
        return _find_player_skin_path()
    here = os.path.dirname(__file__)
    root = os.path.dirname(here)
    if os.path.isabs(str(skin_path)):
        candidates = [str(skin_path)]
    else:
        name = str(skin_path)
        if not name.endswith(".png"):
            name = f"player_skin_texture_atlas_{name}.png"
        candidates = [
            os.path.join(root, name),
            os.path.join(here, '..', name),
        ]
    for path in candidates:
        path = os.path.abspath(path)
        if os.path.exists(path):
            return path
    return None


def _load_player_skin_texture(skin_path=None):
    global _PLAYER_SKIN_TEX_ID, _PLAYER_SKIN_TEX_W, _PLAYER_SKIN_TEX_H
    resolved = _find_named_skin_path(skin_path)
    if not resolved:
        return None
    if skin_path is None and _PLAYER_SKIN_TEX_ID is not None:
        return _PLAYER_SKIN_TEX_ID
    if resolved in _SKIN_TEX_CACHE:
        tex_id, tex_w, tex_h = _SKIN_TEX_CACHE[resolved]
        _PLAYER_SKIN_TEX_W, _PLAYER_SKIN_TEX_H = tex_w, tex_h
        return tex_id
    if pygame is None:
        return None
    try:
        surface = pygame.image.load(resolved).convert_alpha()
        _SKIN_SURFACE_CACHE[resolved] = surface
        _PLAYER_SKIN_TEX_W, _PLAYER_SKIN_TEX_H = surface.get_width(), surface.get_height()
        data = pygame.image.tostring(surface, 'RGBA', True)
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, _PLAYER_SKIN_TEX_W, _PLAYER_SKIN_TEX_H, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        _SKIN_TEX_CACHE[resolved] = (tex_id, _PLAYER_SKIN_TEX_W, _PLAYER_SKIN_TEX_H)
        if skin_path is None:
            _PLAYER_SKIN_TEX_ID = tex_id
        return tex_id
    except Exception:
        if skin_path is None:
            _PLAYER_SKIN_TEX_ID = None
        return None


def _load_skin_surface(skin_path=None):
    resolved = _find_named_skin_path(skin_path)
    if not resolved or pygame is None:
        return None
    if resolved in _SKIN_SURFACE_CACHE:
        return _SKIN_SURFACE_CACHE[resolved]
    try:
        surface = pygame.image.load(resolved).convert_alpha()
        _SKIN_SURFACE_CACHE[resolved] = surface
        return surface
    except Exception:
        return None


def sample_head_nose_color(skin_path=None, fallback=(0.74, 0.56, 0.37)):
    surface = _load_skin_surface(skin_path)
    if surface is None:
        return fallback
    x0, y0, x1, y1 = PLAYER_SKIN_RECTS["head"]["front"]
    px = int(round(x0 + (x1 - x0) * 0.58))
    py = int(round(y0 + (y1 - y0) * 0.70))
    colors = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            sx = max(0, min(surface.get_width() - 1, px + dx))
            sy = max(0, min(surface.get_height() - 1, py + dy))
            r, g, b, a = surface.get_at((sx, sy))
            if a > 0 and not (r < 24 and g < 24 and b < 24) and not (r > 230 and g > 230 and b > 230):
                colors.append((r, g, b))
    if not colors:
        return fallback
    r = sum(c[0] for c in colors) / (255.0 * len(colors))
    g = sum(c[1] for c in colors) / (255.0 * len(colors))
    b = sum(c[2] for c in colors) / (255.0 * len(colors))
    return (r, g, b)


def _rect_uv(rect):
    x0, y0, x1, y1 = rect
    w = float(_PLAYER_SKIN_TEX_W)
    h = float(_PLAYER_SKIN_TEX_H)
    pad = 1.0
    u0 = (x0 + pad) / w
    u1 = (x1 - pad) / w
    # pygame.image.tostring(..., True) voltea el dato verticalmente, por lo que
    # debemos invertir las coordenadas V para usar rectángulos definidos en
    # coordenadas de imagen con origen en la esquina superior izquierda.
    v0 = 1.0 - (y1 - pad) / h
    v1 = 1.0 - (y0 + pad) / h
    return (u0, v0, u1, v1)

_MINECRAFT_HEAD_UV_FLIP = {
    "front": None,
    "back": "h",
    "left": "h",
    "right": None,
    "top": None,
    "bottom": "v",
}


def draw_minecraft_head(cx, cy, cz, sx, sy, sz, face_rects, shade_map=None, skin_path=None):
    """Dibuja una cabeza con orientación de caras al estilo Minecraft."""
    return draw_textured_box(
        cx, cy, cz, sx, sy, sz,
        face_rects,
        uv_flip=_MINECRAFT_HEAD_UV_FLIP,
        shade_map=shade_map,
        skin_path=skin_path,
    )


def draw_textured_box(cx, cy, cz, sx, sy, sz, face_rects, uv_flip=None, shade_map=None, skin_path=None):
    tex_id = _load_player_skin_texture(skin_path)
    if tex_id is None:
        return False
    if shade_map is None:
        shade_map = {"front":1.0, "back":0.82, "left":0.90, "right":0.90, "top":1.08, "bottom":0.70}
    if uv_flip is None:
        uv_flip = {}
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    x0, x1 = cx - hx, cx + hx
    y0, y1 = cy - hy, cy + hy
    z0, z1 = cz - hz, cz + hz

    def tc(face, p1, p2, p3, p4):
        u0, v0, u1, v1 = _rect_uv(face_rects[face])
        flip = uv_flip.get(face)
        if flip == "h" or flip == "hv":
            u0, u1 = u1, u0
        if flip == "v" or flip == "hv":
            v0, v1 = v1, v0
        coords = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        if flip == "r":
            coords = [(u0, v1), (u0, v0), (u1, v0), (u1, v1)]
        elif flip == "l":
            coords = [(u1, v0), (u1, v1), (u0, v1), (u0, v0)]
        f = max(0.0, min(1.2, float(shade_map.get(face, 1.0))))
        glColor3f(f, f, f)
        glTexCoord2f(*coords[0]); glVertex3f(*p1)
        glTexCoord2f(*coords[1]); glVertex3f(*p2)
        glTexCoord2f(*coords[2]); glVertex3f(*p3)
        glTexCoord2f(*coords[3]); glVertex3f(*p4)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    tc("front",  (x0,y0,z1), (x1,y0,z1), (x1,y1,z1), (x0,y1,z1))
    tc("back",   (x1,y0,z0), (x0,y0,z0), (x0,y1,z0), (x1,y1,z0))
    tc("left",   (x0,y0,z0), (x0,y0,z1), (x0,y1,z1), (x0,y1,z0))
    tc("right",  (x1,y0,z1), (x1,y0,z0), (x1,y1,z0), (x1,y1,z1))
    tc("top",    (x0,y1,z1), (x1,y1,z1), (x1,y1,z0), (x0,y1,z0))
    tc("bottom", (x0,y0,z0), (x1,y0,z0), (x1,y0,z1), (x0,y0,z1))
    glEnd()
    glDisable(GL_TEXTURE_2D)
    return True

def _shade(color, factor):
    return [max(0.0, min(1.0, c * factor)) for c in color]

def draw_boxel(cx, cy, cz, ux, uy, uz, color, unit=BOXEL_UNIT):
    """Dibuja una pieza usando la unidad boxel estandar del juego."""
    return draw_box(cx, cy, cz, ux * unit, uy * unit, uz * unit, color)

def draw_box(cx, cy, cz, sx, sy, sz, color):
    """Caja voxel centrada en coordenadas locales."""
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    x0, x1 = cx - hx, cx + hx
    y0, y1 = cy - hy, cy + hy
    z0, z1 = cz - hz, cz + hz
    top = _shade(color, 1.15)
    front = _shade(color, 1.00)
    side = _shade(color, 0.82)
    back = _shade(color, 0.70)
    bottom = _shade(color, 0.55)
    glBegin(GL_QUADS)
    glColor3fv(front);  glVertex3f(x0,y0,z1); glVertex3f(x1,y0,z1); glVertex3f(x1,y1,z1); glVertex3f(x0,y1,z1)
    glColor3fv(back);   glVertex3f(x1,y0,z0); glVertex3f(x0,y0,z0); glVertex3f(x0,y1,z0); glVertex3f(x1,y1,z0)
    glColor3fv(side);   glVertex3f(x0,y0,z0); glVertex3f(x0,y0,z1); glVertex3f(x0,y1,z1); glVertex3f(x0,y1,z0)
    glColor3fv(side);   glVertex3f(x1,y0,z1); glVertex3f(x1,y0,z0); glVertex3f(x1,y1,z0); glVertex3f(x1,y1,z1)
    glColor3fv(top);    glVertex3f(x0,y1,z1); glVertex3f(x1,y1,z1); glVertex3f(x1,y1,z0); glVertex3f(x0,y1,z0)
    glColor3fv(bottom); glVertex3f(x0,y0,z0); glVertex3f(x1,y0,z0); glVertex3f(x1,y0,z1); glVertex3f(x0,y0,z1)
    glEnd()

def draw_wire_box(cx, cy, cz, sx, sy, sz, color=(0,1,0), line_width=2.0):
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    x0, x1 = cx - hx, cx + hx
    y0, y1 = cy - hy, cy + hy
    z0, z1 = cz - hz, cz + hz
    pts = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    glColor3f(*color)
    glLineWidth(line_width)
    glBegin(GL_LINES)
    for a,b in edges:
        glVertex3f(*pts[a]); glVertex3f(*pts[b])
    glEnd()



def draw_shadow_blob(cx, cy, cz, sx, sz, alpha=0.18):
    """Sombra plana y suave para anclar entidades al suelo."""
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    glColor4f(0.03, 0.03, 0.04, alpha)
    glBegin(GL_QUADS)
    glVertex3f(cx - sx * 0.5, cy, cz - sz * 0.5)
    glVertex3f(cx + sx * 0.5, cy, cz - sz * 0.5)
    glVertex3f(cx + sx * 0.5, cy, cz + sz * 0.5)
    glVertex3f(cx - sx * 0.5, cy, cz + sz * 0.5)
    glEnd()
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)

def render_voxel_humanoid(x, base_y, z, yaw=0.0, body_color=(0.15,0.55,0.20), skin_color=(0.86,0.72,0.58), accent_color=(0.1,0.1,0.1), legendary=False, debug_hitbox=False, selected=False, walk_phase=0.0, move_amount=0.0, swimming=False):
    """Humanoide boxel con orientación y animación básica de caminata/nado."""
    move_amount = max(0.0, min(1.0, float(move_amount)))
    step = math.sin(walk_phase) * move_amount
    step2 = math.sin(walk_phase + math.pi) * move_amount
    lift_a = max(0.0, math.sin(walk_phase)) * 0.07 * move_amount
    lift_b = max(0.0, math.sin(walk_phase + math.pi)) * 0.07 * move_amount

    glPushMatrix()
    draw_shadow_blob(x, base_y + 0.015, z, 0.95, 0.78, 0.16)
    glTranslatef(x, base_y, z)
    glRotatef(yaw, 0, 1, 0)

    # Si nada, el cuerpo va un poco mas bajo e inclinado visualmente con brazos abiertos.
    swim_drop = 0.10 if swimming else 0.0
    swim_arm = 0.16 if swimming else 0.0
    swim_bob = math.sin(walk_phase * 0.75) * 0.035 if swimming else 0.0

    leg_col = _shade(body_color, 0.78)
    boot_col = _shade(accent_color, 0.70)
    glove_col = _shade(skin_color, 0.85)
    strap_col = _shade(accent_color, 0.60)

    # Piernas con pseudo-pasos: se adelantan/atrasan en Z y suben un poco.
    # Más gruesas para que se lean desde la cámara de tercera persona.
    left_z = 0.10 * step
    right_z = 0.10 * step2
    draw_box(-0.18, 0.20 + lift_a, left_z, 0.28, 0.18, 0.34, boot_col)
    draw_box( 0.18, 0.20 + lift_b, right_z, 0.28, 0.18, 0.34, boot_col)
    draw_box(-0.18, 0.54 + lift_a * 0.45, left_z * 0.55, 0.24, 0.54, 0.27, leg_col)
    draw_box( 0.18, 0.54 + lift_b * 0.45, right_z * 0.55, 0.24, 0.54, 0.27, leg_col)
    # Rodilleras / marcas para que no parezcan dos postes lisos.
    draw_box(-0.18, 0.64 + lift_a * 0.45, 0.16 + left_z * 0.55, 0.20, 0.08, 0.045, _shade(accent_color, 0.78))
    draw_box( 0.18, 0.64 + lift_b * 0.45, 0.16 + right_z * 0.55, 0.20, 0.08, 0.045, _shade(accent_color, 0.78))

    # Torso: un poco mas definido, con hombros/cinturon/pecho.
    torso_y = 1.02 - swim_drop + swim_bob
    draw_box(0.0, torso_y, -0.02, 0.78, 0.74, 0.42, body_color)
    draw_box(0.0, torso_y + 0.18, 0.225, 0.34, 0.26, 0.045, accent_color if not legendary else (1.0, 0.80, 0.10))
    draw_box(0.0, torso_y + 0.44, 0.14, 0.42, 0.10, 0.11, _shade(body_color, 0.62))
    draw_box(0.0, torso_y - 0.30, 0.02, 0.84, 0.11, 0.32, _shade(accent_color, 0.74))
    # Correas de mochila al frente.
    draw_box(-0.24, torso_y + 0.05, 0.232, 0.055, 0.54, 0.035, strap_col)
    draw_box( 0.24, torso_y + 0.05, 0.232, 0.055, 0.54, 0.035, strap_col)

    # Brazos opuestos a las piernas. En nado se abren un poco para simular flotación.
    arm_swing_l = -0.12 * step + swim_arm
    arm_swing_r = -0.12 * step2 - swim_arm
    draw_box(-0.53, torso_y - 0.02, arm_swing_l, 0.19, 0.76, 0.23, _shade(body_color, 0.90))
    draw_box( 0.53, torso_y - 0.04, arm_swing_r, 0.20, 0.80, 0.24, _shade(body_color, 0.82))
    draw_box(-0.53, torso_y - 0.45, arm_swing_l + 0.02, 0.18, 0.16, 0.20, glove_col)
    draw_box( 0.53, torso_y - 0.47, arm_swing_r + 0.02, 0.18, 0.16, 0.20, glove_col)
    draw_box( 0.42, torso_y + 0.25, -0.02, 0.22, 0.14, 0.28, _shade(accent_color, 0.82))

    # Cabeza y rostro más claro para saber hacia dónde mira.
    head_y = 1.60 - swim_drop + swim_bob
    draw_box(0.0, head_y, 0.0, 0.43, 0.49, 0.43, skin_color)
    hat_col = accent_color if not legendary else (0.95, 0.72, 0.12)
    draw_box(0.0, head_y + 0.28, -0.02, 0.54, 0.16, 0.47, hat_col)
    draw_box(0.0, head_y + 0.16, 0.18, 0.34, 0.08, 0.075, _shade(hat_col, 0.88))
    draw_box(-0.10, head_y + 0.04, 0.225, 0.06, 0.06, 0.03, (0.03, 0.03, 0.03))
    draw_box( 0.10, head_y + 0.04, 0.225, 0.06, 0.06, 0.03, (0.03, 0.03, 0.03))
    draw_box( 0.00, head_y - 0.06, 0.232, 0.07, 0.09, 0.035, _shade(skin_color, 0.86))
    # Nariz/pequeña dirección frontal.
    draw_box(0.0, head_y - 0.01, 0.255, 0.055, 0.055, 0.055, _shade(skin_color, 0.78))

    # Mochila y detalles laterales para que se vea menos cubo.
    draw_box(0.0, torso_y, -0.27, 0.42, 0.48, 0.14, _shade(accent_color, 0.74))
    draw_box(-0.30, torso_y - 0.14, -0.18, 0.09, 0.24, 0.09, _shade(accent_color, 0.90))
    draw_box( 0.31, torso_y - 0.12, -0.18, 0.08, 0.20, 0.08, _shade(accent_color, 0.82))

    if selected:
        draw_wire_box(0.0, 0.98, 0.0, 1.12, 2.04, 0.98, (0.0, 1.0, 0.0), 2.5)
    if debug_hitbox:
        draw_wire_box(0.0, 0.90, 0.0, 0.62, 1.80, 0.62, (1.0, 0.05, 0.05), 1.5)
    glPopMatrix()

def _skin_zone(skin_zones, zone):
    if not skin_zones:
        return None
    return skin_zones.get(zone) or skin_zones.get("all") or None


def _human_shape(body_shape):
    profiles = {
        "standard": {"torso_w": 0.76, "leg_x": 0.19, "leg_w": 0.25, "boot_w": 0.29, "arm_x": 0.54, "arm_w": 0.18},
        "sturdy": {"torso_w": 0.82, "leg_x": 0.20, "leg_w": 0.27, "boot_w": 0.31, "arm_x": 0.57, "arm_w": 0.21},
        "broad": {"torso_w": 0.86, "leg_x": 0.21, "leg_w": 0.28, "boot_w": 0.32, "arm_x": 0.60, "arm_w": 0.22},
        "slim": {"torso_w": 0.68, "leg_x": 0.17, "leg_w": 0.22, "boot_w": 0.27, "arm_x": 0.50, "arm_w": 0.16},
        "compact": {"torso_w": 0.78, "leg_x": 0.18, "leg_w": 0.26, "boot_w": 0.30, "arm_x": 0.53, "arm_w": 0.20},
        "refined": {"torso_w": 0.72, "leg_x": 0.18, "leg_w": 0.23, "boot_w": 0.28, "arm_x": 0.51, "arm_w": 0.17},
    }
    return profiles.get(body_shape or "standard", profiles["standard"])


def render_head_features(head_y, skin_color, hair_color, nose_style="human", ear_style="human", nose_color=None):
    if ear_style and ear_style != "none":
        if ear_style == "elf":
            ear_col = _shade(skin_color, 0.90)
            draw_boxel(-0.265, head_y - 0.005, 0.01, 1, 3, 2, ear_col)
            draw_boxel(-0.320, head_y + 0.015, 0.02, 1, 2, 1, _shade(ear_col, 0.95))
            draw_boxel( 0.265, head_y - 0.005, 0.01, 1, 3, 2, ear_col)
            draw_boxel( 0.320, head_y + 0.015, 0.02, 1, 2, 1, _shade(ear_col, 0.95))
        elif ear_style == "duende":
            ear_col = _shade(skin_color, 0.82)
            draw_boxel(-0.275, head_y - 0.025, 0.02, 2, 3, 2, ear_col)
            draw_boxel(-0.345, head_y - 0.015, 0.025, 1, 1, 1, _shade(ear_col, 0.90))
            draw_boxel( 0.275, head_y - 0.025, 0.02, 2, 3, 2, ear_col)
            draw_boxel( 0.345, head_y - 0.015, 0.025, 1, 1, 1, _shade(ear_col, 0.90))
        else:
            ear_col = _shade(skin_color, 0.88)
            draw_boxel(-0.245, head_y - 0.015, 0.005, 1, 3, 2, ear_col)
            draw_boxel( 0.245, head_y - 0.015, 0.005, 1, 3, 2, ear_col)

    if nose_style and nose_style != "none":
        nose_col = nose_color or skin_color
        draw_boxel(0.0, head_y - 0.075, 0.265, 1, 1, 1, _shade(nose_col, 0.92))
        draw_boxel(0.0, head_y - 0.095, 0.320, 1, 1, 1, _shade(nose_col, 0.82))


def render_back_tool(tool_name, torso_y, steel, wood, gold, dark):
    if not tool_name or tool_name == "none":
        return
    tool_name = str(tool_name).replace("_reserved", "")
    glPushMatrix()
    glTranslatef(0.18, torso_y - 0.01, -0.46)
    glRotatef(-28.0, 0, 0, 1)
    if tool_name == "hammer":
        draw_boxel(0.0, 0.0, 0.0, 1, 14, 1, wood)
        draw_boxel(0.0, 0.36, 0.0, 5, 2, 2, steel)
        draw_boxel(-0.165, 0.36, 0.0, 2, 2, 2, _shade(steel, 0.85))
    elif tool_name == "axe":
        draw_boxel(0.0, 0.0, 0.0, 1, 16, 1, wood)
        draw_boxel(0.085, 0.34, 0.0, 4, 3, 2, steel)
        draw_boxel(0.195, 0.31, 0.0, 2, 2, 1, _shade(steel, 0.82))
    elif tool_name == "pickaxe":
        draw_boxel(0.0, 0.0, 0.0, 1, 16, 1, wood)
        draw_boxel(0.0, 0.37, 0.0, 7, 1, 2, steel)
        draw_boxel(-0.20, 0.33, 0.0, 2, 2, 1, _shade(steel, 0.82))
        draw_boxel(0.20, 0.33, 0.0, 2, 2, 1, _shade(steel, 0.82))
    elif tool_name == "hoe":
        draw_boxel(0.0, 0.0, 0.0, 1, 16, 1, wood)
        draw_boxel(0.11, 0.37, 0.0, 5, 1, 2, steel)
        draw_boxel(0.24, 0.30, 0.0, 1, 3, 1, _shade(steel, 0.78))
    elif tool_name == "bow":
        draw_boxel(-0.09, -0.03, 0.0, 1, 12, 1, wood)
        draw_boxel(-0.04, 0.27, 0.0, 1, 3, 1, _shade(wood, 1.10))
        draw_boxel(0.02, 0.36, 0.0, 1, 2, 1, _shade(wood, 1.05))
        draw_boxel(-0.04, -0.33, 0.0, 1, 3, 1, _shade(wood, 0.88))
        draw_boxel(0.02, -0.42, 0.0, 1, 2, 1, _shade(wood, 0.82))
        draw_boxel(0.11, -0.02, 0.0, 1, 15, 1, _shade(steel, 1.25))
    elif tool_name == "staff":
        draw_boxel(0.0, 0.0, 0.0, 1, 17, 1, wood)
        draw_boxel(0.0, 0.45, 0.0, 3, 3, 2, (0.16, 0.62, 0.58))
        draw_boxel(0.0, 0.45, 0.045, 1, 1, 1, (0.75, 1.0, 0.92))
    elif tool_name == "satchel":
        glRotatef(28.0, 0, 0, 1)
        glTranslatef(-0.03, -0.06, 0.0)
        draw_boxel(0.0, 0.03, 0.0, 5, 5, 2, wood)
        draw_boxel(0.0, 0.15, 0.055, 5, 1, 1, _shade(wood, 0.78))
        draw_boxel(0.0, 0.03, 0.075, 2, 1, 1, gold)
        draw_boxel(-0.17, 0.30, 0.0, 1, 3, 1, _shade(dark, 1.15))
        draw_boxel(0.17, 0.30, 0.0, 1, 3, 1, _shade(dark, 1.15))
    elif tool_name == "sword":
        draw_boxel(0.0, 0.08, 0.0, 1, 16, 1, steel)
        draw_boxel(0.0, -0.38, 0.0, 2, 1, 1, gold)
        draw_boxel(0.0, -0.49, 0.0, 1, 3, 1, dark)
    else:
        draw_boxel(0.0, 0.0, 0.0, 1, 14, 1, wood)
    glPopMatrix()


def render_crafted_weapon(weapon_key, wood, fiber, stone, dark):
    if not weapon_key or weapon_key == "mano":
        return
    weapon_key = str(weapon_key)
    draw_boxel(0.0, -0.02, 0.0, 1, 7, 1, _shade(wood, 0.86))
    draw_boxel(0.0, 0.34, 0.0, 1, 7, 1, wood)
    draw_boxel(0.0, 0.70, 0.0, 1, 6, 1, _shade(wood, 1.08))
    if weapon_key in ("palo_fibra", "palo_piedra"):
        draw_boxel(0.0, 0.17, 0.035, 2, 1, 1, fiber)
        draw_boxel(0.0, 0.42, -0.035, 2, 1, 1, _shade(fiber, 0.88))
        draw_boxel(0.0, 0.61, 0.035, 2, 1, 1, fiber)
    if weapon_key == "palo_piedra":
        draw_boxel(0.0, 0.92, 0.0, 3, 3, 2, stone)
        draw_boxel(-0.105, 0.94, 0.0, 1, 2, 2, _shade(stone, 0.78))
        draw_boxel(0.105, 0.91, 0.0, 1, 2, 2, _shade(stone, 1.12))
        draw_boxel(0.0, 0.76, 0.045, 2, 1, 1, dark)


def render_first_person_grip(weapon_key, skin, sleeve, dark):
    has_weapon = bool(weapon_key and weapon_key != "mano")
    draw_boxel(0.0, -0.22, -0.06, 4, 5, 4, sleeve)
    draw_boxel(0.0, 0.02, 0.0, 4, 4, 4, skin)
    draw_boxel(-0.090, 0.045, 0.085, 1, 2, 2, _shade(skin, 0.92))
    draw_boxel(0.000, 0.055, 0.095, 1, 2, 2, _shade(skin, 0.95))
    draw_boxel(0.090, 0.045, 0.085, 1, 2, 2, _shade(skin, 0.88))
    draw_boxel(-0.125, -0.040, -0.040, 1, 2, 2, _shade(skin, 0.82))
    if has_weapon:
        draw_boxel(0.0, 0.145, 0.0, 4, 1, 4, _shade(dark, 1.22))
        draw_boxel(0.0, 0.210, 0.0, 3, 1, 3, _shade(skin, 0.86))


def render_first_person_weapon(px, py, pz, lx, ly, lz, weapon_key=None, attack_swing=0.0):
    weapon_key = weapon_key or "mano"
    fx = float(lx) - float(px)
    fy = float(ly) - float(py)
    fz = float(lz) - float(pz)
    length = math.sqrt(fx * fx + fy * fy + fz * fz) or 1.0
    fx, fy, fz = fx / length, fy / length, fz / length
    rx, rz = fz, -fx
    rlen = math.sqrt(rx * rx + rz * rz) or 1.0
    rx, rz = rx / rlen, rz / rlen
    attack_swing = max(0.0, min(1.0, float(attack_swing or 0.0)))

    wx = float(px) + fx * (0.82 + 0.18 * attack_swing) + rx * 0.34
    wy = float(py) + fy * 0.82 - 0.36 - 0.08 * attack_swing
    wz = float(pz) + fz * (0.82 + 0.18 * attack_swing) + rz * 0.34
    yaw = math.degrees(math.atan2(fx, fz))

    glPushMatrix()
    glDisable(GL_FOG)
    glDisable(GL_DEPTH_TEST)
    glTranslatef(wx, wy, wz)
    glRotatef(yaw, 0, 1, 0)
    glRotatef(-48.0 - 36.0 * attack_swing, 1, 0, 0)
    glRotatef(-18.0 - 12.0 * attack_swing, 0, 0, 1)
    glScalef(1.16, 1.16, 1.16)
    skin = (0.74, 0.56, 0.37)
    sleeve = (0.18, 0.32, 0.70)
    dark = (0.08, 0.10, 0.13)
    render_first_person_grip(weapon_key, skin, sleeve, dark)
    if weapon_key != "mano":
        glTranslatef(0.0, 0.38, 0.0)
        render_crafted_weapon(
            weapon_key,
            (0.34, 0.22, 0.12),
            (0.56, 0.66, 0.38),
            (0.43, 0.43, 0.40),
            dark,
        )
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_FOG)
    glPopMatrix()


def render_player_avatar(x, base_y, z, yaw=0.0, selected=False, walk_phase=0.0, move_amount=0.0, swimming=False, head_uv_flip=None, accessory_color=None, legendary=False, debug_hitbox=False, skin_zones=None, nose_style="human", ear_style="human", show_hair_volume=True, front_gear="full", back_tool=None, body_shape="standard", held_weapon=None, attack_swing=0.0):
    """Jugador principal con mezcla de textura + boxel.
    La textura da identidad de ropa/cara y las piezas boxel agregan volumen.
    """
    move_amount = max(0.0, min(1.0, float(move_amount)))
    step = math.sin(walk_phase) * move_amount
    step2 = math.sin(walk_phase + math.pi) * move_amount
    lift_a = max(0.0, math.sin(walk_phase)) * 0.07 * move_amount
    lift_b = max(0.0, math.sin(walk_phase + math.pi)) * 0.07 * move_amount

    head_skin = _skin_zone(skin_zones, "head")
    torso_skin = _skin_zone(skin_zones, "torso")
    pants_skin = _skin_zone(skin_zones, "pants")
    tex_id = _load_player_skin_texture(head_skin)
    if tex_id is None:
        fallback_accent = accessory_color if accessory_color is not None else (0.10,0.12,0.16)
        render_voxel_humanoid(
            x, base_y, z, yaw=yaw,
            body_color=(0.18,0.32,0.70),
            skin_color=(0.88,0.74,0.60),
            accent_color=fallback_accent,
            selected=selected,
            debug_hitbox=debug_hitbox,
            walk_phase=walk_phase,
            move_amount=move_amount,
            swimming=swimming,
        )
        return

    if head_uv_flip is None:
        head_uv_flip = {"left": "h", "right": "h"}

    glPushMatrix()
    draw_shadow_blob(x, base_y + 0.015, z, 0.98, 0.80, 0.16)
    glTranslatef(x, base_y, z)
    glRotatef(yaw, 0, 1, 0)

    swim_drop = 0.10 if swimming else 0.0
    swim_arm = 0.16 if swimming else 0.0
    swim_bob = math.sin(walk_phase * 0.75) * 0.035 if swimming else 0.0

    torso_y = 1.03 - swim_drop + swim_bob
    head_y = 1.60 - swim_drop + swim_bob
    left_z = 0.10 * step
    right_z = 0.10 * step2
    arm_swing_l = -0.12 * step + swim_arm
    arm_swing_r = -0.12 * step2 - swim_arm
    attack_swing = max(0.0, min(1.0, float(attack_swing or 0.0)))
    right_attack_z = arm_swing_r + 0.30 * attack_swing
    right_attack_y = -0.08 * attack_swing
    left_guard_z = arm_swing_l - 0.06 * attack_swing

    # Paleta boxel/accesorios.
    dark = (0.08, 0.10, 0.13)
    steel = accessory_color if accessory_color is not None else (0.28, 0.31, 0.35)
    brown = _shade(accessory_color, 0.58) if accessory_color is not None else (0.31, 0.21, 0.12)
    gold = (1.0, 0.78, 0.10) if legendary else (0.68, 0.57, 0.22)
    blue = (0.15, 0.30, 0.60)
    skin = (0.74, 0.56, 0.37)
    hair = (0.36, 0.35, 0.32) if head_skin == "carpintero_viejo" else (0.10, 0.09, 0.08)
    shape = _human_shape(body_shape)
    torso_w = shape["torso_w"]
    leg_x = shape["leg_x"]
    leg_w = shape["leg_w"]
    boot_w = shape["boot_w"]
    arm_x = shape["arm_x"]
    arm_w = shape["arm_w"]

    # Piernas texturadas + refuerzos boxel.
    draw_textured_box(-leg_x, 0.20 + lift_a, left_z, boot_w, 0.18, 0.35, PLAYER_SKIN_RECTS["left_leg"], skin_path=pants_skin)
    draw_textured_box( leg_x, 0.20 + lift_b, right_z, boot_w, 0.18, 0.35, PLAYER_SKIN_RECTS["right_leg"], skin_path=pants_skin)
    draw_textured_box(-leg_x, 0.55 + lift_a * 0.45, left_z * 0.55, leg_w, 0.55, 0.28, PLAYER_SKIN_RECTS["left_leg"], skin_path=pants_skin)
    draw_textured_box( leg_x, 0.55 + lift_b * 0.45, right_z * 0.55, leg_w, 0.55, 0.28, PLAYER_SKIN_RECTS["right_leg"], skin_path=pants_skin)
    draw_box(-leg_x, 0.12 + lift_a, left_z, boot_w + 0.02, 0.09, 0.37, dark)
    draw_box( leg_x, 0.12 + lift_b, right_z, boot_w + 0.02, 0.09, 0.37, dark)
    draw_box(-leg_x, 0.66 + lift_a * 0.45, 0.12 + left_z * 0.40, leg_w * 0.88, 0.08, 0.05, steel)
    draw_box( leg_x, 0.66 + lift_b * 0.45, 0.12 + right_z * 0.40, leg_w * 0.88, 0.08, 0.05, steel)
    draw_box(-leg_x, 0.37 + lift_a * 0.25, 0.15 + left_z * 0.45, leg_w * 0.76, 0.06, 0.04, gold)
    draw_box( leg_x, 0.37 + lift_b * 0.25, 0.15 + right_z * 0.45, leg_w * 0.76, 0.06, 0.04, gold)

    # Torso principal texturizado.
    draw_textured_box(0.0, torso_y, -0.02, torso_w, 0.74, 0.42, PLAYER_SKIN_RECTS["torso"], skin_path=torso_skin)
    # Detalles 3D del torso: los NPCs pueden usar modo limpio para no tapar la textura.
    if front_gear == "full":
        draw_box(0.0, torso_y + 0.16, 0.20, 0.42, 0.20, 0.05, steel)
        draw_box(0.0, torso_y - 0.03, 0.19, 0.56, 0.28, 0.04, steel)
    elif front_gear == "light":
        draw_box(0.0, torso_y - 0.06, 0.205, 0.34, 0.11, 0.035, _shade(steel, 0.82))
    draw_box(0.0, torso_y - 0.28, 0.02, torso_w + 0.08, 0.10, 0.33, brown)
    draw_box(0.0, torso_y - 0.28, 0.20, 0.12, 0.11, 0.05, gold)
    draw_box(-torso_w * 0.30, torso_y + 0.06, 0.225, 0.055, 0.54, 0.035, brown)
    draw_box( torso_w * 0.30, torso_y + 0.06, 0.225, 0.055, 0.54, 0.035, brown)
    if front_gear == "full":
        draw_box(0.0, torso_y + 0.02, -0.29, 0.36, 0.42, 0.14, brown)
        draw_box(0.0, torso_y - 0.04, -0.40, 0.20, 0.16, 0.07, dark)
        draw_box(0.0, torso_y + 0.34, -0.24, 0.24, 0.08, 0.06, steel)
    render_back_tool(back_tool, torso_y, steel, brown, gold, dark)

    # Hombros boxel para que no se vea plano.
    if front_gear == "full":
        draw_box(-torso_w * 0.52, torso_y + 0.25, 0.0, 0.17, 0.14, 0.24, steel)
        draw_box( torso_w * 0.52, torso_y + 0.25, 0.0, 0.17, 0.14, 0.24, steel)

    # Brazos texturizados + brazaletes.
    draw_textured_box(-arm_x, torso_y - 0.03, left_guard_z, arm_w, 0.76, 0.22, PLAYER_SKIN_RECTS["left_arm"], skin_path=torso_skin)
    draw_textured_box( arm_x, torso_y - 0.04 + right_attack_y, right_attack_z, arm_w, 0.78, 0.22, PLAYER_SKIN_RECTS["right_arm"], skin_path=torso_skin)
    if front_gear == "full":
        draw_box(-arm_x, torso_y + 0.20, left_guard_z, arm_w + 0.03, 0.11, 0.25, steel)
        draw_box( arm_x, torso_y + 0.20 + right_attack_y, right_attack_z, arm_w + 0.03, 0.11, 0.25, steel)
        draw_box(-arm_x, torso_y - 0.18, left_guard_z + 0.01, arm_w * 0.82, 0.07, 0.24, gold)
        draw_box( arm_x, torso_y - 0.19 + right_attack_y, right_attack_z + 0.01, arm_w * 0.82, 0.07, 0.24, gold)
    draw_box(-arm_x, torso_y - 0.46, left_guard_z + 0.02, arm_w, 0.14, 0.19, skin)
    draw_box( arm_x, torso_y - 0.48 + right_attack_y, right_attack_z + 0.02, arm_w, 0.14, 0.19, skin)
    if held_weapon and held_weapon != "mano":
        glPushMatrix()
        glTranslatef(arm_x + arm_w * 0.58, torso_y - 0.64 + right_attack_y, right_attack_z + 0.16 + 0.18 * attack_swing)
        glRotatef(-28.0 - 34.0 * attack_swing, 1, 0, 0)
        glRotatef(-12.0 - 10.0 * attack_swing, 0, 0, 1)
        render_crafted_weapon(held_weapon, brown, (0.56, 0.66, 0.38), (0.43, 0.43, 0.40), dark)
        glPopMatrix()

    # Cabeza texturizada + volumen de cabello/capucha.
    draw_textured_box(
        0.0, head_y, 0.0, 0.43, 0.49, 0.43,
        PLAYER_SKIN_RECTS["head"],
        uv_flip=head_uv_flip,
        skin_path=head_skin,
    )
    if show_hair_volume:
        draw_box(0.0, head_y + 0.24, 0.0, 0.47, 0.08, 0.47, hair)
        draw_box(-0.19, head_y + 0.02, 0.0, 0.05, 0.28, 0.40, hair)
        draw_box( 0.19, head_y + 0.02, 0.0, 0.05, 0.28, 0.40, hair)
    nose_color = sample_head_nose_color(head_skin, fallback=skin)
    render_head_features(head_y, skin, hair, nose_style=nose_style, ear_style=ear_style, nose_color=nose_color)
    draw_box(0.0, head_y - 0.26, 0.0, 0.16, 0.07, 0.12, skin)

    if swimming:
        draw_box(0.0, torso_y + 0.05, -0.46, 0.52, 0.08, 0.08, blue)

    if selected:
        draw_wire_box(0.0, 0.98, 0.0, 1.12, 2.04, 0.98, (0.0, 1.0, 0.0), 2.5)
    if debug_hitbox:
        draw_wire_box(0.0, 0.90, 0.0, 0.62, 1.80, 0.62, (1.0, 0.05, 0.05), 1.5)
    glPopMatrix()

def render_voxel_slime(x, base_y, z, yaw=0.0, body_color=(0.85,0.10,0.12), eye_color=(1,1,1), pupil_color=(0.08,0.02,0.02), selected=False, debug_hitbox=False, body_scale=1.0, aggro=0.0, squish_phase=0.0, is_boss=False, detail_level="full"):
    """Slime boxel con frente claro, patas endebles y cuerpo gelatinoso."""
    glPushMatrix()
    wobble = math.sin(squish_phase)
    hop = max(0.0, math.sin(squish_phase * 0.55)) * (0.055 + 0.035 * aggro) * body_scale
    sway = math.sin(squish_phase * 0.72) * (2.0 + 4.0 * aggro)
    draw_shadow_blob(x, base_y + 0.012, z, 1.04 * body_scale, 0.96 * body_scale, 0.13)
    glTranslatef(x, base_y, z)
    glRotatef(yaw, 0, 1, 0)
    glTranslatef(0.0, hop, 0.0)
    glRotatef(sway, 0, 0, 1)

    detail_level = str(detail_level or "full")
    body_alpha = 0.52 if not is_boss else 0.62
    breath = math.sin(squish_phase * 0.38 + 1.2)
    leg_h = (0.16 + 0.32 * aggro + 0.035 * wobble) * body_scale
    body_y = leg_h + (0.44 + 0.04 * wobble) * body_scale
    body_h = (0.72 - 0.07 * wobble + 0.025 * breath) * body_scale
    body_w = (1.04 + 0.07 * wobble - 0.025 * breath) * body_scale
    body_d = (0.98 + 0.06 * wobble - 0.020 * breath) * body_scale

    if detail_level == "far":
        body_y = 0.54 * body_scale
        body_h = 0.76 * body_scale
        body_w = 1.00 * body_scale
        body_d = 0.92 * body_scale
        draw_box_alpha(0.0, body_y, 0.0, body_w, body_h, body_d, body_color, body_alpha)
        eye_z = body_d * 0.52
        eye_y = body_y + 0.09 * body_scale
        eye_sep = 0.19 * body_scale
        draw_box(-eye_sep, eye_y, eye_z, 0.13 * body_scale, 0.09 * body_scale, 0.03 * body_scale, eye_color)
        draw_box( eye_sep, eye_y, eye_z, 0.13 * body_scale, 0.09 * body_scale, 0.03 * body_scale, eye_color)
        if selected:
            draw_wire_box(0.0, body_y, 0.0, 1.12 * body_scale, body_h + 0.18 * body_scale, 1.04 * body_scale, (0.1, 1.0, 0.1), 2.2)
        if debug_hitbox:
            draw_wire_box(0.0, body_y, 0.0, 1.04 * body_scale, body_h, 0.98 * body_scale, (1.0, 0.05, 0.05), 1.5)
        glPopMatrix()
        return

    leg_color = _shade(body_color, 0.68)
    spread_x = 0.31 * body_scale + 0.06 * aggro
    spread_z = 0.28 * body_scale + 0.05 * aggro
    leg_w = 0.115 * body_scale
    # Patitas delgadas y algo torcidas para que se vean frágiles.
    draw_box(-spread_x, leg_h * 0.5, -spread_z - 0.04 * wobble, leg_w, leg_h, leg_w, leg_color)
    draw_box( spread_x, leg_h * 0.5, -spread_z + 0.03 * wobble, leg_w, leg_h * (0.92 + 0.08 * aggro), leg_w, leg_color)
    draw_box(-spread_x + 0.03 * wobble, leg_h * 0.5, spread_z, leg_w, leg_h * (0.94 - 0.05 * wobble), leg_w, leg_color)
    draw_box( spread_x - 0.04 * wobble, leg_h * 0.5, spread_z, leg_w, leg_h, leg_w, leg_color)

    # Cuerpo translúcido como gelatina.
    draw_box_alpha(0.0, body_y, 0.0, body_w, body_h, body_d, body_color, body_alpha)
    # Núcleo interno tenue para que se vea a través.
    if detail_level == "full":
        draw_box_alpha(0.0, body_y - 0.02 * body_scale, 0.0, body_w * 0.55, body_h * 0.48, body_d * 0.55, _shade(body_color, 1.15), body_alpha * 0.30)
        draw_box_alpha(-0.20 * body_scale, body_y + 0.18 * body_scale, body_d * 0.22, 0.20 * body_scale, 0.12 * body_scale, 0.035 * body_scale, _shade(body_color, 1.35), body_alpha * 0.28)

    eye_z = body_d * 0.52
    eye_y = body_y + (0.10 + 0.025 * wobble) * body_scale
    eye_sep = (0.20 + 0.025 * aggro) * body_scale
    draw_box(-eye_sep, eye_y, eye_z, 0.14 * body_scale, 0.105 * body_scale, 0.03 * body_scale, eye_color)
    draw_box( eye_sep, eye_y + 0.015 * wobble * body_scale, eye_z, 0.14 * body_scale, 0.105 * body_scale, 0.03 * body_scale, eye_color)
    if detail_level == "full":
        pupil_shift = 0.018 * math.sin(squish_phase * 0.33)
        draw_box(-eye_sep + pupil_shift * body_scale, eye_y, eye_z + 0.012 * body_scale, 0.052 * body_scale, 0.052 * body_scale, 0.02 * body_scale, pupil_color)
        draw_box( eye_sep + pupil_shift * body_scale, eye_y + 0.015 * wobble * body_scale, eye_z + 0.012 * body_scale, 0.052 * body_scale, 0.052 * body_scale, 0.02 * body_scale, pupil_color)
    mouth_w = (0.20 + 0.10 * aggro + 0.03 * max(0.0, -wobble)) * body_scale
    draw_box(0.0, body_y - 0.11 * body_scale, eye_z, mouth_w, 0.05 * body_scale, 0.03 * body_scale, _shade(body_color, 0.42))
    if detail_level == "full" and aggro > 0.35:
        brow_col = _shade(body_color, 0.28)
        draw_box(-eye_sep, eye_y + 0.105 * body_scale, eye_z + 0.014 * body_scale, 0.16 * body_scale, 0.035 * body_scale, 0.025 * body_scale, brow_col)
        draw_box( eye_sep, eye_y + 0.105 * body_scale, eye_z + 0.014 * body_scale, 0.16 * body_scale, 0.035 * body_scale, 0.025 * body_scale, brow_col)

    if is_boss:
        draw_box_alpha(0.0, body_y + body_h * 0.58, 0.0, 0.54 * body_scale, 0.12 * body_scale, 0.54 * body_scale, (0.92, 0.16, 0.90), 0.72)

    total_h = leg_h + body_h
    if selected:
        draw_wire_box(0.0, total_h * 0.5, 0.0, 1.16 * body_scale, total_h + 0.18 * body_scale, 1.10 * body_scale, (0.1, 1.0, 0.1), 2.2)
    if debug_hitbox:
        draw_wire_box(0.0, total_h * 0.5, 0.0, 1.04 * body_scale, total_h, 0.98 * body_scale, (1.0, 0.05, 0.05), 1.5)
    glPopMatrix()


def draw_box_alpha(cx, cy, cz, sx, sy, sz, color, alpha=0.6):
    """Caja translúcida simple para materiales gelatinosos."""
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    x0, x1 = cx - hx, cx + hx
    y0, y1 = cy - hy, cy + hy
    z0, z1 = cz - hz, cz + hz
    top = _shade(color, 1.12)
    front = _shade(color, 1.00)
    side = _shade(color, 0.82)
    back = _shade(color, 0.72)
    bottom = _shade(color, 0.58)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    glBegin(GL_QUADS)
    glColor4f(front[0], front[1], front[2], alpha);  glVertex3f(x0,y0,z1); glVertex3f(x1,y0,z1); glVertex3f(x1,y1,z1); glVertex3f(x0,y1,z1)
    glColor4f(back[0], back[1], back[2], alpha);   glVertex3f(x1,y0,z0); glVertex3f(x0,y0,z0); glVertex3f(x0,y1,z0); glVertex3f(x1,y1,z0)
    glColor4f(side[0], side[1], side[2], alpha);   glVertex3f(x0,y0,z0); glVertex3f(x0,y0,z1); glVertex3f(x0,y1,z1); glVertex3f(x0,y1,z0)
    glColor4f(side[0], side[1], side[2], alpha);   glVertex3f(x1,y0,z1); glVertex3f(x1,y0,z0); glVertex3f(x1,y1,z0); glVertex3f(x1,y1,z1)
    glColor4f(top[0], top[1], top[2], alpha);    glVertex3f(x0,y1,z1); glVertex3f(x1,y1,z1); glVertex3f(x1,y1,z0); glVertex3f(x0,y1,z0)
    glColor4f(bottom[0], bottom[1], bottom[2], alpha); glVertex3f(x0,y0,z0); glVertex3f(x1,y0,z0); glVertex3f(x1,y0,z1); glVertex3f(x0,y0,z1)
    glEnd()
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)


def render_slime_puddle(x, y, z, color=(0.9,0.1,0.12), alpha=0.4, scale=1.0):
    glPushMatrix()
    glTranslatef(x, y + 0.075, z)
    draw_box_alpha(0.0, 0.0, 0.0, 1.02 * scale, 0.055, 0.92 * scale, color, alpha)
    draw_box_alpha(0.16 * scale, 0.012, -0.10 * scale, 0.45 * scale, 0.035, 0.32 * scale, _shade(color, 1.08), alpha * 0.8)
    draw_box_alpha(-0.22 * scale, 0.018, 0.13 * scale, 0.30 * scale, 0.030, 0.22 * scale, _shade(color, 1.18), alpha * 0.45)
    glPopMatrix()
