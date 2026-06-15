"""Construccion neutral de ChunkMeshData para chunks del mundo."""

import math

from .mesh_data import ChunkMeshData
from .env_config import read_env_float
from .world_detail import _world_detail_density
def _shade_color(color, factor):
    return tuple(max(0.0, min(1.0, float(c) * factor)) for c in color)


def _add_box_to_mesh(mesh, name, cx, cy, cz, sx, sy, sz, color, material=None):
    """Caja simple neutral para MeshData. Sirve para rocas/deco rumbo a Vulkan."""
    material = material or name
    batch = mesh.batch(name, primitive="quads", material=material, alpha=1.0)
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    x0, x1 = cx - hx, cx + hx
    y0, y1 = cy, cy + sy
    z0, z1 = cz - hz, cz + hz
    front = _shade_color(color, 1.00)
    back = _shade_color(color, 0.70)
    side = _shade_color(color, 0.82)
    top = _shade_color(color, 1.15)
    bottom = _shade_color(color, 0.55)
    batch.add_quad(front,  (x0,y0,z1), (x1,y0,z1), (x1,y1,z1), (x0,y1,z1))
    batch.add_quad(back,   (x1,y0,z0), (x0,y0,z0), (x0,y1,z0), (x1,y1,z0))
    batch.add_quad(side,   (x0,y0,z0), (x0,y0,z1), (x0,y1,z1), (x0,y1,z0))
    batch.add_quad(side,   (x1,y0,z1), (x1,y0,z0), (x1,y1,z0), (x1,y1,z1))
    batch.add_quad(top,    (x0,y1,z1), (x1,y1,z1), (x1,y1,z0), (x0,y1,z0))
    batch.add_quad(bottom, (x0,y0,z0), (x1,y0,z0), (x1,y0,z1), (x0,y0,z1))

def _add_shadow_to_mesh(mesh, cx, cy, cz, sx, sz, alpha=0.12):
    """Sombra plana barata en MeshData; reemplaza shadows legacy para arboles."""
    batch = mesh.batch("shadows", primitive="quads", material="shadow", alpha=alpha)
    col = (0.03, 0.03, 0.04, alpha)
    x0, x1 = cx - sx * 0.5, cx + sx * 0.5
    z0, z1 = cz - sz * 0.5, cz + sz * 0.5
    y = cy + 0.018
    batch.add_quad(col, (x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1))


def _add_ground_patch_to_mesh(mesh, name, cx, cy, cz, sx, sz, color):
    batch = mesh.batch(name, primitive="quads", material="plant", alpha=1.0)
    x0, x1 = cx - sx * 0.5, cx + sx * 0.5
    z0, z1 = cz - sz * 0.5, cz + sz * 0.5
    y = cy + 0.024
    batch.add_quad(color, (x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1))


