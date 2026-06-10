"""Stage32 Vulkan J - framebuffer + command buffer + drawIndexed probe.

Esta prueba mantiene OpenGL como render jugable. Valida si Vulkan puede crear
la cadena minima offscreen para grabar un drawIndexed: render pass, imagen de
color, image view, framebuffer, shader modules, pipeline layout, pipeline,
command pool/buffer y comando vkCmdDrawIndexed.

No presenta imagen en pantalla todavia: es un paso de verificacion tecnica.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
import struct

from motor_juegos.vulkan_shader_probe import run_vulkan_shader_probe


@dataclass
class VulkanFramebufferDrawProbeReport:
    ok: bool = False
    vulkan_imported: bool = False
    physical_devices: int = 0
    spirv_generated: bool = False
    compiler_found: bool = False
    vertex_spirv_bytes: int = 0
    fragment_spirv_bytes: int = 0
    shader_modules_created: int = 0
    pipeline_layout_created: bool = False
    render_pass_created: bool = False
    color_image_created: bool = False
    color_memory_bound: bool = False
    image_view_created: bool = False
    framebuffer_created: bool = False
    graphics_pipeline_created: bool = False
    command_pool_created: bool = False
    command_buffers_allocated: int = 0
    render_pass_begun: bool = False
    draw_indexed_recorded: bool = False
    allocated_kb: int = 0
    errors: str = ""

    def to_dict(self):
        return asdict(self)

    def summary(self) -> str:
        return (
            f"ok={int(self.ok)} vk={int(self.vulkan_imported)} dev={self.physical_devices} "
            f"spv={int(self.spirv_generated)} mods={self.shader_modules_created} "
            f"rp={int(self.render_pass_created)} fb={int(self.framebuffer_created)} "
            f"pipe={int(self.graphics_pipeline_created)} cmd={self.command_buffers_allocated} "
            f"drawIdx={int(self.draw_indexed_recorded)} allocKB={self.allocated_kb}"
        )


def _spv_u32_words(path: Path) -> list[int]:
    data = path.read_bytes()
    if len(data) % 4 != 0:
        raise RuntimeError(f"SPIR-V invalido, tamano no multiplo de 4: {path}")
    words = list(struct.unpack("<" + "I" * (len(data) // 4), data))
    if not words or words[0] != 0x07230203:
        raise RuntimeError(f"SPIR-V magic invalido en {path}")
    return words


def _asset_spv_paths() -> tuple[Path, Path]:
    asset_dir = Path(__file__).resolve().parent.parent / "assets" / "shaders" / "vulkan_probe"
    return asset_dir / "probe.vert.spv", asset_dir / "probe.frag.spv"


def _find_memory_type(vk, physical_device, type_filter: int, properties: int) -> int:
    mem_props = vk.vkGetPhysicalDeviceMemoryProperties(physical_device)
    for i in range(mem_props.memoryTypeCount):
        if (type_filter & (1 << i)) and (mem_props.memoryTypes[i].propertyFlags & properties) == properties:
            return i
    raise RuntimeError("No se encontro tipo de memoria Vulkan compatible")


def run_vulkan_framebuffer_draw_probe(width: int = 256, height: int = 256) -> VulkanFramebufferDrawProbeReport:
    report = VulkanFramebufferDrawProbeReport()

    shader_report = run_vulkan_shader_probe(write_assets=True)
    report.vulkan_imported = bool(shader_report.vulkan_imported)
    report.physical_devices = int(shader_report.physical_devices or 0)
    report.spirv_generated = bool(shader_report.spirv_generated)
    report.compiler_found = bool(shader_report.compiler_found)
    report.vertex_spirv_bytes = int(shader_report.vertex_spirv_bytes or 0)
    report.fragment_spirv_bytes = int(shader_report.fragment_spirv_bytes or 0)
    if shader_report.errors:
        report.errors += f"shaderG:{shader_report.errors}; "

    try:
        import vulkan as vk  # type: ignore
        report.vulkan_imported = True

        app = vk.VkApplicationInfo(
            sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName="JUEGO Stage32 Vulkan J Framebuffer Draw Probe",
            applicationVersion=1,
            pEngineName="JUEGO Vulkan Prep",
            engineVersion=1,
            apiVersion=vk.VK_API_VERSION_1_0,
        )
        instance_info = vk.VkInstanceCreateInfo(
            sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            pApplicationInfo=app,
        )
        instance = vk.vkCreateInstance(instance_info, None)

        device = None
        render_pass = None
        pipeline_layout = None
        vert_module = None
        frag_module = None
        pipeline = None
        color_image = None
        color_memory = None
        image_view = None
        framebuffer = None
        command_pool = None
        command_buffer = None

        try:
            physical_devices = vk.vkEnumeratePhysicalDevices(instance)
            report.physical_devices = len(physical_devices or [])
            if not physical_devices:
                raise RuntimeError("No hay GPU Vulkan disponible")
            physical_device = physical_devices[0]

            queue_families = vk.vkGetPhysicalDeviceQueueFamilyProperties(physical_device)
            graphics_index: Optional[int] = None
            for i, q in enumerate(queue_families or []):
                if q.queueFlags & vk.VK_QUEUE_GRAPHICS_BIT:
                    graphics_index = i
                    break
            if graphics_index is None:
                raise RuntimeError("No se encontro queue family grafica")

            qinfo = vk.VkDeviceQueueCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
                queueFamilyIndex=graphics_index,
                queueCount=1,
                pQueuePriorities=[1.0],
            )
            dinfo = vk.VkDeviceCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
                queueCreateInfoCount=1,
                pQueueCreateInfos=[qinfo],
            )
            device = vk.vkCreateDevice(physical_device, dinfo, None)

            color_format = vk.VK_FORMAT_R8G8B8A8_UNORM
            attachment = vk.VkAttachmentDescription(
                format=color_format,
                samples=vk.VK_SAMPLE_COUNT_1_BIT,
                loadOp=vk.VK_ATTACHMENT_LOAD_OP_CLEAR,
                storeOp=vk.VK_ATTACHMENT_STORE_OP_STORE,
                stencilLoadOp=vk.VK_ATTACHMENT_LOAD_OP_DONT_CARE,
                stencilStoreOp=vk.VK_ATTACHMENT_STORE_OP_DONT_CARE,
                initialLayout=vk.VK_IMAGE_LAYOUT_UNDEFINED,
                finalLayout=vk.VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
            )
            color_ref = vk.VkAttachmentReference(
                attachment=0,
                layout=vk.VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
            )
            subpass = vk.VkSubpassDescription(
                pipelineBindPoint=vk.VK_PIPELINE_BIND_POINT_GRAPHICS,
                colorAttachmentCount=1,
                pColorAttachments=[color_ref],
            )
            rp_info = vk.VkRenderPassCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO,
                attachmentCount=1,
                pAttachments=[attachment],
                subpassCount=1,
                pSubpasses=[subpass],
            )
            render_pass = vk.vkCreateRenderPass(device, rp_info, None)
            report.render_pass_created = render_pass is not None

            image_info = vk.VkImageCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO,
                imageType=vk.VK_IMAGE_TYPE_2D,
                extent=vk.VkExtent3D(width=width, height=height, depth=1),
                mipLevels=1,
                arrayLayers=1,
                format=color_format,
                tiling=vk.VK_IMAGE_TILING_OPTIMAL,
                initialLayout=vk.VK_IMAGE_LAYOUT_UNDEFINED,
                usage=vk.VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | vk.VK_IMAGE_USAGE_TRANSFER_SRC_BIT,
                samples=vk.VK_SAMPLE_COUNT_1_BIT,
                sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE,
            )
            color_image = vk.vkCreateImage(device, image_info, None)
            report.color_image_created = color_image is not None
            mem_req = vk.vkGetImageMemoryRequirements(device, color_image)
            memory_type = _find_memory_type(vk, physical_device, mem_req.memoryTypeBits, vk.VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT)
            alloc_info = vk.VkMemoryAllocateInfo(
                sType=vk.VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
                allocationSize=mem_req.size,
                memoryTypeIndex=memory_type,
            )
            color_memory = vk.vkAllocateMemory(device, alloc_info, None)
            vk.vkBindImageMemory(device, color_image, color_memory, 0)
            report.color_memory_bound = True
            report.allocated_kb += int(mem_req.size) // 1024

            view_info = vk.VkImageViewCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,
                image=color_image,
                viewType=vk.VK_IMAGE_VIEW_TYPE_2D,
                format=color_format,
                subresourceRange=vk.VkImageSubresourceRange(
                    aspectMask=vk.VK_IMAGE_ASPECT_COLOR_BIT,
                    baseMipLevel=0,
                    levelCount=1,
                    baseArrayLayer=0,
                    layerCount=1,
                ),
            )
            image_view = vk.vkCreateImageView(device, view_info, None)
            report.image_view_created = image_view is not None

            fb_info = vk.VkFramebufferCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO,
                renderPass=render_pass,
                attachmentCount=1,
                pAttachments=[image_view],
                width=width,
                height=height,
                layers=1,
            )
            framebuffer = vk.vkCreateFramebuffer(device, fb_info, None)
            report.framebuffer_created = framebuffer is not None

            vert_path, frag_path = _asset_spv_paths()
            if not vert_path.exists() or not frag_path.exists():
                raise RuntimeError("No hay SPIR-V para crear pipeline")
            vert_words = _spv_u32_words(vert_path)
            frag_words = _spv_u32_words(frag_path)
            report.vertex_spirv_bytes = vert_path.stat().st_size
            report.fragment_spirv_bytes = frag_path.stat().st_size
            report.spirv_generated = True

            vert_module = vk.vkCreateShaderModule(device, vk.VkShaderModuleCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
                codeSize=report.vertex_spirv_bytes,
                pCode=vert_words,
            ), None)
            report.shader_modules_created += 1
            frag_module = vk.vkCreateShaderModule(device, vk.VkShaderModuleCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
                codeSize=report.fragment_spirv_bytes,
                pCode=frag_words,
            ), None)
            report.shader_modules_created += 1

            pipeline_layout = vk.vkCreatePipelineLayout(device, vk.VkPipelineLayoutCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
                setLayoutCount=0,
                pSetLayouts=None,
                pushConstantRangeCount=0,
                pPushConstantRanges=None,
            ), None)
            report.pipeline_layout_created = pipeline_layout is not None

            stages = [
                vk.VkPipelineShaderStageCreateInfo(
                    sType=vk.VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
                    stage=vk.VK_SHADER_STAGE_VERTEX_BIT,
                    module=vert_module,
                    pName="main",
                ),
                vk.VkPipelineShaderStageCreateInfo(
                    sType=vk.VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
                    stage=vk.VK_SHADER_STAGE_FRAGMENT_BIT,
                    module=frag_module,
                    pName="main",
                ),
            ]
            vertex_input = vk.VkPipelineVertexInputStateCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO,
                vertexBindingDescriptionCount=0,
                vertexAttributeDescriptionCount=0,
            )
            input_asm = vk.VkPipelineInputAssemblyStateCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO,
                topology=vk.VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST,
                primitiveRestartEnable=False,
            )
            viewport = vk.VkViewport(x=0.0, y=0.0, width=float(width), height=float(height), minDepth=0.0, maxDepth=1.0)
            scissor = vk.VkRect2D(offset=vk.VkOffset2D(x=0, y=0), extent=vk.VkExtent2D(width=width, height=height))
            viewport_state = vk.VkPipelineViewportStateCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO,
                viewportCount=1,
                pViewports=[viewport],
                scissorCount=1,
                pScissors=[scissor],
            )
            raster = vk.VkPipelineRasterizationStateCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO,
                depthClampEnable=False,
                rasterizerDiscardEnable=False,
                polygonMode=vk.VK_POLYGON_MODE_FILL,
                cullMode=vk.VK_CULL_MODE_BACK_BIT,
                frontFace=vk.VK_FRONT_FACE_CLOCKWISE,
                depthBiasEnable=False,
                lineWidth=1.0,
            )
            multisample = vk.VkPipelineMultisampleStateCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO,
                rasterizationSamples=vk.VK_SAMPLE_COUNT_1_BIT,
                sampleShadingEnable=False,
            )
            color_blend_att = vk.VkPipelineColorBlendAttachmentState(
                blendEnable=False,
                colorWriteMask=(
                    vk.VK_COLOR_COMPONENT_R_BIT
                    | vk.VK_COLOR_COMPONENT_G_BIT
                    | vk.VK_COLOR_COMPONENT_B_BIT
                    | vk.VK_COLOR_COMPONENT_A_BIT
                ),
            )
            color_blend = vk.VkPipelineColorBlendStateCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO,
                logicOpEnable=False,
                attachmentCount=1,
                pAttachments=[color_blend_att],
            )
            pipeline_info = vk.VkGraphicsPipelineCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO,
                stageCount=len(stages),
                pStages=stages,
                pVertexInputState=vertex_input,
                pInputAssemblyState=input_asm,
                pViewportState=viewport_state,
                pRasterizationState=raster,
                pMultisampleState=multisample,
                pColorBlendState=color_blend,
                layout=pipeline_layout,
                renderPass=render_pass,
                subpass=0,
            )
            # El binding de Python puede devolver lista o handle segun version.
            created = vk.vkCreateGraphicsPipelines(device, vk.VK_NULL_HANDLE, 1, [pipeline_info], None)
            pipeline = created[0] if isinstance(created, (list, tuple)) else created
            report.graphics_pipeline_created = pipeline is not None

            command_pool = vk.vkCreateCommandPool(device, vk.VkCommandPoolCreateInfo(
                sType=vk.VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
                queueFamilyIndex=graphics_index,
                flags=vk.VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT,
            ), None)
            report.command_pool_created = command_pool is not None
            buffers = vk.vkAllocateCommandBuffers(device, vk.VkCommandBufferAllocateInfo(
                sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
                commandPool=command_pool,
                level=vk.VK_COMMAND_BUFFER_LEVEL_PRIMARY,
                commandBufferCount=1,
            ))
            command_buffer = buffers[0] if isinstance(buffers, (list, tuple)) else buffers
            report.command_buffers_allocated = 1 if command_buffer is not None else 0

            vk.vkBeginCommandBuffer(command_buffer, vk.VkCommandBufferBeginInfo(
                sType=vk.VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
                flags=vk.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT,
            ))
            clear = vk.VkClearValue(color=vk.VkClearColorValue(float32=[0.08, 0.10, 0.14, 1.0]))
            begin_info = vk.VkRenderPassBeginInfo(
                sType=vk.VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO,
                renderPass=render_pass,
                framebuffer=framebuffer,
                renderArea=vk.VkRect2D(offset=vk.VkOffset2D(x=0, y=0), extent=vk.VkExtent2D(width=width, height=height)),
                clearValueCount=1,
                pClearValues=[clear],
            )
            vk.vkCmdBeginRenderPass(command_buffer, begin_info, vk.VK_SUBPASS_CONTENTS_INLINE)
            report.render_pass_begun = True
            vk.vkCmdBindPipeline(command_buffer, vk.VK_PIPELINE_BIND_POINT_GRAPHICS, pipeline)
            # Aun sin vertex/index buffer real conectado: grabamos el plan de drawIndexed.
            vk.vkCmdDrawIndexed(command_buffer, 3, 1, 0, 0, 0)
            report.draw_indexed_recorded = True
            vk.vkCmdEndRenderPass(command_buffer)
            vk.vkEndCommandBuffer(command_buffer)

        finally:
            # Destruir en orden inverso. Todo protegido porque algunas pruebas pueden fallar a medias.
            for fn in [
                lambda: vk.vkDestroyCommandPool(device, command_pool, None) if device and command_pool else None,
                lambda: vk.vkDestroyPipeline(device, pipeline, None) if device and pipeline else None,
                lambda: vk.vkDestroyPipelineLayout(device, pipeline_layout, None) if device and pipeline_layout else None,
                lambda: vk.vkDestroyShaderModule(device, vert_module, None) if device and vert_module else None,
                lambda: vk.vkDestroyShaderModule(device, frag_module, None) if device and frag_module else None,
                lambda: vk.vkDestroyFramebuffer(device, framebuffer, None) if device and framebuffer else None,
                lambda: vk.vkDestroyImageView(device, image_view, None) if device and image_view else None,
                lambda: vk.vkDestroyImage(device, color_image, None) if device and color_image else None,
                lambda: vk.vkFreeMemory(device, color_memory, None) if device and color_memory else None,
                lambda: vk.vkDestroyRenderPass(device, render_pass, None) if device and render_pass else None,
                lambda: vk.vkDestroyDevice(device, None) if device else None,
                lambda: vk.vkDestroyInstance(instance, None),
            ]:
                try:
                    fn()
                except Exception:
                    pass
    except Exception as exc:
        report.errors += f"framebufferDraw:{exc}; "

    report.ok = bool(
        report.vulkan_imported
        and report.physical_devices > 0
        and report.render_pass_created
        and report.framebuffer_created
        and report.graphics_pipeline_created
        and report.command_buffers_allocated > 0
        and report.render_pass_begun
        and report.draw_indexed_recorded
    )
    return report


if __name__ == "__main__":
    print(run_vulkan_framebuffer_draw_probe().to_dict())
