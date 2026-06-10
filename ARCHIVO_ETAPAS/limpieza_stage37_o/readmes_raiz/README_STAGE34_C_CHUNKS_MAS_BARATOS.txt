STAGE34 C - CHUNKS MAS BARATOS

Objetivo:
- Reducir el costo de generar chunks al moverse.
- Mantener OpenGL estable como modo jugable.
- Mantener current como metodo default porque conserva mejor lagos, mesetas y biomas.

Cambios:
- La suavizacion escalar de biomas ya no usa np.clip por cada celda.
- La tabla base de biomas se calcula una sola vez, no miles de veces por chunk.
- Se conserva la regla especial de cuevas.

Resultado observado:
- Chunk current antes de esta fase: cerca de 480-510 ms.
- Chunk current despues: cerca de 208-233 ms en las pruebas locales.
- fast_noise_lite solo gana alrededor de x1.08 y pierde agua visible en la muestra.

Decision:
- Default recomendado: current.
- Lanzador recomendado: LANZAR_OPENGL.bat.
- Vulkan sigue como laboratorio, no como render principal.

Siguiente paso:
- Probar movimiento real con LANZAR_OPENGL.bat.
- Si todavia hay bajones, ejecutar logs de movimiento y atacar render/decoraciones visibles.

No se hizo ZIP.
