"""API neutral de render previa a Vulkan.

Stage31 Pre-T:
- Define una interfaz estricta que OpenGL implementa ahora.
- Vulkan debera implementar la misma API despues.
- El objetivo es que main.py dependa menos de OpenGL/GLU y mas de RendererBackend.
"""

from dataclasses import dataclass
from typing import Any, Optional, Tuple, Protocol


@dataclass
class FrameClearConfig:
    color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)
    clear_color: bool = True
    clear_depth: bool = True


@dataclass
class FogConfig:
    color: Tuple[float, float, float] = (0.75, 0.88, 1.0)
    start: float = 60.0
    end: float = 180.0


@dataclass
class CameraSnapshot:
    px: float
    py: float
    pz: float
    lx: float
    ly: float
    lz: float
    fov: float
    aspect: float
    near: float = 0.1
    far: float = 400.0


class RendererBackendAPI(Protocol):
    """Contrato que deberan cumplir OpenGLRenderer y VulkanRenderer."""

    name: str

    def begin_frame(self) -> Any: ...
    def end_frame(self) -> None: ...
    def clear(self, config: Optional[FrameClearConfig] = None) -> None: ...
    def configure_fog(self, config: FogConfig) -> None: ...
    def draw_skybox(self, env_module: Any, px: float, py: float, pz: float, size: float = 300.0) -> None: ...
    def project_to_screen(self, x: float, y: float, z: float) -> Optional[Tuple[int, int]]: ...
    def upload_chunk_mesh(self, mesh_data: Any) -> Any: ...
    def draw_compiled_chunk(self, handle: Any) -> None: ...
    def upload_entity_mesh(self, static_mesh: Any) -> Any: ...
    def draw_entity_static_mesh(self, buffer_data: Any, instance: Any) -> bool: ...
    def release_gpu_handle(self, handle: Any) -> None: ...
    def shutdown(self) -> None: ...
