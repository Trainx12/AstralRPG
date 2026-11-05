# Reparacion selectiva de Portales y Forja

Preparacion del 05/11/2026. La inspeccion de regiones descargadas de Aternos
encontro solo aire en las llegadas de Portales y en el portal del End.
Forja usaba un generador normal de terreno en sus metadatos Paper 26.1.
No se establecio que cambio anterior produjo estos estados.

`datapack-src/restaurar_mundos.py` prepara archivos privados en
`.local/restauracion-mundos-2026-11-05/`. Requiere las copias privadas existentes,
`portal_END.schem` y el `world_gen_settings.dat` descargado de Forja en Downloads.
Los mapas de terceros y los respaldos nunca se publican en GitHub.

El End se reconstruye con el Offset del schematic v3 y el punto de pegado original
`146 82 78`. Se retira terreno natural, se sostienen los pisos de polvo y se
rellenan huecos interiores del piso con concreto negro. No es una copia binaria
del ultimo mundo editado: se recupera desde la construccion original.
Guardianes se recupera de la copia separada privada y se alinea con la llegada
guardada `-2192.5 81 90.5`, desplazando su origen 92 bloques al sur.
Se conserva el portal activo. `/umbrales` y sus destinos no cambian.

Forja se recupera de las 16 regiones preparadas de `volcano.zip`, sin agua.
El generador Paper se cambia a plano de aire, sin estructuras. Se conserva el
nombre `forja_volcano`, la semilla, las otras dimensiones y los datos del servidor.
La llegada sigue en `82.5 52 -55.5`. El espacio de combate y su controlador
siguen pendientes de seleccion, como antes de esta reparacion.

Instalacion, siempre con el servidor apagado:

- Respaldar las regiones actuales y los metadatos de Forja.
- Los cuatro `.mca` de `portales_astrales/region` preparados van unicamente a
  `world/dimensions/minecraft/portales_astrales/region/`.
- Los 16 `.mca` de `forja_volcano/region` van unicamente a
  `world/dimensions/minecraft/forja_volcano/region/`.
- `forja_volcano/data/minecraft/world_gen_settings.dat` va a la misma ruta dentro
  de esa dimension. No reemplazar el `world_gen_settings.dat` del mundo principal.
- No subir `level.dat`, ZIP de mundo, inventarios, entidades ni datapacks.
- Iniciar y comprobar consola, pisos y dos bloques de aire en las tres llegadas,
  portales activos y generacion de aire fuera de la Forja.
- Reponer los aldeanos de Portales solo si faltan; aplicar proteccion y reglas
  de Forja. Retirar todas las cargas temporales de revision.

El script verifica las llegadas y el End activo antes de producir el informe
privado con hashes SHA-256. Estas comprobaciones locales no sustituyen las de
la consola despues de instalar.
