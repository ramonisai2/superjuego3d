"""Precarga inicial de chunks antes de entrar al mundo."""

import pygame


def preload_initial_chunks(
    base_cx,
    base_cz,
    *,
    mundo_chunks,
    mundo_chunks_simple,
    draw_loading_screen,
    engine,
    render_backend,
    r2d,
    ancho,
    alto,
    env,
    resource_runtime,
    chunk_size,
    seed,
    subdivisions,
    subdivisions_lod,
    radio_vision,
    radio_detalle,
):
    """Pantalla de carga menos agresiva: LOD alrededor y 9 chunks detallados iniciales."""
    lod_coords = []
    for dx in range(-radio_vision, radio_vision + 1):
        for dz in range(-radio_vision, radio_vision + 1):
            lod_coords.append((base_cx + dx, base_cz + dz))
    lod_coords.sort(key=lambda coord: (coord[0] - base_cx) ** 2 + (coord[1] - base_cz) ** 2)

    detail_coords = []
    for dx in range(-radio_detalle, radio_detalle + 1):
        for dz in range(-radio_detalle, radio_detalle + 1):
            detail_coords.append((base_cx + dx, base_cz + dz))
    detail_coords.sort(key=lambda coord: (coord[0] - base_cx) ** 2 + (coord[1] - base_cz) ** 2)

    total = len(lod_coords) + len(detail_coords)
    step_num = 0
    for coord in lod_coords:
        step_num += 1
        draw_loading_screen(engine, render_backend, r2d, ancho, alto, f"LOD alrededor {step_num}/{total}...")
        pygame.event.pump()
        if coord not in mundo_chunks_simple and coord not in mundo_chunks:
            try:
                mundo_chunks_simple[coord] = render_backend.register_gpu_handle(
                    env.build_simple_chunk_list(
                        coord[0],
                        coord[1],
                        chunk_size,
                        seed,
                        subdivisions=subdivisions_lod,
                    )
                )
            except Exception as exc:
                print(f"[PRELOAD] Error creando LOD {coord}: {exc}")

    for coord in detail_coords:
        step_num += 1
        draw_loading_screen(engine, render_backend, r2d, ancho, alto, f"Detalle 9 chunks cercanos {step_num}/{total}...")
        pygame.event.pump()
        try:
            cx, cz, q, g, r, d, w, h = env.calculate_chunk_data_background(
                coord[0],
                coord[1],
                chunk_size,
                subdivisions,
                seed,
            )
            env._height_cache[(int(cx), int(cz))] = h
            resource_runtime.add_rocks_for_chunk(r, cx, cz)
            resource_runtime.add_resources_for_chunk(g, d, cx, cz)
            mesh_data = env.build_chunk_mesh_data(cx, cz, q, g, r, d, w, size=chunk_size, lod="detail", height_map=h)
            mundo_chunks[(int(cx), int(cz))] = render_backend.upload_chunk_mesh(mesh_data)
            if coord in mundo_chunks_simple:
                render_backend.release_gpu_handle(mundo_chunks_simple[coord])
                del mundo_chunks_simple[coord]
        except Exception as exc:
            print(f"[PRELOAD] Error creando detalle {coord}: {exc}")
