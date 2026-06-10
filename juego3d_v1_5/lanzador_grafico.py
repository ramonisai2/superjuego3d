import os
import subprocess
import sys
import tkinter as tk
from motor_juegos.version_info import full_update_name, UPDATE_CODENAME, UPDATE_SUBTITLE
from motor_juegos.render_mode_status import write_render_mode_log
from tkinter import messagebox

ROOT = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(ROOT, "main.py")


def run_backend(backend: str, graphics_preset: str = None):
    env = os.environ.copy()
    if graphics_preset:
        env["JUEGO_GRAPHICS_PRESET"] = graphics_preset
    if backend == "opengl":
        env["JUEGO_RENDER_BACKEND"] = "opengl"
    elif backend == "opengl_stream_bridge":
        env["JUEGO_RENDER_BACKEND"] = "opengl"
        env["JUEGO_STREAM_BRIDGE_SAFE"] = "1"
    elif backend == "vulkan":
        # Ruta Vulkan experimental actual. Cambiar aqui cuando el backend Vulkan avance.
        env["JUEGO_RENDER_BACKEND"] = "vulkan_present"
    elif backend == "vulkan_probe":
        env["JUEGO_RENDER_BACKEND"] = "vulkan_shader_module"
    else:
        env["JUEGO_RENDER_BACKEND"] = backend

    try:
        if backend == "diagnostic":
            subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_render.py")], cwd=ROOT, env=env)
            return
        os.environ.update({"JUEGO_RENDER_BACKEND": env.get("JUEGO_RENDER_BACKEND", "opengl")})
        write_render_mode_log(f"launcher backend={backend}")
        subprocess.Popen([sys.executable, MAIN], cwd=ROOT, env=env)
    except Exception as exc:
        messagebox.showerror("Error al iniciar", str(exc))


def run_bat(script_name: str):
    try:
        subprocess.Popen([os.path.join(ROOT, script_name)], cwd=ROOT, shell=True)
    except Exception as exc:
        messagebox.showerror("Error al iniciar", str(exc))


