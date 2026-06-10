import pygame
from pygame.locals import *
from OpenGL.GL import *
from PIL import Image, ImageDraw
from motor_juegos import GameEngine, r3d, r2d
import game.voxel_models as voxel_models
from game.voxel_models import (
    render_player_avatar,
    draw_textured_box,
    draw_minecraft_head,
    draw_wire_box,
    PLAYER_SKIN_RECTS,
    _load_player_skin_texture,
    _rect_uv,
)

VARIANTS = [
    ("default", None),
    ("flip_lr", {"left": "h", "right": "h"}),
    ("flip_fb", {"front": "h", "back": "h"}),
    ("flip_lr_fb", {"left": "h", "right": "h", "front": "h", "back": "h"}),
    ("flip_topbot", {"top": "v", "bottom": "v"}),
    ("rot_cw", {"front": "r", "back": "r", "left": "r", "right": "r", "top": "r", "bottom": "r"}),
    ("rot_ccw", {"front": "l", "back": "l", "left": "l", "right": "l", "top": "l", "bottom": "l"}),
]

LABEL_COLOR = (245, 245, 210)

engine = GameEngine(1280, 720, title="Skin Variant Preview")

_DEBUG_SKIN_TEX_ID = None

DEBUG_HEAD_COLORS = {
    "top": (255, 0, 0, 128),
    "bottom": (0, 255, 0, 128),
    "front": (0, 0, 255, 128),
    "back": (255, 255, 0, 128),
    "left": (0, 255, 255, 128),
    "right": (255, 0, 255, 128),
}


def _load_debug_skin_texture():
    global _DEBUG_SKIN_TEX_ID
    if _DEBUG_SKIN_TEX_ID is not None:
        return _DEBUG_SKIN_TEX_ID
    skin_path = voxel_models._find_player_skin_path()
    if not skin_path:
        return None
    image = Image.open(skin_path).convert("RGBA")
    draw = ImageDraw.Draw(image)
    for face, rect in voxel_models.PLAYER_SKIN_RECTS["head"].items():
        draw.rectangle(rect, outline=(255, 255, 255, 255), width=2)
        draw.rectangle(rect, fill=DEBUG_HEAD_COLORS[face])
        draw.text((rect[0] + 2, rect[1] + 2), face[:2].upper(), fill=(255, 255, 255, 255))
    raw_data = image.tobytes("raw", "RGBA")
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, raw_data)
    _DEBUG_SKIN_TEX_ID = tex_id
    return tex_id

# Patch module loader so all head renders in this debug can use the overlay texture.
voxel_models._load_player_skin_texture = _load_debug_skin_texture


def draw_ground():
    glDisable(GL_TEXTURE_2D)
    glColor3f(0.16, 0.20, 0.14)
    glBegin(GL_QUADS)
    glVertex3f(-12.0, 0.0, -12.0)
    glVertex3f( 12.0, 0.0, -12.0)
    glVertex3f( 12.0, 0.0,  12.0)
    glVertex3f(-12.0, 0.0,  12.0)
    glEnd()
    glColor3f(1.0, 1.0, 1.0)


def draw_labels():
    r2d.begin_2d(engine.width, engine.height)
    for idx, (name, _) in enumerate(VARIANTS):
        x = int(48 + idx * 242)
        y = engine.height - 42
        r2d.draw_text_2d(f"{idx+1}: {name}", x, y, LABEL_COLOR)
    r2d.draw_text_2d("Esc para salir", 16, 18, LABEL_COLOR)
    r2d.end_2d()


def update(dt):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            engine.is_running = False
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            engine.is_running = False


def draw_rotated_head(x, y, z, uv_flip=None, angle=45.0):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle, 0.0, 1.0, 0.0)
    draw_textured_box(
        0.0, 0.0, 0.0,
        0.86, 0.98, 0.86,
        PLAYER_SKIN_RECTS["head"],
        uv_flip=uv_flip,
    )
    draw_wire_box(0.0, 0.0, 0.0, 0.86, 0.98, 0.86, color=(1.0, 1.0, 1.0), line_width=1.0)
    glPopMatrix()