def _add_abandoned_camp_to_mesh(mesh, dx, dy, dz, variant):
    dirt = [0.34, 0.25, 0.15]
    dirt_dark = [0.23, 0.17, 0.11]
    ash = [0.08, 0.075, 0.065]
    ember = [0.40, 0.13, 0.06]
    patches = (
        (0.00, 0.00, 2.55, 2.10, dirt),
        (-0.82, 0.02, 1.16, 1.44, _shade_color(dirt, 0.92)),
        (0.78, -0.04, 1.20, 1.34, _shade_color(dirt, 0.88)),
        (0.04, -0.86, 1.54, 0.84, dirt_dark),
        (-0.05, 0.82, 1.44, 0.76, _shade_color(dirt, 0.95)),
    )
    for ox, oz, sx, sz, color in patches:
        _add_ground_patch_to_mesh(mesh, "camp_dirt", dx + ox, dy, dz + oz, sx, sz, color)

    _add_ground_patch_to_mesh(mesh, "camp_ash", dx, dy + 0.006, dz, 0.84, 0.56, ash)
    _add_box_to_mesh(mesh, "camp_charred_wood", dx - 0.18, dy + 0.030, dz, 0.18, 0.10, 0.92, ash, "tree_trunk")
    _add_box_to_mesh(mesh, "camp_charred_wood", dx + 0.22, dy + 0.032, dz + 0.02, 0.16, 0.09, 0.86, _shade_color(ash, 1.18), "tree_trunk")
    _add_box_to_mesh(mesh, "camp_charred_wood", dx + 0.02, dy + 0.034, dz - 0.20, 0.78, 0.08, 0.15, _shade_color(ash, 0.85), "tree_trunk")
    _add_box_to_mesh(mesh, "camp_embers", dx + 0.10, dy + 0.052, dz + 0.05, 0.12, 0.035, 0.10, ember, "tree_trunk")

    if str(variant) == "con_bolsa":
        bx, bz = dx + 0.74, dz - 0.62
        _add_box_to_mesh(mesh, "camp_empty_bag", bx, dy + 0.035, bz, 0.46, 0.20, 0.34, [0.48,0.34,0.18], "tree_trunk")
        _add_box_to_mesh(mesh, "camp_empty_bag", bx - 0.12, dy + 0.22, bz, 0.18, 0.10, 0.28, [0.36,0.24,0.13], "tree_trunk")
        _add_box_to_mesh(mesh, "camp_empty_bag", bx + 0.03, dy + 0.245, bz, 0.34, 0.055, 0.07, [0.25,0.17,0.10], "tree_trunk")


def _add_leaf_impostor_to_mesh(mesh, cx, cy, cz, width, height, depth, main_color, dark_color=None, light_color=None):
    """Copa tipo billboard: pocos planos cruzados en vez de muchas cajas."""
    batch = mesh.batch("tree_leaf_impostors", primitive="quads", material="tree_leaf", alpha=1.0)
    planes = int(_world_detail_density().get("leaf_planes", 3))
    dark_color = dark_color or _shade_color(main_color, 0.72)
    light_color = light_color or _shade_color(main_color, 1.16)
    xh = width * 0.5
    zh = depth * 0.5
    y0 = cy - height * 0.5
    y1 = cy + height * 0.5

    # Dos planos cruzados principales: silueta 3D barata estilo N64.
    batch.add_quad(main_color, (cx - xh, y0, cz), (cx + xh, y0, cz), (cx + xh, y1, cz), (cx - xh, y1, cz))
    if planes >= 2:
        batch.add_quad(dark_color, (cx, y0, cz - zh), (cx, y0, cz + zh), (cx, y1, cz + zh), (cx, y1, cz - zh))

    # Un plano diagonal pequeno rompe la cruz perfecta sin volver a llenar de cubos.
    if planes >= 3:
        dx = xh * 0.70
        dz = zh * 0.70
        batch.add_quad(light_color, (cx - dx, y0 + height * 0.16, cz - dz), (cx + dx, y0 + height * 0.16, cz + dz), (cx + dx, y1, cz + dz), (cx - dx, y1, cz - dz))


def _add_deco_impostor_to_mesh(mesh, name, cx, cy, cz, width, height, color, color2=None, material="plant"):
    """Decoracion baja en planos cruzados: barata y legible a media distancia."""
    batch = mesh.batch(name, primitive="quads", material=material, alpha=1.0)
    planes = int(_world_detail_density().get("deco_planes", 2))
    color2 = color2 or _shade_color(color, 0.82)
    half = width * 0.5
    y0 = cy
    y1 = cy + height
    batch.add_quad(color,  (cx - half, y0, cz), (cx + half, y0, cz), (cx + half, y1, cz), (cx - half, y1, cz))
    if planes >= 2:
        batch.add_quad(color2, (cx, y0, cz - half), (cx, y0, cz + half), (cx, y1, cz + half), (cx, y1, cz - half))


TREE_TYPES = {
    "arbol_bosque",
    "arbol_pantano",
    "arbol_seco",
    "arbol_roble",
    "arbol_pino",
    "arbol_abedul",
    "arbol_sauce",
    "arbol_cipres",
}


