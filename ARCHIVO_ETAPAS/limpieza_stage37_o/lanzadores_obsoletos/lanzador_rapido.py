import os
import subprocess
import sys

base = os.path.dirname(os.path.abspath(__file__))
game_dir = os.path.join(base, "juego3d_v1_5")
os.chdir(game_dir)
subprocess.call([sys.executable, "main.py"])
