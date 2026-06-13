"""Audita tamanos de archivos Python para trabajar mejor con LLMs locales."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPORT_NAME = "tamano_py_report.txt"
TARGET_MAX_LINES = 1000
IGNORED_DIRS = {"__pycache__", ".git", "logs", "previews", "debug_head_faces"}


@dataclass
class PyFileSize:
    path: str
    lines: int


SPLIT_HINTS = {
    "main.py": [
        "main_config.py: presets, constantes y lectura JUEGO_*.",
        "main_world_queries.py: altura, agua, celdas y busquedas de recursos.",
        "main_runtime_state.py: estado global inicializado del juego.",
        "main_rendering.py: render de mundo, entidades, HUD y estadisticas.",
        "main_loop.py: update principal y arranque.",
    ],
    "game\\npc_manager.py": [
        "npc_identity.py: nombres, profesiones, ids y semillas estables.",
        "npc_needs.py: hambre, energia, estres, confianza y rutinas.",
        "npc_ai.py: decision de trabajo/descanso/interaccion.",
        "npc_render.py: detalle visual, etiquetas y modelo humanoide.",
        "npc_manager.py: fachada pequena que conserva imports antiguos.",
    ],
    "motor_juegos\\environment.py": [
        "terrain_runtime.py: seleccion current/fast_noise y caches.",
        "world_detail.py: densidades, impostores y decoracion.",
        "water_surface.py: ajuste de agua, orillas y altura visual.",
        "chunk_mesh_builder.py: construccion de MeshData/handles.",
        "environment.py: fachada pequena que conserva API publica.",
    ],
}


def _iter_python_files(root: Path):
    for path in root.rglob("*.py"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        yield path


def _count_lines(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:
        return 0


def scan_sizes(root: str | None = None) -> list[PyFileSize]:
    base = Path(root).resolve() if root else Path(__file__).resolve().parent
    items = []
    for path in _iter_python_files(base):
        rel = str(path.relative_to(base))
        items.append(PyFileSize(path=rel, lines=_count_lines(path)))
    return sorted(items, key=lambda item: item.lines, reverse=True)


def build_report(root: str | None = None, target_max_lines: int = TARGET_MAX_LINES) -> str:
    base = Path(root).resolve() if root else Path(__file__).resolve().parent
    items = scan_sizes(str(base))
    oversized = [item for item in items if item.lines > target_max_lines]

    lines = [
        "JUEGO 1.6 - REPORTE DE TAMANO PY PARA LLM LOCAL",
        "",
        f"Meta recomendada: archivos principales de {target_max_lines} lineas o menos.",
        "",
        "Lectura:",
        "- No conviene partir por numero exacto si rompe responsabilidades.",
        "- Conviene dejar fachadas pequenas para no romper imports antiguos.",
        "- Los LLM locales trabajan mejor con modulos pequenos y nombres claros.",
        "",
        "Archivos mas grandes:",
    ]
    for item in items[:30]:
        marker = "DIVIDIR" if item.lines > target_max_lines else "ok"
        lines.append(f"{item.lines:>5}  {marker:<7}  {item.path}")

    lines.extend(["", "Candidatos sobre la meta:"])
    if oversized:
        for item in oversized:
            lines.append(f"- {item.path}: {item.lines} lineas")
            hints = SPLIT_HINTS.get(item.path)
            if hints:
                for hint in hints:
                    lines.append(f"  * {hint}")
    else:
        lines.append("- Ningun archivo supera la meta actual.")

    lines.extend([
        "",
        "Ruta segura para refactorizar:",
        "1. Crear modulo nuevo con funciones puras o datos constantes.",
        "2. Importarlo desde el archivo grande.",
        "3. Verificar py_compile y una prueba pequena.",
        "4. Solo despues mover otro bloque.",
        "5. Mantener archivo fachada si otros modulos importan desde el nombre antiguo.",
        "",
        "Prompts utiles para Continue/Ollama:",
        "- Trabaja solo en el archivo indicado y su modulo nuevo.",
        "- No cambies comportamiento publico ni nombres importados.",
        "- Mantén cada archivo por debajo de 1000 lineas cuando sea razonable.",
        "- Despues de mover codigo, ejecuta py_compile del archivo viejo y nuevo.",
        "",
    ])
    return "\n".join(lines)


def write_report(root: str | None = None) -> str:
    base = Path(root).resolve() if root else Path(__file__).resolve().parent
    logs_dir = base / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    path = logs_dir / REPORT_NAME
    path.write_text(build_report(str(base)), encoding="utf-8")
    return str(path)


if __name__ == "__main__":
    report_path = write_report()
    print(build_report())
    print("Reporte:", report_path)