def main():
    app = tk.Tk()
    app.title("JUEGO 1.6 - Lanzador de render")
    app.geometry("450x820")
    app.resizable(False, False)

    tk.Label(app, text="JUEGO 1.6", font=("Arial", 18, "bold")).pack(pady=(12, 2))
    tk.Label(app, text=full_update_name(), font=("Arial", 10, "bold"), fg="#334455").pack(pady=(0, 2))
    tk.Label(app, text=f"Nombre clave: {UPDATE_CODENAME}", font=("Arial", 10), fg="#555555").pack(pady=(0, 4))
    tk.Label(app, text="Selecciona motor de render", font=("Arial", 11)).pack(pady=(0, 16))

    tk.Button(
        app,
        text="Iniciar con OpenGL estable",
        font=("Arial", 12, "bold"),
        width=34,
        height=2,
        command=lambda: run_backend("opengl"),
    ).pack(pady=6)

    tk.Button(
        app,
        text="OpenGL bajo FPS",
        font=("Arial", 10),
        width=34,
        command=lambda: run_backend("opengl", "low"),
    ).pack(pady=3)

    tk.Button(
        app,
        text="OpenGL alto detalle",
        font=("Arial", 10),
        width=34,
        command=lambda: run_backend("opengl", "high"),
    ).pack(pady=3)

    tk.Button(
        app,
        text="OpenGL + Puente Seguro",
        font=("Arial", 11, "bold"),
        width=34,
        height=1,
        command=lambda: run_backend("opengl_stream_bridge"),
    ).pack(pady=4)

    tk.Button(
        app,
        text="OpenGL + Puente Balanced",
        font=("Arial", 10),
        width=34,
        command=lambda: run_bat("LANZAR_OPENGL_STREAM_BRIDGE_BALANCED.bat"),
    ).pack(pady=4)

    tk.Button(
        app,
        text="Probar Vulkan experimental",
        font=("Arial", 12, "bold"),
        width=34,
        height=2,
        command=lambda: run_backend("vulkan"),
    ).pack(pady=6)

    tk.Button(
        app,
        text="Vulkan probe técnico",
        font=("Arial", 10),
        width=34,
        command=lambda: run_backend("vulkan_probe"),
    ).pack(pady=6)


    tk.Button(
        app,
        text="Diagnóstico de render",
        font=("Arial", 10),
        width=34,
        command=lambda: run_backend("diagnostic"),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Diagnóstico Surface Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_surface_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Diagnóstico Surface Real Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_surface_real_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Ventana Vulkan dedicada",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_vulkan_ventana.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Puente SDL/Vulkan Surface",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_surface_bridge.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="SDL2 directo Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_sdl2_direct_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Crear Surface Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_surface_create.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Swapchain Vulkan Real",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_swapchain_real.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Crear Swapchain Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_swapchain_create.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Frames Swapchain Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_swapchain_frame.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Present Clear Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_present_clear.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Backend Vulkan Persistente",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_backend_vulkan_persistente.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Vulkan Clear Visible",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "lanzar_vulkan_clear_visible.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Modo Vulkan Experimental Z",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "lanzar_vulkan_experimental.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="MeshData Chunk Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_meshdata_chunk_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Chunk Buffer Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_chunk_buffer_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Chunk drawIndexed Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_chunk_drawindexed_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Pipeline Terreno Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_terrain_pipeline_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="RenderPass Primer Chunk",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "diagnostico_first_chunk_renderpass_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)


    tk.Button(
        app,
        text="Primer Chunk Visible Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "lanzar_first_chunk_visible_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)

    tk.Button(
        app,
        text="Anillo de Chunks Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "lanzar_multi_chunk_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)

    tk.Button(
        app,
        text="Varios Chunks Visibles Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "lanzar_multi_chunk_visible_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)

    tk.Button(
        app,
        text="Anillo Jugador/Camara Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "lanzar_player_chunk_ring_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)

    tk.Button(
        app,
        text="Streaming Chunks Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "lanzar_chunk_streaming_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)

    tk.Button(
        app,
        text="Puente Mundo/Chunks Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "lanzar_world_chunk_bridge_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)

    tk.Button(
        app,
        text="Puente Seguro Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "lanzar_safe_stream_bridge_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)

    tk.Button(
        app,
        text="Stats Puente Seguro Vulkan",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "lanzar_stream_bridge_stats_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)

    tk.Button(
        app,
        text="Comparar Puente Seguro",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "lanzar_stream_bridge_comparison_vulkan.py")], cwd=ROOT),
    ).pack(pady=4)

    tk.Button(
        app,
        text="Probe Prueba Jugable",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "lanzar_guided_playtest_probe.py")], cwd=ROOT),
    ).pack(pady=4)

    tk.Button(
        app,
        text="Analizar Logs Playtest",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "analizar_playtest_logs.py")], cwd=ROOT),
    ).pack(pady=4)

    tk.Button(
        app,
        text="Recomendar Ajustes",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "recomendar_ajustes_playtest.py")], cwd=ROOT),
    ).pack(pady=4)

    tk.Button(
        app,
        text="Presupuesto Puente",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "lanzar_stream_bridge_budget_probe.py")], cwd=ROOT),
    ).pack(pady=4)

    tk.Button(
        app,
        text="Comparar Presets Puente",
        font=("Arial", 10),
        width=34,
        command=lambda: subprocess.Popen([sys.executable, os.path.join(ROOT, "comparar_presets_stream_bridge.py")], cwd=ROOT),
    ).pack(pady=4)

    tk.Label(
        app,
        text="OpenGL = modo jugable. Vulkan = prueba experimental.",
        font=("Arial", 9),
        fg="#444444",
    ).pack(pady=(12, 0))

    app.mainloop()


if __name__ == "__main__":
    main()
