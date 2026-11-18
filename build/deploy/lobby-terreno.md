# Terreno del lobby — propuesta del 17/11/2026

> **18/11: VIGENTE la v4** en `.local/lobby/propuesta-v4/` (config `.local/lobby/config-v4.json`, 778 sectores,
> 1.220.437 bloques). Pedido del dueno: base de isla flotante en vez de pared recta. La profundidad de las columnas
> nuevas crece desde el borde (6 bloques) hacia adentro (hasta 50), con ruido y puntas colgantes, y la piel de abajo
> usa los materiales medidos en el original (terracota cian, losas de pizarra, ladrillos de piedra negra, concreto
> gris). Ladera exterior mas tendida (`outer_exponent` 1.1). Control de accesos: 55 vias, 21 bloques de portal y
> 258 carteles detectados, ninguno con bloques nuevos a menos de 3 bloques al costado ni 6 arriba.
> **PEGADO el 18/11 01:43** desde la consola (sin jugador): `//world lobby`, `//placement pos1`, y por sector
> `//pos1 X,Y,Z` + `//schem load lobby_N_despues.schem` + `//paste -a`. Se uso `propuesta-v4b` (misma propuesta
> regenerada con el lobby bajado el 18/11; resultado identico a v4). 778/778 sectores, 1.232.668 bloques segun
> WorldEdit = bloques no-aire de los schematics. Respaldo del panel previo: "Antes terreno lobby 18-11" (851 MB).
> Los `lobby_N_antes.schem` quedan en `plugins/WorldEdit/schematics/` para deshacer (`//paste` SIN `-a`).

Generado por `datapack-src/lobby_terreno.py`. Estado: **borrador para aprobacion visual;
no instalado ni pegado**. Solo Parte B. Doble salto del lobby conservado; Parte A
ya instalada en `054db88`, no se genera ni se sube ningun Skript en esta entrega.
Empower es el servidor principal; Aternos conserva una copia.

## Archivos y reproduccion

Original intacto: `C:/Users/Trainx/Downloads/Parrot Spawn.zip` (Parrot Spawn, terceros).
Nueve regiones actuales descargadas por lectura oficial a `.local/lobby/actual/region/`:
`r.X.Z.mca` para cada combinacion X/Z de -1, 0 y 1. No se descargo ni ejecuto codigo
del mapa. La copia leida con el servidor activo es una referencia de trabajo,
no reemplaza un respaldo coherente del panel ni garantiza que el lobby siga igual.

Configuracion privada revisada: `.local/lobby/config-v3.json`.
Salida vigente: `.local/lobby/propuesta-final/`. Conservar las propuestas v1/v2 como historial, no instalarlas.
Los archivos privados NO estan en GitHub. En otra maquina se necesita acceso a estas
copias y su configuracion; no reconstruir el mapa desde el repositorio publico.

```powershell
.\.local\tanda17-venv\Scripts\python.exe datapack-src/lobby_terreno.py --actual .local/lobby/actual/region --original 'C:/Users/Trainx/Downloads/Parrot Spawn.zip' --config .local/lobby/config-v3.json --out .local/lobby/propuesta-revision --delivery
```

Requiere Python con `numpy` y `Pillow`. Usar una carpeta de salida nueva; el generador
rechaza sobrescribir respaldos/propuestas. La accion `download` de `tools/empower_api.py`
usa `/files/download` oficial, exige HTTPS y no imprime claves ni URLs firmadas:

```text
python tools/empower_api.py --yes download /world/dimensions/minecraft/lobby/region/r.0.0.mca .local/lobby/nueva-lectura/region/r.0.0.mca
```

Repetir para las nueve regiones. Sin `--yes` simula sin leer claves ni conectar.
No se usa ninguna API privada de Aternos ni se modifica el mundo remoto en esta tarea.

## Propuesta y protecciones

Se comparan alturas del original y del lobby actual en las mismas coordenadas.
Las muestras de referencia excluyen la torre del loro del sur. Suelo medido a Y94–102;
roca medida por bandas de ocho bloques. El original no tiene la paleta supuesta en las
capturas: se usan los materiales efectivamente presentes, sin inventar podzol/rooted dirt.
Los conteos y proporciones exactos estan en `manifest.json` (privado).

- Suelo medido: coarse_dirt 702, dirt 184, grass_block 726, moss_block 973, mud 1.
- Roca medida: cobbled_deepslate 228, cobblestone 8, polished_deepslate 262.
- Altura de referencia P95 de roca: Y145; se modula hacia abajo con ruido.
- Manchas: escala 2.0 bloques, mediana de tramos de suelo originales;
  se ordena el ruido para respetar las proporciones de la paleta superficial.
- 978 columnas candidatas de pasto/tierra agregados. Solo una capa
  superficial; se conserva el pasto original y el suelo cerca de edificios/caminos.
- Anillo cerrado con cresta irregular, base solida y cobertura de musgo/pasto;
  123 bambues y 13 arboles sinteticos.
  Hojas de jungla y madera vertical presentes en el original; no se copian arboles enteros.
- 21430 columnas protegidas por construcciones, agua/caminos no naturales
  y margen de cinco bloques; block entities con margen adicional. Exclusion explicita
  del centro de servicios/spawn en la configuracion. La union baja solo rellena columnas
  vacias hasta Y97; no levanta montanas dentro de los margenes protegidos.
- Los caminos de piedra, edificios, portales, carteles, cofres e inventarios no se cambian.
  No se copian entidades ni biomas. Se rechazan chunks sin descargar y anillos recortados.