def draw_textured_quad(rect, x, y, z, width, height, rotation_y=0.0):
    tex_id = _load_player_skin_texture()
    if tex_id is None:
        return
    u0, v0, u1, v1 = _rect_uv(rect)
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation_y, 0.0, 1.0, 0.0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    hw = width * 0.5
    hh = height * 0.5
    glBegin(GL_QUADS)
    glTexCoord2f(u0, v0); glVertex3f(-hw, -hh, 0.0)
    glTexCoord2f(u1, v0); glVertex3f( hw, -hh, 0.0)
    glTexCoord2f(u1, v1); glVertex3f( hw,  hh, 0.0)
    glTexCoord2f(u0, v1); glVertex3f(-hw,  hh, 0.0)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(1.0)
    glBegin(GL_LINE_LOOP)
    glVertex3f(-hw, -hh, 0.0)
    glVertex3f( hw, -hh, 0.0)
    glVertex3f( hw,  hh, 0.0)
    glVertex3f(-hw,  hh, 0.0)
    glEnd()
    glPopMatrix()


def draw_face_map():
    faces = ["front", "back", "left", "right", "top", "bottom"]
    spacing_x = 2.3
    spacing_y = 1.7
    base_x = -4.6
    base_y = 5.0
    for idx, face in enumerate(faces):
        col = idx % 3
        row = idx // 3
        x = base_x + col * spacing_x
        y = base_y - row * spacing_y
        draw_textured_quad(
            PLAYER_SKIN_RECTS["head"][face],
            x, y, -0.8,
            1.8, 1.8,
            rotation_y=0.0,
        )


def draw_face_map_labels():
    faces = ["front", "back", "left", "right", "top", "bottom"]
    spacing_x = 2.3
    spacing_y = 1.7
    base_x = -4.6
    base_y = 5.0
    r2d.begin_2d(engine.width, engine.height)
    for idx, face in enumerate(faces):
        col = idx % 3
        row = idx // 3
        x = int((base_x + col * spacing_x + 0.9) / 9.0 * engine.width + 24)
        y = int((base_y - row * spacing_y + 2.5) / 7.2 * engine.height)
        r2d.draw_text_2d(f"head {face}", x, y, LABEL_COLOR)
    r2d.end_2d()


BODY_PART_DEBUG = [
    ("torso", 0.0, 1.1, -1.8, 1.4, 1.0, 0.7),
    ("left_arm", -1.2, 1.1, 0.0, 0.5, 1.4, 0.5),
    ("right_arm", 1.2, 1.1, 0.0, 0.5, 1.4, 0.5),
    ("left_leg", -0.6, -0.6, 0.0, 0.5, 1.6, 0.5),
    ("right_leg", 0.6, -0.6, 0.0, 0.5, 1.6, 0.5),
]


def draw_body_part_cubes():
    for part_name, x, y, z, sx, sy, sz in BODY_PART_DEBUG:
        draw_textured_box(x, y, z, sx, sy, sz, PLAYER_SKIN_RECTS[part_name])
        draw_wire_box(x, y, z, sx, sy, sz, color=(1.0, 1.0, 1.0), line_width=1.0)
        # draw label in screen space
        r2d.begin_2d(engine.width, engine.height)
        screen_x = int((x + 5.0) / 10.0 * engine.width)
        screen_y = int(engine.height * 0.85 if y > 0 else engine.height * 0.92)
        r2d.draw_text_2d(part_name, screen_x, screen_y, LABEL_COLOR)
        r2d.end_2d()


def render_3d():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    r3d.setup_perspective(50.0, engine.width / engine.height, 0.1, 80.0)
    r3d.setup_camera(0.0, 2.7, 14.0, 0.0, 1.4, 0.0)
    draw_ground()

    # Full avatars for context.
    for idx, (_, uv_flip) in enumerate(VARIANTS):
        x = (idx - (len(VARIANTS) - 1) / 2.0) * 3.0
        render_player_avatar(
            x, 0.0, 0.0,
            yaw=0.0,
            selected=False,
            walk_phase=0.0,
            move_amount=0.0,
            swimming=False,
            head_uv_flip=None if uv_flip == "mine" else uv_flip,
        )

    # Bare heads for clearer comparison from the front.
    for idx, (_, uv_flip) in enumerate(VARIANTS):
        x = (idx - (len(VARIANTS) - 1) / 2.0) * 3.0
        head_y = 3.9
        if uv_flip is voxel_models._MINECRAFT_HEAD_UV_FLIP:
            draw_minecraft_head(
                x, head_y, 0.0,
                0.86, 0.98, 0.86,
                PLAYER_SKIN_RECTS["head"],
            )
        else:
            draw_rotated_head(x, head_y, 0.0, uv_flip=uv_flip, angle=0.0)

    # Head-atlas faces for direct texture inspection.
    draw_face_map()
    draw_face_map_labels()

    # Body-part cubes for torso/limbs texture check.
    draw_body_part_cubes()


def render_2d():
    draw_labels()


if __name__ == "__main__":
    glClearColor(0.08, 0.10, 0.14, 1.0)
    engine.run(update, render_2d, render_3d)
