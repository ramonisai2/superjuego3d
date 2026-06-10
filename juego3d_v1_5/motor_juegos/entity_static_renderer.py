"""Renderer experimental de entidades StaticMesh.

Stage31 Pre-R:
- Dibuja EntityMeshBufferData usando OpenGL inmediato como prueba visual.
- No reemplaza aun el render artistico principal por defecto.
- Sirve para comprobar que StaticMesh + InstanceData + buffers neutrales ya
  pueden producir una entidad visible sin llamar a enemy.render()/npc.render().

Activacion:
- variable de entorno: JUEGO_STATIC_ENTITY_RENDER=1
- o cambiar use_static_entity_renderer=True en OpenGLRenderBackend.
"""

from OpenGL.GL import *


def _color_tuple(color, alpha=1.0):
    if len(color) >= 4:
        return float(color[0]), float(color[1]), float(color[2]), float(color[3])
    return float(color[0]), float(color[1]), float(color[2]), float(alpha)


def draw_entity_mesh_buffer(buffer_data, instance):
    """Dibuja un buffer neutral de entidad con transform de instancia.

    Esta ruta aun no es Vulkan: es un renderer de prueba que usa los mismos datos
    neutrales que luego Vulkan convertira a VkBuffer.
    """
    if buffer_data is None or instance is None:
        return False

    x, y, z = instance.position
    yaw = float(getattr(instance, "yaw", 0.0))
    scale = float(getattr(instance, "scale", 1.0) or 1.0)

    glPushMatrix()
    glTranslatef(float(x), float(y), float(z))
    glRotatef(yaw, 0, 1, 0)
    glScalef(scale, scale, scale)

    any_drawn = False
    for batch in getattr(buffer_data, "batches", {}).values():
        vertices = getattr(batch, "vertices", []) or []
        colors = getattr(batch, "colors", []) or []
        if not vertices:
            continue

        blend = bool(getattr(batch, "blend", False)) or float(getattr(batch, "alpha", 1.0)) < 0.999
        alpha = float(getattr(batch, "alpha", 1.0))
        if blend:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            if not bool(getattr(batch, "depth_write", True)):
                glDepthMask(GL_FALSE)

        primitive = getattr(batch, "primitive", "quads")
        glBegin(GL_TRIANGLES if primitive == "triangles" else GL_QUADS)
        for i, v in enumerate(vertices):
            col = colors[i] if i < len(colors) else (1.0, 1.0, 1.0)
            r, g, b, a = _color_tuple(col, alpha)
            if blend:
                glColor4f(r, g, b, a)
            else:
                glColor3f(r, g, b)
            glVertex3f(float(v[0]), float(v[1]), float(v[2]))
        glEnd()
        any_drawn = True

        if blend:
            glDepthMask(GL_TRUE)
            glDisable(GL_BLEND)

    glPopMatrix()
    return any_drawn