def _add_branch_box(mesh, cx, cy, cz, sx, sy, sz, color):
    _add_box_to_mesh(mesh, "tree_branches", cx, cy, cz, sx, sy, sz, color, "tree_trunk")


def _add_branch_cluster(mesh, dx, dy, dz, top, trunk_color, scale=1.0, style="spread"):
    if style == "willow":
        _add_branch_box(mesh, dx - 0.34 * scale, top - 0.34 * scale, dz, 0.58 * scale, 0.12 * scale, 0.10 * scale, trunk_color)
        _add_branch_box(mesh, dx + 0.36 * scale, top - 0.42 * scale, dz + 0.08 * scale, 0.54 * scale, 0.11 * scale, 0.10 * scale, trunk_color)
        _add_branch_box(mesh, dx, top - 0.30 * scale, dz - 0.36 * scale, 0.10 * scale, 0.12 * scale, 0.58 * scale, trunk_color)
        return
    if style == "pine":
        for k, yoff in enumerate((0.18, 0.58, 0.96)):
            width = (0.78 - k * 0.14) * scale
            _add_branch_box(mesh, dx, top + yoff * scale, dz, width, 0.10 * scale, 0.10 * scale, trunk_color)
            _add_branch_box(mesh, dx, top + (yoff + 0.12) * scale, dz, 0.10 * scale, 0.10 * scale, width, trunk_color)
        return
    if style == "cypress":
        _add_branch_box(mesh, dx - 0.18 * scale, top + 0.08 * scale, dz, 0.30 * scale, 0.10 * scale, 0.08 * scale, trunk_color)
        _add_branch_box(mesh, dx + 0.16 * scale, top + 0.44 * scale, dz, 0.26 * scale, 0.09 * scale, 0.08 * scale, trunk_color)
        _add_branch_box(mesh, dx, top + 0.76 * scale, dz - 0.15 * scale, 0.08 * scale, 0.08 * scale, 0.24 * scale, trunk_color)
        return
    _add_branch_box(mesh, dx - 0.42 * scale, top - 0.08 * scale, dz + 0.04 * scale, 0.72 * scale, 0.13 * scale, 0.11 * scale, trunk_color)
    _add_branch_box(mesh, dx + 0.40 * scale, top + 0.12 * scale, dz - 0.03 * scale, 0.68 * scale, 0.12 * scale, 0.10 * scale, trunk_color)
    _add_branch_box(mesh, dx + 0.04 * scale, top + 0.02 * scale, dz - 0.42 * scale, 0.10 * scale, 0.12 * scale, 0.70 * scale, trunk_color)


