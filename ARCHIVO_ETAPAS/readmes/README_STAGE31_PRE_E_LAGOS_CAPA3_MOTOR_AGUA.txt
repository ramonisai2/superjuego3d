STAGE 31 PRE-E - LAGOS EN CAPA 3 + MOTOR DE AGUA

Base:
- Stage31 Pre-D 4 capas experimental.

Cambios principales:
1) Lagos bajos un poco mas frecuentes.
   - Se suavizo la probabilidad de cuencas bajas.
   - Se bajo un poco el umbral para que los lagos no sean tan raros.

2) Nuevo sistema experimental de lagunas altas en capa 3.
   - Se agrego _high_lake_basin_field().
   - Genera lagunas mas pequenas que los lagos bajos.
   - Solo aparece en altura media-alta / capa 3.
   - La capa 4 queda casi sin lagos comunes.

3) Motor de agua por capas.
   - Nivel de agua bajo: ~5.25.
   - Nivel de laguna alta: ~13.25.
   - Cada tipo usa terrazas locales distintas.
   - El sistema distingue agua baja y agua alta antes de elegir el water_level.

4) HUD/contexto actualizado.
   - Si estas dentro de agua alta, muestra: Dentro de laguna alta / Capa 3 alta-fresca.
   - Si estas en orilla alta, muestra: Orilla de laguna alta / Transicion alta.

Notas de diseno:
- La capa 4 debe sentirse fria, extrema y rara, por eso no se lleno con lagos comunes.
- Las lagunas de capa 3 ayudan a que las zonas altas no se sientan secas o muertas.
- Si aparecen demasiadas lagunas o muy pocas, ajustar:
  _high_lake_basin_field(), high_water_level, pond_core_high y high_layer_gate.
