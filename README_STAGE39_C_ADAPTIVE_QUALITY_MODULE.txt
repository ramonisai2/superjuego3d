JUEGO 1.6 - Stage39 C - ADAPTIVE QUALITY MODULE

Objetivo
- Reducir main.py para que sea mas manejable con LLM local.
- Separar las reglas de calidad adaptativa, fog, distancias de render y limite LOD.

Cambios
- Se agrego juego3d_v1_5\main_adaptive_quality.py.
- main.py crea un AdaptiveQualityRuntime y consulta sus metodos durante update/render.
- La estructura y el estado rapido ahora verifican el modulo nuevo.

Notas
- No cambia el modo recomendado: OpenGL estable sigue siendo la ruta jugable.
- Vulkan sigue como laboratorio futuro.
- No se genero ZIP.
