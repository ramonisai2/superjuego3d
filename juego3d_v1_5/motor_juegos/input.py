import pygame, math
try:
    from game.debug_log import log_event, log_exception, log_throttled
except Exception:
    def log_event(*args, **kwargs): pass
    def log_exception(*args, **kwargs): pass
    def log_throttled(*args, **kwargs): pass

class FirstPersonCamera:
    def __init__(self, x=0, y=10, z=0):
        self.pos_x = x
        self.pos_y = y
        self.pos_z = z
        self.yaw = -90.0
        self.pitch = 0.0
        self.speed = 5.0
        self.sensitivity = 0.10
        self.player_height = 1.8
        self.velocity_y = 0.0
        self.gravity = -22.0
        self.jump_force = 7.5
        self.is_grounded = False
        self.max_fall_speed = -40.0
        self.smooth_step_speed = 15.0
        self.camera_mode = "first"
        self.third_person_distance = 5.5
        self.third_person_height = 1.5
        self._camera_toggle_down = False
        self._camera_distance_down = False
        # Tercera persona: orientacion visual independiente de la camara.
        # El cuerpo debe mirar hacia donde camina, no arrastrarse mirando siempre a la camara.
        self.visual_yaw = self.yaw + 90.0
        self.walk_phase = 0.0
        self.move_amount = 0.0
        self._last_move_dx = 0.0
        self._last_move_dz = -1.0
        self._last_safe_x = x
        self._last_safe_y = y
        self._last_safe_z = z
        self._fall_frames = 0
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.mouse.get_rel()

    def process_mouse(self):
        dx, dy = pygame.mouse.get_rel()
        self.yaw += dx * self.sensitivity
        self.pitch -= dy * self.sensitivity
        self.pitch = max(-89, min(89, self.pitch))

    def _update_vertical(self, terrain_func, dt):
        """
        Fijacion vertical robusta.
        El bug del ciclo venia de caer por debajo del terreno y luego hacer reset al origen.
        Ahora, si los pies cruzan el suelo, se pega directo al suelo en vez de subir lentamente.
        """
        try:
            suelo = terrain_func(self.pos_x, self.pos_z)
        except Exception as exc:
            log_exception("TERRAIN_FUNC_ERROR", exc)
            suelo = getattr(self, "_last_safe_y", self.pos_y) - self.player_height

        if not math.isfinite(suelo) or suelo < -50 or suelo > 180:
            log_throttled("TERRAIN_HEIGHT_WEIRD", 0.5, x=self.pos_x, z=self.pos_z, suelo=suelo, y=self.pos_y)
            suelo = getattr(self, "_last_safe_y", self.pos_y) - self.player_height

        surface_offset = float(getattr(self, "surface_offset", self.player_height))
        target = suelo + surface_offset
        pies = self.pos_y - surface_offset

        # Si el jugador esta bajo el suelo o tocandolo, NO suavizamos hacia arriba.
        # Suavizar hacia arriba permitia que siguiera cayendo hasta activar el reset vertical.
        if pies <= suelo + 0.08:
            diff = target - self.pos_y
            if abs(diff) > 2.0:
                log_throttled("GROUND_SNAP_LARGE", 0.35, x=self.pos_x, y=self.pos_y, z=self.pos_z, suelo=suelo, target=target, diff=diff, velocity_y=self.velocity_y)
            self.pos_y = target
            self.velocity_y = 0.0
            self.is_grounded = True
            self._fall_frames = 0
            self._last_safe_x = self.pos_x
            self._last_safe_y = self.pos_y
            self._last_safe_z = self.pos_z
            return

        # Si esta apenas por encima del suelo, lo consideramos pegado para evitar micro-caidas.
        if pies - suelo < 0.22 and self.velocity_y <= 0:
            self.pos_y = target
            self.velocity_y = 0.0
            self.is_grounded = True
            self._fall_frames = 0
            self._last_safe_x = self.pos_x
            self._last_safe_y = self.pos_y
            self._last_safe_z = self.pos_z
            return

        self.is_grounded = False
        self._fall_frames += 1

    def _smooth_visual_yaw_towards(self, target_yaw, dt):
        """Gira suavemente el cuerpo hacia la direccion de movimiento."""
        current = float(getattr(self, "visual_yaw", target_yaw))
        # Diferencia angular corta en rango -180..180.
        diff = (target_yaw - current + 180.0) % 360.0 - 180.0
        max_turn = 720.0 * max(0.0, dt)
        if abs(diff) <= max_turn:
            current = target_yaw
        else:
            current += max_turn if diff > 0 else -max_turn
        self.visual_yaw = current % 360.0

    def process_keyboard(self, dt, terrain_func):
        keys = pygame.key.get_pressed()
        # V alterna primera/tercera persona. B cambia distancia de cámara.
        v_down = bool(keys[pygame.K_v])
        if v_down and not self._camera_toggle_down:
            self.camera_mode = "third" if self.camera_mode == "first" else "first"
            pygame.mouse.get_rel()
        self._camera_toggle_down = v_down
        b_down = bool(keys[pygame.K_b])
        if b_down and not self._camera_distance_down:
            self.third_person_distance += 2.0
            if self.third_person_distance > 10.0:
                self.third_person_distance = 4.0
        self._camera_distance_down = b_down

        yaw_rad = math.radians(self.yaw)
        fx = math.cos(yaw_rad)
        fz = math.sin(yaw_rad)
        sp = self.speed * dt
        dx, dz = 0,0
        if keys[pygame.K_w]: dx += fx; dz += fz
        if keys[pygame.K_s]: dx -= fx; dz -= fz
        if keys[pygame.K_a]: dx += fz; dz -= fx
        if keys[pygame.K_d]: dx -= fz; dz += fx

        length = math.hypot(dx, dz)
        raw_dx, raw_dz = dx, dz

        if length > 0:
            raw_dx /= length
            raw_dz /= length
            dx = raw_dx
            dz = raw_dz
            # El modelo mira hacia la direccion real de movimiento.
            # La caja del personaje mira por su eje local +Z, por eso usamos atan2(x,z).
            desired_visual_yaw = math.degrees(math.atan2(raw_dx, raw_dz))
            self._smooth_visual_yaw_towards(desired_visual_yaw, dt)
            self._last_move_dx = raw_dx
            self._last_move_dz = raw_dz
            self.move_amount = min(1.0, self.move_amount + dt * 8.0)
            anim_speed = 8.5 if not getattr(self, "is_swimming", False) else 4.2
            self.walk_phase += dt * anim_speed * (1.0 if not keys[pygame.K_LSHIFT] else 1.25)
        else:
            # No parar en seco: decae para que la animacion no se corte raro.
            self.move_amount = max(0.0, self.move_amount - dt * 7.0)
        max_step = 0.3
        steps = max(1, int(length/max_step)+1)
        dx /= steps
        dz /= steps
        for _ in range(steps):
            old_x, old_z = self.pos_x, self.pos_z
            try:
                old_ground = terrain_func(old_x, old_z)
            except Exception:
                old_ground = self.pos_y - self.player_height

            next_x = self.pos_x + dx * sp
            next_z = self.pos_z + dz * sp
            try:
                next_ground = terrain_func(next_x, next_z)
            except Exception:
                next_ground = old_ground

            # FIX R - Regla de escalado por salto:
            # El jugador puede subir desniveles hasta aprox. 3 veces la altura real de su salto.
            # La altura del salto se estima con física básica: h = v^2 / (2*g).
            # Si el desnivel supera este límite, se trata como risco/meseta y se debe rodear.
            jump_height = (self.jump_force * self.jump_force) / max(0.001, (2.0 * abs(self.gravity)))
            max_climb = max(0.75, jump_height * 3.0)
            next_is_water = False
            old_is_water = False
            water_probe = getattr(self, "water_probe_func", None)
            if callable(water_probe):
                try:
                    old_is_water = bool(water_probe(old_x, old_z))
                    next_is_water = bool(water_probe(next_x, next_z))
                except Exception as exc:
                    log_exception("WATER_PROBE_ERROR", exc)
                    next_is_water = False
                    old_is_water = False

            height_delta = next_ground - old_ground
            if height_delta > max_climb and not (next_is_water or old_is_water):
                log_throttled("CLIMB_LIMIT_BLOCKED", 0.8, x=old_x, z=old_z, next_x=next_x, next_z=next_z,
                              old_ground=old_ground, next_ground=next_ground, delta=height_delta,
                              jump_height=jump_height, max_climb=max_climb)
                self.pos_x = old_x
                self.pos_z = old_z
                self._update_vertical(terrain_func, dt)
                continue
            elif height_delta > max_climb and (next_is_water or old_is_water):
                log_throttled("WATER_ENTRY_SLOPE_ALLOWED", 1.0, x=old_x, z=old_z, next_x=next_x, next_z=next_z,
                              old_ground=old_ground, next_ground=next_ground, delta=height_delta,
                              max_climb=max_climb, old_water=old_is_water, next_water=next_is_water)

            self.pos_x = next_x
            self.pos_z = next_z
            self._update_vertical(terrain_func, dt)

        # Gravedad solo si realmente esta en el aire. Antes se aplicaba siempre,
        # incluso estando en suelo, y eso podia iniciar micro-caidas repetidas.
        if not self.is_grounded:
            self.velocity_y += self.gravity * dt
            if self.velocity_y < self.max_fall_speed:
                self.velocity_y = self.max_fall_speed
            self.pos_y += self.velocity_y * dt
            self._update_vertical(terrain_func, dt)
        else:
            self.velocity_y = 0.0

        if keys[pygame.K_SPACE] and self.is_grounded:
            self.velocity_y = self.jump_force
            self.is_grounded = False
            self.pos_y += self.velocity_y * dt

        if self.pos_y < -10 or self.pos_y > 200:
            # Diagnostico: este era otro posible culpable del ciclo.
            # Antes mandaba al jugador a (0,0) silenciosamente. Ahora registra el evento
            # y usa respawn_x/z si existen.
            old_x, old_y, old_z = self.pos_x, self.pos_y, self.pos_z
            # Primero intenta volver al ultimo punto seguro real.
            rx = float(getattr(self, "_last_safe_x", getattr(self, "respawn_x", self.pos_x)))
            rz = float(getattr(self, "_last_safe_z", getattr(self, "respawn_z", self.pos_z)))
            source = "last_safe"
            # Si por alguna razon no hay punto seguro, usa respawn_x/z.
            if not math.isfinite(rx) or not math.isfinite(rz):
                rx = float(getattr(self, "respawn_x", self.pos_x))
                rz = float(getattr(self, "respawn_z", self.pos_z))
                source = "respawn"
            log_event("VERTICAL_OUT_OF_BOUNDS", old_x=old_x, old_y=old_y, old_z=old_z,
                      target_x=rx, target_z=rz, target_source=source, velocity_y=self.velocity_y)
            try:
                terrain_y = terrain_func(rx, rz)
                self.pos_x = rx
                self.pos_z = rz
                self.pos_y = terrain_y + float(getattr(self, "surface_offset", self.player_height)) + 0.08
            except Exception as exc:
                log_exception("VERTICAL_RESET_TERRAIN_ERROR", exc)
                terrain_y = terrain_func(0,0)
                self.pos_x = 0
                self.pos_z = 0
                self.pos_y = terrain_y + float(getattr(self, "surface_offset", self.player_height)) + 0.08
            self.velocity_y = 0
            self.is_grounded = True
            self._fall_frames = 0
            self._last_safe_x = self.pos_x
            self._last_safe_y = self.pos_y
            self._last_safe_z = self.pos_z
            log_event("VERTICAL_RESET_DONE", x=self.pos_x, y=self.pos_y, z=self.pos_z)

    def get_camera_vectors(self):
        yr = math.radians(self.yaw)
        pr = math.radians(self.pitch)
        fx = math.cos(pr) * math.cos(yr)
        fy = math.sin(pr)
        fz = math.cos(pr) * math.sin(yr)

        if self.camera_mode == "third":
            cam_x = self.pos_x - math.cos(yr) * self.third_person_distance
            cam_z = self.pos_z - math.sin(yr) * self.third_person_distance
            cam_y = self.pos_y + self.third_person_height + max(0.0, -self.pitch * 0.02)
            target_x = self.pos_x + fx * 1.2
            target_y = self.pos_y + 0.65 + fy * 0.7
            target_z = self.pos_z + fz * 1.2
            return (cam_x, cam_y, cam_z, target_x, target_y, target_z)

        lx = self.pos_x + fx
        ly = self.pos_y + fy
        lz = self.pos_z + fz
        return (self.pos_x, self.pos_y, self.pos_z, lx, ly, lz)
