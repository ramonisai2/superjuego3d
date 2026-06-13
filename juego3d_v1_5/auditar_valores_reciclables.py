"""Audita literales repetidos para decidir que valores conviene reciclar.

No todos los numeros repetidos son deuda: 0, 1, colores y coordenadas de modelos
suelen ser datos locales. Este reporte prioriza valores que aparecen en varios
archivos y parecen tuning reutilizable.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import ast


REPORT_NAME = "valores_reciclables_report.txt"
IGNORED_DIRS = {"__pycache__", ".git", "logs", "previews", "debug_head_faces"}
COMMON_NUMBERS = {"-1", "0", "1", "0.0", "1.0", "2", "3", "4", "5", "255"}
COMMON_STRINGS = {"__main__", "utf-8", ".1f", ".2f", ": ", "; ", ". "}


@dataclass
class LiteralHit:
    value: str
    count: int
    file_count: int
    samples: list[str]


def _iter_python_files(root: Path):
    for path in root.rglob("*.py"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        yield path


def _scan_literals(root: Path):
    number_counts: Counter[str] = Counter()
    string_counts: Counter[str] = Counter()
    number_files: defaultdict[str, set[str]] = defaultdict(set)
    string_files: defaultdict[str, set[str]] = defaultdict(set)
    number_samples: defaultdict[str, list[str]] = defaultdict(list)
    string_samples: defaultdict[str, list[str]] = defaultdict(list)

    for path in _iter_python_files(root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        display_path = str(path.relative_to(root))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant):
                continue
            value = node.value
            lineno = int(getattr(node, "lineno", 0) or 0)
            if isinstance(value, bool) or value is None:
                continue
            if isinstance(value, (int, float)):
                key = repr(value)
                number_counts[key] += 1
                number_files[key].add(display_path)
                if len(number_samples[key]) < 8:
                    number_samples[key].append(f"{display_path}:{lineno}")
            elif isinstance(value, str) and 2 <= len(value) <= 48:
                key = value
                string_counts[key] += 1
                string_files[key].add(display_path)
                if len(string_samples[key]) < 8:
                    string_samples[key].append(f"{display_path}:{lineno}")

    return number_counts, string_counts, number_files, string_files, number_samples, string_samples


def _rank_hits(counts, files, samples, *, min_count=8, min_files=2, ignored=None):
    ignored = ignored or set()
    hits = []
    for value, count in counts.items():
        if value in ignored:
            continue
        file_count = len(files[value])
        if count >= min_count and file_count >= min_files:
            hits.append(LiteralHit(value=value, count=count, file_count=file_count, samples=list(samples[value])))
    return sorted(hits, key=lambda hit: (hit.file_count, hit.count), reverse=True)


def _format_hit(hit: LiteralHit) -> str:
    return f"{hit.value!r:<18} x{hit.count:<4} archivos={hit.file_count:<3} muestras={', '.join(hit.samples)}"


def build_report(root: str | None = None) -> str:
    base = Path(root).resolve() if root else Path(__file__).resolve().parent
    number_counts, string_counts, number_files, string_files, number_samples, string_samples = _scan_literals(base)
    number_hits = _rank_hits(number_counts, number_files, number_samples, ignored=COMMON_NUMBERS)
    string_hits = _rank_hits(string_counts, string_files, string_samples, min_count=6, ignored=COMMON_STRINGS)

    lines = [
        "JUEGO 1.6 - REPORTE DE VALORES RECICLABLES",
        "",
        "Lectura:",
        "- Repetido no siempre significa malo.",
        "- Prioridad alta: valores con significado de gameplay, rendimiento, distancias, densidades o rutas.",
        "- Prioridad baja: coordenadas de modelos, colores puntuales, 0/1 y texto de reportes.",
        "",
        "Candidatos numericos repetidos:",
    ]
    if number_hits:
        for hit in number_hits[:40]:
            lines.append(_format_hit(hit))
    else:
        lines.append("- Sin candidatos claros.")

    lines.extend(["", "Candidatos de texto repetidos:"])
    if string_hits:
        for hit in string_hits[:40]:
            lines.append(_format_hit(hit))
    else:
        lines.append("- Sin candidatos claros.")

    lines.extend([
        "",
        "Acciones recomendadas:",
        "- Reciclar primero valores que ya tienen nombre en otro modulo.",
        "- Evitar crear constantes globales para colores o medidas artisticas muy locales.",
        "- Si un valor controla gameplay/render y aparece en varios archivos, moverlo a un modulo de tuning.",
        "- Si un valor solo se repite dentro de una funcion corta, dejarlo local salvo que confunda.",
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
