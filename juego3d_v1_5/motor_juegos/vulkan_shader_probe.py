
"""Stage32 Vulkan G - Shader/SPIR-V probe.

Esta prueba NO reemplaza el render jugable. Sirve para validar que la ruta Vulkan
ya tiene una pareja de shaders minima y que, si hay herramientas instaladas,
puede producir SPIR-V para el pipeline grafico.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

VERT_GLSL = """#version 450
layout(location = 0) in vec2 in_pos;
layout(location = 1) in vec3 in_color;
layout(location = 0) out vec3 frag_color;
void main() {
    frag_color = in_color;
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
"""

FRAG_GLSL = """#version 450
layout(location = 0) in vec3 frag_color;
layout(location = 0) out vec4 out_color;
void main() {
    out_color = vec4(frag_color, 1.0);
}
"""


@dataclass
class VulkanShaderProbeReport:
    ok: bool = False
    vulkan_imported: bool = False
    physical_devices: int = 0
    shader_sources_ready: bool = False
    compiler_found: bool = False
    compiler_name: str = "none"
    spirv_generated: bool = False
    vertex_spirv_bytes: int = 0
    fragment_spirv_bytes: int = 0
    errors: str = ""

    def to_dict(self):
        return asdict(self)

    def summary(self) -> str:
        return (
            f"ok={int(self.ok)} vk={int(self.vulkan_imported)} dev={self.physical_devices} "
            f"src={int(self.shader_sources_ready)} compiler={self.compiler_name} "
            f"spirv={int(self.spirv_generated)} vs={self.vertex_spirv_bytes} fs={self.fragment_spirv_bytes}"
        )


def _probe_vulkan(report: VulkanShaderProbeReport) -> None:
    try:
        import vulkan as vk  # type: ignore
        report.vulkan_imported = True
        app = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO Stage32 Vulkan G Shader Probe",
            applicationVersion=1,
            pEngineName="JUEGO Vulkan Prep",
            engineVersion=1,
            apiVersion=vk.VK_API_VERSION_1_0,
        )
        info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app,
        )
        instance = vk.vkCreateInstance(info, None)
        try:
            devices = vk.vkEnumeratePhysicalDevices(instance)
            report.physical_devices = len(devices or [])
        finally:
            vk.vkDestroyInstance(instance, None)
    except Exception as exc:
        report.errors += f"vulkan:{exc}; "


def _find_compiler() -> tuple[str, str | None]:
    # Preferimos glslangValidator porque genera SPIR-V directamente desde GLSL.
    glslang = shutil.which("glslangValidator")
    if glslang:
        return "glslangValidator", glslang
    glslc = shutil.which("glslc")
    if glslc:
        return "glslc", glslc
    return "none", None


def _compile_with_tool(tool_name: str, tool_path: str, stage: str, src: Path, out: Path) -> None:
    if tool_name == "glslangValidator":
        cmd = [tool_path, "-V", "-S", stage, str(src), "-o", str(out)]
    elif tool_name == "glslc":
        # glslc detecta etapa por extension; usamos extension .vert/.frag.
        cmd = [tool_path, str(src), "-o", str(out)]
    else:
        raise RuntimeError("No shader compiler available")
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def run_vulkan_shader_probe(write_assets: bool = True) -> VulkanShaderProbeReport:
    report = VulkanShaderProbeReport(shader_sources_ready=True)
    _probe_vulkan(report)
    compiler_name, compiler_path = _find_compiler()
    report.compiler_name = compiler_name
    report.compiler_found = compiler_path is not None

    try:
        if write_assets:
            asset_dir = Path(__file__).resolve().parent.parent / "assets" / "shaders" / "vulkan_probe"
            asset_dir.mkdir(parents=True, exist_ok=True)
            (asset_dir / "probe.vert").write_text(VERT_GLSL, encoding="utf-8")
            (asset_dir / "probe.frag").write_text(FRAG_GLSL, encoding="utf-8")
        else:
            asset_dir = Path(tempfile.mkdtemp(prefix="juego_vk_shader_probe_"))
            (asset_dir / "probe.vert").write_text(VERT_GLSL, encoding="utf-8")
            (asset_dir / "probe.frag").write_text(FRAG_GLSL, encoding="utf-8")

        if compiler_path:
            vert_out = asset_dir / "probe.vert.spv"
            frag_out = asset_dir / "probe.frag.spv"
            _compile_with_tool(compiler_name, compiler_path, "vert", asset_dir / "probe.vert", vert_out)
            _compile_with_tool(compiler_name, compiler_path, "frag", asset_dir / "probe.frag", frag_out)
            report.vertex_spirv_bytes = vert_out.stat().st_size if vert_out.exists() else 0
            report.fragment_spirv_bytes = frag_out.stat().st_size if frag_out.exists() else 0
            report.spirv_generated = report.vertex_spirv_bytes > 0 and report.fragment_spirv_bytes > 0
    except subprocess.CalledProcessError as exc:
        report.errors += f"compile:{exc.stderr or exc}; "
    except Exception as exc:
        report.errors += f"shader:{exc}; "

    # ok significa: hay Vulkan disponible y fuentes listas; si hay compilador, SPIR-V debe generarse.
    report.ok = bool(report.vulkan_imported and report.shader_sources_ready and (not report.compiler_found or report.spirv_generated))
    return report


if __name__ == "__main__":
    print(run_vulkan_shader_probe().to_dict())
