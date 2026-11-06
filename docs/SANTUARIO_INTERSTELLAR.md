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

## Instalado y verificado

Instalado en Aternos desde `2627ba6`, junto con la recuperacion de Bosque.
Se respaldo `region/` y se sustituyeron solo sus cuatro `.mca`, con el servidor
apagado. Se instalaron los dos YAML generados de Santuario y se cambio solo su
destino en el script de viajes. FreeMap9 permanece aparte, sin ser el acceso
activo de la mazmorra. Se conservaron los otros destinos del script.

La consola comprobo piso de hierro y dos bloques de aire en llegada y arena,
ademas de un volumen de 9x9x6 de aire en la zona de aparicion. Se fijo el spawn
en la llegada original y se desactivo su ajuste automatico. Faltaba el controlador
en esta dimension: se creo uno y se consulto su posicion `46.5 180 48.5`.
Se mantuvo la aparicion de mobs de plugins y se aplicaron protecciones de cofres
y PvP, sin mobs naturales y conservando el inventario.

Se retiraron las tres cargas temporales de esta dimension y se confirmo el
guardado con `save-all flush`. Los scripts cargaron sin errores y no se
observaron fallos al leer el mapa. El servidor quedo online con 20 TPS.
Tambien se comprobo que el aldeano del Nether conserva la nueva posicion.

Validacion local: 25 pruebas pasaron, ademas de la comprobacion directa de ambos
escenarios por sus generadores. Sigue pendiente el recorrido y combate completo
con jugadores. Respaldos y comprobantes privados en
`.local/santuario-correcto-2026-11-05/`: `region-antes.zip`, `informe.json`,
`consola-verificacion.txt` y `aternos-online.jpg`.
