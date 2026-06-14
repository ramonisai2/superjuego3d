"""Puente temporal para llamadas OpenGL legacy.

Stage31 Pre-S:
- No elimina OpenGL todavía.
- Evita que main.py tenga llamadas OpenGL sueltas.
- Centraliza helpers que Vulkan reemplazará por operaciones del backend.
"""

from OpenGL.GL import (
    glPushMatrix, glPopMatrix, glTranslatef,
    glGetDoublev, glGetIntegerv,
    glFogf,
    glMatrixMode, glLoadIdentity, glOrtho,
    glDisable, glEnable, glDepthMask, glBegin, glEnd, glColor4f, glVertex2f,
    glBlendFunc,
    GL_MODELVIEW_MATRIX, GL_PROJECTION_MATRIX, GL_VIEWPORT,
    GL_FOG_START, GL_FOG_END,
    GL_PROJECTION, GL_MODELVIEW, GL_DEPTH_TEST, GL_FOG, GL_BLEND,
    GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_QUADS,
    glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
)
from OpenGL.GLU import gluProject


def set_fog_range(start=60.0, end=180.0):
    """Configura rango de niebla legacy. Vulkan lo hará por uniform/material."""
    glFogf(GL_FOG_START, float(start))
    glFogf(GL_FOG_END, float(end))


def draw_skybox_at_camera(env_module, px, py, pz, size=300.0):
    """Dibuja skybox centrado en cámara sin exponer glPush/glTranslate a main.py."""
    glPushMatrix()
    glTranslatef(float(px), float(py), float(pz))
    env_module.draw_procedural_skybox(size=float(size))
    glPopMatrix()


def world_to_screen_legacy(x, y, z):
    """Proyección legacy para labels/UI 2D sobre objetos 3D."""
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)
    try:
        wx, wy, wz = gluProject(x, y, z, modelview, projection, viewport)
    except Exception:
        return None
    screen_x = int(wx)
    screen_y = int(viewport[3] - wy)
    if wz < 0 or wz > 1:
        return None
    return screen_x, screen_y


def clear_color_depth():
    """Limpia pantalla/profundidad desde un punto legacy centralizado."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


def draw_world_tint_overlay(width, height, color):
    """Capa atmosferica barata para que dia/noche afecte la escena 3D."""
    if not color or len(color) < 4:
        return
    alpha = max(0.0, min(0.75, float(color[3])))
    if alpha <= 0.005:
        return
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, float(width), float(height), 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_FOG)
    glDepthMask(False)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(float(color[0]), float(color[1]), float(color[2]), alpha)
    glBegin(GL_QUADS)
    glVertex2f(0.0, 0.0)
    glVertex2f(float(width), 0.0)
    glVertex2f(float(width), float(height))
    glVertex2f(0.0, float(height))
    glEnd()
    glDepthMask(True)
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
