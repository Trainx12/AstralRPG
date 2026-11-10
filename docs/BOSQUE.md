# Bosque Astral (tala con motosierras)

Pedido del dueño (08/11/2026): un bosque para talar, con muchos tipos de árboles, sobre todo abetos
gigantes, que vuelven a crecer **3 minutos** después de talarlos. Todo sale de
`datapack-src/bosque_talar.py` → `build/bosque/astral_bosque.sk` y `build/bosque/instalacion.txt`.

## Cómo funciona

- **Mundo propio** `astral_bosque` (vacío, sin mobs ni clima, mediodía fijo). Se entra con el botón
  **Bosque Astral** (casilla 47, abajo a la izquierda) del menú `/minas`, o con `/bosque` desde el lobby,
  las minas o el bosque.
- **64 árboles** en una grilla de 8 × 8 (celdas de 14 × 14, esquina en `0 0`, pasto en Y 64). 33 son
  abetos gigantes (`mega_spruce` y `mega_pine`); el resto: abeto, pino, roble, roble grande, abedul,
  abedul alto, roble oscuro, jungla, jungla gigante, acacia y cerezo. Los genera Minecraft con
  `place feature` (formas naturales), con una semilla fija: siempre sale el mismo bosque.
- **Moldes:** cada árbol tiene una copia idéntica debajo (pasto en Y −60), en los mismos chunks.
  Regenerar es `clone ... masked` del molde a su lugar: solo pone lo que falta.
- **Regeneración:** al romper un tronco u hoja a mano se anota la hora. La motosierra del datapack no
  dispara eventos de Skript, así que además cada 5 s se revisa el tronco de cada árbol (Y 65). A los
  3 minutos se copia el molde. Si el chunk no está cargado, se reintenta.
- **Protección:** solo se rompen troncos, madera, hojas, enredaderas, cacao y colmenas, y solo dentro de
  la grilla. No se puede poner bloques, vaciar baldes ni recibir daño; las hojas no se caen; las
  explosiones no rompen nada. Si alguien cae bajo Y 55 vuelve al spawn (`-4.5 65 56.5`).
- **Venta rápida:** `astral_npc_bosque_venta` («Venta rapida - maderas») reutiliza
  `am_sale_menu`, la interfaz `minas-venta` y el cobro de Minas. Vende troncos, troncos
  sin corteza, madera de seis caras con/sin corteza y tablones de roble, abeto, abedul,
  jungla, acacia, roble oscuro, cerezo y mangle. Excluye Nether y objetos con nombre o
  lore. Usa precios fijos de `services_catalog.json`, catálogo de EconomyShopGUI.
  Minas conserva sus precios de `minas.py`. Actualizar el catálogo y regenerar si cambia la tienda.
- **Precios pendientes:** faltan `stripped_cherry_log`, `stripped_cherry_wood`,
  `stripped_mangrove_log` y `stripped_mangrove_wood` en el catálogo. Estas cuatro
  variantes permanecen en el inventario: no se inventa su precio ni se venden aún.
- **Viajes:** `astral_npc_bosque_viaje` («Viajes - minas y lobby») abre el mismo
  `/minas` mediante `minasmenu`; incluye el botón Lobby. Constantes del generador:
  `VENDOR=(-1.5,65,56.5,90)` y `TRAVEL=(-7.5,65,56.5,-90)`, a tres bloques del
  spawn mirando hacia él. Piso de pasto Y 64 fuera de la plataforma de piedra.
- **Recolección:** romper normalmente usa los drops de la herramienta (incluida
  Fortuna), `clear drops` y `am_give`, igual que Minas; sin espacio caen a los pies.
  La motosierra usa `tool/bosque_loot`: marca solo entidades creadas por su comando
  de loot, excluyendo todas las que ya estaban allí. Un componente temporal evita
  mezclarlas con drops manuales; el retraso de recogida evita recoger esa marca.
  Cada dos ticks el Skript retira el componente y entrega las pilas marcadas a un
  jugador a hasta 48 bloques (incluye las copas altas). Entregar y eliminar la
  entidad ocurre sin esperas, para impedir doble cobro. Si no entra la pila completa,
  retira la marca y deja el objeto a los pies para recogida normal. No hace falta
  seguir sosteniendo la motosierra después del corte.
- Las motosierras funcionan normal: `astral_bosque` no está en la lista de mundos bloqueados del datapack
  y el jugador pierde la marca `astral.mines` al salir de las minas.

## Instalar

Seguir `build/bosque/instalacion.txt`: crear el mundo con Multiverse, subir `astral_bosque.sk` y el
`astral_minas.sk` nuevo, recargar y correr `bosquegenerar` desde la consola (≈30 s). Revisar parado en
el spawn que estén los 64 árboles; los que no se pudieron colocar quedan sin molde y se ignoran.
`/bosquereset` vuelve a copiar todos los moldes. Comandos de admin: permiso `astral.minas.admin`.

## Estado en Empower (08/11/2026)

Mundo creado, script cargado sin errores y `bosquegenerar` corrido: 64 copias, ninguna vacía
(entre 220 y 889 bloques por árbol). `time set noon` falla en 26.1 ("world without world clock");
si el bosque queda oscuro hay que resolver la hora de otra forma. Falta probar talando.

## Actualización Tanda 2c (preparada, sin desplegar)

Lista exacta: `build/deploy/tanda2c.md`. Apagar para reemplazar el datapack, subir los
scripts de Minas/Bosque y los mobs MythicMobs indicados, iniciar y revisar consola.
Cargar Minas antes del Bosque: el Bosque comparte sus funciones. Para esta actualización
no ejecutar `bosquegenerar`, no recrear mundos ni reemplazar moldes. Los comandos para
los dos aldeanos están al final de `build/bosque/instalacion.txt`, rodeados de
`mob-spawning allow` y `deny`. Falta confirmar en Paper la carga de Skript, ventas,
Fortuna, inventario lleno, drops manuales y tala de dos jugadores a la vez.
