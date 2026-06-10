"""Audita llamadas OpenGL legacy restantes.
Ejecutar desde juego3d_v1_5: python tools/audit_opengl_legacy.py
"""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    r"from OpenGL", r"import OpenGL", r"glBegin", r"glEnd", r"glVertex", r"glColor",
    r"glPushMatrix", r"glPopMatrix", r"glCallList", r"glNewList", r"glDeleteLists",
]
rx = re.compile("|".join(PATTERNS))
counts = {}
for path in sorted(ROOT.rglob("*.py")):
    if "__pycache__" in path.parts:
        continue
    n = 0
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if rx.search(line):
            n += 1
    if n:
        counts[str(path.relative_to(ROOT))] = n
print("OpenGL legacy audit")
print("===================")
for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
    print(f"{v:4d}  {k}")
print("-------------------")
print(f"Total archivos: {len(counts)}")
print(f"Total llamadas/imports detectados: {sum(counts.values())}")
