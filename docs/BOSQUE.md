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
- **Pago:** la madera se vende en la tienda como cualquier tronco (lo que paga cada árbol).
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
