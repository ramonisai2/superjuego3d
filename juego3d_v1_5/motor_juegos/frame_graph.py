"""FrameGraph simple para preparar el render hacia Vulkan.

Stage31 Pre-M:
- El juego todavia renderiza con OpenGL.
- Pero antes de dibujar, el frame se organiza en paquetes/pases.
- Vulkan necesitara una estructura similar: ordenar terreno, agua,
  decoracion, entidades, transparencias y UI antes de grabar command buffers.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from motor_juegos.instance_data import InstanceFrameData, build_entity_instance
from motor_juegos.entity_mesh_catalog import DEFAULT_ENTITY_MESH_CATALOG, catalog_stats


@dataclass
class RenderPacket:
    """Unidad neutral de render.

    Por ahora contiene handles de OpenGL, pero el campo payload puede convertirse
    despues en buffers Vulkan, descriptors o command buffer references.
    """

    kind: str
    payload: Any
    coord: Tuple[int, int] = (0, 0)
    material: str = "default"
    lod: str = "detail"
    transparent: bool = False


@dataclass
class RenderPass:
    name: str
    order: int
    transparent: bool = False
    packets: List[RenderPacket] = field(default_factory=list)

    def add(self, packet: RenderPacket) -> None:
        self.packets.append(packet)


class RenderFrameGraph:
    """Organiza los paquetes visibles de un frame.

    Esto es intencionalmente pequeño para no romper el motor actual. La meta es
    que main.py deje de pensar en 'dibujar ahora mismo' y empiece a pensar en
    'preparar pases de render'.
    """

    def __init__(self):
        self.passes: Dict[str, RenderPass] = {}
        self.instances = InstanceFrameData()
        self.frame_index = 0
        self.entity_mesh_catalog = DEFAULT_ENTITY_MESH_CATALOG

    def begin_frame(self) -> None:
        self.passes.clear()
        self.instances.clear()
        self.frame_index += 1

    def get_pass(self, name: str, order: int, transparent: bool = False) -> RenderPass:
        if name not in self.passes:
            self.passes[name] = RenderPass(name=name, order=order, transparent=transparent)
        return self.passes[name]

    def add_chunk(self, coord, handle, *, lod="detail", transparent=False) -> None:
        # Los chunks detallados van antes que LOD para que el terreno principal
        # tenga prioridad. El LOD simple queda como fondo barato.
        if lod == "detail":
            pass_obj = self.get_pass("world_detail", 20, transparent=False)
        else:
            pass_obj = self.get_pass("world_lod", 10, transparent=False)
        pass_obj.add(RenderPacket(kind="chunk", payload=handle, coord=coord, material="chunk", lod=lod, transparent=transparent))

    def add_entity(self, kind: str, entity_ref: Any, *, render_fn=None, transparent=False, priority=0) -> None:
        """Agrega una entidad visible al frame.

        Stage31 Pre-N: las entidades dejan de dibujarse directo desde main.py.
        Por ahora el payload puede contener una funcion legacy de render; luego
        Vulkan lo reemplazara por buffers/instancias/materiales.
        """
        if transparent:
            pass_obj = self.get_pass("transparent_entities", 65 + int(priority), transparent=True)
        else:
            pass_obj = self.get_pass("entities", 40 + int(priority), transparent=False)

        # Stage31 Pre-O: cada entidad visible produce tambien datos de instancia
        # neutrales. OpenGL aun usa render_fn, Vulkan podra usar instance buffers.
        instance = build_entity_instance(kind, entity_ref, transparent=transparent, material=kind)
        self.instances.add(instance)
        static_mesh = self.entity_mesh_catalog.get(instance.mesh_id)
        payload = {"entity": entity_ref, "render_fn": render_fn, "instance": instance, "static_mesh": static_mesh}
        pass_obj.add(RenderPacket(kind=kind, payload=payload, material=kind, transparent=transparent))

    def ordered_passes(self) -> List[RenderPass]:
        # Opacos primero. Transparentes al final.
        return sorted(self.passes.values(), key=lambda p: (1 if p.transparent else 0, p.order, p.name))

    @property
    def pass_count(self) -> int:
        return len(self.passes)

    @property
    def packet_count(self) -> int:
        return sum(len(p.packets) for p in self.passes.values())

    def _accumulate_visible_chunk_cost(self, render_stats: Dict[str, int], handle: Any, lod: str) -> None:
        desc = getattr(handle, "desc", None)
        if desc is None:
            return
        try:
            vertices = int(getattr(desc, "vertex_count", 0) or 0)
            indices = int(getattr(desc, "index_count", 0) or 0)
            bytes_size = int(getattr(desc, "byte_size", 0) or 0)
            batches = int(getattr(desc, "material_batches", 0) or 0)
        except Exception:
            return
        render_stats["visible_chunk_vertices"] = render_stats.get("visible_chunk_vertices", 0) + vertices
        render_stats["visible_chunk_indices"] = render_stats.get("visible_chunk_indices", 0) + indices
        render_stats["visible_chunk_bytes"] = render_stats.get("visible_chunk_bytes", 0) + bytes_size
        render_stats["visible_chunk_batches"] = render_stats.get("visible_chunk_batches", 0) + batches
        if lod == "detail":
            render_stats["visible_detail_vertices"] = render_stats.get("visible_detail_vertices", 0) + vertices
            render_stats["visible_detail_bytes"] = render_stats.get("visible_detail_bytes", 0) + bytes_size
        else:
            render_stats["visible_lod_vertices"] = render_stats.get("visible_lod_vertices", 0) + vertices
            render_stats["visible_lod_bytes"] = render_stats.get("visible_lod_bytes", 0) + bytes_size

    def execute(self, render_backend, render_stats: Dict[str, int]) -> None:
        """Ejecuta los pases del frame con el backend actual.

        Chunks: usan handles/meshes subidos al backend.
        Entidades: usan callbacks legacy temporalmente.
        Esta separacion ya parece mas a un command buffer sencillo.
        """
        for pass_obj in self.ordered_passes():
            for packet in pass_obj.packets:
                if packet.kind == "chunk":
                    render_backend.draw_compiled_chunk(packet.payload)
                    self._accumulate_visible_chunk_cost(render_stats, packet.payload, packet.lod)
                    if packet.lod == "detail":
                        render_stats["chunks_detalle"] = render_stats.get("chunks_detalle", 0) + 1
                    else:
                        render_stats["chunks_lod"] = render_stats.get("chunks_lod", 0) + 1
                    continue

                payload = packet.payload
                render_fn = payload.get("render_fn") if isinstance(payload, dict) else None

                # Stage31 Pre-Q: cada entidad visible fuerza la creacion/cache de
                # un buffer neutral a partir de StaticMeshInfo. Aun se dibuja con
                # render_fn legacy, pero Vulkan ya tendra los datos listos.
                static_mesh = payload.get("static_mesh") if isinstance(payload, dict) else None
                entity_buffer = None
                if static_mesh is not None and hasattr(render_backend, "upload_entity_mesh"):
                    try:
                        entity_buffer = render_backend.upload_entity_mesh(static_mesh)
                    except Exception:
                        entity_buffer = None

                # Stage31 Pre-R: ruta StaticMesh experimental. Si esta apagada o falla,
                # se conserva el render legacy para no romper el arte actual.
                instance = payload.get("instance") if isinstance(payload, dict) else None
                static_drawn = False
                if entity_buffer is not None and instance is not None and hasattr(render_backend, "draw_entity_static_mesh"):
                    try:
                        static_drawn = bool(render_backend.draw_entity_static_mesh(entity_buffer, instance))
                    except Exception:
                        static_drawn = False

                if static_drawn:
                    render_stats["entidades_render"] = render_stats.get("entidades_render", 0) + 1
                    render_stats["entidades_staticmesh"] = render_stats.get("entidades_staticmesh", 0) + 1
                    if packet.transparent:
                        render_stats["entidades_transparentes"] = render_stats.get("entidades_transparentes", 0) + 1
                elif callable(render_fn):
                    render_fn()
                    render_stats["entidades_render"] = render_stats.get("entidades_render", 0) + 1
                    if packet.transparent:
                        render_stats["entidades_transparentes"] = render_stats.get("entidades_transparentes", 0) + 1

    # Compatibilidad temporal con Pre-M.
    def execute_chunks(self, render_backend, render_stats: Dict[str, int]) -> None:
        self.execute(render_backend, render_stats)

    def as_stats(self) -> Dict[str, int]:
        data = {
            "render_passes": self.pass_count,
            "render_packets": self.packet_count,
        }
        data.update(self.instances.stats())
        data.update(catalog_stats())
        return data
