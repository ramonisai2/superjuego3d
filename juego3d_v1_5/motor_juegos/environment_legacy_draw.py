try:
    from OpenGL.GL import *
except ModuleNotFoundError:
    # Allows importing terrain helpers without OpenGL during headless audits.
    pass
import math


def draw_optimized_rock(bx, base_y, bz, sx, sy, sz, col):
    c_top = [min(1, c * 1.12) for c in col]
    c_s1 = [c * 0.92 for c in col]
    c_s2 = [c * 0.78 for c in col]
    c_s3 = [c * 0.68 for c in col]
    hx, hz = sx / 2, sz / 2

    seed = math.sin(bx * 12.9898 + bz * 78.233) * 43758.5453
    frac = seed - math.floor(seed)
    frac2 = (seed * 1.371) - math.floor(seed * 1.371)
    frac3 = (seed * 1.917) - math.floor(seed * 1.917)
    frac4 = (seed * 2.231) - math.floor(seed * 2.231)
    inset = 0.10 + 0.10 * frac
    lift0 = sy * (0.90 + 0.10 * frac2)
    lift1 = sy * (0.88 + 0.14 * frac3)
    lift2 = sy * (0.92 + 0.08 * frac4)
    lift3 = sy * (0.86 + 0.12 * frac)

    b0 = [bx - hx, base_y, bz - hz]
    b1 = [bx + hx, base_y, bz - hz]
    b2 = [bx + hx, base_y, bz + hz]
    b3 = [bx - hx, base_y, bz + hz]

    t0 = [bx - hx * (1.0 - inset), base_y + lift0, bz - hz * (1.0 - 0.08 - frac * 0.04)]
    t1 = [bx + hx * (1.0 - inset * 0.8), base_y + lift1, bz - hz * (1.0 - inset)]
    t2 = [bx + hx * (1.0 - 0.06 - frac2 * 0.05), base_y + lift2, bz + hz * (1.0 - inset * 0.9)]
    t3 = [bx - hx * (1.0 - inset), base_y + lift3, bz + hz * (1.0 - 0.05 - frac3 * 0.05)]

    peak = [bx + (frac - 0.5) * hx * 0.25, base_y + sy * (1.02 + 0.08 * frac2), bz + (frac3 - 0.5) * hz * 0.25]

    glBegin(GL_QUADS)
    glColor3fv(c_s1); glVertex3fv(b0); glVertex3fv(b1); glVertex3fv(t1); glVertex3fv(t0)
    glColor3fv(c_s2); glVertex3fv(b1); glVertex3fv(b2); glVertex3fv(t2); glVertex3fv(t1)
    glColor3fv(c_s3); glVertex3fv(b2); glVertex3fv(b3); glVertex3fv(t3); glVertex3fv(t2)
    glColor3fv(c_s2); glVertex3fv(b3); glVertex3fv(b0); glVertex3fv(t0); glVertex3fv(t3)
    glEnd()

    glBegin(GL_TRIANGLES)
    glColor3fv(c_top); glVertex3fv(t0); glVertex3fv(t1); glVertex3fv(peak)
    glColor3fv(c_top); glVertex3fv(t1); glVertex3fv(t2); glVertex3fv(peak)
    glColor3fv(c_top); glVertex3fv(t2); glVertex3fv(t3); glVertex3fv(peak)
    glColor3fv(c_top); glVertex3fv(t3); glVertex3fv(t0); glVertex3fv(peak)
    glEnd()


def _draw_ground_shadow(cx, y, cz, sx, sz, alpha=0.10):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    glColor4f(0.02, 0.03, 0.02, alpha)
    glBegin(GL_QUADS)
    glVertex3f(cx - sx * 0.5, y + 0.01, cz - sz * 0.5)
    glVertex3f(cx + sx * 0.5, y + 0.01, cz - sz * 0.5)
    glVertex3f(cx + sx * 0.5, y + 0.01, cz + sz * 0.5)
    glVertex3f(cx - sx * 0.5, y + 0.01, cz + sz * 0.5)
    glEnd()
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)