def _add_tree_to_mesh(mesh, d_type, dx, dy, dz, variant):
    """Arbol boxel simplificado en MeshData.

    No intenta copiar cada cubo legacy, pero conserva silueta: tronco + copa por bloques.
    Esto reduce llamadas inmediatas de OpenGL y deja los arboles listos para buffers Vulkan.
    """
    detail = _world_detail_density()
    tree_layers = int(detail.get("tree_layers", 2))
    low_tree = tree_layers <= 1
    if d_type == "arbol_bosque":
        d_type = "arbol_roble"
    elif d_type == "arbol_pantano":
        d_type = "arbol_sauce"

    if d_type == "arbol_roble":
        if not low_tree:
            _add_shadow_to_mesh(mesh, dx, dy, dz, 2.25, 2.05, 0.13)
        trunk = [0.35, 0.22, 0.12]
        leaf_main = [0.10, 0.38, 0.13]
        leaf_dark = [0.07, 0.28, 0.09]
        leaf_light = [0.16, 0.48, 0.18]
        alto = 2.95 if variant == "alto" else 2.58
        _add_box_to_mesh(mesh, "tree_trunks", dx, dy, dz, 0.38, alto, 0.38, trunk, "tree_trunk")
        top = dy + alto
        if not low_tree:
            _add_branch_cluster(mesh, dx, dy, dz, top, trunk, scale=1.0, style="spread")
        _add_box_to_mesh(mesh, "tree_leaves_core", dx, top - 0.18, dz, 0.54, 0.34, 0.54, leaf_dark, "tree_leaf")
        _add_leaf_impostor_to_mesh(mesh, dx, top + 0.28, dz, 2.05, 1.28, 1.86, leaf_main, leaf_dark, leaf_light)
        if not low_tree:
            _add_leaf_impostor_to_mesh(mesh, dx + 0.28, top + 0.72, dz - 0.12, 1.24, 0.66, 1.08, leaf_light, leaf_main, leaf_light)
        return True

    if d_type == "arbol_abedul":
        if not low_tree:
            _add_shadow_to_mesh(mesh, dx, dy, dz, 1.90, 1.75, 0.11)
        trunk = [0.78, 0.76, 0.64]
        bark_dark = [0.12, 0.12, 0.10]
        leaf_main = [0.20, 0.50, 0.17]
        leaf_dark = [0.10, 0.34, 0.10]
        leaf_light = [0.38, 0.62, 0.22]
        alto = 3.18 if variant == "alto" else 2.82
        _add_box_to_mesh(mesh, "tree_trunks", dx, dy, dz, 0.28, alto, 0.28, trunk, "tree_trunk")
        if not low_tree:
            _add_branch_box(mesh, dx - 0.03, dy + 0.74, dz, 0.31, 0.08, 0.30, bark_dark)
            _add_branch_box(mesh, dx + 0.04, dy + 1.55, dz, 0.30, 0.08, 0.28, bark_dark)
        top = dy + alto
        if not low_tree:
            _add_branch_cluster(mesh, dx, dy, dz, top, bark_dark, scale=0.72, style="spread")
        _add_leaf_impostor_to_mesh(mesh, dx, top + 0.26, dz, 1.48, 1.14, 1.34, leaf_main, leaf_dark, leaf_light)
        _add_leaf_impostor_to_mesh(mesh, dx - 0.14, top + 0.78, dz + 0.10, 0.98, 0.58, 0.88, leaf_light, leaf_main, leaf_light)
        return True

    if d_type == "arbol_pino":
        if not low_tree:
            _add_shadow_to_mesh(mesh, dx, dy, dz, 1.75, 1.75, 0.10)
        trunk = [0.30, 0.18, 0.10]
        leaf_main = [0.06, 0.26, 0.12]
        leaf_dark = [0.04, 0.18, 0.09]
        leaf_light = [0.10, 0.34, 0.16]
        alto = 3.55 if variant == "alto" else 3.20
        _add_box_to_mesh(mesh, "tree_trunks", dx, dy, dz, 0.26, alto, 0.26, trunk, "tree_trunk")
        top = dy + alto
        if not low_tree:
            _add_branch_cluster(mesh, dx, dy, dz, dy + 1.55, trunk, scale=0.95, style="pine")
        _add_leaf_impostor_to_mesh(mesh, dx, dy + 2.20, dz, 1.90, 2.15, 1.72, leaf_main, leaf_dark, leaf_light)
        _add_leaf_impostor_to_mesh(mesh, dx, top + 0.20, dz, 1.08, 1.26, 0.96, leaf_light, leaf_dark, leaf_light)
        return True

    if d_type == "arbol_sauce":
        if not low_tree:
            _add_shadow_to_mesh(mesh, dx, dy, dz, 2.25, 2.15, 0.15)
        trunk = [0.24, 0.15, 0.09]
        leaf_main = [0.13, 0.32, 0.12]
        leaf_dark = [0.07, 0.22, 0.08]
        leaf_light = [0.24, 0.44, 0.18]
        alto = 2.48 if variant == "alto" else 2.24
        _add_box_to_mesh(mesh, "tree_trunks", dx, dy, dz, 0.40, alto, 0.40, trunk, "tree_trunk")
        top = dy + alto
        if not low_tree:
            _add_branch_cluster(mesh, dx, dy, dz, top, trunk, scale=1.12, style="willow")
        _add_leaf_impostor_to_mesh(mesh, dx, top + 0.10, dz, 2.15, 1.35, 1.95, leaf_main, leaf_dark, leaf_light)
        _add_leaf_impostor_to_mesh(mesh, dx - 0.20, top - 0.34, dz + 0.14, 1.24, 1.05, 1.08, leaf_dark, leaf_dark, leaf_main)
        _add_leaf_impostor_to_mesh(mesh, dx + 0.22, top - 0.42, dz - 0.08, 1.10, 0.98, 1.02, leaf_dark, leaf_dark, leaf_main)
        return True

    if d_type == "arbol_cipres":
        if not low_tree:
            _add_shadow_to_mesh(mesh, dx, dy, dz, 1.55, 1.50, 0.12)
        trunk = [0.20, 0.12, 0.08]
        leaf_main = [0.04, 0.18, 0.08]
        leaf_dark = [0.025, 0.11, 0.055]
        leaf_light = [0.08, 0.25, 0.10]
        alto = 3.35 if variant == "alto" else 3.02
        _add_box_to_mesh(mesh, "tree_trunks", dx, dy, dz, 0.30, alto, 0.30, trunk, "tree_trunk")
        top = dy + alto
        if not low_tree:
            _add_branch_cluster(mesh, dx, dy, dz, dy + 1.70, trunk, scale=0.90, style="cypress")
        _add_leaf_impostor_to_mesh(mesh, dx, dy + 2.05, dz, 1.24, 2.55, 1.16, leaf_main, leaf_dark, leaf_light)
        _add_leaf_impostor_to_mesh(mesh, dx, top + 0.42, dz, 0.66, 0.98, 0.62, leaf_light, leaf_dark, leaf_light)
        return True

    if d_type == "arbol_bosque":
        if not low_tree:
            _add_shadow_to_mesh(mesh, dx, dy, dz, 2.15, 2.0, 0.13)
        trunk = [0.36, 0.23, 0.13]
        leaf_main = [0.10, 0.38, 0.13]
        leaf_dark = [0.07, 0.30, 0.09]
        leaf_light = [0.13, 0.45, 0.16]
        alto = 3.10 if variant == "alto" else 2.65
        _add_box_to_mesh(mesh, "tree_trunks", dx, dy, dz, 0.34, alto, 0.34, trunk, "tree_trunk")
        top = dy + alto
        core_size = 0.42 if low_tree else 0.58
        _add_box_to_mesh(mesh, "tree_leaves_core", dx, top - 0.18, dz, core_size, 0.34, core_size, leaf_dark, "tree_leaf")
        _add_leaf_impostor_to_mesh(mesh, dx, top + 0.35, dz, 1.95, 1.34, 1.78, leaf_main, leaf_dark, leaf_light)
        if not low_tree:
            _add_leaf_impostor_to_mesh(mesh, dx + 0.18, top + 0.84, dz - 0.10, 1.18, 0.72, 1.02, leaf_light, leaf_main, leaf_light)
        return True

    if d_type == "arbol_pantano":
        if not low_tree:
            _add_shadow_to_mesh(mesh, dx, dy, dz, 2.0, 1.95, 0.14)
        trunk = [0.22, 0.16, 0.10]
        leaf_main = [0.12, 0.28, 0.12]
        leaf_dark = [0.08, 0.20, 0.08]
        leaf_sick = [0.18, 0.34, 0.12]
        alto = 2.55
        _add_box_to_mesh(mesh, "tree_trunks", dx, dy, dz, 0.36, alto, 0.36, trunk, "tree_trunk")
        top = dy + alto
        core_size = 0.40 if low_tree else 0.56
        _add_box_to_mesh(mesh, "tree_leaves_core", dx, top - 0.20, dz, core_size, 0.32, core_size, leaf_dark, "tree_leaf")
        _add_leaf_impostor_to_mesh(mesh, dx, top + 0.25, dz, 1.78, 1.08, 1.62, leaf_main, leaf_dark, leaf_sick)
        if not low_tree:
            _add_leaf_impostor_to_mesh(mesh, dx - 0.14, top + 0.76, dz + 0.10, 1.06, 0.62, 0.94, leaf_sick, leaf_dark, leaf_sick)
        # Musgo/raíces colgantes como cajas finas.
        if not low_tree:
            _add_box_to_mesh(mesh, "tree_moss", dx-0.26, dy+1.12, dz+0.18, 0.08, 0.82, 0.08, [0.10,0.20,0.09], "tree_leaf")
            _add_box_to_mesh(mesh, "tree_moss", dx+0.30, dy+1.02, dz-0.14, 0.07, 0.66, 0.07, [0.10,0.20,0.09], "tree_leaf")
        return True

    if d_type == "arbol_seco":
        if not low_tree:
            _add_shadow_to_mesh(mesh, dx, dy, dz, 1.65, 1.55, 0.10)
        trunk = [0.48, 0.36, 0.20]
        leaf = [0.56, 0.45, 0.20]
        leaf_dark = [0.45, 0.34, 0.15]
        alto = 2.45
        _add_box_to_mesh(mesh, "tree_trunks", dx, dy, dz, 0.28, alto, 0.28, trunk, "tree_trunk")
        top = dy + alto
        if not low_tree:
            _add_box_to_mesh(mesh, "tree_leaves_core", dx, top + 0.02, dz, 0.42, 0.24, 0.40, leaf_dark, "tree_leaf")
        _add_leaf_impostor_to_mesh(mesh, dx, top + 0.38, dz, 1.18, 0.76, 1.02, leaf, leaf_dark, [0.62,0.50,0.24])
        return True

    return False


