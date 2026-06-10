"""Diagnostico simple de paquetes para elegir Python destino."""

from __future__ import annotations

import importlib.util


MODULES = (
    ("numpy", "numpy"),
    ("pygame", "pygame"),
    ("PyOpenGL", "OpenGL"),
    ("Pillow", "PIL"),
)


def main() -> None:
    missing = [name for name, module in MODULES if importlib.util.find_spec(module) is None]
    score = len(MODULES) - len(missing)
    print(f"{score}|{', '.join(missing) if missing else 'ninguno'}")


if __name__ == "__main__":
    main()
