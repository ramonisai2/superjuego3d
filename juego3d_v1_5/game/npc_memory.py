"""Memoria persistente y notas compactas de NPCs."""

from __future__ import annotations


NPC_MEMORY_REGISTRY = {}
NPC_MEMORY_MAX_NOTES = 8


def need_status_text(need_name):
    return {
        "food": "necesito comida antes de seguir trabajando",
        "water": "necesito agua; asi nadie rinde",
        "energy": "me falta descanso",
        "security": "este lugar no se siente seguro",
        "social": "me vendria bien hablar con alguien",
        "calm": "por ahora estoy tranquilo",
    }.get(need_name, "estoy observando la zona")


def compact_memory_notes(record, limit=4):
    notes = record.get("notes", []) if isinstance(record, dict) else []
    compact = []
    for note in notes[-limit:]:
        if not isinstance(note, dict):
            continue
        compact.append({
            "event": str(note.get("event", "")),
            "mood": str(note.get("mood", "")),
            "stance": str(note.get("stance", "")),
            "detail": str(note.get("detail", ""))[:160],
        })
    return compact


def npc_memory_for(npc):
    record = NPC_MEMORY_REGISTRY.get(npc.id)
    if record is None:
        record = {
            "id": npc.id,
            "canonical": _memory_canonical(npc),
            "encounters": 0,
            "trust": 0.0,
            "last_need": npc.current_need,
            "last_intent": npc.intent,
            "last_activity": getattr(npc, "activity", "wander"),
            "last_mood": getattr(npc, "mood", "calmado"),
            "last_stance": getattr(npc, "stance", "abierto"),
            "last_position": (round(npc.x, 2), round(npc.z, 2)),
            "notes": [],
        }
        NPC_MEMORY_REGISTRY[npc.id] = record
    else:
        canonical = record.setdefault("canonical", _memory_canonical(npc))
        npc.nombre = canonical.get("name", npc.nombre)
        npc.titulo = canonical.get("title", npc.titulo)
    record["last_need"] = npc.current_need
    record["last_intent"] = npc.intent
    record["last_activity"] = getattr(npc, "activity", "wander")
    record["last_mood"] = getattr(npc, "mood", "calmado")
    record["last_stance"] = getattr(npc, "stance", "abierto")
    record["last_position"] = (round(npc.x, 2), round(npc.z, 2))
    return record


def remember_npc_event(npc, event, detail=None):
    record = npc_memory_for(npc)
    if event == "interaction":
        record["encounters"] += 1
        record["trust"] = _clamp(record.get("trust", 0.0) + 1.5, 0.0, 100.0)
    note = {
        "event": event,
        "need": npc.current_need,
        "intent": npc.intent,
        "activity": getattr(npc, "activity", "wander"),
        "mood": getattr(npc, "mood", "calmado"),
        "stance": getattr(npc, "stance", "abierto"),
        "detail": detail or need_status_text(npc.current_need),
    }
    notes = record.setdefault("notes", [])
    notes.append(note)
    if len(notes) > NPC_MEMORY_MAX_NOTES:
        del notes[:-NPC_MEMORY_MAX_NOTES]
    return record


def npc_memory_snapshot(npc):
    record = npc_memory_for(npc)
    canonical = record.get("canonical", {})
    return {
        "id": record["id"],
        "identity": canonical.get("identity"),
        "name": canonical.get("name"),
        "title": canonical.get("title"),
        "profession": canonical.get("profession"),
        "encounters": record.get("encounters", 0),
        "trust": round(record.get("trust", 0.0), 2),
        "last_need": record.get("last_need", "calm"),
        "last_intent": record.get("last_intent", "wander"),
        "last_activity": record.get("last_activity", "wander"),
        "last_mood": record.get("last_mood", "calmado"),
        "last_stance": record.get("last_stance", "abierto"),
        "last_position": record.get("last_position"),
        "last_note": record.get("notes", [])[-1] if record.get("notes") else None,
    }


def export_npc_memory():
    records = []
    for record in NPC_MEMORY_REGISTRY.values():
        safe = _safe_memory_record(record)
        if safe["id"]:
            records.append(safe)
    return {
        "version": "stage35_p_npc_memory_v2",
        "records": records,
    }


def import_npc_memory(payload, merge=True):
    if not payload:
        return 0
    records = payload.get("records", payload if isinstance(payload, list) else [])
    if not isinstance(records, list):
        return 0
    if not merge:
        NPC_MEMORY_REGISTRY.clear()
    loaded = 0
    for record in records:
        if not isinstance(record, dict):
            continue
        npc_id = str(record.get("id", ""))
        if not npc_id:
            continue
        safe = _safe_memory_record(record)
        safe["id"] = npc_id
        NPC_MEMORY_REGISTRY[npc_id] = safe
        loaded += 1
    return loaded


def clear_npc_memory():
    NPC_MEMORY_REGISTRY.clear()


def _memory_canonical(npc):
    return {
        "name": npc.nombre,
        "title": npc.titulo,
        "profession": npc.profession,
        "identity": npc.identity_key,
        "seed": int(npc.seed),
        "hostility": int(npc.hostilidad),
        "damage": int(getattr(npc, "daño", getattr(npc, "dano", 0))),
        "tool": npc.back_tool,
        "tool_label": npc.tool_label,
        "temper": npc.temper,
        "skin_preset": npc.skin_preset,
    }


def _safe_memory_record(record):
    canonical = dict(record.get("canonical", {}))
    notes = list(record.get("notes", []))[-NPC_MEMORY_MAX_NOTES:]
    last_position = record.get("last_position", (0.0, 0.0)) or (0.0, 0.0)
    if len(last_position) < 2:
        last_position = (0.0, 0.0)
    return {
        "id": str(record.get("id", "")),
        "canonical": canonical,
        "encounters": int(record.get("encounters", 0)),
        "trust": round(_clamp(float(record.get("trust", 0.0))), 2),
        "last_need": str(record.get("last_need", "calm")),
        "last_intent": str(record.get("last_intent", "wander")),
        "last_activity": str(record.get("last_activity", "wander")),
        "last_mood": str(record.get("last_mood", "calmado")),
        "last_stance": str(record.get("last_stance", "abierto")),
        "last_position": [float(last_position[0]), float(last_position[1])],
        "notes": notes,
    }


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))
