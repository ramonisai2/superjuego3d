"""Render 3D runtime y armado del frame graph."""

from __future__ import annotations

from motor_juegos.atmospheric_sky import current_sky_profile, set_sky_rescue_level, sky_runtime_stats, update_distant_biome_sky
from motor_juegos.far_terrain_lod import draw_far_terrain_lod, far_terrain_stats
from motor_juegos.forest_impostor_lod import draw_forest_impostor_lod, forest_impostor_stats
from motor_juegos.render_api import FogConfig
from game.voxel_models import BOXEL_UNIT, draw_boxel, render_player_avatar, render_first_person_weapon


def render_runtime_3d(
    *,
    current_fov,
    ancho,
    alto,
    r3d,
    env,
    render_backend,
    render_graph,
    perf_tracker,
    stream_bridge_stats,
    adaptive_quality,
    adaptive_runtime,
    adaptive_streaming,
    world_detail_debug_status,
    resource_amount_func,
    resource_runtime,
    player,
    enemies,
    npcs,
    slime_remnants,
    stone_projectiles,
    admin_hub,
    z_target,
    z_target_type,
    mundo_chunks_simple,
    mundo_chunks,
    debug_render_all_chunks,
    debug_render_all_entities,
    chunk_size,
    detail_chunk_near_keep,
    detail_chunk_back_margin,
    chunk_render_extra,
    chunk_render_min_extra,
    lods_crear_por_tanda,
    remnant_render_distance,
    entity_render_distance,
    entity_label_distance,
    seed,
):
    z_target_screen = None
    npc_label_screen = None
    frame_stats = render_backend.begin_frame() if render_backend else None
    render_stats = frame_stats.as_dict() if frame_stats else {
        "chunks_detalle": 0,
        "chunks_lod": 0,
        "chunks_ocultos": 0,
        "entidades_render": 0,
        "entidades_ocultas": 0,
        "entidades_transparentes": 0,
        "backend": "opengl",
        "render_passes": 0,
        "render_packets": 0,
    }
    render_stats.update({f"stream_bridge_{k}": v for k, v in stream_bridge_stats.items()})
    render_stats.update({f"perf_{k}": v for k, v in perf_tracker.snapshot_for_render().items()})
    render_stats["adaptive_quality_enabled"] = int(bool(adaptive_quality.get("enabled", True)))
    render_stats["adaptive_quality_scale"] = float(adaptive_quality.get("scale", 1.0) or 1.0)
    render_stats["adaptive_quality_state"] = str(adaptive_quality.get("state", "OK"))
    render_stats["adaptive_quality_fps_avg"] = float(adaptive_quality.get("fps_avg", 0.0) or 0.0)
    chunk_render_distance = adaptive_runtime.chunk_render_distance()
    detail_chunk_render_distance = adaptive_runtime.detail_chunk_render_distance()
    fog_start, fog_end = adaptive_runtime.fog_range()
    render_stats["adaptive_chunk_distance"] = int(chunk_render_distance)
    render_stats["adaptive_detail_chunk_distance"] = int(detail_chunk_render_distance)
    render_stats["adaptive_detail_near_keep"] = int(chunk_size * max(0.65, float(detail_chunk_near_keep)))
    render_stats["adaptive_detail_back_margin"] = float(detail_chunk_back_margin)
    render_stats["adaptive_chunk_extra"] = float(chunk_render_extra)
    render_stats["adaptive_chunk_min_extra"] = float(chunk_render_min_extra)
    render_stats["adaptive_fog_end"] = int(fog_end)
    render_stats["adaptive_stream_interval_ms"] = int(float(adaptive_streaming.get("interval", 0.05)) * 1000)
    render_stats["adaptive_stream_lod_limit"] = int(adaptive_streaming.get("lod_limit", lods_crear_por_tanda))
    render_stats["adaptive_stream_forced"] = int(adaptive_streaming.get("forced", 0))
    rescue = adaptive_runtime.rescue_settings()
    render_stats["frame_rescue_level"] = int(rescue.get("level", 0) or 0)
    render_stats["frame_rescue_label"] = str(rescue.get("label", "OK"))
    world_detail_status = world_detail_debug_status(env, resource_amount_func)
    render_stats["world_detail_preset"] = str(world_detail_status.get("preset", "balanced")).upper()
    render_stats["world_detail_grass"] = float(world_detail_status.get("grass", 0.0) or 0.0)
    render_stats["world_detail_deco"] = float(world_detail_status.get("deco", 0.0) or 0.0)
    render_stats["world_detail_rock"] = float(world_detail_status.get("rock", 0.0) or 0.0)
    render_stats["world_detail_planes"] = (
        int(world_detail_status.get("grass_planes", 0) or 0),
        int(world_detail_status.get("deco_planes", 0) or 0),
        int(world_detail_status.get("leaf_planes", 0) or 0),
        int(world_detail_status.get("tree_layers", 0) or 0),
        int(world_detail_status.get("rock_detail", 0) or 0),
    )
    render_stats["world_resource_amounts"] = (
        int(world_detail_status.get("fibra_amount", 1) or 1),
        int(world_detail_status.get("madera_amount", 1) or 1),
        int(world_detail_status.get("piedra_amount", 1) or 1),
    )

    r3d.setup_perspective(current_fov, ancho / alto, 0.1, 400.0)
    px, py, pz, lx, ly, lz = player.get_camera_vectors()
    r3d.setup_camera(px, py, pz, lx, ly, lz)

    if int(rescue.get("level", 0) or 0) < 3:
        update_distant_biome_sky(env, px, pz, lx, lz, seed)
    sky_profile = current_sky_profile()
    color_horizonte = list(sky_profile.fog)
    render_stats["sky_hour"] = round(float(sky_profile.hour), 2)
    render_stats["sky_daylight"] = round(float(sky_profile.daylight), 3)
    render_stats["sky_night"] = round(float(sky_profile.night), 3)
    world_tint = _world_tint_from_sky(sky_profile)
    render_stats["sky_world_tint_alpha"] = round(float(world_tint[3]), 3)
    r3d.setup_fog(color_horizonte)
    render_backend.configure_fog(FogConfig(tuple(color_horizonte), fog_start, fog_end))
    set_sky_rescue_level(rescue.get("level", 0), rescue.get("sky_cloud_scale", 1.0))
    render_backend.draw_skybox(env, px, py, pz, size=300.0)
    render_stats.update({f"sky_{k}": v for k, v in sky_runtime_stats().items()})
    draw_far_terrain_lod(env, px, py, pz, seed, rescue=rescue)
    render_stats.update({f"far_terrain_{k}": v for k, v in far_terrain_stats().items()})
    draw_forest_impostor_lod(env, px, py, pz, seed, rescue=rescue)
    render_stats.update({f"forest_impostor_{k}": v for k, v in forest_impostor_stats().items()})

    render_graph.begin_frame()
    if debug_render_all_chunks:
        _add_all_chunks_to_render_graph(render_graph, mundo_chunks_simple, mundo_chunks)
    else:
        _add_visible_chunks_to_render_graph(
            render_graph,
            render_backend,
            env,
            render_stats,
            mundo_chunks_simple,
            mundo_chunks,
            px,
            pz,
            lx,
            lz,
            chunk_size=chunk_size,
            adaptive_runtime=adaptive_runtime,
            detail_chunk_near_keep=detail_chunk_near_keep,
            detail_chunk_back_margin=detail_chunk_back_margin,
        )

    if debug_render_all_entities:
        _add_all_entities_to_render_graph(render_graph, player, enemies, npcs, slime_remnants, admin_hub)
    else:
        if getattr(player, "camera_mode", "first") == "third":
            _add_player_to_render_graph(render_graph, player)

        remnant_distance = adaptive_runtime.distance(remnant_render_distance, 0.50)
        entity_distance = adaptive_runtime.distance(entity_render_distance, 0.58)
        label_distance = adaptive_runtime.distance(entity_label_distance, 0.62)

        for rem in slime_remnants:
            if env.is_point_visible_for_render(rem.x, rem.z, px, pz, lx, lz, max_distance=remnant_distance):
                render_graph.add_entity("slime_remnant", rem, render_fn=lambda rem=rem: rem.render(), transparent=True, priority=5)
            else:
                render_stats["entidades_ocultas"] += 1

        for enemy in enemies:
            locked = bool(getattr(enemy, "z_locked", False))
            visible = locked or env.is_point_visible_for_render(enemy.x, enemy.z, px, pz, lx, lz, max_distance=entity_distance)
            if visible:
                detail = adaptive_runtime.entity_detail_level(px, pz, enemy.x, enemy.z, forced_full=locked or bool(getattr(enemy, "selected", False)))
                render_graph.add_entity("enemy", enemy, render_fn=lambda enemy=enemy, detail=detail: enemy.render(detail_level=detail), transparent=False)
            else:
                render_stats["entidades_ocultas"] += 1
            if locked:
                z_target_screen = _world_to_screen(render_backend, enemy.x, enemy.y + 0.9, enemy.z)

        for npc in npcs:
            locked = bool(getattr(npc, "z_locked", False))
            highlighted = bool(npc.highlight)
            visible = locked or highlighted or env.is_point_visible_for_render(npc.x, npc.z, px, pz, lx, lz, max_distance=entity_distance)
            if visible:
                detail = adaptive_runtime.entity_detail_level(px, pz, npc.x, npc.z, forced_full=locked or highlighted)
                render_graph.add_entity(
                    "npc", npc,
                    render_fn=lambda npc=npc, highlighted=highlighted, locked=locked, detail=detail: npc.render(
                        highlight=bool(highlighted or locked),
                        debug_hitbox=bool(highlighted and admin_hub and admin_hub.visible),
                        detail_level=detail,
                    ),
                    transparent=False
                )
            else:
                render_stats["entidades_ocultas"] += 1

            if highlighted:
                dx = npc.x - player.pos_x
                dz = npc.z - player.pos_z
                if dx * dx + dz * dz <= label_distance * label_distance:
                    npc.screen_label = _world_to_screen(render_backend, npc.x, npc.y + (npc.height if hasattr(npc, 'height') else 1.6) + 0.15, npc.z)
                    if npc.screen_label is not None:
                        npc_label_screen = npc.screen_label
            if locked:
                z_target_screen = _world_to_screen(render_backend, npc.x, npc.y + 2.1, npc.z)

        for proj in stone_projectiles:
            render_graph.add_entity("stone_projectile", proj, render_fn=lambda proj=proj: proj.render(), transparent=False)

        if resource_runtime and hasattr(resource_runtime, "iter_loose_stones_near"):
            loose_stone_distance = min(float(entity_distance), 72.0)
            loose_stones_visible = 0
            for stone in resource_runtime.iter_loose_stones_near(px, pz, max_distance=loose_stone_distance, max_count=72):
                sx, sy, sz, variant = stone
                if env.is_point_visible_for_render(sx, sz, px, pz, lx, lz, max_distance=loose_stone_distance):
                    stone_ref = _LooseStoneRef(sx, sy, sz, variant)
                    render_graph.add_entity(
                        "loose_stone",
                        stone_ref,
                        render_fn=lambda stone_ref=stone_ref: _render_loose_stone(stone_ref),
                        transparent=False,
                        priority=-2,
                    )
                    loose_stones_visible += 1
            render_stats["loose_stones_visible"] = loose_stones_visible

    render_graph.execute(render_backend, render_stats)
    render_stats.update(render_graph.as_stats())
    if getattr(player, "camera_mode", "first") == "first":
        render_first_person_weapon(
            px, py, pz, lx, ly, lz,
            weapon_key=player.visible_weapon_key() if hasattr(player, "visible_weapon_key") else (player.weapon_key() if hasattr(player, "weapon_key") else None),
            attack_swing=player.attack_swing_value() if hasattr(player, "attack_swing_value") else 0.0,
        )

    from motor_juegos.gl_legacy_bridge import draw_world_tint_overlay
    draw_world_tint_overlay(ancho, alto, world_tint)
    r3d.disable_fog()
    return render_stats, z_target_screen, npc_label_screen