def _add_rock_to_mesh(mesh, bx, base_y, bz, sx, sy, sz, col):
    """Roca prismática en MeshData: lados en quads y tapa en triangles."""
    if int(_world_detail_density().get("rock_detail", 2)) <= 1:
        _add_box_to_mesh(mesh, "rocks_simple", bx, base_y, bz, sx, sy, sz, col, "rock")
        return
    c_top = _shade_color(col, 1.12)
    c_s1 = _shade_color(col, 0.92)
    c_s2 = _shade_color(col, 0.78)
    c_s3 = _shade_color(col, 0.68)
    sides = mesh.batch("rocks_sides", primitive="quads", material="rock", alpha=1.0)
    caps = mesh.batch("rocks_caps", primitive="triangles", material="rock", alpha=1.0)
    hx, hz = sx/2, sz/2
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
    b0 = (bx-hx, base_y, bz-hz)
    b1 = (bx+hx, base_y, bz-hz)
    b2 = (bx+hx, base_y, bz+hz)
    b3 = (bx-hx, base_y, bz+hz)
    t0 = (bx-hx*(1.0-inset), base_y + lift0, bz-hz*(1.0-0.08-frac*0.04))
    t1 = (bx+hx*(1.0-inset*0.8), base_y + lift1, bz-hz*(1.0-inset))
    t2 = (bx+hx*(1.0-0.06-frac2*0.05), base_y + lift2, bz+hz*(1.0-inset*0.9))
    t3 = (bx-hx*(1.0-inset), base_y + lift3, bz+hz*(1.0-0.05-frac3*0.05))
    peak = (bx + (frac-0.5)*hx*0.25, base_y + sy * (1.02 + 0.08 * frac2), bz + (frac3-0.5)*hz*0.25)
    sides.add_quad(c_s1, b0, b1, t1, t0)
    sides.add_quad(c_s2, b1, b2, t2, t1)
    sides.add_quad(c_s3, b2, b3, t3, t2)
    sides.add_quad(c_s2, b3, b0, t0, t3)
    caps.add_triangle(c_top, t0, t1, peak)
    caps.add_triangle(c_top, t1, t2, peak)
    caps.add_triangle(c_top, t2, t3, peak)
    caps.add_triangle(c_top, t3, t0, peak)


