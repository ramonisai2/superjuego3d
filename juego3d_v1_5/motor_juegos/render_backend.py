"""Capa de backend de render para preparar migracion futura a Vulkan.

Stage31 Pre-H:
- OpenGL sigue siendo el backend real.
- El juego ya no deberia llamar directamente a env.draw_compiled_chunk/glDeleteLists
  desde todas partes; estas llamadas pasan por este modulo.
- VulkanRenderer queda como esqueleto/documentacion ejecutable, no como backend activo.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, Any
import os

from OpenGL.GL import glDeleteLists
from motor_juegos.render_api import FrameClearConfig, FogConfig
from motor_juegos.gpu_resources import NeutralBufferDesc, NeutralMeshHandle


@dataclass
class RenderFrameStats:
    chunks_detalle: int = 0
    chunks_lod: int = 0
    chunks_ocultos: int = 0
    entidades_render: int = 0
    entidades_ocultas: int = 0
    mesh_vertices: int = 0
    mesh_indices: int = 0
    mesh_quads: int = 0
    mesh_bytes: int = 0
    material_batches: int = 0
    uploads_frame: int = 0
    live_mesh_handles: int = 0
    live_mesh_bytes: int = 0
    neutral_mesh_created: int = 0
    neutral_mesh_released: int = 0
    static_meshes: int = 0
    static_mesh_vertices: int = 0
    entity_mesh_cached: int = 0
    entity_mesh_uploads: int = 0
    entity_mesh_vertices: int = 0
    entity_mesh_indices: int = 0
    entity_mesh_bytes: int = 0
    entidades_staticmesh: int = 0
    static_entity_debug: int = 0
    backend: str = "opengl"
    vulkan_probe_ok: int = 0
    vulkan_devices: int = 0
    vulkan_triangle_ok: int = 0
    vulkan_triangle_buffers: int = 0
    vulkan_chunk_upload_ok: int = 0
    vulkan_chunk_buffers: int = 0
    vulkan_upload_bytes: int = 0
    vulkan_memory_ok: int = 0
    vulkan_memory_bound: int = 0
    vulkan_alloc_kb: int = 0
    vulkan_staging_ok: int = 0
    vulkan_staging_mapped: int = 0
    vulkan_staging_write_kb: int = 0
    vulkan_command_ok: int = 0
    vulkan_command_buffers: int = 0
    vulkan_copy_commands: int = 0
    vulkan_submits: int = 0
    vulkan_draw_ok: int = 0
    vulkan_render_pass_plan: int = 0
    vulkan_pipeline_plan: int = 0
    vulkan_draw_indexed_plan: int = 0
    vulkan_shader_ok: int = 0
    vulkan_spirv_generated: int = 0
    vulkan_shader_compiler: int = 0
    vulkan_shader_bytes: int = 0
    vulkan_shader_modules: int = 0
    vulkan_pipeline_layout_ok: int = 0
    vulkan_framebuffer_ok: int = 0
    vulkan_graphics_pipeline_ok: int = 0
    vulkan_renderpass_begin_ok: int = 0
    vulkan_draw_indexed_recorded: int = 0

    def as_dict(self) -> Dict[str, int]:
        return {
            "chunks_detalle": self.chunks_detalle,
            "chunks_lod": self.chunks_lod,
            "chunks_ocultos": self.chunks_ocultos,
            "entidades_render": self.entidades_render,
            "entidades_ocultas": self.entidades_ocultas,
            "mesh_vertices": self.mesh_vertices,
            "mesh_indices": self.mesh_indices,
            "mesh_quads": self.mesh_quads,
            "mesh_bytes": self.mesh_bytes,
            "material_batches": self.material_batches,
            "uploads_frame": self.uploads_frame,
            "live_mesh_handles": self.live_mesh_handles,
            "live_mesh_bytes": self.live_mesh_bytes,
            "neutral_mesh_created": self.neutral_mesh_created,
            "neutral_mesh_released": self.neutral_mesh_released,
            "static_meshes": self.static_meshes,
            "static_mesh_vertices": self.static_mesh_vertices,
            "entity_mesh_cached": self.entity_mesh_cached,
            "entity_mesh_uploads": self.entity_mesh_uploads,
            "entity_mesh_vertices": self.entity_mesh_vertices,
            "entity_mesh_indices": self.entity_mesh_indices,
            "entity_mesh_bytes": self.entity_mesh_bytes,
            "entidades_staticmesh": self.entidades_staticmesh,
            "static_entity_debug": self.static_entity_debug,
            "backend": self.backend,
            "vulkan_probe_ok": self.vulkan_probe_ok,
            "vulkan_devices": self.vulkan_devices,
            "vulkan_triangle_ok": self.vulkan_triangle_ok,
            "vulkan_triangle_buffers": self.vulkan_triangle_buffers,
            "vulkan_chunk_upload_ok": self.vulkan_chunk_upload_ok,
            "vulkan_chunk_buffers": self.vulkan_chunk_buffers,
            "vulkan_upload_bytes": self.vulkan_upload_bytes,
            "vulkan_memory_ok": self.vulkan_memory_ok,
            "vulkan_memory_bound": self.vulkan_memory_bound,
            "vulkan_alloc_kb": self.vulkan_alloc_kb,
            "vulkan_staging_ok": self.vulkan_staging_ok,
            "vulkan_staging_mapped": self.vulkan_staging_mapped,
            "vulkan_staging_write_kb": self.vulkan_staging_write_kb,
            "vulkan_command_ok": self.vulkan_command_ok,
            "vulkan_command_buffers": self.vulkan_command_buffers,
            "vulkan_copy_commands": self.vulkan_copy_commands,
            "vulkan_submits": self.vulkan_submits,
            "vulkan_draw_ok": self.vulkan_draw_ok,
            "vulkan_render_pass_plan": self.vulkan_render_pass_plan,
            "vulkan_pipeline_plan": self.vulkan_pipeline_plan,
            "vulkan_draw_indexed_plan": self.vulkan_draw_indexed_plan,
            "vulkan_shader_ok": self.vulkan_shader_ok,
            "vulkan_spirv_generated": self.vulkan_spirv_generated,
            "vulkan_shader_compiler": self.vulkan_shader_compiler,
            "vulkan_shader_bytes": self.vulkan_shader_bytes,
            "vulkan_shader_modules": self.vulkan_shader_modules,
            "vulkan_pipeline_layout_ok": self.vulkan_pipeline_layout_ok,
            "vulkan_framebuffer_ok": self.vulkan_framebuffer_ok,
            "vulkan_graphics_pipeline_ok": self.vulkan_graphics_pipeline_ok,
            "vulkan_renderpass_begin_ok": self.vulkan_renderpass_begin_ok,
            "vulkan_draw_indexed_recorded": self.vulkan_draw_indexed_recorded,
        }


@dataclass
class ChunkRenderItem:
    coord: Tuple[int, int]
    handle: Any
    lod: str = "detail"  # detail | lod
    bounds_radius: float = 0.0


class RenderBackendBase:
    name = "base"

    def begin_frame(self) -> RenderFrameStats:
        return RenderFrameStats(backend=self.name)

    def end_frame(self) -> None:
        """Cierre de frame. Vulkan lo usara para submit/present."""
        pass

    def clear(self, config: Optional[FrameClearConfig] = None) -> None:
        raise NotImplementedError

    def configure_fog(self, config: FogConfig) -> None:
        raise NotImplementedError

    def draw_skybox(self, env_module: Any, px: float, py: float, pz: float, size: float = 300.0) -> None:
        raise NotImplementedError

    def project_to_screen(self, x: float, y: float, z: float):
        raise NotImplementedError

    def upload_chunk_mesh(self, mesh_data: Any) -> Any:
        raise NotImplementedError

    def register_gpu_handle(self, handle: Any) -> Any:
        return handle

    def draw_entity_static_mesh(self, buffer_data: Any, instance: Any) -> bool:
        """Ruta experimental Pre-R: dibuja entidad desde StaticMesh/InstanceData.

        Por defecto esta desactivada para conservar el estilo visual actual.
        Activar con JUEGO_STATIC_ENTITY_RENDER=1.
        """
        if not self.use_static_entity_renderer:
            return False
        try:
            from motor_juegos.entity_static_renderer import draw_entity_mesh_buffer
            ok = bool(draw_entity_mesh_buffer(buffer_data, instance))
            if ok:
                self.static_entity_draws += 1
            return ok
        except Exception:
            return False

    def draw_compiled_chunk(self, handle: Any) -> None:
        raise NotImplementedError

    def upload_entity_mesh(self, static_mesh: Any) -> Any:
        raise NotImplementedError

    def release_gpu_handle(self, handle: Any) -> None:
        raise NotImplementedError

    def is_chunk_visible(
        self,
        env_module,
        cx: int,
        cz: int,
        px: float,
        pz: float,
        lx: float,
        lz: float,
        *,
        size: float,
        max_distance: float,
        near_keep: Optional[float] = None,
        back_margin: Optional[float] = None,
    ) -> bool:
        kwargs = {"size": size, "max_distance": max_distance}
        if near_keep is not None:
            kwargs["near_keep"] = near_keep
        if back_margin is not None:
            kwargs["back_margin"] = back_margin
        return env_module.is_chunk_visible(cx, cz, px, pz, lx, lz, **kwargs)

    def shutdown(self) -> None:
        pass


class OpenGLRenderBackend(RenderBackendBase):
    """Backend actual. Envuelve las display lists de OpenGL.

    La idea es que el resto del juego empiece a pensar en 'handles de render'
    y no en llamadas directas a OpenGL. Vulkan luego reemplazara este archivo.
    """

    name = "opengl"

    def __init__(self):
        from motor_juegos.entity_mesh_buffers import EntityMeshBufferCache
        self.entity_mesh_cache = EntityMeshBufferCache()
        self.live_handles = set()
        self.live_mesh_bytes = 0
        self.neutral_mesh_created_total = 0
        self.neutral_mesh_released_total = 0
        self.uploads_this_frame = 0
        self.last_mesh_vertices = 0
        self.last_mesh_quads = 0
        self.last_mesh_indices = 0
        self.last_mesh_bytes = 0
        self.last_material_batches = 0
        self.use_static_entity_renderer = os.environ.get("JUEGO_STATIC_ENTITY_RENDER", "0").strip().lower() in ("1", "true", "yes", "on")
        self.static_entity_draws = 0

    def begin_frame(self) -> RenderFrameStats:
        stats = RenderFrameStats(backend=self.name)
        stats.uploads_frame = self.uploads_this_frame
        stats.mesh_vertices = self.last_mesh_vertices
        stats.mesh_quads = self.last_mesh_quads
        stats.mesh_indices = self.last_mesh_indices
        stats.mesh_bytes = self.last_mesh_bytes
        stats.material_batches = self.last_material_batches
        stats.live_mesh_handles = len(self.live_handles)
        stats.live_mesh_bytes = int(self.live_mesh_bytes)
        stats.neutral_mesh_created = int(self.neutral_mesh_created_total)
        stats.neutral_mesh_released = int(self.neutral_mesh_released_total)
        stats.static_entity_debug = 1 if self.use_static_entity_renderer else 0
        stats.entidades_staticmesh = self.static_entity_draws
        self.static_entity_draws = 0
        cache_stats = self.entity_mesh_cache.stats()
        stats.entity_mesh_cached = cache_stats.get("entity_mesh_cached", 0)
        stats.entity_mesh_uploads = cache_stats.get("entity_mesh_uploads", 0)
        stats.entity_mesh_vertices = cache_stats.get("entity_mesh_vertices", 0)
        stats.entity_mesh_indices = cache_stats.get("entity_mesh_indices", 0)
        stats.entity_mesh_bytes = cache_stats.get("entity_mesh_bytes", 0)
        self.uploads_this_frame = 0
        return stats

    def clear(self, config: Optional[FrameClearConfig] = None) -> None:
        # Puente Pre-T: main.py ya no llama glClear directamente.
        from motor_juegos.gl_legacy_bridge import clear_color_depth
        clear_color_depth()

    def configure_fog(self, config: FogConfig) -> None:
        from motor_juegos.gl_legacy_bridge import set_fog_range
        set_fog_range(config.start, config.end)

    def draw_skybox(self, env_module: Any, px: float, py: float, pz: float, size: float = 300.0) -> None:
        from motor_juegos.gl_legacy_bridge import draw_skybox_at_camera
        draw_skybox_at_camera(env_module, px, py, pz, size=size)

    def project_to_screen(self, x: float, y: float, z: float):
        from motor_juegos.gl_legacy_bridge import world_to_screen_legacy
        return world_to_screen_legacy(x, y, z)

    def register_gpu_handle(self, handle: Any) -> Any:
        if handle:
            self.live_handles.add(handle)
            try:
                self.live_mesh_bytes += int(getattr(handle, "byte_size", 0) or 0)
            except Exception:
                pass
        return handle

    def upload_chunk_mesh(self, mesh_data: Any) -> Any:
        # Import local para evitar ciclos al cargar motor_juegos.
        from motor_juegos import environment as env
        gl_handle = env.build_gpu_list_from_mesh_data(mesh_data)
        try:
            vertex_count = int(getattr(mesh_data, "vertex_count", 0))
            index_count = int(getattr(mesh_data, "index_count", 0))
            quad_count = int(getattr(mesh_data, "quad_count", 0))
            byte_size = int(mesh_data.byte_estimate()) if hasattr(mesh_data, "byte_estimate") else 0
            material_batches = len(getattr(mesh_data, "batches", {}) or {})
        except Exception:
            vertex_count = index_count = quad_count = byte_size = material_batches = 0
        handle = NeutralMeshHandle(
            backend=self.name,
            backend_handle=gl_handle,
            desc=NeutralBufferDesc(
                kind="chunk_mesh",
                vertex_count=vertex_count,
                index_count=index_count,
                byte_size=byte_size,
                material_batches=material_batches,
                transparent=False,
            ),
            label="chunk_mesh",
            coord=getattr(mesh_data, "coord", None),
            lod=str(getattr(mesh_data, "lod", "detail")),
        )
        self.register_gpu_handle(handle)
        self.uploads_this_frame += 1
        self.neutral_mesh_created_total += 1
        self.last_mesh_vertices = vertex_count
        self.last_mesh_indices = index_count
        self.last_mesh_quads = quad_count
        self.last_mesh_bytes = byte_size
        self.last_material_batches = material_batches
        return handle

    def upload_entity_mesh(self, static_mesh: Any) -> Any:
        # Pre-Q: OpenGL todavia renderiza entidades con funciones legacy, pero
        # ya convertimos sus StaticMesh a buffers neutrales y los dejamos cacheados.
        # Vulkan reemplazara este retorno por handles reales de VkBuffer.
        return self.entity_mesh_cache.get_or_build(static_mesh)

    def draw_compiled_chunk(self, handle: Any) -> None:
        # Import local para evitar ciclos al cargar motor_juegos.
        from motor_juegos import environment as env
        if handle:
            raw = getattr(handle, "backend_handle", handle)
            env.draw_compiled_chunk(raw)

    def release_gpu_handle(self, handle: Any) -> None:
        if not handle:
            return
        raw = getattr(handle, "backend_handle", handle)
        try:
            glDeleteLists(raw, 1)
        except Exception:
            pass
        if handle in self.live_handles:
            try:
                self.live_mesh_bytes = max(0, self.live_mesh_bytes - int(getattr(handle, "byte_size", 0) or 0))
            except Exception:
                pass
            self.neutral_mesh_released_total += 1
        self.live_handles.discard(handle)

    def shutdown(self) -> None:
        for handle in list(self.live_handles):
            self.release_gpu_handle(handle)
        self.live_handles.clear()


class VulkanRenderBackend(RenderBackendBase):
    """Backend Vulkan experimental Pre-W.

    Este backend todavia NO dibuja el juego. Su objetivo en esta etapa es:
    - probar si Python puede importar Vulkan,
    - crear/destruir una instancia Vulkan minima,
    - enumerar GPUs compatibles,
    - dejar clara la ruta para swapchain/buffers en etapas siguientes.

    OpenGL sigue siendo el backend jugable.
    """

    name = "vulkan_probe"

    def __init__(self):
        from motor_juegos.vulkan_bootstrap import probe_vulkan
        self.report = probe_vulkan(create_instance=True)
        self.last_error = self.report.error

    def begin_frame(self) -> RenderFrameStats:
        stats = RenderFrameStats(backend=self.name)
        stats.vulkan_probe_ok = 1 if self.report.ok else 0
        stats.vulkan_devices = int(self.report.physical_devices or 0)
        return stats

    def _not_ready(self, op: str):
        detail = self.report.summary() if hasattr(self.report, "summary") else "Vulkan probe sin reporte."
        raise RuntimeError(f"Vulkan Pre-W solo es probe/bootstrap; no puede ejecutar {op}. {detail}")

    def clear(self, config: Optional[FrameClearConfig] = None) -> None:
        self._not_ready("clear")

    def configure_fog(self, config: FogConfig) -> None:
        self._not_ready("configure_fog")

    def draw_skybox(self, env_module: Any, px: float, py: float, pz: float, size: float = 300.0) -> None:
        self._not_ready("draw_skybox")

    def project_to_screen(self, x: float, y: float, z: float):
        self._not_ready("project_to_screen")

    def upload_chunk_mesh(self, mesh_data: Any) -> Any:
        self._not_ready("upload_chunk_mesh")

    def upload_entity_mesh(self, static_mesh: Any) -> Any:
        self._not_ready("upload_entity_mesh")

    def draw_compiled_chunk(self, handle: Any) -> None:
        self._not_ready("draw_compiled_chunk")

    def draw_entity_static_mesh(self, buffer_data: Any, instance: Any) -> bool:
        return False

    def release_gpu_handle(self, handle: Any) -> None:
        pass



class VulkanTriangleProbeOpenGLBackend(OpenGLRenderBackend):
    """Stage31 Pre-Y: backend jugable OpenGL + prueba Vulkan de buffers.

    Mantiene el juego funcionando con OpenGL, pero al iniciar intenta crear
    device/buffers Vulkan para triangulo/quad. Esto permite avanzar hacia
    Vulkan sin dejar al juego injugable.
    """

    name = "opengl+vulkan_triangle_probe"

    def __init__(self):
        super().__init__()
        try:
            from motor_juegos.vulkan_triangle_probe import run_vulkan_triangle_probe
            self.vulkan_triangle_report = run_vulkan_triangle_probe()
            print("[Stage31 Pre-Y]", self.vulkan_triangle_report.summary())
        except Exception as exc:
            self.vulkan_triangle_report = None
            print("[Stage31 Pre-Y] Vulkan triangle probe no disponible:", exc)

    def begin_frame(self) -> RenderFrameStats:
        stats = super().begin_frame()
        stats.backend = self.name
        report = getattr(self, "vulkan_triangle_report", None)
        if report is not None:
            stats.vulkan_probe_ok = 1 if getattr(report, "python_package_available", False) else 0
            stats.vulkan_devices = int(getattr(report, "physical_devices", 0) or 0)
            stats.vulkan_triangle_ok = 1 if getattr(report, "ok", False) else 0
            stats.vulkan_triangle_buffers = int(getattr(report, "created_buffers", 0) or 0)
        return stats



class VulkanChunkUploadProbeOpenGLBackend(OpenGLRenderBackend):
    """Stage32 Vulkan A: backend jugable OpenGL + probe de buffers de chunk.

    Mantiene el juego funcionando con OpenGL. Al arrancar prueba la ruta de
    Vulkan para crear device y buffers tipo chunk. No reemplaza el render todavia.
    """

    name = "opengl+vulkan_chunk_upload_probe"

    def __init__(self):
        super().__init__()
        try:
            from motor_juegos.vulkan_chunk_probe import run_vulkan_chunk_upload_probe
            self.vulkan_chunk_report = run_vulkan_chunk_upload_probe([])
            print("[Stage32 Vulkan A]", self.vulkan_chunk_report.summary())
        except Exception as exc:
            self.vulkan_chunk_report = None
            print("[Stage32 Vulkan A] Vulkan chunk upload probe no disponible:", exc)

    def upload_chunk_mesh(self, mesh_data: Any) -> Any:
        # Prepara un plan neutral de subida para que el futuro backend Vulkan pueda
        # usar vertex/index buffers reales. OpenGL sigue subiendo como antes.
        try:
            from motor_juegos.vulkan_memory_upload import create_upload_plan_from_mesh_data
            self.last_vulkan_upload_plan = create_upload_plan_from_mesh_data(mesh_data, label="chunk_mesh")
        except Exception:
            self.last_vulkan_upload_plan = None
        return super().upload_chunk_mesh(mesh_data)

    def begin_frame(self) -> RenderFrameStats:
        stats = super().begin_frame()
        stats.backend = self.name
        report = getattr(self, "vulkan_chunk_report", None)
        if report is not None:
            stats.vulkan_probe_ok = 1 if getattr(report, "python_package_available", False) else 0
            stats.vulkan_devices = int(getattr(report, "physical_devices", 0) or 0)
            stats.vulkan_chunk_upload_ok = 1 if getattr(report, "ok", False) else 0
            stats.vulkan_chunk_buffers = int(getattr(report, "created_buffers", 0) or 0)
            stats.vulkan_upload_bytes = int(getattr(report, "upload_bytes_planned", 0) or 0)
        plan = getattr(self, "last_vulkan_upload_plan", None)
        if plan is not None:
            stats.vulkan_upload_bytes = int(getattr(plan, "total_bytes", 0) or 0)
            stats.vulkan_chunk_buffers = int(len(getattr(plan, "vertex_requests", []) or []) + len(getattr(plan, "index_requests", []) or []))
        return stats


class VulkanChunkMemoryProbeOpenGLBackend(OpenGLRenderBackend):
    """Stage32 Vulkan B: OpenGL jugable + probe de buffers con memoria.

    Esta ruta intenta crear VkBuffer, consultar requisitos, asignar memoria y
    hacer bind de memoria para buffers de chunk. No renderiza mundo con Vulkan aun.
    """

    name = "opengl+vulkan_chunk_memory_probe"

    def __init__(self):
        super().__init__()
        try:
            from motor_juegos.vulkan_chunk_memory_probe import run_vulkan_chunk_memory_probe
            self.vulkan_memory_report = run_vulkan_chunk_memory_probe([])
            print("[Stage32 Vulkan B]", self.vulkan_memory_report.summary())
        except Exception as exc:
            self.vulkan_memory_report = None
            print("[Stage32 Vulkan B] Vulkan memory probe no disponible:", exc)
        self.last_vulkan_upload_plan = None

    def upload_chunk_mesh(self, mesh_data: Any) -> Any:
        try:
            from motor_juegos.vulkan_memory_upload import create_upload_plan_from_mesh_data
            self.last_vulkan_upload_plan = create_upload_plan_from_mesh_data(mesh_data, label="chunk_mesh")
        except Exception:
            self.last_vulkan_upload_plan = None
        return super().upload_chunk_mesh(mesh_data)

    def begin_frame(self) -> RenderFrameStats:
        stats = super().begin_frame()
        stats.backend = self.name
        report = getattr(self, "vulkan_memory_report", None)
        if report is not None:
            stats.vulkan_probe_ok = 1 if getattr(report, "python_package_available", False) else 0
            stats.vulkan_devices = int(getattr(report, "physical_devices", 0) or 0)
            stats.vulkan_chunk_upload_ok = 1 if getattr(report, "ok", False) else 0
            stats.vulkan_memory_ok = 1 if getattr(report, "ok", False) else 0
            stats.vulkan_chunk_buffers = int(getattr(report, "buffers_created", 0) or 0)
            stats.vulkan_memory_bound = int(getattr(report, "buffers_bound", 0) or 0)
            stats.vulkan_alloc_kb = int(getattr(report, "allocated_bytes", 0) or 0) // 1024
            stats.vulkan_upload_bytes = int(getattr(report, "upload_bytes_planned", 0) or 0)
        plan = getattr(self, "last_vulkan_upload_plan", None)
        if plan is not None:
            stats.vulkan_upload_bytes = int(getattr(plan, "total_bytes", 0) or 0)
            stats.vulkan_chunk_buffers = int(len(getattr(plan, "vertex_requests", []) or []) + len(getattr(plan, "index_requests", []) or []))
        return stats


class VulkanStagingUploadProbeOpenGLBackend(OpenGLRenderBackend):
    """Stage32 Vulkan C: OpenGL jugable + probe de staging/upload.

    Prueba buffers HOST_VISIBLE/HOST_COHERENT, vkMapMemory y escritura de bytes
    de prueba. Todavia no ejecuta command buffers ni presenta Vulkan.
    """

    name = "opengl+vulkan_staging_upload_probe"

    def __init__(self):
        super().__init__()
        try:
            from motor_juegos.vulkan_staging_upload_probe import run_vulkan_staging_upload_probe
            self.vulkan_staging_report = run_vulkan_staging_upload_probe([])
            print("[Stage32 Vulkan C]", self.vulkan_staging_report.summary())
        except Exception as exc:
            self.vulkan_staging_report = None
            print("[Stage32 Vulkan C] Vulkan staging/upload probe no disponible:", exc)
        self.last_vulkan_upload_plan = None

    def upload_chunk_mesh(self, mesh_data: Any) -> Any:
        try:
            from motor_juegos.vulkan_memory_upload import create_upload_plan_from_mesh_data
            self.last_vulkan_upload_plan = create_upload_plan_from_mesh_data(mesh_data, label="chunk_mesh")
        except Exception:
            self.last_vulkan_upload_plan = None
        return super().upload_chunk_mesh(mesh_data)

    def begin_frame(self) -> RenderFrameStats:
        stats = super().begin_frame()
        stats.backend = self.name
        report = getattr(self, "vulkan_staging_report", None)
        if report is not None:
            stats.vulkan_probe_ok = 1 if getattr(report, "python_package_available", False) else 0
            stats.vulkan_devices = int(getattr(report, "physical_devices", 0) or 0)
            stats.vulkan_chunk_upload_ok = 1 if getattr(report, "ok", False) else 0
            stats.vulkan_memory_ok = 1 if getattr(report, "ok", False) else 0
            stats.vulkan_staging_ok = 1 if getattr(report, "ok", False) else 0
            stats.vulkan_chunk_buffers = int(getattr(report, "buffers_created", 0) or 0)
            stats.vulkan_memory_bound = int(getattr(report, "buffers_bound", 0) or 0)
            stats.vulkan_staging_mapped = int(getattr(report, "mapped_allocations", 0) or 0)
            stats.vulkan_staging_write_kb = int(getattr(report, "bytes_written", 0) or 0) // 1024
            stats.vulkan_alloc_kb = int(getattr(report, "allocated_bytes", 0) or 0) // 1024
            stats.vulkan_upload_bytes = int(getattr(report, "upload_bytes_planned", 0) or 0)
        plan = getattr(self, "last_vulkan_upload_plan", None)
        if plan is not None:
            stats.vulkan_upload_bytes = int(getattr(plan, "total_bytes", 0) or 0)
            stats.vulkan_chunk_buffers = int(len(getattr(plan, "vertex_requests", []) or []) + len(getattr(plan, "index_requests", []) or []))
        return stats


class VulkanCommandCopyProbeOpenGLBackend(OpenGLRenderBackend):
    """Stage32 Vulkan D: OpenGL jugable + probe de command buffer/copy buffer.

    Prueba command pool, command buffer, vkCmdCopyBuffer y queue submit.
    Todavia no renderiza ni presenta frames con Vulkan.
    """

    name = "opengl+vulkan_command_copy_probe"

    def __init__(self):
        super().__init__()
        try:
            from motor_juegos.vulkan_command_copy_probe import run_vulkan_command_copy_probe
            self.vulkan_command_report = run_vulkan_command_copy_probe([])
            print("[Stage32 Vulkan D]", self.vulkan_command_report.summary())
        except Exception as exc:
            self.vulkan_command_report = None
            print("[Stage32 Vulkan D] Vulkan command/copy probe no disponible:", exc)
        self.last_vulkan_upload_plan = None

    def upload_chunk_mesh(self, mesh_data: Any) -> Any:
        try:
            from motor_juegos.vulkan_memory_upload import create_upload_plan_from_mesh_data
            self.last_vulkan_upload_plan = create_upload_plan_from_mesh_data(mesh_data, label="chunk_mesh")
        except Exception:
            self.last_vulkan_upload_plan = None
        return super().upload_chunk_mesh(mesh_data)

    def begin_frame(self) -> RenderFrameStats:
        stats = super().begin_frame()
        stats.backend = self.name
        report = getattr(self, "vulkan_command_report", None)
        if report is not None:
            stats.vulkan_probe_ok = 1 if getattr(report, "python_package_available", False) else 0
            stats.vulkan_devices = int(getattr(report, "physical_devices", 0) or 0)
            stats.vulkan_chunk_upload_ok = 1 if getattr(report, "ok", False) else 0
            stats.vulkan_memory_ok = 1 if getattr(report, "ok", False) else 0
            stats.vulkan_command_ok = 1 if getattr(report, "ok", False) else 0
            stats.vulkan_chunk_buffers = int(getattr(report, "buffers_created", 0) or 0)
            stats.vulkan_memory_bound = int(getattr(report, "buffers_bound", 0) or 0)
            stats.vulkan_staging_mapped = int(getattr(report, "mapped_allocations", 0) or 0)
            stats.vulkan_staging_write_kb = int(getattr(report, "bytes_written", 0) or 0) // 1024
            stats.vulkan_alloc_kb = int(getattr(report, "allocated_bytes", 0) or 0) // 1024
            stats.vulkan_command_buffers = int(getattr(report, "command_buffers_allocated", 0) or 0)
            stats.vulkan_copy_commands = int(getattr(report, "copy_commands_recorded", 0) or 0)
            stats.vulkan_submits = int(getattr(report, "submits", 0) or 0)
            stats.vulkan_upload_bytes = int(getattr(report, "upload_bytes_planned", 0) or 0)
        plan = getattr(self, "last_vulkan_upload_plan", None)
        if plan is not None:
            stats.vulkan_upload_bytes = int(getattr(plan, "total_bytes", 0) or 0)
            stats.vulkan_chunk_buffers = int(len(getattr(plan, "vertex_requests", []) or []) + len(getattr(plan, "index_requests", []) or []))
        return stats


class VulkanDrawProbeOpenGLBackend(OpenGLRenderBackend):
    """Stage32 Vulkan F: OpenGL jugable + probe de draw indexed/pipeline plan.

    Esta ruta intenta crear instancia/device/queue y valida que ya existe un plan de
    render pass, pipeline y drawIndexed. Todavia no presenta imagen Vulkan en pantalla.
    """

    name = "opengl+vulkan_draw_probe"

    def __init__(self):
        super().__init__()
        try:
            from motor_juegos.vulkan_draw_probe import run_vulkan_draw_probe
            self.vulkan_draw_report = run_vulkan_draw_probe()
            print("[Stage32 Vulkan F]", self.vulkan_draw_report.summary())
        except Exception as exc:
            self.vulkan_draw_report = None
            print("[Stage32 Vulkan F] Vulkan draw probe no disponible:", exc)
        self.last_vulkan_upload_plan = None

    def upload_chunk_mesh(self, mesh_data: Any) -> Any:
        try:
            from motor_juegos.vulkan_memory_upload import create_upload_plan_from_mesh_data
            self.last_vulkan_upload_plan = create_upload_plan_from_mesh_data(mesh_data, label="chunk_mesh")
        except Exception:
            self.last_vulkan_upload_plan = None
        return super().upload_chunk_mesh(mesh_data)

    def begin_frame(self) -> RenderFrameStats:
        stats = super().begin_frame()
        stats.backend = self.name
        report = getattr(self, "vulkan_draw_report", None)
        if report is not None:
            stats.vulkan_probe_ok = 1 if getattr(report, "vulkan_imported", False) else 0
            stats.vulkan_devices = int(getattr(report, "physical_devices", 0) or 0)
            stats.vulkan_draw_ok = 1 if getattr(report, "ok", False) else 0
            stats.vulkan_render_pass_plan = 1 if getattr(report, "render_pass_plan", False) else 0
            stats.vulkan_pipeline_plan = 1 if getattr(report, "graphics_pipeline_plan", False) else 0
            stats.vulkan_draw_indexed_plan = 1 if getattr(report, "draw_indexed_plan", False) else 0
        plan = getattr(self, "last_vulkan_upload_plan", None)
        if plan is not None:
            stats.vulkan_upload_bytes = int(getattr(plan, "total_bytes", 0) or 0)
            stats.vulkan_chunk_buffers = int(len(getattr(plan, "vertex_requests", []) or []) + len(getattr(plan, "index_requests", []) or []))
        return stats


class VulkanShaderProbeOpenGLBackend(OpenGLRenderBackend):
    """Stage32 Vulkan G: OpenGL jugable + prueba de shaders/SPIR-V.

    Valida fuentes GLSL 450 minimas para Vulkan y, si existe glslangValidator
    o glslc en la PC, genera SPIR-V para el pipeline experimental.
    """

    name = "opengl+vulkan_shader_probe"

    def __init__(self):
        super().__init__()
        try:
            from motor_juegos.vulkan_shader_probe import run_vulkan_shader_probe
            self.vulkan_shader_report = run_vulkan_shader_probe(write_assets=True)
            print("[Stage32 Vulkan G]", self.vulkan_shader_report.summary())
        except Exception as exc:
            self.vulkan_shader_report = None
            print("[Stage32 Vulkan G] Vulkan shader probe no disponible:", exc)

    def begin_frame(self) -> RenderFrameStats:
        stats = super().begin_frame()
        stats.backend = self.name
        report = getattr(self, "vulkan_shader_report", None)
        if report is not None:
            stats.vulkan_probe_ok = 1 if getattr(report, "vulkan_imported", False) else 0
            stats.vulkan_devices = int(getattr(report, "physical_devices", 0) or 0)
            stats.vulkan_shader_ok = 1 if getattr(report, "ok", False) else 0
            stats.vulkan_spirv_generated = 1 if getattr(report, "spirv_generated", False) else 0
            stats.vulkan_shader_compiler = 1 if getattr(report, "compiler_found", False) else 0
            stats.vulkan_shader_bytes = int(getattr(report, "vertex_spirv_bytes", 0) or 0) + int(getattr(report, "fragment_spirv_bytes", 0) or 0)
        return stats


class VulkanShaderModuleProbeOpenGLBackend(OpenGLRenderBackend):
    """Stage32 Vulkan H: OpenGL jugable + prueba de VkShaderModule/PipelineLayout.

    Reutiliza los shaders SPIR-V de Stage32 Vulkan G. Si existe glslangValidator
    o glslc, intenta generar SPIR-V y crear VkShaderModule + VkPipelineLayout.
    """

    name = "opengl+vulkan_shader_module_probe"

    def __init__(self):
        super().__init__()
        try:
            from motor_juegos.vulkan_shader_module_probe import run_vulkan_shader_module_probe
            self.vulkan_shader_module_report = run_vulkan_shader_module_probe()
            print("[Stage32 Vulkan H]", self.vulkan_shader_module_report.summary())
        except Exception as exc:
            self.vulkan_shader_module_report = None
            print("[Stage32 Vulkan H] Vulkan shader module probe no disponible:", exc)

    def begin_frame(self) -> RenderFrameStats:
        stats = super().begin_frame()
        stats.backend = self.name
        report = getattr(self, "vulkan_shader_module_report", None)
        if report is not None:
            stats.vulkan_probe_ok = 1 if getattr(report, "vulkan_imported", False) else 0
            stats.vulkan_devices = int(getattr(report, "physical_devices", 0) or 0)
            stats.vulkan_shader_ok = 1 if getattr(report, "ok", False) else 0
            stats.vulkan_spirv_generated = 1 if getattr(report, "spirv_generated", False) else 0
            stats.vulkan_shader_compiler = 1 if getattr(report, "compiler_found", False) else 0
            stats.vulkan_shader_bytes = int(getattr(report, "vertex_spirv_bytes", 0) or 0) + int(getattr(report, "fragment_spirv_bytes", 0) or 0)
            stats.vulkan_shader_modules = int(getattr(report, "shader_modules_created", 0) or 0)
            stats.vulkan_pipeline_layout_ok = 1 if getattr(report, "pipeline_layout_created", False) else 0
            stats.vulkan_pipeline_plan = stats.vulkan_pipeline_layout_ok
        return stats


class VulkanFramebufferDrawProbeOpenGLBackend(OpenGLRenderBackend):
    """Stage32 Vulkan J: prueba offscreen de framebuffer + command buffer + drawIndexed.

    OpenGL sigue dibujando el juego. Vulkan solo valida que ya podemos crear
    render pass, framebuffer, pipeline y grabar un drawIndexed experimental.
    """

    name = "opengl+vulkan_framebuffer_draw_probe"

    def __init__(self):
        super().__init__()
        try:
            from motor_juegos.vulkan_framebuffer_draw_probe import run_vulkan_framebuffer_draw_probe
            self.vulkan_framebuffer_draw_report = run_vulkan_framebuffer_draw_probe()
            print("[Stage32 Vulkan J]", self.vulkan_framebuffer_draw_report.summary())
        except Exception as exc:
            self.vulkan_framebuffer_draw_report = None
            print("[Stage32 Vulkan J] Vulkan framebuffer/draw probe no disponible:", exc)

    def begin_frame(self) -> RenderFrameStats:
        stats = super().begin_frame()
        stats.backend = self.name
        report = getattr(self, "vulkan_framebuffer_draw_report", None)
        if report is not None:
            stats.vulkan_probe_ok = 1 if getattr(report, "vulkan_imported", False) else 0
            stats.vulkan_devices = int(getattr(report, "physical_devices", 0) or 0)
            stats.vulkan_shader_ok = 1 if getattr(report, "spirv_generated", False) else 0
            stats.vulkan_spirv_generated = 1 if getattr(report, "spirv_generated", False) else 0
            stats.vulkan_shader_compiler = 1 if getattr(report, "compiler_found", False) else 0
            stats.vulkan_shader_bytes = int(getattr(report, "vertex_spirv_bytes", 0) or 0) + int(getattr(report, "fragment_spirv_bytes", 0) or 0)
            stats.vulkan_shader_modules = int(getattr(report, "shader_modules_created", 0) or 0)
            stats.vulkan_pipeline_layout_ok = 1 if getattr(report, "pipeline_layout_created", False) else 0
            stats.vulkan_render_pass_plan = 1 if getattr(report, "render_pass_created", False) else 0
            stats.vulkan_framebuffer_ok = 1 if getattr(report, "framebuffer_created", False) else 0
            stats.vulkan_pipeline_plan = 1 if getattr(report, "graphics_pipeline_created", False) else 0
            stats.vulkan_graphics_pipeline_ok = 1 if getattr(report, "graphics_pipeline_created", False) else 0
            stats.vulkan_command_ok = 1 if getattr(report, "command_pool_created", False) else 0
            stats.vulkan_command_buffers = int(getattr(report, "command_buffers_allocated", 0) or 0)
            stats.vulkan_renderpass_begin_ok = 1 if getattr(report, "render_pass_begun", False) else 0
            stats.vulkan_draw_indexed_plan = 1 if getattr(report, "draw_indexed_recorded", False) else 0
            stats.vulkan_draw_indexed_recorded = 1 if getattr(report, "draw_indexed_recorded", False) else 0
            stats.vulkan_draw_ok = 1 if getattr(report, "ok", False) else 0
            stats.vulkan_memory_ok = 1 if getattr(report, "color_memory_bound", False) else 0
            stats.vulkan_memory_bound = 1 if getattr(report, "color_memory_bound", False) else 0
            stats.vulkan_alloc_kb = int(getattr(report, "allocated_kb", 0) or 0)
        return stats

def create_render_backend(kind: str = "opengl") -> RenderBackendBase:
    kind = (kind or "opengl").lower().strip()
    if kind in ("opengl", "gl"):
        return OpenGLRenderBackend()
    if kind in ("vulkan_probe", "vk_probe", "probe"):
        return VulkanRenderBackend()
    if kind in ("vulkan_triangle", "vk_triangle", "triangle", "vulkan_quad", "vk_quad"):
        return VulkanTriangleProbeOpenGLBackend()
    if kind in ("vulkan_chunk", "vk_chunk", "vulkan_upload", "vk_upload", "chunk_upload"):
        return VulkanChunkUploadProbeOpenGLBackend()
    if kind in ("vulkan_memory", "vk_memory", "vulkan_chunk_memory", "vk_chunk_memory", "chunk_memory"):
        return VulkanChunkMemoryProbeOpenGLBackend()
    if kind in ("vulkan_staging", "vk_staging", "vulkan_upload_map", "vk_upload_map", "staging_upload"):
        return VulkanStagingUploadProbeOpenGLBackend()
    if kind in ("vulkan_command", "vk_command", "vulkan_copy", "vk_copy", "command_copy", "copy_buffer"):
        return VulkanCommandCopyProbeOpenGLBackend()
    if kind in ("vulkan_draw", "vk_draw", "vulkan_pipeline_draw", "vk_pipeline_draw", "draw_probe"):
        return VulkanDrawProbeOpenGLBackend()
    if kind in ("vulkan_shader", "vk_shader", "vulkan_spirv", "vk_spirv", "shader_probe"):
        return VulkanShaderProbeOpenGLBackend()
    if kind in ("vulkan_shader_module", "vk_shader_module", "vulkan_shader_modules", "vk_shader_modules", "shader_module", "shader_modules", "vulkan_layout", "vk_layout"):
        return VulkanShaderModuleProbeOpenGLBackend()
    if kind in ("vulkan_framebuffer", "vk_framebuffer", "vulkan_draw_indexed", "vk_draw_indexed", "vulkan_framebuffer_draw", "vk_framebuffer_draw", "framebuffer_draw"):
        return VulkanFramebufferDrawProbeOpenGLBackend()
    if kind in ("vulkan", "vk"):
        # Pre-W: Vulkan real aun no es jugable. Para no romper el juego,
        # se usa OpenGL y se permite probar Vulkan con JUEGO_RENDER_BACKEND=vulkan_probe.
        print("[Stage31 Pre-W] Vulkan real aun no esta listo; usando OpenGL. Usa JUEGO_RENDER_BACKEND=vulkan_probe para solo probar Vulkan.")
        return OpenGLRenderBackend()
    raise ValueError(f"Backend de render desconocido: {kind}")