Limite: las detecciones automaticas no reconocen todos los usos del lobby. Revisar
especialmente accesos al tren, laterales del castillo, portales, senderos y bordes
de las extensiones. Las protecciones pueden dejar una ladera mas baja junto a un edificio.
La propuesta aun requiere aprobacion del dueno con las vistas y, preferiblemente,
una copia de prueba del lobby. No se verifico carga/pegado con WorldEdit real.

## Revision privada

Ver en `.local/lobby/propuesta-final/previews/`:

- `lobby_terreno_antes_planta.png` y `lobby_terreno_despues_planta.png`.
- `lobby_terreno_antes_tres_cuartos.png` y `lobby_terreno_despues_tres_cuartos.png`.

Son renders CPU con colores de materiales y caras de voxeles; no capturas en Minecraft.
No publicarlos en `build/previews/` ni en GitHub: son derivados de un mapa de terceros.
Este criterio sigue `docs/TERCEROS.md` y corrige la ruta publica sugerida en el plan.

## Lista exacta para instalar DESPUES de aprobar

Origen local: `.local/lobby/propuesta-final/schematics/`.
Destino remoto unico: `plugins/WorldEdit/schematics/`.

Son 1602 archivos: por cada entero N entre **0000 y 0800, inclusive**, subir
`lobby_N_antes.schem` y `lobby_N_despues.schem` (cuatro digitos, sin saltos).
**No mezclar archivos de propuestas distintas**: los mismos nombres se reutilizan.
Conservar tambien el manifest/respaldos locales de esta version. El listado individual
con SHA-256, caja XYZ, esquina de pegado y destino esta en `.local/lobby/propuesta-final/manifest.json`.
No subir `manifest.json`, `validation.json`, vistas, `.mca`, ZIP original ni configuracion
privada al servidor o al repositorio publico.

1. Cerrar el acceso al lobby para mantenimiento y verificar que no hubo ediciones
   desde la descarga. Si cambio, volver a descargar/regenerar y aprobar la nueva propuesta.
2. Antes de pegar: **apagar el servidor para obtener un respaldo coherente del panel**;
   comprobar que termino y que contiene el lobby. Reiniciar sin reemplazar mundos.
   Los backups de antes de esta tarea no sustituyen el respaldo inmediatamente previo.
3. Subir solamente los schematics indicados. WorldEdit los lee al cargar: **sin comando
   de recarga de plugins, datapack ni resource pack**. Pegarlos con el servidor encendido,
   un unico jugador OP y acceso al lobby cerrado. No hace falta otro reinicio por terreno.
4. Probar primero un sector en una copia de prueba. Verificar que WorldEdit instalado
   reconoce Sponge v3 y DataVersion 4790. Hay muchos sectores: aplicar
   de a uno o en tandas cortas, esperar que termine cada operacion y revisar consola/TPS.
   No aumentar limites globales ni automatizar los 801 pegados en el servidor activo.
5. Seguir en orden `.local/lobby/propuesta-final/pegar.txt`. Contiene 801 bloques de comandos exactos,
   cada uno con el TP a la **esquina minima XYZ** especifica del sector, seguido por:

   ```text
   //schem load lobby_N_despues
   //paste -a
   ```

   Ejecutar como jugador OP en **lobby** (`/mvtp w:lobby` antes del primer TP).
   El TP es `/minecraft:tp @s X Y Z`; pasar a espectador para evitar quedar atrapado
   y restaurar el modo previo al terminar. Offset `[0,0,0]`: no rotar, voltear ni
   usar `//paste -o`. El TP fija la esquina, no el centro del schematic.
6. Revisar consola por errores y recorrer en cliente la union, accesos y suelo.
   Solo afirmar despliegue tras verificar el resultado. No ejecutar setup del lobby.

Nunca usar Worlds > Upload en la fila `world`, ni sustituir mundos ni regiones.
No se cambia el datapack, JAR, pack FINAL/R2, gameplay o MythicMobs en esta entrega.

## Reversion

Para el ultimo pegado de la misma sesion: `//undo` (conservar la sesion y el historial).
Para restaurar los sectores aplicados, usar sus lineas correspondientes en
`.local/lobby/propuesta-final/restaurar.txt`: mismo mundo y esquina, `//schem load lobby_N_antes` y **`//paste`
sin `-a`**. El aire del respaldo retira roca, plantas y arboles nuevos. No restaurar
sectores que no se aplicaron ni hacerlo sobre ediciones posteriores de otros usuarios.
Los cubos completos conservan estados originales; no incluyen cofres/carteles con NBT.
El respaldo del panel queda como recuperacion independiente si se pierde el historial.

## Verificaciones de esta propuesta

- 801 pares Sponge v3 releidos; 1,933,046 posiciones comparadas
  contra los bloques descargados; 1,555,424 cambios.
- 1,554,721 posiciones de aire incluidas en los respaldos. No se elimina
  ningun bloque en la propuesta y los cambios sobre bloques existentes son solo pasto/tierra.
- Propiedades de bloques conservadas; block entities, entidades y biomas excluidos.
- Pruebas de lector MCA moderno, coordenadas negativas, varints >127, respaldo con aire,
  division alrededor de cofres, exclusiones, limites, descarga binaria y simulacion sin red.
- Carga de WorldEdit real, aprobacion visual y despliegue remoto: **pendientes**.

Formato: [especificacion oficial Sponge v3](https://github.com/SpongePowered/Schematic-Specification/blob/master/versions/schematic-3.md).
