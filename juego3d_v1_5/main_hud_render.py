"""Render 2D/HUD del runtime principal."""

from __future__ import annotations


def render_runtime_hud(
    *,
    r2d,
    ancho,
    alto,
    engine,
    player,
    enemies,
    npcs,
    admin_hub,
    render_stats,
    adaptive_quality,
    npc_name_label,
    npc_prompt,
    npc_description,
    npc_dialog,
    npc_label_screen,
    z_target,
    z_target_type,
    z_target_screen,
    draw_ui,
    draw_pickup_notices,
    draw_world_context,
    draw_adaptive_quality,
    draw_fps_counter,
    draw_npc_label,
    draw_npc_prompt,
    draw_npc_description,
    draw_npc_dialog,
    draw_npc_world_label,
    draw_z_target_ui,
    draw_z_target_marker,
    draw_npc_ai_telemetry,
):
    r2d.begin_2d(ancho, alto)
    draw_ui(player)
    draw_pickup_notices(player)
    draw_world_context(player)
    fps = engine.clock.get_fps() if engine and hasattr(engine, "clock") else 0
    draw_adaptive_quality(adaptive_quality.get("state", "OK"), adaptive_quality.get("scale", 1.0), ancho - 222, alto - 44)
    draw_fps_counter(fps, ancho - 104, alto - 44)
    if admin_hub and admin_hub.visible:
        r2d.draw_text_2d(
            f"Render[{render_stats.get('backend','opengl')}]: {fps:.0f} FPS | chunks D:{render_stats.get('chunks_detalle',0)} LOD:{render_stats.get('chunks_lod',0)} ocultos:{render_stats.get('chunks_ocultos',0)} | ent:{render_stats.get('entidades_render',0)}/{render_stats.get('entidades_ocultas',0)}",
            24, 132, (190, 235, 210)
        )
        r2d.draw_text_2d(
            f"AutoQuality: {render_stats.get('adaptive_quality_state','OK')} rescue:{render_stats.get('frame_rescue_label','OK')} nivel:{render_stats.get('frame_rescue_level',0)} escala:{render_stats.get('adaptive_quality_scale',1.0):.2f} fpsAvg:{render_stats.get('adaptive_quality_fps_avg',0.0):.1f} chunk:{render_stats.get('adaptive_chunk_distance',0)} detail:{render_stats.get('adaptive_detail_chunk_distance',0)}/{render_stats.get('adaptive_detail_near_keep',0)} fog:{render_stats.get('adaptive_fog_end',0)} stream:{render_stats.get('adaptive_stream_interval_ms',0)}ms lod:{render_stats.get('adaptive_stream_lod_limit',0)}",
            24, 264, (180, 235, 180)
        )
        planes = render_stats.get("world_detail_planes", (0, 0, 0, 0, 0))
        amounts = render_stats.get("world_resource_amounts", (1, 1, 1))
        r2d.draw_text_2d(
            f"WorldPreset: {render_stats.get('world_detail_preset','BALANCED')} dens G:{render_stats.get('world_detail_grass',0):.2f} D:{render_stats.get('world_detail_deco',0):.2f} R:{render_stats.get('world_detail_rock',0):.2f} planes g/d/l/t/r:{planes[0]}/{planes[1]}/{planes[2]}/{planes[3]}/{planes[4]} res F/M/P:{amounts[0]}/{amounts[1]}/{amounts[2]}",
            24, 286, (205, 225, 255)
        )
        r2d.draw_text_2d(
            f"FarHorizon: rescue:{render_stats.get('frame_rescue_label','OK')} on:{render_stats.get('far_terrain_enabled',0)} tiles:{render_stats.get('far_terrain_tiles_visible',0)}/{render_stats.get('far_terrain_max_visible',0)} built:{render_stats.get('far_terrain_tiles_built',0)} cache:{render_stats.get('far_terrain_tiles_cached',0)} tile:{render_stats.get('far_terrain_tile_size',0)} sub:{render_stats.get('far_terrain_subdivisions',0)} r:{render_stats.get('far_terrain_radius',0)} h:{render_stats.get('far_terrain_height_scale',0):.2f} sky:{render_stats.get('sky_biome_hint','none')} tint:{render_stats.get('sky_biome_tint_strength',0):.2f}/{render_stats.get('sky_world_tint_alpha',0):.2f}",
            24, 308, (180, 230, 230)
        )
        if render_stats.get("perf_frame"):
            r2d.draw_text_2d(
                f"Perf ms: frame:{render_stats.get('perf_frame',0):.1f} update:{render_stats.get('perf_update',0):.1f} chunks:{render_stats.get('perf_chunk_total',0):.1f} r3d:{render_stats.get('perf_render3d',0):.1f} flip:{render_stats.get('perf_flip',0):.1f}",
                24, 242, (255, 210, 140)
            )
        r2d.draw_text_2d(
            f"Mesh upload: V:{render_stats.get('mesh_vertices',0)} I:{render_stats.get('mesh_indices',0)} Q:{render_stats.get('mesh_quads',0)} Batches:{render_stats.get('material_batches',0)} RAM~GPU:{render_stats.get('mesh_bytes',0)//1024}KB Uploads:{render_stats.get('uploads_frame',0)} | Visible V:{render_stats.get('visible_chunk_vertices',0)} D:{render_stats.get('visible_detail_vertices',0)} L:{render_stats.get('visible_lod_vertices',0)} KB:{render_stats.get('visible_chunk_bytes',0)//1024}",
            24, 154, (185, 220, 245)
        )
        r2d.draw_text_2d(
            f"Instances: total:{render_stats.get('instance_total',0)} kinds:{render_stats.get('instance_kinds',0)} transp:{render_stats.get('instance_transparent',0)} player:{render_stats.get('instance_player',0)} enemy:{render_stats.get('instance_enemy',0)} npc:{render_stats.get('instance_npc',0)} StaticDraw:{render_stats.get('entidades_staticmesh',0)} Debug:{render_stats.get('static_entity_debug',0)}",
            24, 176, (220, 210, 245)
        )
        r2d.draw_text_2d(
            f"VulkanPrep: probe:{render_stats.get('vulkan_probe_ok',0)} tri:{render_stats.get('vulkan_triangle_ok',0)} chunk:{render_stats.get('vulkan_chunk_upload_ok',0)} mem:{render_stats.get('vulkan_memory_ok',0)} map:{render_stats.get('vulkan_staging_mapped',0)} cmd:{render_stats.get('vulkan_command_ok',0)} draw:{render_stats.get('vulkan_draw_ok',0)} rp:{render_stats.get('vulkan_render_pass_plan',0)} pipe:{render_stats.get('vulkan_pipeline_plan',0)} idx:{render_stats.get('vulkan_draw_indexed_plan',0)} sh:{render_stats.get('vulkan_shader_ok',0)} spv:{render_stats.get('vulkan_spirv_generated',0)} mods:{render_stats.get('vulkan_shader_modules',0)} layout:{render_stats.get('vulkan_pipeline_layout_ok',0)} fb:{render_stats.get('vulkan_framebuffer_ok',0)} begin:{render_stats.get('vulkan_renderpass_begin_ok',0)} didx:{render_stats.get('vulkan_draw_indexed_recorded',0)} comp:{render_stats.get('vulkan_shader_compiler',0)} shKB:{render_stats.get('vulkan_shader_bytes',0)//1024} copy:{render_stats.get('vulkan_copy_commands',0)} sub:{render_stats.get('vulkan_submits',0)} writeKB:{render_stats.get('vulkan_staging_write_kb',0)} allocKB:{render_stats.get('vulkan_alloc_kb',0)} vkKB:{render_stats.get('vulkan_upload_bytes',0)//1024} dev:{render_stats.get('vulkan_devices',0)}",
            24, 198, (245, 220, 160)
        )
        if render_stats.get("stream_bridge_enabled"):
            r2d.draw_text_2d(
                f"StreamBridge: ON calls:{render_stats.get('stream_bridge_calls',0)} center:{render_stats.get('stream_bridge_last_center_x',0)},{render_stats.get('stream_bridge_last_center_z',0)} req:{render_stats.get('stream_bridge_detail_requested_total',0)} lod+:{render_stats.get('stream_bridge_lod_created_total',0)} freeD:{render_stats.get('stream_bridge_detail_released_total',0)} freeL:{render_stats.get('stream_bridge_lod_released_total',0)} cancel:{render_stats.get('stream_bridge_requests_cancelled_total',0)} q:{render_stats.get('stream_bridge_queue_len',0)} pend:{render_stats.get('stream_bridge_pending_len',0)} loaded D:{render_stats.get('stream_bridge_detail_loaded',0)} L:{render_stats.get('stream_bridge_lod_loaded',0)}",
                24, 220, (170, 245, 190)
            )
    r2d.draw_rect_2d((ancho // 2) - 2, (alto // 2) - 2, 4, 4, (1, 1, 1))
    draw_npc_label(npc_name_label)
    draw_npc_prompt(npc_prompt)
    draw_npc_description(npc_description)
    draw_npc_dialog(npc_dialog)
    if npc_label_screen:
        draw_npc_world_label(npc_name_label, npc_label_screen[0], npc_label_screen[1])

    draw_z_target_ui(z_target, z_target_type)
    draw_z_target_marker(z_target_screen)
    draw_npc_ai_telemetry()

    if admin_hub:
        fps = engine.clock.get_fps() if engine and hasattr(engine, "clock") else 0
        admin_hub.draw(player, enemies, npcs, fps)

    r2d.end_2d()