def _draw_round_trunk(cx, base_y, cz, radius, height, col, segments=5):
    top_col = [min(1.0, c * 1.10) for c in col]
    for i in range(segments):
        a0 = (i / segments) * math.pi * 2.0
        a1 = ((i + 1) / segments) * math.pi * 2.0
        x0 = cx + math.cos(a0) * radius
        z0 = cz + math.sin(a0) * radius
        x1 = cx + math.cos(a1) * radius
        z1 = cz + math.sin(a1) * radius
        shade = 0.78 + 0.18 * ((i % 2) / 1.0)
        side_col = [max(0.0, min(1.0, c * shade)) for c in col]
        glBegin(GL_QUADS)
        glColor3fv(side_col)
        glVertex3f(x0, base_y, z0)
        glVertex3f(x1, base_y, z1)
        glVertex3f(x1, base_y + height, z1)
        glVertex3f(x0, base_y + height, z0)
        glEnd()

    peak_y = base_y + height
    glBegin(GL_TRIANGLES)
    for i in range(segments):
        a0 = (i / segments) * math.pi * 2.0
        a1 = ((i + 1) / segments) * math.pi * 2.0
        x0 = cx + math.cos(a0) * radius
        z0 = cz + math.sin(a0) * radius
        x1 = cx + math.cos(a1) * radius
        z1 = cz + math.sin(a1) * radius
        glColor3fv(top_col)
        glVertex3f(cx, peak_y + radius * 0.06, cz)
        glVertex3f(x0, peak_y, z0)
        glVertex3f(x1, peak_y, z1)
    glEnd()