def _add_small_deco_to_mesh(mesh, d_type, dx, dy, dz, variant):
    """Migra decoracion y arboles a MeshData. Devuelve False si debe quedarse legacy."""
    if d_type in TREE_TYPES:
        return _add_tree_to_mesh(mesh, d_type, dx, dy, dz, variant)
    if d_type == "campamento_abandonado":
        _add_abandoned_camp_to_mesh(mesh, dx, dy, dz, variant)
        return True
    if d_type == "hongo":
        _add_deco_impostor_to_mesh(mesh, "deco_mushrooms", dx, dy, dz, 0.14, 0.20, [0.90,0.86,0.72], [0.72,0.64,0.52], "plant")
        _add_deco_impostor_to_mesh(mesh, "deco_mushrooms", dx, dy+0.12, dz, 0.30, 0.13, [0.85,0.15,0.15], [0.62,0.08,0.10], "plant")
        return True
    if d_type == "cactus":
        _add_box_to_mesh(mesh, "deco_cactus", dx, dy, dz, 0.22, 1.6, 0.22, [0.13,0.48,0.16], "plant")
        _add_box_to_mesh(mesh, "deco_cactus", dx+0.22, dy+0.65, dz, 0.18, 0.55, 0.18, [0.12,0.42,0.14], "plant")
        _add_box_to_mesh(mesh, "deco_cactus", dx-0.20, dy+0.85, dz, 0.16, 0.45, 0.16, [0.12,0.42,0.14], "plant")
        return True
    if d_type == "cristal":
        _add_rock_to_mesh(mesh, dx, dy, dz, 0.22, 0.70, 0.22, [0,0.9,0.9])
        return True
    if d_type == "flores":
        col_f = [0.85,0.15,0.45] if variant == "rojo" else [0.9,0.8,0.1]
        _add_deco_impostor_to_mesh(mesh, "deco_flowers", dx, dy, dz, 0.18, 0.34, [0.18,0.48,0.18], [0.12,0.36,0.13], "plant")
        _add_deco_impostor_to_mesh(mesh, "deco_flowers", dx, dy+0.20, dz, 0.20, 0.10, col_f, _shade_color(col_f, 0.74), "plant")
        return True
    if d_type == "arbusto_verde":
        _add_deco_impostor_to_mesh(mesh, "deco_bushes", dx, dy, dz, 0.78, 0.48, [0.12,0.44,0.14], [0.08,0.32,0.10], "plant")
        _add_deco_impostor_to_mesh(mesh, "deco_bushes", dx+0.18, dy+0.10, dz-0.08, 0.52, 0.34, [0.16,0.52,0.18], [0.10,0.36,0.12], "plant")
        return True
    if d_type == "arbusto_seco":
        _add_deco_impostor_to_mesh(mesh, "deco_bushes", dx, dy, dz, 0.68, 0.42, [0.46,0.38,0.26], [0.34,0.26,0.16], "plant")
        _add_deco_impostor_to_mesh(mesh, "deco_bushes", dx-0.16, dy+0.08, dz+0.10, 0.42, 0.28, [0.38,0.30,0.18], [0.30,0.22,0.12], "plant")
        return True
    if d_type == "junco":
        _add_deco_impostor_to_mesh(mesh, "deco_reeds", dx, dy, dz, 0.22, 0.82, [0.34,0.48,0.18], [0.22,0.34,0.12], "plant")
        _add_deco_impostor_to_mesh(mesh, "deco_reeds", dx+0.10, dy, dz-0.06, 0.16, 0.62, [0.42,0.55,0.20], [0.24,0.38,0.13], "plant")
        return True
    if d_type == "helecho":
        _add_deco_impostor_to_mesh(mesh, "deco_ferns", dx, dy, dz, 0.76, 0.44, [0.10,0.42,0.16], [0.06,0.28,0.10], "plant")
        _add_deco_impostor_to_mesh(mesh, "deco_ferns", dx-0.12, dy+0.04, dz+0.08, 0.54, 0.34, [0.14,0.50,0.18], [0.08,0.32,0.12], "plant")
        return True
    if d_type == "hierba_alta":
        _add_deco_impostor_to_mesh(mesh, "deco_tall_grass", dx, dy, dz, 0.30, 0.70, [0.22,0.52,0.20], [0.14,0.38,0.14], "grass")
        return True
    if d_type == "flor_azul":
        _add_deco_impostor_to_mesh(mesh, "deco_blue_flowers", dx, dy, dz, 0.18, 0.38, [0.16,0.42,0.18], [0.10,0.30,0.12], "plant")
        _add_deco_impostor_to_mesh(mesh, "deco_blue_flowers", dx, dy+0.24, dz, 0.18, 0.10, [0.22,0.36,0.92], [0.12,0.20,0.62], "plant")
        return True
    if d_type == "maleza_oscura":
        _add_deco_impostor_to_mesh(mesh, "deco_dark_underbrush", dx, dy, dz, 0.82, 0.52, [0.04,0.18,0.08], [0.025,0.11,0.05], "plant")
        _add_deco_impostor_to_mesh(mesh, "deco_dark_underbrush", dx+0.16, dy+0.06, dz-0.10, 0.48, 0.36, [0.06,0.24,0.09], [0.03,0.14,0.05], "plant")
        return True
    return False