def _world_tint_from_sky(profile):
    night_alpha = max(0.0, min(0.42, float(profile.night) * 0.34))
    dawn_alpha = max(0.0, min(0.18, float(profile.dawn) * 0.16))
    if dawn_alpha > night_alpha * 0.65:
        return (0.95, 0.30, 0.10, dawn_alpha)
    return (0.02, 0.045, 0.13, night_alpha)


class _LooseStoneRef:
    def __init__(self, x, y, z, variant):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.variant = str(variant)
        self.body_scale = 0.18


def _render_loose_stone(stone):
    colors = {
        "oscura": (0.34, 0.34, 0.35),
        "clara": (0.58, 0.57, 0.52),
        "gris": (0.46, 0.46, 0.44),
    }
    col = colors.get(getattr(stone, "variant", "gris"), colors["gris"])
    wobble = abs((stone.x * 7.13 + stone.z * 3.71) % 1.0)
    base_y = stone.y + BOXEL_UNIT
    draw_boxel(stone.x, base_y, stone.z, 4, 2, 3, col)
    if wobble > 0.28:
        draw_boxel(stone.x + BOXEL_UNIT * 1.6, base_y + BOXEL_UNIT * 0.5, stone.z - BOXEL_UNIT * 0.9, 2, 1, 2, col)
    if wobble < 0.72:
        draw_boxel(stone.x - BOXEL_UNIT * 1.3, base_y + BOXEL_UNIT * 0.5, stone.z + BOXEL_UNIT * 1.1, 2, 1, 1, col)


