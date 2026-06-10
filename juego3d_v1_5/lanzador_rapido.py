import os
import sys
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
print("JUEGO 1.6 - Lanzador rapido")
print("Dependencias: pygame PyOpenGL numpy")
subprocess.call([sys.executable, "main.py"])
