STAGE33 X - TORNEO TERRENO

Objetivo:
- Comparar metodos completos antes de elegir el final.
- No cambiar el default todavia.
- Medir elevacion y chunk completo.

Competidores:
- current: metodo actual completo.
- fast_noise: elevacion economica + agua/biomas actuales.
- fast_noise_lite: elevacion economica + agua simplificada.

Lanzadores:
- PROBAR_RUIDO_TERRENO.bat
- ELEGIR_METODO_TERRENO.bat
- LANZAR_OPENGL.bat
- LANZAR_OPENGL_FAST_NOISE.bat
- LANZAR_OPENGL_FAST_NOISE_LITE.bat

Regla de decision:
- Si current se ve mucho mejor, se queda current y se optimiza por partes.
- Si fast_noise se ve bien y gana mucho, sera el candidato principal.
- Si fast_noise_lite gana pero se ve pobre, se usa solo como referencia de rendimiento.

Resultado observado:
- En elevacion pura, fast_noise gano cerca de x7.5.
- En chunk completo, la ganancia vario bastante: en la ultima lectura fast_noise quedo cerca de x1.12 y fast_noise_lite cerca de x1.19.
- La muestra perdio agua visible en fast_noise/fast_noise_lite.
- Decision actual del recomendador: mantener current como default y probar fast_noise/lite solo visualmente.

No se hizo ZIP.