def _world_to_screen(render_backend, x, y, z):
    return render_backend.project_to_screen(x, y, z) if render_backend else None


def _add_visible_chunks_to_render_graph(
    render_graph,
    render_backend,
    env,
    render_stats,
    mundo_chunks_simple,
    mundo_chunks,
    px,
    pz,
    lx,
    lz,
    *,
    chunk_size,
    adaptive_runtime,
    detail_chunk_near_keep,
    detail_chunk_back_margin,
):
    max_lod_chunk_distance = adaptive_runtime.chunk_render_distance()
    max_detail_chunk_distance = adaptive_runtime.detail_chunk_render_distance()
    detail_near_keep = chunk_size * max(0.65, float(detail_chunk_near_keep))
    for chunk_map, lod in ((mundo_chunks_simple, "lod"), (mundo_chunks, "detail")):
        max_chunk_distance = max_detail_chunk_distance if lod == "detail" else max_lod_chunk_distance
        near_keep = detail_near_keep if lod == "detail" else None
        back_margin = float(detail_chunk_back_margin) if lod == "detail" else None
        for (cx, cz), id_list in chunk_map.items():
            if render_backend.is_chunk_visible(
                env, cx, cz, px, pz, lx, lz,
                size=chunk_size,
                max_distance=max_chunk_distance,
                near_keep=near_keep,
                back_margin=back_margin,
            ):
                render_graph.add_chunk((cx, cz), id_list, lod=lod)
            else:
                render_stats["chunks_ocultos"] += 1


