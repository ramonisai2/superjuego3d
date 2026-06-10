from OpenGL.GL import *
import pygame

_font = None

def begin_2d(width, height):
    """Cambia la matriz a modo ortográfico plano y limpia los estados 3D."""
    global _font
    if _font is None:
        pygame.font.init()
        # Usamos la fuente por defecto para máxima compatibilidad
        _font = pygame.font.Font(None, 24)

    # --- RESETEO ABSOLUTO DE ESTADOS GRÁFICOS INTERNOS ---
    glDisable(GL_DEPTH_TEST) # Apagar profundidad
    glDisable(GL_CULL_FACE)   # Evita que el texto se invierta/desaparezca por culling
    glDisable(GL_LIGHTING)   # Apagar luces
    glBindTexture(GL_TEXTURE_2D, 0) # Desvincular cualquier textura del terreno anterior
    # ------------------------------------------------------

    # Guardar y limpiar Matriz de Proyección
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity() # <- Fuerza el borrado de la perspectiva 3D anterior
    glOrtho(0, width, height, 0, -1, 1)
    
    # Guardar y limpiar Matriz de Vista de Modelo
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity() # <- Inicializa el lienzo plano en coordenadas (0,0) limpias

def end_2d():
    """Restaura las matrices y devuelve el control al motor 3D."""
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    
    # Reactivar la profundidad para que el mundo 3D funcione en el próximo cuadro
    glEnable(GL_DEPTH_TEST)

def draw_rect_2d(x, y, w, h, color=(1, 1, 1)):
    """Dibuja formas planas en la interfaz (HUD)."""
    glDisable(GL_TEXTURE_2D) # Desactivar texturas para pintar colores sólidos limpios
    has_alpha = len(color) >= 4
    if has_alpha:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(color[0], color[1], color[2], color[3])
    else:
        glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()
    if has_alpha:
        glDisable(GL_BLEND)

def draw_text_2d(text, x, y, color=(255, 255, 255)):
    """Convierte las letras en una textura temporal nítida y la estampa en primer plano."""
    global _font
    if _font is None:
        return
        
    # 1. Renderizar el texto en Pygame
    text_surface = _font.render(text, True, color)
    width, height = text_surface.get_size()
    text_data = pygame.image.tostring(text_surface, "RGBA", False)
    
    # 2. Registrar la textura de la tipografía en la GPU
    text_texture = glGenTextures(1)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, text_texture)
    
    # Ajustes obligatorios de nitidez de píxeles
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    # 3. Configurar mezcla alfa para recortar las letras perfectamente
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Forzar color blanco neutro para que las letras no se tiñan del verde del suelo
    glColor4f(1.0, 1.0, 1.0, 1.0)
    
    # 4. Dibujar el cuadro ortográfico con el texto mapeado
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x, y)
    glTexCoord2f(1, 0); glVertex2f(x + width, y)
    glTexCoord2f(1, 1); glVertex2f(x + width, y + height)
    glTexCoord2f(0, 1); glVertex2f(x, y + height)
    glEnd()
    
    # 5. Liberar la textura inmediatamente de la memoria de video
    glDisable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)
    glDeleteTextures([text_texture])