def build_chunk_mesh_data(cx, cz, quads, grass, rocks, deco, water=None, size=100, lod="detail", height_map=None):
    """Convierte los datos procedurales del chunk a un formato neutral.

    Esta es la pieza importante rumbo a Vulkan: el chunk ya puede existir como
    datos de malla antes de ser subido a OpenGL. En etapas posteriores, rocas y
    decoraciones tambien dejaran de ser legacy.
    """
    if water is None:
        water = []
    mesh = ChunkMeshData(coord=(int(cx), int(cz)), size=float(size), lod=str(lod), height_map=height_map)

    terrain_batch = mesh.batch("terrain", primitive="quads", material="terrain", alpha=1.0)
    for col, v0, v1, v2, v3 in quads:
        terrain_batch.add_quad(col, v0, v1, v2, v3)

    if water:
        water_alpha = read_env_float("JUEGO_WATER_ALPHA", 0.20, 0.08, 0.55)
        lake_alpha = read_env_float("JUEGO_WATER_IMPOSTOR_ALPHA", 0.24, 0.05, 0.55)
        water_batch = mesh.batch("water", primitive="quads", material="water", alpha=water_alpha)
        lake_batch = mesh.batch("lake_impostor", primitive="quads", material="water", alpha=lake_alpha)
        for item in water:
            if item and item[0] == "lake_impostor":
                _kind, col, v0, v1, v2, v3 = item
                lake_batch.add_quad(tuple(col) + (lake_alpha,), v0, v1, v2, v3)
            else:
                col, v0, v1, v2, v3 = item
                water_batch.add_quad(tuple(col) + (water_alpha,), v0, v1, v2, v3)

    if grass:
        grass_batch = mesh.batch("grass", primitive="quads", material="grass", alpha=1.0)
        grass_planes = int(_world_detail_density().get("grass_planes", 2))
        for gcol, gx, gy, gz, gh in grass:
            w = 0.05
            grass_batch.add_quad(gcol, (gx-w, gy, gz-w), (gx+w, gy+gh, gz+w), (gx+w, gy+gh, gz+w), (gx-w, gy+gh, gz-w))
            if grass_planes >= 2:
                grass_batch.add_quad(gcol, (gx-w, gy, gz+w), (gx+w, gy+gh, gz-w), (gx+w, gy+gh, gz-w), (gx-w, gy+gh, gz+w))

    # Stage31 Pre-K: rocas, decoracion pequeña y arboles simplificados ya entran a MeshData.
    # Esto baja el acoplamiento a OpenGL y prepara buffers de Vulkan.
    for rock in (rocks or []):
        try:
            _add_rock_to_mesh(mesh, *rock)
        except Exception:
            mesh.legacy_rocks.append(rock)

    for item in (deco or []):
        try:
            if item and item[0] == "piedra_suelta":
                continue
            if not _add_small_deco_to_mesh(mesh, *item):
                # Decoracion compleja no migrada queda legacy por ahora.
                mesh.legacy_deco.append(item)
        except Exception:
            mesh.legacy_deco.append(item)
    return mesh
