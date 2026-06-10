import os
import time
import traceback

LOG_NAME = "respawn_debug.log"
_last_event = {}


def _log_path():
    # El log queda junto a main.py / lanzador_rapido.py.
    return os.path.join(os.getcwd(), LOG_NAME)


def log_event(tag, message="", **data):
    """Escribe una linea legible para rastrear el ciclo de reaparicion."""
    try:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        parts = [f"[{now}]", str(tag)]
        if message:
            parts.append(str(message))
        for key, value in data.items():
            try:
                if isinstance(value, float):
                    value = f"{value:.4f}"
                parts.append(f"{key}={value}")
            except Exception:
                parts.append(f"{key}=<error_repr>")
        line = " | ".join(parts)
        with open(_log_path(), "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line)
    except Exception:
        # Nunca debe romper el juego por fallar el log.
        pass


def log_exception(tag, exc):
    try:
        log_event(tag, "EXCEPTION", error=repr(exc))
        with open(_log_path(), "a", encoding="utf-8") as f:
            traceback.print_exc(file=f)
    except Exception:
        pass


def log_throttled(tag, seconds=1.0, message="", **data):
    now = time.time()
    last = _last_event.get(tag, 0.0)
    if now - last >= seconds:
        _last_event[tag] = now
        log_event(tag, message, **data)
