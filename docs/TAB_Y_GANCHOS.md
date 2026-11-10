# Tabulador y dos ganchos de prueba (05/11/2026)

Publicado en `20eb286` e instalado en Aternos el 05/11/2026.
Se reemplazaron el datapack y `astral_gameplay.sk`, se actualizaron encabezado,
pie y objetivo de vida de TAB conservando el panel instalado, y se aplicaron
los colores de grupos y las dos animaciones Astral. Respaldos de TAB en
`.local/backups/tab-gancho-2026-11-05/` (ignorados por Git).

Arranque completo confirmado: los nueve scripts cargaron sin errores,
`datapack list enabled` incluyo AstralRPG y `tab reload` termino correctamente.
ByTrainx se conecto y recibio una unidad de cada gancho. La consola confirmo
ambas entregas. Captura local: `build/Aternos-tab-ganchos-instalados.jpg`.

El tabulador comparte titulo, degradado azul/violeta, separadores, textos claros
y colores secundarios con `sidebar.py`. Conserva jugadores, vida, oro, poder,
ping, TPS y ubicacion; fecha e IP tambien salen del mismo estilo del panel.
Los nombres y el poder de cada fila usan esa paleta. Las antiguas animaciones
siguen disponibles con el estilo compartido y la IP del panel.

Hay dos objetos independientes:

- `gancho`: Gancho de Escalada original, conserva el impulso por mirada.
- `gancho_realista`: Gancho realista, caña vanilla con anzuelo e hilo reales.
  Usar en la mano principal: clic derecho lanza, otro clic recoge. Solo tira
  del jugador si el anzuelo esta clavado en un bloque o engancho una entidad.
  La direccion depende del anclaje, aunque cambies la mirada. Recoger en el
  aire o pescar en agua no impulsa. Es un tiron con velocidad y colisiones
  normales, no un teletransporte ni un sistema de balanceo permanente.

El nuevo gancho tiene alcance de tiron de 32 bloques, comparte recarga de dos
segundos con el anterior y proteccion de caida durante el lanzamiento. Ambos
siguen bloqueados en mazmorras. No tiene receta, precio ni premios de gacha:
es una variante para probar. Usa el modelo nativo, sin cambiar el resource pack.
Su identidad se comprueba por `custom_data`, no por el nombre de un yunque;
el lanzamiento se vincula al UUID del jugador y del anzuelo.

Para obtenerlos en Minecraft (OP), una vez instalado:

```mcfunction
/loot give @s loot astral:item/gancho
/loot give @s loot astral:item/gancho_realista
```

Tambien estan en `/function astral:admin/kit_especiales`.

Instalacion:

1. Con el servidor apagado, reemplazar `world/datapacks/AstralRPG-Items.zip`
   por `build/AstralRPG-Items.zip`.
2. Reemplazar `plugins/Skript/scripts/astral_gameplay.sk` con el de
   `build/gameplay/astral_gameplay.sk`.
3. Aplicar las secciones generadas en `build/lobby/TAB/secciones-config.yml`
   al config de TAB, reemplazar `groups.yml` y las dos animaciones Astral.
4. Arrancar, ejecutar `tab reload` y probar ambos objetos.

Generacion: `python datapack-src/build.py` y `python datapack-src/lobby.py`.
Validacion automatica: 4 pruebas del nuevo gancho, 8 de gameplay y 13 de
misiones; `verify.py` comprueba JSON y referencias. Paper 26.1.2 y Skript 2.17.1
cargaron el datapack y el script; la recarga termino sin errores (registro en
`build/gameplay/gancho-validacion-local.txt`). La sensacion del tiron,
las colisiones y la apariencia del tabulador requieren prueba con jugador.

## Correccion de contacto y ubicacion (05/11/2026)

La prueba del jugador encontro que la boya vanilla rebotaba en las paredes y
caia: `bobber in ground` no bastaba para anclarla. Ahora se comprueba contacto
con las seis caras del bloque, se guarda ese bloque y la posicion de contacto,
y se fija la boya sin gravedad manteniendo el sedal. Al recoger se acepta ese
anclaje tambien si Minecraft emite `reel in`. Aire y agua no sirven; romper el
bloque libera el gancho. Distancia y propietario siguen validados.

Prueba de contacto ejecutada en Paper/Skript local: 8/8 (seis caras, aire y
agua); cinco pruebas Python del gancho. El script carga sin errores.
El tabulador y panel muestran `Portales Astrales`; el contador de capacidad
usa `%server_max_players%` en lugar del placeholder sin resolver.

## Saltador y Gancho (08/11/2026)

- `gancho` se llama **Saltador** y se ve como una **bola de slime** (`minecraft:slime_ball`).
  Mas adelante tendra skin propia.
- `gancho_realista` se llama **Gancho** y usa la skin del gancho (`astral:gancho`, ya esta en el
  resource pack). Al lanzarlo no cambia de aspecto (la skin no tiene estado "lanzado").
- El aspecto se fuerza en `build.py`, despues de los bucles de texturas que ponen `astral:<id>`.
- `ITEM_VERSION` 10: los que ya tienen los objetos los ven actualizados al entrar.

## Panel lateral preparado el 10/11/2026

Vuelve TAB como panel general, con las diez filas de BetterHud y nombre de mundo. Minas Astrales conserva su tablero. `/sb` se recuerda mediante `astral_panel.sk`; BetterHud queda apagado por defecto. No se cambio Duels ni la barra roja de Momia. Vista `build/previews/panel-tab.png`, colores exactos `build/deploy/panel-tab-lineas.txt`, instalacion pendiente `build/deploy/tanda1.md`.