def draw_decorations(d_type, dx, dy, dz, variant):
    if d_type in ("arbol_roble", "arbol_abedul"):
        d_type = "arbol_bosque"
    elif d_type == "arbol_pino":
        d_type = "arbol_seco"
    elif d_type in ("arbol_sauce", "arbol_cipres"):
        d_type = "arbol_pantano"

    if d_type == "hongo":
        draw_optimized_rock(dx, dy, dz, 0.08, 0.16, 0.08, [0.9, 0.9, 0.9])
        draw_optimized_rock(dx, dy + 0.1, dz, 0.24, 0.08, 0.24, [0.85, 0.15, 0.15])
    elif d_type == "cactus":
        draw_optimized_rock(dx, dy, dz, 0.22, 1.6, 0.22, [0.13, 0.48, 0.16])
        draw_optimized_rock(dx + 0.22, dy + 0.65, dz, 0.18, 0.55, 0.18, [0.12, 0.42, 0.14])
        draw_optimized_rock(dx - 0.20, dy + 0.85, dz, 0.16, 0.45, 0.16, [0.12, 0.42, 0.14])
    elif d_type == "cristal":
        draw_optimized_rock(dx, dy, dz, 0.22, 0.7, 0.22, [0, 0.9, 0.9])
    elif d_type == "flores":
        draw_optimized_rock(dx, dy, dz, 0.04, 0.3, 0.04, [0.2, 0.5, 0.2])
        col_f = [0.85, 0.15, 0.45] if variant == "rojo" else [0.9, 0.8, 0.1]
        draw_optimized_rock(dx, dy + 0.15, dz, 0.14, 0.06, 0.14, col_f)
    elif d_type == "arbusto_verde":
        draw_optimized_rock(dx, dy, dz, 0.55, 0.36, 0.55, [0.12, 0.44, 0.14])
        draw_optimized_rock(dx + 0.22, dy + 0.05, dz - 0.10, 0.35, 0.28, 0.35, [0.10, 0.38, 0.12])
    elif d_type == "arbusto_seco":
        draw_optimized_rock(dx, dy, dz, 0.45, 0.35, 0.45, [0.46, 0.38, 0.26])
        draw_optimized_rock(dx - 0.18, dy + 0.06, dz + 0.12, 0.28, 0.28, 0.28, [0.38, 0.30, 0.18])
    elif d_type == "junco":
        draw_optimized_rock(dx, dy, dz, 0.08, 0.78, 0.08, [0.34, 0.48, 0.18])
        draw_optimized_rock(dx + 0.10, dy, dz - 0.06, 0.06, 0.58, 0.06, [0.42, 0.55, 0.20])
    elif d_type == "helecho":
        draw_optimized_rock(dx, dy, dz, 0.55, 0.28, 0.55, [0.10, 0.42, 0.16])
        draw_optimized_rock(dx - 0.12, dy + 0.04, dz + 0.08, 0.35, 0.22, 0.35, [0.14, 0.50, 0.18])
    elif d_type == "hierba_alta":
        draw_optimized_rock(dx, dy, dz, 0.12, 0.62, 0.12, [0.22, 0.52, 0.20])
    elif d_type == "flor_azul":
        draw_optimized_rock(dx, dy, dz, 0.05, 0.32, 0.05, [0.16, 0.42, 0.18])
        draw_optimized_rock(dx, dy + 0.20, dz, 0.15, 0.08, 0.15, [0.22, 0.36, 0.92])
    elif d_type == "maleza_oscura":
        draw_optimized_rock(dx, dy, dz, 0.55, 0.34, 0.55, [0.04, 0.18, 0.08])
        draw_optimized_rock(dx + 0.16, dy + 0.04, dz - 0.10, 0.34, 0.24, 0.34, [0.06, 0.24, 0.09])
    elif d_type == "arbol_bosque":
        _draw_ground_shadow(dx, dy, dz, 2.20, 2.05, 0.13)
        trunk = [0.36, 0.23, 0.13]
        leaf_main = [0.10, 0.38, 0.13]
        leaf_dark = [0.07, 0.30, 0.09]
        leaf_light = [0.13, 0.45, 0.16]
        alto = 3.10 if variant == "alto" else 2.65
        _draw_round_trunk(dx, dy, dz, 0.30, alto, trunk, segments=5)
        top = dy + alto
        draw_optimized_rock(dx, top - 0.16, dz, 0.86, 0.66, 0.86, leaf_dark)
        draw_optimized_rock(dx, top + 0.28, dz, 1.34, 0.82, 1.24, leaf_main)
        draw_optimized_rock(dx + 0.58, top + 0.18, dz + 0.04, 0.92, 0.66, 0.88, leaf_dark)
        draw_optimized_rock(dx - 0.56, top + 0.16, dz - 0.05, 0.90, 0.64, 0.86, leaf_dark)
        draw_optimized_rock(dx + 0.05, top + 0.15, dz + 0.58, 0.92, 0.66, 0.86, leaf_main)
        draw_optimized_rock(dx - 0.05, top + 0.13, dz - 0.58, 0.90, 0.62, 0.84, leaf_main)
        draw_optimized_rock(dx, top + 0.78, dz, 0.84, 0.56, 0.80, leaf_light)
        draw_optimized_rock(dx + 0.30, top + 0.68, dz - 0.28, 0.62, 0.42, 0.58, leaf_light)
    elif d_type == "arbol_pantano":
        _draw_ground_shadow(dx, dy, dz, 2.00, 1.95, 0.14)
        trunk = [0.22, 0.16, 0.10]
        leaf_main = [0.12, 0.28, 0.12]
        leaf_dark = [0.08, 0.20, 0.08]
        leaf_sick = [0.18, 0.34, 0.12]
        alto = 2.55
        _draw_round_trunk(dx, dy, dz, 0.32, alto, trunk, segments=5)
        top = dy + alto
        draw_optimized_rock(dx, top - 0.16, dz, 0.88, 0.62, 0.84, leaf_dark)
        draw_optimized_rock(dx, top + 0.18, dz, 1.24, 0.72, 1.14, leaf_main)
        draw_optimized_rock(dx + 0.50, top + 0.08, dz + 0.10, 0.82, 0.56, 0.76, leaf_dark)
        draw_optimized_rock(dx - 0.48, top + 0.06, dz - 0.08, 0.82, 0.56, 0.76, leaf_dark)
        draw_optimized_rock(dx, top + 0.06, dz + 0.52, 0.80, 0.54, 0.74, leaf_main)
        draw_optimized_rock(dx, top + 0.04, dz - 0.50, 0.78, 0.52, 0.72, leaf_main)
        draw_optimized_rock(dx, top + 0.60, dz, 0.70, 0.44, 0.66, leaf_sick)
        draw_optimized_rock(dx - 0.28, dy + 1.20, dz + 0.22, 0.10, 0.95, 0.10, [0.10, 0.20, 0.09])
        draw_optimized_rock(dx + 0.32, dy + 1.05, dz - 0.18, 0.09, 0.78, 0.09, [0.10, 0.20, 0.09])
        draw_optimized_rock(dx + 0.08, dy + 1.36, dz + 0.34, 0.08, 0.68, 0.08, [0.12, 0.23, 0.10])
    elif d_type == "arbol_seco":
        _draw_ground_shadow(dx, dy, dz, 1.65, 1.55, 0.10)
        trunk = [0.48, 0.36, 0.20]
        alto = 2.45
        _draw_round_trunk(dx, dy, dz, 0.24, alto, trunk, segments=7)
        top = dy + alto
        leaf = [0.56, 0.45, 0.20]
        leaf_dark = [0.45, 0.34, 0.15]
        draw_optimized_rock(dx, top + 0.04, dz, 0.64, 0.34, 0.60, leaf_dark)
        draw_optimized_rock(dx, top + 0.32, dz, 0.92, 0.44, 0.82, leaf)
        draw_optimized_rock(dx + 0.48, top + 0.20, dz, 0.52, 0.28, 0.42, leaf_dark)
        draw_optimized_rock(dx - 0.46, top + 0.18, dz, 0.48, 0.26, 0.40, leaf_dark)
        draw_optimized_rock(dx, top + 0.16, dz + 0.44, 0.48, 0.26, 0.40, leaf)
        draw_optimized_rock(dx, top + 0.14, dz - 0.42, 0.46, 0.24, 0.38, leaf)
        draw_optimized_rock(dx, top + 0.64, dz, 0.46, 0.24, 0.40, [0.62, 0.50, 0.24])
