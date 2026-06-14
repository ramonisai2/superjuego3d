"""Runtime de streaming, LOD y compilacion de chunks."""

import math

from motor_juegos.stream_bridge_budget import get_stream_bridge_budget
from motor_juegos.world_chunk_stream_bridge import build_world_chunk_stream_plan


class MainChunkRuntime:
    def __init__(
        self,
        *,
        env,
        render_backend,
        resource_runtime,
        stream_bridge_stats,
        mundo_chunks,
        mundo_chunks_simple,
        cola_de_peticiones,
        cola_lod_peticiones,
        chunks_pendientes,
        pipe_juego,
        chunk_size,
        seed,
        subdivisions_lod,
        lods_crear_por_tanda,
        radio_detalle,
        radio_vision,
        max_cola_peticiones,
        enable_stream_bridge_safe,
        chunks_compilar_por_frame,
    ):
        self.env = env
        self.render_backend = render_backend
        self.resource_runtime = resource_runtime
        self.stream_bridge_stats = stream_bridge_stats
        self.mundo_chunks = mundo_chunks
        self.mundo_chunks_simple = mundo_chunks_simple
        self.cola_de_peticiones = cola_de_peticiones
        self.cola_lod_peticiones = cola_lod_peticiones
        self.chunks_pendientes = chunks_pendientes
        self.pipe_juego = pipe_juego
        self.chunk_size = chunk_size
        self.seed = seed
        self.subdivisions_lod = subdivisions_lod
        self.lods_crear_por_tanda = lods_crear_por_tanda
        self.radio_detalle = radio_detalle
        self.radio_vision = radio_vision
        self.max_cola_peticiones = max_cola_peticiones
        self.enable_stream_bridge_safe = enable_stream_bridge_safe
        self.chunks_compilar_por_frame = chunks_compilar_por_frame
        self.chunk_generandose_ahora = False

    def encolar_lod_chunk(self, coord):
        coord = (int(coord[0]), int(coord[1]))
        if coord in self.mundo_chunks or coord in self.mundo_chunks_simple or coord in self.cola_lod_peticiones:
            return False
        self.cola_lod_peticiones.append(coord)
        return True

    def cancelar_lod_chunk(self, coord):
        coord = (int(coord[0]), int(coord[1]))
        if coord in self.cola_lod_peticiones:
            self.cola_lod_peticiones.remove(coord)
            return True
        return False

    def procesar_lods_pendientes(self, player_cx, player_cz, limit_override=None):
        """Crea pocos LOD por tanda para evitar picos al cruzar fronteras de chunk."""
        if not self.cola_lod_peticiones:
            return 0
        p_cx, p_cz = int(player_cx), int(player_cz)
        self.cola_lod_peticiones.sort(key=lambda c: (c[0] - p_cx) ** 2 + (c[1] - p_cz) ** 2)
        creados = 0
        intentos = 0
        limite = int(limit_override if limit_override is not None else self.lods_crear_por_tanda)
        if limite <= 0:
            self.stream_bridge_stats["lod_queue_len"] = len(self.cola_lod_peticiones)
            self.stream_bridge_stats["lod_loaded"] = len(self.mundo_chunks_simple)
            return 0
        limite = max(1, limite)
        while self.cola_lod_peticiones and creados < limite and intentos < limite * 3:
            intentos += 1
            coord = self.cola_lod_peticiones.pop(0)
            if coord in self.mundo_chunks or coord in self.mundo_chunks_simple:
                continue
            try:
                self.mundo_chunks_simple[coord] = self.render_backend.register_gpu_handle(
                    self.env.build_simple_chunk_list(
                        coord[0],
                        coord[1],
                        self.chunk_size,
                        self.seed,
                        subdivisions=self.subdivisions_lod,
                    )
                )
                creados += 1
            except Exception as exc:
                print(f"[LOD] No se pudo crear chunk simple {coord}: {exc}")
        self.stream_bridge_stats["lod_created_total"] += creados
        self.stream_bridge_stats["lod_queue_len"] = len(self.cola_lod_peticiones)
        self.stream_bridge_stats["lod_loaded"] = len(self.mundo_chunks_simple)
        return creados

    def administrar_rejilla_chunks_stream_bridge(self, player_cx, player_cz):
        """Gestion experimental via Stage33 L. Solo corre con JUEGO_STREAM_BRIDGE_SAFE=1."""
        p_cx, p_cz = int(player_cx), int(player_cz)
        budget = get_stream_bridge_budget(self.radio_detalle, self.radio_vision, self.max_cola_peticiones)
        plan = build_world_chunk_stream_plan(
            center=(p_cx, p_cz),
            loaded_detail=self.mundo_chunks.keys(),
            loaded_lod=self.mundo_chunks_simple.keys(),
            queued_detail=self.cola_de_peticiones,
            pending_detail=self.chunks_pendientes.keys(),
            detail_radius=budget.detail_radius,
            lod_radius=budget.lod_radius,
            max_detail_requests=max(0, budget.max_detail_requests - len(self.cola_de_peticiones)),
        )
        self.stream_bridge_stats["enabled"] = 1
        self.stream_bridge_stats["preset"] = budget.preset
        self.stream_bridge_stats["detail_radius"] = budget.detail_radius
        self.stream_bridge_stats["lod_radius"] = budget.lod_radius
        self.stream_bridge_stats["max_requests"] = budget.max_detail_requests
        self.stream_bridge_stats["calls"] += 1
        self.stream_bridge_stats["last_center_x"] = p_cx
        self.stream_bridge_stats["last_center_z"] = p_cz

        lod_queued = 0
        detail_requested = 0
        detail_released = 0
        lod_released = 0
        requests_cancelled = 0

        for coord in plan.create_lod:
            if coord not in self.mundo_chunks and coord not in self.mundo_chunks_simple:
                if self.encolar_lod_chunk(coord):
                    lod_queued += 1

        for coord in plan.request_detail:
            if len(self.cola_de_peticiones) >= self.max_cola_peticiones:
                break
            if coord not in self.mundo_chunks and coord not in self.cola_de_peticiones and coord not in self.chunks_pendientes:
                self.cola_de_peticiones.append(coord)
                detail_requested += 1

        for coord in plan.release_detail:
            if coord in self.mundo_chunks:
                self.render_backend.release_gpu_handle(self.mundo_chunks[coord])
                del self.mundo_chunks[coord]
                self.env.clean_cache_for_chunk(*coord)
                self.resource_runtime.remove_rocks_for_chunk(*coord)
                detail_released += 1
            if coord in self.cola_de_peticiones:
                self.cola_de_peticiones.remove(coord)
                requests_cancelled += 1
            if self.cancelar_lod_chunk(coord):
                requests_cancelled += 1
            if coord in self.chunks_pendientes:
                del self.chunks_pendientes[coord]
                requests_cancelled += 1

        for coord in plan.release_lod:
            self.cancelar_lod_chunk(coord)
            if coord in self.mundo_chunks_simple:
                self.render_backend.release_gpu_handle(self.mundo_chunks_simple[coord])
                del self.mundo_chunks_simple[coord]
                lod_released += 1

        for coord in plan.cancel_requests:
            if coord in self.cola_de_peticiones:
                self.cola_de_peticiones.remove(coord)
                requests_cancelled += 1
            if self.cancelar_lod_chunk(coord):
                requests_cancelled += 1
            if coord in self.chunks_pendientes:
                del self.chunks_pendientes[coord]
                requests_cancelled += 1

        self.stream_bridge_stats["lod_queued_total"] += lod_queued
        self.stream_bridge_stats["detail_requested_total"] += detail_requested
        self.stream_bridge_stats["detail_released_total"] += detail_released
        self.stream_bridge_stats["lod_released_total"] += lod_released
        self.stream_bridge_stats["requests_cancelled_total"] += requests_cancelled
        self.stream_bridge_stats["queue_len"] = len(self.cola_de_peticiones)
        self.stream_bridge_stats["lod_queue_len"] = len(self.cola_lod_peticiones)
        self.stream_bridge_stats["pending_len"] = len(self.chunks_pendientes)
        self.stream_bridge_stats["detail_loaded"] = len(self.mundo_chunks)
        self.stream_bridge_stats["lod_loaded"] = len(self.mundo_chunks_simple)

    def administrar_rejilla_chunks(self, player_cx, player_cz, dir_x, dir_z):
        """Gestion menos agresiva de chunks."""
        if self.enable_stream_bridge_safe:
            self.administrar_rejilla_chunks_stream_bridge(player_cx, player_cz)
            return

        chunks_simples = set()
        chunks_detalle = set()
        p_cx, p_cz = int(player_cx), int(player_cz)

        for dx in range(-self.radio_vision, self.radio_vision + 1):
            for dz in range(-self.radio_vision, self.radio_vision + 1):
                chunks_simples.add((p_cx + dx, p_cz + dz))

        for dx in range(-self.radio_detalle, self.radio_detalle + 1):
            for dz in range(-self.radio_detalle, self.radio_detalle + 1):
                chunks_detalle.add((p_cx + dx, p_cz + dz))
                chunks_simples.add((p_cx + dx, p_cz + dz))

        if dir_x != 0 or dir_z != 0:
            norm = math.hypot(dir_x, dir_z)
            if norm > 0:
                dir_x /= norm
                dir_z /= norm
                chunks_simples.add((p_cx + int(round(dir_x)), p_cz + int(round(dir_z))))

        for coord in sorted(chunks_simples, key=lambda c: (c[0] - p_cx) ** 2 + (c[1] - p_cz) ** 2):
            if coord not in self.mundo_chunks and coord not in self.mundo_chunks_simple:
                self.encolar_lod_chunk(coord)

        detalle_ordenado = sorted(chunks_detalle, key=lambda c: (c[0] - p_cx) ** 2 + (c[1] - p_cz) ** 2)
        for coord in detalle_ordenado:
            if coord not in self.mundo_chunks and coord not in self.cola_de_peticiones and coord not in self.chunks_pendientes:
                if len(self.cola_de_peticiones) < self.max_cola_peticiones:
                    self.cola_de_peticiones.append(coord)

        for coord in list(self.mundo_chunks.keys()):
            if coord not in chunks_detalle:
                self.render_backend.release_gpu_handle(self.mundo_chunks[coord])
                del self.mundo_chunks[coord]
                self.env.clean_cache_for_chunk(*coord)
                self.resource_runtime.remove_rocks_for_chunk(*coord)
                if coord in self.cola_de_peticiones:
                    self.cola_de_peticiones.remove(coord)
                self.cancelar_lod_chunk(coord)
                if coord in self.chunks_pendientes:
                    del self.chunks_pendientes[coord]

        for coord in list(self.mundo_chunks_simple.keys()):
            if coord not in chunks_simples or coord in self.mundo_chunks:
                self.render_backend.release_gpu_handle(self.mundo_chunks_simple[coord])
                del self.mundo_chunks_simple[coord]
                self.cancelar_lod_chunk(coord)

    def procesar_comunicacion_multiproceso(self):
        if not self.chunk_generandose_ahora and self.cola_de_peticiones:
            proximo = self.cola_de_peticiones.pop(0)
            self.pipe_juego.send((int(proximo[0]), int(proximo[1])))
            self.chunk_generandose_ahora = True

        if self.chunk_generandose_ahora and self.pipe_juego.poll():
            try:
                recibido = self.pipe_juego.recv()
                if len(recibido) == 8:
                    cx, cz, q, g, r, d, w, h = recibido
                else:
                    cx, cz, q, g, r, d, h = recibido
                    w = []
                self.env._height_cache[(int(cx), int(cz))] = h
                self.chunks_pendientes[(int(cx), int(cz))] = (q, g, r, d, w)
                self.resource_runtime.add_rocks_for_chunk(r, cx, cz)
                self.resource_runtime.add_resources_for_chunk(g, d, cx, cz)
            except Exception as exc:
                print(f"[ERROR] al recibir chunk: {exc}")
            self.chunk_generandose_ahora = False

    def compilar_un_chunk_pendiente(self, player):
        if not self.chunks_pendientes:
            return False
        px, _, pz, _, _, _ = player.get_camera_vectors()

        def distancia(coord):
            cx, cz = coord
            return (cx * self.chunk_size - px) ** 2 + (cz * self.chunk_size - pz) ** 2

        coord = min(self.chunks_pendientes.keys(), key=distancia)
        data = self.chunks_pendientes.pop(coord)
        if len(data) == 5:
            q, g, r, d, w = data
        else:
            q, g, r, d = data
            w = []
        mesh_data = self.env.build_chunk_mesh_data(coord[0], coord[1], q, g, r, d, w, size=self.chunk_size, lod="detail")
        self.mundo_chunks[coord] = self.render_backend.upload_chunk_mesh(mesh_data)
        if coord in self.mundo_chunks_simple:
            self.render_backend.release_gpu_handle(self.mundo_chunks_simple[coord])
            del self.mundo_chunks_simple[coord]
        return True