def _add_all_chunks_to_render_graph(render_graph, mundo_chunks_simple, mundo_chunks):
    for chunk_map, lod in ((mundo_chunks_simple, "lod"), (mundo_chunks, "detail")):
        for coord, id_list in chunk_map.items():
            render_graph.add_chunk(coord, id_list, lod=lod)


def _add_all_entities_to_render_graph(render_graph, player, enemies, npcs, slime_remnants, admin_hub):
    if getattr(player, "camera_mode", "first") == "third":
        _add_player_to_render_graph(render_graph, player)

    for rem in slime_remnants:
        render_graph.add_entity("slime_remnant", rem, render_fn=lambda rem=rem: rem.render(), transparent=True, priority=5)

    for enemy in enemies:
        render_graph.add_entity("enemy", enemy, render_fn=lambda enemy=enemy: enemy.render(), transparent=False)

    for npc in npcs:
        highlighted = bool(npc.highlight)
        render_graph.add_entity(
            "npc", npc,
            render_fn=lambda npc=npc, highlighted=highlighted: npc.render(
                highlight=highlighted,
                debug_hitbox=bool(highlighted and admin_hub and admin_hub.visible)
            ),
            transparent=False
        )


def _add_player_to_render_graph(render_graph, player):
    render_graph.add_entity(
        "player", player,
        render_fn=lambda player=player: render_player_avatar(
            player.pos_x,
            player.pos_y - player.player_height,
            player.pos_z,
            yaw=getattr(player, "visual_yaw", player.yaw + 90.0),
            walk_phase=getattr(player, "walk_phase", 0.0),
            move_amount=getattr(player, "move_amount", 0.0),
            swimming=getattr(player, "is_swimming", False),
            held_weapon=player.visible_weapon_key() if hasattr(player, "visible_weapon_key") else (player.weapon_key() if hasattr(player, "weapon_key") else None),
            attack_swing=player.attack_swing_value() if hasattr(player, "attack_swing_value") else 0.0,
        ),
        transparent=False, priority=-5
    )
