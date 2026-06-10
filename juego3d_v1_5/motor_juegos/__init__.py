"""Entrada ligera del paquete motor_juegos.

Los probes tecnicos de Vulkan importan submodulos del paquete sin necesitar
cargar Pygame/OpenGL completo. Las clases pesadas se importan bajo demanda.
"""

from importlib import import_module


__all__ = ['GameEngine', 'AudioManager', 'FirstPersonCamera', 'r3d', 'r2d', 'biomes', 'env']


def __getattr__(name):
    if name == "GameEngine":
        from .core import GameEngine
        return GameEngine
    if name == "AudioManager":
        from .audio import AudioManager
        return AudioManager
    if name == "FirstPersonCamera":
        from .input import FirstPersonCamera
        return FirstPersonCamera
    if name == "r3d":
        return import_module(f"{__name__}.renderer3d")
    if name == "r2d":
        return import_module(f"{__name__}.renderer2d")
    if name == "biomes":
        return import_module(f"{__name__}.biomes")
    if name == "env":
        return import_module(f"{__name__}.environment")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
