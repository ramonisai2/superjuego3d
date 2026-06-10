
BIOME_NPCS={
 'swamp':['Rey del Pantano','Recolector','Chamán'],
 'desert':['Bandido','Mercader','Ermitaño'],
 'forest':['Cazador','Druida','Leñador']
}
def get_biome_npcs(biome):
    return BIOME_NPCS.get(biome,[])
