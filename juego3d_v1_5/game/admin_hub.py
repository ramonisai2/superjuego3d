import math
import random
import pygame
from motor_juegos import r2d

class AdminHub:
    """
    Panel de administración dibujado con OpenGL 2D.
    No usa pygame.blit sobre la ventana OPENGL, porque eso suele quedar oculto.
    """

    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.visible = False
        self._f1_was_down = False
        self._mouse_was_down = False
        self._key_was_down = {}
        self.message = "F1: Admin Hub"
        self.message_timer = 0.0
        self.buttons = []
        self.ai_enabled = True
        self.spawn_distance = 7.0

    def toggle(self):
        self.visible = not self.visible
        pygame.mouse.set_visible(self.visible)
        pygame.event.set_grab(not self.visible)
        pygame.mouse.get_rel()
        self.message = "Admin Hub abierto" if self.visible else "Admin Hub cerrado"
        self.message_timer = 2.0

    def _front_position(self, player, distance=None):
        if distance is None:
            distance = self.spawn_distance
        yaw = math.radians(player.yaw)
        x = player.pos_x + math.cos(yaw) * distance
        z = player.pos_z + math.sin(yaw) * distance
        return x, z

    def _spawn_npc(self, player, npcs, get_height, NPC, semilla):
        x, z = self._front_position(player, 6.0)
        y = get_height(x, z)
        seed = random.randint(1, 9999999) ^ semilla
        npc = NPC(seed, x, z, y + 0.8, id_source="admin", id_slot=len(npcs))
        npc.terrain_height_func = get_height
        npc.wander_radius = 10.0
        npc.descripcion = "NPC creado desde Admin Hub."
        npc.admin_spawned = True
        npcs.append(npc)
        self._notify(f"NPC creado: {npc.nombre} {npc.titulo}")

    def _spawn_enemy(self, player, enemies, get_height, Enemy, semilla):
        x, z = self._front_position(player, 8.0)
        y = get_height(x, z)
        enemy = Enemy(x, y, z, get_height)
        enemy.lock_spawn_biome_color(semilla)
        enemy.admin_spawned = True
        enemies.append(enemy)
        self._notify("Slime enemigo creado frente al jugador")

    def _spawn_boss(self, player, enemies, get_height, Enemy, semilla):
        x, z = self._front_position(player, 11.0)
        y = get_height(x, z)
        boss = Enemy(x, y, z, get_height)
        boss.lock_spawn_biome_color(semilla)
        boss.health = 8
        boss.max_health = 8
        boss.hit_points = 8
        boss.speed = 1.8
        boss.height = 1.9
        boss.body_scale = 1.45
        boss.is_boss = True
        boss.admin_spawned = True
        enemies.append(boss)
        self._notify("Jefe creado")

    def _spawn_legendary(self, player, npcs, get_height, NPC, semilla):
        x, z = self._front_position(player, 9.0)
        y = get_height(x, z)
        seed = (semilla ^ 0xB0170) + len(npcs) * 777
        npc = NPC(seed, x, z, y + 0.8, id_source="legendary", id_slot=len(npcs))
        npc.terrain_height_func = get_height
        npc.nombre = random.choice(["Bolvo", "Roy", "Mork", "Runia"])
        npc.titulo = random.choice(["hijo de Runia", "el Calvo Legendario", "Guardián Gris", "Rey del Pantano"])
        npc.daño = 35
        npc.hostilidad = 90
        npc.descripcion = "Entidad legendaria invocada desde el Admin Hub."
        npc.wander_radius = 18.0
        npc.is_legendary = True
        npc.admin_color = (1.0, 0.85, 0.1)
        npcs.append(npc)
        self._notify(f"Legendario creado: {npc.nombre} {npc.titulo}")

    def _clear_admin_entities(self, enemies, npcs):
        before = len(enemies) + len(npcs)
        enemies[:] = [e for e in enemies if not getattr(e, "admin_spawned", False)]
        npcs[:] = [n for n in npcs if not getattr(n, "admin_spawned", False)]
        removed = before - (len(enemies) + len(npcs))
        self._notify(f"Entidades admin eliminadas: {removed}")

    def _clear_all_entities(self, enemies, npcs):
        enemies.clear()
        npcs.clear()
        self._notify("Todas las entidades fueron eliminadas")

    def _notify(self, text):
        self.message = text
        self.message_timer = 3.0
        print("[ADMIN]", text)

    def update(self, dt, keys, player, enemies, npcs, get_height, NPC, Enemy, semilla):
        if self.message_timer > 0:
            self.message_timer -= dt

        f1_down = keys[pygame.K_F1]
        if f1_down and not self._f1_was_down:
            self.toggle()
        self._f1_was_down = f1_down

        if not self.visible:
            return

        # Atajos rápidos mientras el panel está abierto, con debounce.
        if self._pressed_once(keys, pygame.K_1):
            self._spawn_npc(player, npcs, get_height, NPC, semilla)
        elif self._pressed_once(keys, pygame.K_2):
            self._spawn_enemy(player, enemies, get_height, Enemy, semilla)
        elif self._pressed_once(keys, pygame.K_3):
            self._spawn_boss(player, enemies, get_height, Enemy, semilla)
        elif self._pressed_once(keys, pygame.K_4):
            self._spawn_legendary(player, npcs, get_height, NPC, semilla)

        mouse_down = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()
        if mouse_down and not self._mouse_was_down:
            self._handle_click(mouse_pos, player, enemies, npcs, get_height, NPC, Enemy, semilla)
        self._mouse_was_down = mouse_down

    def _pressed_once(self, keys, key):
        down = bool(keys[key])
        was_down = self._key_was_down.get(key, False)
        self._key_was_down[key] = down
        return down and not was_down

    def _handle_click(self, mouse_pos, player, enemies, npcs, get_height, NPC, Enemy, semilla):
        mx, my = mouse_pos
        for button in self.buttons:
            x, y, w, h, action = button
            if x <= mx <= x + w and y <= my <= y + h:
                if action == "spawn_npc":
                    self._spawn_npc(player, npcs, get_height, NPC, semilla)
                elif action == "spawn_enemy":
                    self._spawn_enemy(player, enemies, get_height, Enemy, semilla)
                elif action == "spawn_boss":
                    self._spawn_boss(player, enemies, get_height, Enemy, semilla)
                elif action == "spawn_legendary":
                    self._spawn_legendary(player, npcs, get_height, NPC, semilla)
                elif action == "toggle_ai":
                    self.ai_enabled = not self.ai_enabled
                    self._notify("IA activada" if self.ai_enabled else "IA pausada")
                elif action == "clear_admin":
                    self._clear_admin_entities(enemies, npcs)
                elif action == "clear_all":
                    self._clear_all_entities(enemies, npcs)
                elif action == "close":
                    self.toggle()
                return

    def draw(self, player, enemies, npcs, fps=0):
        # Mensaje pequeño aun con el panel cerrado.
        if not self.visible:
            if self.message_timer > 0:
                r2d.draw_rect_2d(18, self.height - 42, 360, 28, (0.02, 0.02, 0.02))
                r2d.draw_text_2d(self.message, 28, self.height - 36, (255, 255, 180))
            return

        x = 30
        y = 35
        w = 360
        h = 520
        self.buttons = []

        # Fondo principal
        r2d.draw_rect_2d(x, y, w, h, (0.03, 0.03, 0.04))
        r2d.draw_rect_2d(x + 4, y + 4, w - 8, 42, (0.10, 0.12, 0.16))
        r2d.draw_text_2d("ADMIN HUB - STAGE 15 TURBO", x + 18, y + 16, (255, 230, 120))

        info_y = y + 62
        r2d.draw_text_2d(f"FPS: {fps:.0f}", x + 18, info_y, (220, 220, 220))
        r2d.draw_text_2d(f"Jugador: X {player.pos_x:.1f}  Y {player.pos_y:.1f}  Z {player.pos_z:.1f}", x + 18, info_y + 24, (220, 220, 220))
        r2d.draw_text_2d(f"NPCs: {len(npcs)}   Enemigos: {len(enemies)}   IA: {'ON' if self.ai_enabled else 'OFF'}", x + 18, info_y + 48, (220, 220, 220))
        r2d.draw_text_2d("V: 1ra/3ra persona   B: distancia", x + 18, info_y + 72, (190, 210, 255))

        btn_y = info_y + 112
        self._button(x + 18, btn_y, 310, 34, "1  Spawn NPC", "spawn_npc")
        self._button(x + 18, btn_y + 42, 310, 34, "2  Spawn Enemigo", "spawn_enemy")
        self._button(x + 18, btn_y + 84, 310, 34, "3  Spawn Jefe", "spawn_boss")
        self._button(x + 18, btn_y + 126, 310, 34, "4  Spawn Legendario", "spawn_legendary")
        self._button(x + 18, btn_y + 168, 310, 34, "Pausar / Activar IA", "toggle_ai")
        self._button(x + 18, btn_y + 210, 310, 34, "Limpiar entidades Admin", "clear_admin")
        self._button(x + 18, btn_y + 252, 310, 34, "Limpiar TODAS las entidades", "clear_all")
        self._button(x + 18, btn_y + 294, 310, 34, "Cerrar Hub", "close")

        if self.message:
            r2d.draw_rect_2d(x + 18, y + h - 48, w - 36, 30, (0.10, 0.09, 0.03))
            r2d.draw_text_2d(self.message[:42], x + 28, y + h - 41, (255, 255, 190))

    def _button(self, x, y, w, h, label, action):
        self.buttons.append((x, y, w, h, action))
        r2d.draw_rect_2d(x, y, w, h, (0.12, 0.14, 0.18))
        r2d.draw_rect_2d(x + 2, y + 2, w - 4, h - 4, (0.18, 0.20, 0.26))
        r2d.draw_text_2d(label, x + 12, y + 9, (245, 245, 245))
