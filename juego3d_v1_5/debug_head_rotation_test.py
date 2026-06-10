import os
import pygame
from pygame.locals import *
from OpenGL.GL import *
from motor_juegos import GameEngine, r3d, r2d
import game.voxel_models as voxel_models

engine = GameEngine(1280, 720, title="Head Rotation Test")

VARIANTS = [
    ("default", None),
    ("rot_cw", {"front":"r", "back":"r", "left":"r", "right":"r", "top":"r", "bottom":"r"}),
    ("rot_ccw", {"front":"l", "back":"l", "left":"l", "right":"l", "top":"l", "bottom":"l"}),
    ("rot_180", {"front":"180", "back":"180", "left":"180", "right":"180", "top":"180", "bottom":"180"}),
    ("flip_lr", {"left":"h", "right":"h"}),
    ("flip_fb", {"front":"h", "back":"h"}),
]

LABEL_COLOR = (245, 245, 210)

_TEXTURE_ID = None
_TEXTURE_SIZE = (1, 1)


def load_atlas_texture():
    global _TEXTURE_ID, _TEXTURE_SIZE
    if _TEXTURE_ID is not None:
        return _TEXTURE_ID
    path = voxel_models._find_player_skin_path()
    if not path:
        return None
    surface = pygame.image.load(path).convert_alpha()
    width, height = surface.get_width(), surface.get_height()
    data = pygame.image.tostring(surface, "RGBA", True)
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    _TEXTURE_ID = tex_id
    _TEXTURE_SIZE = (width, height)
    return tex_id


def rect_uv(rect):
    x0, y0, x1, y1 = rect
    w, h = _TEXTURE_SIZE
    pad = 1.0
    u0 = (x0 + pad) / w
    u1 = (x1 - pad) / w
    v0 = 1.0 - (y1 - pad) / h
    v1 = 1.0 - (y0 + pad) / h
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def rotate_face_uvs(uvs, mode):
    if mode == "r":
        return [uvs[3], uvs[0], uvs[1], uvs[2]]
    if mode == "l":
        return [uvs[1], uvs[2], uvs[3], uvs[0]]
    if mode == "180":
        return [uvs[2], uvs[3], uvs[0], uvs[1]]
    return uvs


def draw_textured_cube(cx, cy, cz, sx, sy, sz, face_rects, face_rotations=None):
    tex_id = load_atlas_texture()
    if tex_id is None:
        return
    if face_rotations is None:
        face_rotations = {}
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    x0, x1 = cx - hx, cx + hx
    y0, y1 = cy - hy, cy + hy
    z0, z1 = cz - hz, cz + hz

    def quad(face, p1, p2, p3, p4):
        uvs = rect_uv(face_rects[face])
        uvs = rotate_face_uvs(uvs, face_rotations.get(face))
        glTexCoord2f(*uvs[0]); glVertex3f(*p1)
        glTexCoord2f(*uvs[1]); glVertex3f(*p2)
        glTexCoord2f(*uvs[2]); glVertex3f(*p3)
        glTexCoord2f(*uvs[3]); glVertex3f(*p4)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    quad("front",  (x0,y0,z1), (x1,y0,z1), (x1,y1,z1), (x0,y1,z1))
    quad("back",   (x1,y0,z0), (x0,y0,z0), (x0,y1,z0), (x1,y1,z0))
    quad("left",   (x0,y0,z0), (x0,y0,z1), (x0,y1,z1), (x0,y1,z0))
    quad("right",  (x1,y0,z1), (x1,y0,z0), (x1,y1,z0), (x1,y1,z1))
    quad("top",    (x0,y1,z1), (x1,y1,z1), (x1,y1,z0), (x0,y1,z0))
    quad("bottom", (x0,y0,z0), (x1,y0,z0), (x1,y0,z1), (x0,y0,z1))
    glEnd()
    glDisable(GL_TEXTURE_2D)


def draw_textured_quad(rect, cx, cy, cz, width, height):
    tex_id = load_atlas_texture()
    if tex_id is None:
        return
    uvs = rect_uv(rect)
    hx = width / 2.0
    hy = height / 2.0
    x0 = cx - hx
    x1 = cx + hx
    y0 = cy - hy
    y1 = cy + hy
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    glTexCoord2f(*uvs[0]); glVertex3f(x0, y0, cz)
    glTexCoord2f(*uvs[1]); glVertex3f(x1, y0, cz)
    glTexCoord2f(*uvs[2]); glVertex3f(x1, y1, cz)
    glTexCoord2f(*uvs[3]); glVertex3f(x0, y1, cz)
    glEnd()
    glDisable(GL_TEXTURE_2D)


def draw_ground():
    glDisable(GL_TEXTURE_2D)
    glColor3f(0.18, 0.22, 0.14)
    glBegin(GL_QUADS)
    glVertex3f(-10, 0, -10)
    glVertex3f(10, 0, -10)
    glVertex3f(10, 0, 10)
    glVertex3f(-10, 0, 10)
    glEnd()
    glColor3f(1.0, 1.0, 1.0)


def draw_labels():
    r2d.begin_2d(engine.width, engine.height)
    for idx, (name, _) in enumerate(VARIANTS):
        x = 54 + idx * 200
        y = engine.height - 44
        r2d.draw_text_2d(f"{idx+1}: {name}", x, y, LABEL_COLOR)
    r2d.draw_text_2d("Esc para salir", 12, 16, LABEL_COLOR)
    r2d.end_2d()


def draw_reference_faces():
    faces = ["front", "back", "left", "right", "top", "bottom"]
    for idx, face in enumerate(faces):
        uv = rect_uv(voxel_models.PLAYER_SKIN_RECTS["head"][face])
        x = -5.0 + (idx % 3) * 3.0
        y = 5.0 - (idx // 3) * 2.5
        draw_textured_quad(voxel_models.PLAYER_SKIN_RECTS["head"][face], x, y, -0.9, 1.4, 1.4)


def update(dt):
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            engine.is_running = False


def render_3d():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    r3d.setup_perspective(55.0, engine.width / engine.height, 0.1, 80.0)
    r3d.setup_camera(0.0, 2.5, 14.0, 0.0, 1.2, 0.0)
    draw_ground()

    for idx, (_, face_rotations) in enumerate(VARIANTS):
        x = (idx - (len(VARIANTS) - 1) / 2.0) * 3.2
        draw_textured_cube(
            x, 3.6, 0.0,
            0.9, 1.0, 0.9,
            voxel_models.PLAYER_SKIN_RECTS["head"],
            face_rotations,
        )

    draw_reference_faces()


def render_2d():
    draw_labels()


if __name__ == "__main__":
    glClearColor(0.06, 0.08, 0.14, 1.0)
    engine.run(update, render_2d, render_3d)
