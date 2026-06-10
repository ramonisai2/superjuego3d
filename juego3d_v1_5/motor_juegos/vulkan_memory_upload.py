"""Stage32 Vulkan A: planificador de subida de MeshData a buffers Vulkan.

Este modulo NO reemplaza el render OpenGL. Convierte MeshData neutral del motor
(chunks, entidades, etc.) en solicitudes de buffers que un backend Vulkan puede
subir despues a VkBuffer/VkDeviceMemory.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple
import struct


@dataclass
class VulkanBufferRequest:
    label: str
    usage: str  # vertex | index | staging
    byte_size: int
    item_count: int = 0
    material: str = "default"


@dataclass
class VulkanUploadPlan:
    label: str
    vertex_requests: List[VulkanBufferRequest] = field(default_factory=list)
    index_requests: List[VulkanBufferRequest] = field(default_factory=list)
    total_vertex_bytes: int = 0
    total_index_bytes: int = 0
    total_vertices: int = 0
    total_indices: int = 0
    batches: int = 0

    @property
    def total_bytes(self) -> int:
        return int(self.total_vertex_bytes + self.total_index_bytes)

    def summary(self) -> str:
        return (
            f"{self.label}: batches={self.batches} vertices={self.total_vertices} "
            f"indices={self.total_indices} bytes={self.total_bytes}"
        )


@dataclass
class VulkanMemoryStats:
    plans: int = 0
    vertex_buffers: int = 0
    index_buffers: int = 0
    total_vertices: int = 0
    total_indices: int = 0
    total_bytes: int = 0

    def as_dict(self) -> Dict[str, int]:
        return {
            "vk_upload_plans": self.plans,
            "vk_vertex_buffers": self.vertex_buffers,
            "vk_index_buffers": self.index_buffers,
            "vk_upload_vertices": self.total_vertices,
            "vk_upload_indices": self.total_indices,
            "vk_upload_bytes": self.total_bytes,
        }


def _estimate_batch_counts(batch: Any) -> Tuple[int, int, int, int]:
    vertices = getattr(batch, "vertices", []) or []
    indices = getattr(batch, "indices", []) or []
    vertex_count = len(vertices)
    index_count = len(indices)
    # Pos(3) + Color(4) por ahora. En Vulkan real esto sera VertexLayout.
    vertex_bytes = vertex_count * 7 * 4
    index_bytes = index_count * 4
    return vertex_count, index_count, vertex_bytes, index_bytes


def create_upload_plan_from_mesh_data(mesh_data: Any, label: str = "chunk_mesh") -> VulkanUploadPlan:
    plan = VulkanUploadPlan(label=label)
    batches = getattr(mesh_data, "batches", {}) or {}
    for material, batch in batches.items():
        v_count, i_count, v_bytes, i_bytes = _estimate_batch_counts(batch)
        if v_count:
            plan.vertex_requests.append(VulkanBufferRequest(
                label=f"{label}:{material}:vertex",
                usage="vertex",
                byte_size=v_bytes,
                item_count=v_count,
                material=str(material),
            ))
        if i_count:
            plan.index_requests.append(VulkanBufferRequest(
                label=f"{label}:{material}:index",
                usage="index",
                byte_size=i_bytes,
                item_count=i_count,
                material=str(material),
            ))
        plan.total_vertices += v_count
        plan.total_indices += i_count
        plan.total_vertex_bytes += v_bytes
        plan.total_index_bytes += i_bytes
    plan.batches = len(batches)
    return plan


def accumulate_upload_stats(plans: List[VulkanUploadPlan]) -> VulkanMemoryStats:
    stats = VulkanMemoryStats(plans=len(plans))
    for plan in plans:
        stats.vertex_buffers += len(plan.vertex_requests)
        stats.index_buffers += len(plan.index_requests)
        stats.total_vertices += plan.total_vertices
        stats.total_indices += plan.total_indices
        stats.total_bytes += plan.total_bytes
    return stats
