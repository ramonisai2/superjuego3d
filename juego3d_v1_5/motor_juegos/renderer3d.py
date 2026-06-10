from OpenGL.GL import *
from OpenGL.GLU import *

def setup_perspective(fov=45, aspect=800/600, near=0.1, far=100.0):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fov, aspect, near, far)
    glMatrixMode(GL_MODELVIEW)

def setup_camera(pos_x, pos_y, pos_z, look_x, look_y, look_z):
    glLoadIdentity()
    gluLookAt(pos_x, pos_y, pos_z, look_x, look_y, look_z, 0, 1, 0)

def setup_fog(color_horizonte):
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogfv(GL_FOG_COLOR, color_horizonte + [1.0])
    glHint(GL_FOG_HINT, GL_NICEST)

def disable_fog(): glDisable(GL_FOG)

def draw_bullet_cube(bx, by, bz, size=0.25):
    """Dibuja un proyectil 3D de color naranja fluorescente."""
    h = size / 2.0
    v = [[bx-h, by-h, bz-h], [bx+h, by-h, bz-h], [bx+h, by+h, bz-h], [bx-h, by+h, bz-h], [bx-h, by-h, bz+h], [bx+h, by-h, bz+h], [bx+h, by+h, bz+h], [bx-h, by+h, bz+h]]
    glBegin(GL_QUADS)
    glColor3f(1.0, 0.4, 0.0) # Naranja brillante
    glVertex3fv(v[3]); glVertex3fv(v[2]); glVertex3fv(v[6]); glVertex3fv(v[7])
    glVertex3fv(v[0]); glVertex3fv(v[1]); glVertex3fv(v[2]); glVertex3fv(v[3])
    glVertex3fv(v[5]); glVertex3fv(v[4]); glVertex3fv(v[7]); glVertex3fv(v[6])
    glVertex3fv(v[4]); glVertex3fv(v[0]); glVertex3fv(v[3]); glVertex3fv(v[7])
    glVertex3fv(v[1]); glVertex3fv(v[5]); glVertex3fv(v[6]); glVertex3fv(v[2])
    glEnd()
