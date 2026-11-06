# Santuario: mapa confirmado por el dueno

El 05/11/2026 el dueno corrigio su seleccion y confirmo
`mapa_Santuari_Mazmorra.zip` como mapa de la mazmorra. Contiene un unico archivo,
`interstellar.litematic`. La copia privada usada anteriormente coincide byte por
byte con el archivo dentro de este ZIP. FreeMap9 deja de ser el destino activo.

`datapack-src/santuario_interstellar.py` extrae esa fuente del ZIP original y
genera cuatro regiones privadas en `.local/santuario-correcto-2026-11-05/`.
No se importan entidades, inventarios, datapacks ni configuraciones del mapa.
Se excluyen bloques de logica activa. El origen del escenario es `-152 48 -152`.

Llegada: `34.5 180 40.5`. Controlador: `46.5 180 48.5`, radio 18. Ambas posiciones
tienen piso original de hierro y tres bloques de aire. El generador comprueba
ademas un area de 9x9 con seis bloques libres para las apariciones de radio 4.
Se conservan las cinco oleadas, recompensas, permisos y progreso existentes.

SHA-256 del ZIP confirmado:
`7f267ce135cfc599df52d83141215b657cf3bf397c6f5496dc9b3440ea5ee032`.

Instalar con el servidor apagado solo las cuatro regiones generadas en
`world/dimensions/minecraft/santuario_interstellar/region/`, despues de respaldar
las anteriores. No reemplazar world ni usar Worlds > Upload. Mantener la
dimension FreeMap9 aparte, sin cambiar sus archivos.

Regenerar `mobs/mazmorra.py` y `viajes_mazmorras.py`. Instalar los YAML de mobs y
skills de Santuario y actualizar su destino en el script de viajes, conservando
los otros destinos instalados. Comprobar el controlador existente antes de
crear uno nuevo. No duplicarlo. Registrar aparte el recorrido y combate real.
