# Santuario: mapa entregado por el dueno

El 05/11/2026 el dueno proporciono `mapa_santuario.rar` y pidio instalarlo como
mapa de la mazmorra. Esta version reemplaza el destino de la mazmorra, conservando
las dimensiones anteriores. No se publica el mapa de terceros en GitHub.

Fuente: `FreeMap9.schematic`, Minecraft 1.12.2. Sus dimensiones son 154x127x175
(X/Y/Z), con origen de seleccion `-43 70 -124`. Se compararon 141 muestras no
vacias del schematic contra el mundo incluido: todas coinciden en ese origen.
`CORDS.txt` no indica un piso seguro para la construccion y no se uso como llegada.

`santuario_mapa.py` separa bloques y decoracion estatica, elimina entidades,
inventarios y logica activa, y convierte 72 chunks mediante el DataFixer del
Paper local 26.1.2. `ConvertLegacyChunks.java` es el ayudante de conversion.
La preparacion genera cuatro regiones y metadatos nativos con generador plano
de aire, sin estructuras, para la dimension nueva `santuario_freemap9`.
No se importan los datapacks, jugadores ni configuraciones del mundo original.

Ejecutar con un Java 25 local y las bibliotecas del servidor de prueba:

```text
python santuario_mapa.py --schematic ../.local/santuario-freemap9/original/FreeMap9.schematic --java <ruta-java.exe> --server ../.local/asw-native/server --out ../.local/santuario-freemap9/preparacion
```

La carpeta `santuario_freemap9` resultante se sube desde Files a
`world/dimensions/minecraft/`, solo si ese nombre esta libre y con el servidor
apagado. No usar Worlds > Upload sobre `world`. Luego importar con
`mv import minecraft:santuario_freemap9 normal` y comprobar el generador.

Llegada: `33.5 103 -40.5`, sobre tablones de abedul, mirando al norte.
Controlador: `33.5 103 -60.5`, sobre bloque de hueso, radio 32.
La inspeccion local comprobo piso y seis bloques de aire en un area de 13x13
alrededor de ambos puntos. El radio de aparicion de jefes es 4, dentro de ese
espacio. Se conservan las cinco oleadas: Cangrejo, Chaman, Momia, Yeti y Golem.
La llegada queda a 20 bloques del controlador y activa la sala.

Regenerar con `python mobs/mazmorra.py` y `python viajes_mazmorras.py`.
Instalar `build/mythicmobs/{mobs,skills}/santuario.yml` en MythicMobs y
`build/mapas_exploracion/astral_viajes.sk` en `plugins/Skript/scripts/`.
Los dos generadores toman el destino del mismo catalogo. El nombre del permiso
`astral.descubierto.santuario` y los accesos del menu se conservan.

Crear un unico controlador en el punto indicado, luego de verificar piso y
espacio. Aplicar las reglas y protecciones de los comandos generados. No hacer
aparecer otro NPC de descubrimiento si el del mapa de expedicion ya existe.
La prueba completa del combate con jugadores debe registrarse por separado.
