
import math
import random
from game.npc_identity import (
    FIRST_NAMES,
    HUMAN_PROFESSIONS,
    HUMAN_PROFESSION_PROFILES,
    SKIN_ZONE_PRESETS,
    TITLES,
    build_npc_id,
    choose_skin_zone_preset,
    profession_identity,
    profile_for_profession,
    skin_zones_for_preset,
    stable_digest as _stable_digest,
    stable_float01 as _stable_float01,
    stable_offset as _stable_offset,
    visible_tool_name,
)
from game.npc_memory import (
    clear_npc_memory,
    compact_memory_notes,
    export_npc_memory,
    import_npc_memory,
    need_status_text,
    npc_memory_for,
    npc_memory_snapshot,
    remember_npc_event,
)
from game.npc_ai_runtime import (
    LocalCommandNPCBackend,
    LocalNPCModelAdapter,
    _clamp,
    activity_for_need,
    apply_npc_local_model_config,
    build_npc_dialogue_prompt,
    clear_npc_ai_cache,
    clear_npc_ai_queue,
    clear_npc_ai_telemetry,
    clear_npc_local_model_backend,
    configure_npc_command_backend,
    configure_npc_local_model,
    contextual_dialogue_line,
    dialogue_tone_prefix,
    drain_npc_ai_queue,
    get_npc_local_model_adapter,
    load_npc_local_model_config,
    mood_for_npc,
    normalize_npc_local_model_config,
    npc_ai_cache_stats,
    npc_ai_context_packet,
    npc_ai_pending_for,
    npc_ai_queue_stats,
    npc_ai_runtime_stats,
    npc_ai_status_for,
    npc_ai_telemetry_stats,
    npc_local_ai_reply,
    npc_local_model_config_snapshot,
    npc_local_model_status,
    pop_npc_ai_reply,
    probe_npc_local_model_backend,
    queue_npc_ai_reply,
    save_npc_local_model_config,
    set_npc_local_model_backend,
)
class NPC:
    def __init__(self, seed, x=0, z=0, y=0, npc_id=None, id_source="world", id_slot=0):
        r = random.Random(seed)
        self.id = npc_id or build_npc_id(seed, x, z, id_source, id_slot)
        self.seed = seed
        self.x = x
        self.y = y
        self.z = z
        self.spawn_x = x
        self.spawn_z = z
        self.nombre = r.choice(FIRST_NAMES)
        self.titulo = r.choice(TITLES)
        self.daño = r.randint(8,18)
        self.hostilidad = r.randint(0,100)
        self.height = 1.85
        self.collider_size = (0.62, 1.80, 0.62)
        self.visual_size = (1.15, 2.10, 1.00)
        self.yaw = 0.0
        self.profession = r.choice(HUMAN_PROFESSIONS)
        self.speed = 1.2 + r.random() * 0.8
        self.wander_radius = 10.0
        self.direction = r.uniform(0, 2 * math.pi)
        self.wander_timer = 0.0
        self.wander_change = 1.5 + r.random() * 1.5
        self.memoria = 0
        self.highlight = False
        self.terrain_height_func = None
        self.dialogos = [
            "Esta zona ha cambiado mucho.",
            "No todos los viajeros son de fiar.",
            "Si necesitas agua, ve hacia el oeste.",
            "No me molesten cuando estoy ocupado."
        ]
        self.descripcion = r.choice([
            "Un viajero de paso.",
            "Parece conocer estas tierras.",
            "Tiene una mirada cansada.",
            "Anda con cuidado, lleva cosas valiosas."
        ]) + f" Profesion: {self.profession}."
        self.target_x = self.x
        self.target_z = self.z
        self.max_health = 100.0
        self.health = 100.0
        needs_r = random.Random(int(seed) ^ 0x4E454544)
        self.needs = {
            "food": 72.0 + needs_r.random() * 18.0,
            "water": 70.0 + needs_r.random() * 20.0,
            "energy": 68.0 + needs_r.random() * 24.0,
            "security": 62.0 + needs_r.random() * 28.0,
            "social": 45.0 + needs_r.random() * 35.0,
        }
        self.need_rates = {
            "food": 0.008 + needs_r.random() * 0.006,
            "water": 0.011 + needs_r.random() * 0.008,
            "energy": 0.006 + needs_r.random() * 0.005,
            "social": 0.003 + needs_r.random() * 0.004,
        }
        self.stress = 0.0
        self.current_need = "calm"
        self.intent = "wander"
        self.activity = "wander"
        self.activity_detail = "explorar cerca"
        self.activity_step = 0
        self.activity_effect = "none"
        self.activity_progress = 0.0
        self.mood = "calmado"
        self.stance = "abierto"
        self.mood_detail = "no tiene una urgencia fuerte"
        self.pending_ai_request = None
        self.last_ai_reply = ""
        self.last_ai_status = "idle"
        self.needs_speed_factor = 1.0
        self.walk_phase = 0.0
        self.move_amount = 0.0
        self.skin_preset = choose_skin_zone_preset(seed, self.profession)
        profile = profile_for_profession(self.profession)
        preset = SKIN_ZONE_PRESETS.get(self.skin_preset)
        self.skin_zones = skin_zones_for_preset(self.skin_preset, self.profession)
        self.visual_profession = (preset["visual_profession"] if preset else self.profession) or self.profession
        self.face_type = preset["face_type"] if preset else "neutral"
        self.torso_type = preset["torso_type"] if preset else "neutral"
        self.nose_style = preset["nose_style"] if preset else "human"
        self.ear_style = preset["ear_style"] if preset else "human"
        self.profession_color = profile["color"]
        self.body_shape = profile["shape"]
        self.favorite_tool = profile["tool"]
        self.back_equipment_reserved = False
        self.back_tool = visible_tool_name(self.favorite_tool)
        identity = profession_identity(profile)
        self.tool_label = identity["tool_label"]
        self.workplace = identity["workplace"]
        self.work_material = identity["material"]
        self.work_action = identity["action"]
        self.temper = identity["temper"]
        self.identity_key = _stable_digest("identity", self.id, self.profession, self.skin_preset)[:12]
        work_dx, work_dz = _stable_offset(self.id, f"work_{self.profession}", 2.5, 7.5)
        rest_dx, rest_dz = _stable_offset(self.id, "rest", 1.5, 4.0)
        social_dx, social_dz = _stable_offset(self.id, "social", 3.0, 6.0)
        self.work_anchor = (self.spawn_x + work_dx, self.spawn_z + work_dz)
        self.rest_anchor = (self.spawn_x + rest_dx, self.spawn_z + rest_dz)
        self.social_anchor = (self.spawn_x + social_dx, self.spawn_z + social_dz)
        self.memory = npc_memory_for(self)
        self.memoria = int(self.memory.get("encounters", 0))
        self.update_mood()

    def update_needs(self, dt, threat_level=0.0):
        dt = _clamp(float(dt), 0.0, 2.0)
        threat_level = _clamp(float(threat_level), 0.0, 1.0)
        self.needs["food"] = _clamp(self.needs["food"] - self.need_rates["food"] * dt)
        self.needs["water"] = _clamp(self.needs["water"] - self.need_rates["water"] * dt)
        self.needs["energy"] = _clamp(self.needs["energy"] - self.need_rates["energy"] * dt)
        self.needs["social"] = _clamp(self.needs["social"] - self.need_rates["social"] * dt)
        if threat_level > 0.0:
            self.needs["security"] = _clamp(self.needs["security"] - (0.45 + threat_level * 2.4) * dt)
        else:
            self.needs["security"] = _clamp(self.needs["security"] + 0.018 * dt)

        need_name, need_value = min(self.needs.items(), key=lambda item: item[1])
        self.current_need = need_name if need_value < 38.0 else "calm"
        intent_by_need = {
            "food": "seek_food",
            "water": "seek_water",
            "energy": "rest",
            "security": "seek_safety",
            "social": "seek_company",
        }
        self.intent = intent_by_need.get(self.current_need, "wander")
        self.activity, self.activity_detail = activity_for_need(self)
        urgency = max(0.0, 35.0 - need_value)
        self.stress = _clamp(self.stress + urgency * 0.018 * dt + threat_level * 18.0 * dt - 0.55 * dt)
        self.needs_speed_factor = 0.72 + 0.28 * (self.needs["energy"] / 100.0)
        self.update_mood()

    def needs_snapshot(self):
        self.update_mood()
        memory = npc_memory_snapshot(self)
        return {
            "id": self.id,
            "identity": self.identity_key,
            "memory": memory,
            "name": self.nombre,
            "title": self.titulo,
            "profession": self.profession,
            "visual_profession": self.visual_profession,
            "tool": self.back_tool,
            "tool_label": self.tool_label,
            "workplace": self.workplace,
            "work_action": self.work_action,
            "temper": self.temper,
            "need": self.current_need,
            "intent": self.intent,
            "activity": self.activity,
            "activity_detail": self.activity_detail,
            "activity_effect": self.activity_effect,
            "activity_progress": round(self.activity_progress, 2),
            "mood": self.mood,
            "stance": self.stance,
            "mood_detail": self.mood_detail,
            "conversation_context": self.conversation_context(),
            "ai_context_ready": True,
            "ai_status": self.ai_status(),
            "work_anchor": (round(self.work_anchor[0], 2), round(self.work_anchor[1], 2)),
            "stress": round(self.stress, 2),
            "food": round(self.needs["food"], 2),
            "water": round(self.needs["water"], 2),
            "energy": round(self.needs["energy"], 2),
            "security": round(self.needs["security"], 2),
            "social": round(self.needs["social"], 2),
        }

    def remember_event(self, event, detail=None):
        self.memory = remember_npc_event(self, event, detail)
        self.memoria = int(self.memory.get("encounters", self.memoria))
        return self.memory

    def memory_snapshot(self):
        return npc_memory_snapshot(self)

    def update_mood(self):
        self.mood, self.stance, self.mood_detail = mood_for_npc(self)
        return self.mood

    def conversation_context(self):
        return {
            "mood": self.mood,
            "stance": self.stance,
            "need": self.current_need,
            "activity": self.activity,
            "detail": self.mood_detail,
            "tone": dialogue_tone_prefix(self),
            "trust": round(float(getattr(self, "memory", {}).get("trust", 0.0)), 2),
        }

    def ai_context_packet(self):
        return npc_ai_context_packet(self)

    def ai_status(self):
        return npc_ai_status_for(self)

    def dialogue_prompt(self, player_text=""):
        return build_npc_dialogue_prompt(self, player_text)

    def reply_to_player(self, player_text="", responder=None, use_cache=True):
        active_responder = responder if responder is not None else get_npc_local_model_adapter()
        return npc_local_ai_reply(self, player_text, responder=active_responder, use_cache=use_cache)

    def queue_reply_to_player(self, player_text="", use_cache=True):
        return queue_npc_ai_reply(self, player_text, use_cache=use_cache)

    def pop_queued_reply(self, request_id, forget=True):
        result = pop_npc_ai_reply(request_id, forget=forget)
        if result:
            self.pending_ai_request = None
            self.last_ai_reply = result.get("reply", "")
            self.last_ai_status = "idle" if result.get("status") == "ready" else result.get("status", "idle")
        return result

    def _activity_anchor(self):
        if self.current_need == "energy":
            return self.rest_anchor
        if self.current_need == "social":
            return self.social_anchor
        if self.current_need == "security":
            return (self.spawn_x, self.spawn_z)
        if self.current_need == "water":
            return (self.spawn_x - self.wander_radius * 0.55, self.spawn_z + self.wander_radius * 0.25)
        if self.current_need == "food":
            return (self.spawn_x + self.wander_radius * 0.35, self.spawn_z - self.wander_radius * 0.45)
        return self.work_anchor

    def choose_activity_target(self):
        anchor_x, anchor_z = self._activity_anchor()
        spread = 1.4 if self.current_need in ("energy", "security") else 2.8
        if self.current_need == "calm":
            spread = 3.5
        self.activity_step += 1
        jitter_x, jitter_z = _stable_offset(self.id, f"{self.activity}_{self.activity_step}", 0.4, spread)
        self.target_x = anchor_x + jitter_x
        self.target_z = anchor_z + jitter_z

    def apply_activity_effects(self, dt):
        anchor_x, anchor_z = self._activity_anchor()
        dist = math.hypot(self.x - anchor_x, self.z - anchor_z)
        self.activity_progress = max(0.0, min(1.0, 1.0 - dist / 4.0))
        if self.activity_progress <= 0.0:
            self.activity_effect = "travelling"
            return

        gain = dt * self.activity_progress
        if self.current_need == "food":
            self.needs["food"] = _clamp(self.needs["food"] + 2.8 * gain)
            self.activity_effect = "food_recover"
        elif self.current_need == "water":
            self.needs["water"] = _clamp(self.needs["water"] + 3.4 * gain)
            self.activity_effect = "water_recover"
        elif self.current_need == "energy":
            self.needs["energy"] = _clamp(self.needs["energy"] + 2.5 * gain)
            self.stress = _clamp(self.stress - 1.4 * gain)
            self.activity_effect = "rest_recover"
        elif self.current_need == "security":
            self.needs["security"] = _clamp(self.needs["security"] + 3.0 * gain)
            self.stress = _clamp(self.stress - 1.8 * gain)
            self.activity_effect = "security_recover"
        elif self.current_need == "social":
            self.needs["social"] = _clamp(self.needs["social"] + 2.4 * gain)
            self.stress = _clamp(self.stress - 0.9 * gain)
            self.activity_effect = "social_recover"
        else:
            self.needs["energy"] = _clamp(self.needs["energy"] + 0.10 * gain)
            self.needs["social"] = _clamp(self.needs["social"] + 0.05 * gain)
            self.stress = _clamp(self.stress - 0.35 * gain)
            self.activity_effect = f"work_{self.profession}"
        self.update_mood()

    def update(self, dt):
        self.update_needs(dt)
        moved = False
        if self.terrain_height_func:
            self.wander_timer += dt
            if self.wander_timer >= self.wander_change or math.hypot(self.target_x - self.x, self.target_z - self.z) < 0.3:
                self.wander_timer = 0.0
                self.wander_change = 1.5 + random.random() * 2.5
                self.choose_activity_target()

            dx = self.target_x - self.x
            dz = self.target_z - self.z
            dist = math.hypot(dx, dz)
            if dist > 0.05:
                step = self.speed * self.needs_speed_factor * dt
                move_x = dx / dist * min(step, dist)
                move_z = dz / dist * min(step, dist)
                self.x += move_x
                self.z += move_z
                self.yaw = math.degrees(math.atan2(move_x, move_z))
                moved = True

            # Mantener dentro del radio para que no se pierda
            dxs = self.x - self.spawn_x
            dzs = self.z - self.spawn_z
            if math.hypot(dxs, dzs) > self.wander_radius:
                ang = math.atan2(dzs, dxs) + math.pi
                self.x = self.spawn_x + math.cos(ang) * self.wander_radius
                self.z = self.spawn_z + math.sin(ang) * self.wander_radius
                self.direction = ang

            self.y = self.terrain_height_func(self.x, self.z) + self.height / 2
        self.apply_activity_effects(dt)
        target_move = 1.0 if moved else 0.0
        self.move_amount += (target_move - self.move_amount) * min(1.0, dt * 8.0)
        self.walk_phase += dt * (4.0 + self.speed * 2.0) * self.move_amount

    def render(self, highlight=False, debug_hitbox=False, detail_level="full"):
        from game.voxel_models import render_player_avatar, render_voxel_humanoid
        base_y = self.y - self.height / 2.0
        if hasattr(self, "admin_color"):
            body = self.admin_color
        else:
            # Color por profesion/hostilidad. Mantiene identidad sin usar modelos copiados.
            body = self.profession_color
        legendary = bool(getattr(self, "is_legendary", False))
        accent = (0.08, 0.08, 0.08) if not legendary else (1.0, 0.78, 0.10)
        detail_level = str(detail_level or "full")
        if detail_level == "far" and not highlight and not debug_hitbox:
            render_voxel_humanoid(
                self.x, base_y, self.z,
                yaw=self.yaw,
                body_color=body,
                skin_color=(0.78, 0.58, 0.40),
                accent_color=accent,
                legendary=legendary,
                debug_hitbox=False,
                selected=False,
                walk_phase=self.walk_phase,
                move_amount=min(0.45, self.move_amount),
                swimming=False,
            )
            return
        back_tool = None if detail_level != "full" else self.back_tool
        render_voxel_humanoid(
            self.x, base_y, self.z,
            yaw=self.yaw,
            body_color=body,
            skin_color=(0.78, 0.58, 0.40),
            accent_color=accent,
            legendary=legendary,
            debug_hitbox=debug_hitbox,
            selected=highlight,
            walk_phase=self.walk_phase,
            move_amount=self.move_amount,
            swimming=False,
        )

    def interactuar(self):
        self.update_mood()
        self.remember_event("interaction")
        if self.memoria == 1:
            line = f"Soy {self.nombre} {self.titulo}. Trabajo como {self.profession} y llevo mi {self.tool_label}."
            self.remember_event("dialogue", line)
            return line
        if self.memoria == 2:
            line = f"Mi asunto ahora es {self.work_action}; suelo moverme cerca de {self.workplace}."
            self.remember_event("dialogue", line)
            return line
        if self.memoria == 3:
            line = f"Estado: {self.mood}. {need_status_text(self.current_need)}."
            self.remember_event("dialogue", line)
            return line
        if self.memoria == 4:
            line = f"Actitud: {self.stance}. {self.mood_detail}."
            self.remember_event("dialogue", line)
            return line
        line = f"{dialogue_tone_prefix(self)} {contextual_dialogue_line(self, self.memoria)}"
        self.remember_event("dialogue", line)
        return line


def generar_npcs_chunk(cx, cz, semilla):
    r = random.Random((cx*92821) ^ (cz*68917) ^ semilla)
    npcs = []
    cantidad = r.randint(0, 3)
    for i in range(cantidad):
        seed = r.randint(1,999999)
        x = cx*100 + r.randint(0,99)
        z = cz*100 + r.randint(0,99)
        npcs.append(NPC(seed, x, z, id_source=f"chunk_{cx}_{cz}", id_slot=i))
    return npcs

