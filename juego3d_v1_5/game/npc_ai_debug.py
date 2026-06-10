from game.npc_manager import npc_ai_runtime_stats


def _clip(text, limit):
    text = str(text)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def npc_ai_telemetry_lines(stats=None):
    stats = stats or npc_ai_runtime_stats()
    telemetry = stats.get("telemetry", {})
    queue = stats.get("queue", {})
    cache = stats.get("cache", {})
    requests = int(telemetry.get("requests", 0) or 0)
    backend = int(telemetry.get("backend_replies", 0) or 0)
    fallback = int(telemetry.get("fallback_replies", 0) or 0)
    hits = int(telemetry.get("cache_hits", 0) or 0)
    errors = int(telemetry.get("errors", 0) or 0)
    pending = int(queue.get("pending", 0) or 0)
    completed = int(queue.get("completed", 0) or 0)
    cache_entries = int(cache.get("entries", 0) or 0)
    avg_ms = float(telemetry.get("avg_ms", 0.0) or 0.0)
    max_ms = float(telemetry.get("max_ms", 0.0) or 0.0)
    last_ms = float(telemetry.get("last_ms", 0.0) or 0.0)
    source = telemetry.get("last_source", "none")
    error = telemetry.get("last_error") or "sin error"
    return [
        f"IA NPC req:{requests} back:{backend} cache:{hits} fall:{fallback} err:{errors}",
        f"Tiempo avg:{avg_ms:.1f} max:{max_ms:.1f} last:{last_ms:.1f} ms src:{source}",
        f"Cola pend:{pending} ready:{completed} cache:{cache_entries}",
        f"Ultimo: {_clip(error, 38)}",
    ]
