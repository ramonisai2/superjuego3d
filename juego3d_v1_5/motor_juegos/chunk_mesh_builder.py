"""Construccion neutral de ChunkMeshData para chunks del mundo."""

import math

from .mesh_data import ChunkMeshData
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


def _add_tree_to_mesh(mesh, d_type, dx, dy, dz, variant):
    """Arbol boxel simplificado en MeshData.

    No intenta copiar cada cubo legacy, pero conserva silueta: tronco + copa por bloques.
    Esto reduce llamadas inmediatas de OpenGL y deja los arboles listos para buffers Vulkan.
    """
    detail = _world_detail_density()
    tree_layers = int(detail.get("tree_layers", 2))
    low_tree = tree_layers <= 1
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
    if d_type in ("arbol_bosque", "arbol_pantano", "arbol_seco"):
        return _add_tree_to_mesh(mesh, d_type, dx, dy, dz, variant)
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
        water_batch = mesh.batch("water", primitive="quads", material="water", alpha=0.34)
        for item in water:
            col, v0, v1, v2, v3 = item
            water_batch.add_quad(tuple(col) + (0.34,), v0, v1, v2, v3)

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
            if not _add_small_deco_to_mesh(mesh, *item):
                # Decoracion compleja no migrada queda legacy por ahora.
                mesh.legacy_deco.append(item)
        except Exception:
            mesh.legacy_deco.append(item)
    return mesh
