# Tarjetas para Gemini (21/11/2026): pagina 2 de Portales y de Minas

Claude no puede hablar con Gemini: el dueno pega estos pedidos en Gemini y guarda las imagenes.
Hasta que esten, el juego usa arte provisorio (cabecera de la ventana del Oceano, la carta End
oscurecida con la cinta PROXIMAMENTE y el bosque de Expediciones).

## Donde guardar cada imagen

| Tarjeta | Archivo | Forma |
|---|---|---|
| Oceano Astral | `datapack-src/pack-source/ref/gemini/tarjeta_oceano.png` | apaisada, 3:2 |
| Mazmorra del End | `datapack-src/pack-source/ref/gemini/tarjeta_end_nave.png` | apaisada, 3:2 |
| Bosque Astral | `datapack-src/pack-source/ref/gemini/tarjeta_bosque.png` | apaisada, 16:9 |

`travel_ui.card_art()` las toma solas si existen. Fondo magenta puro (#FF00FF) alrededor: se borra
solo. Solo la pintura: el marco dorado, el nombre y la cinta PROXIMAMENTE los dibuja el generador
con el mismo estilo de las tarjetas de la pagina 1. Despues: `python build_pack.py pack-source`,
subir el pack a R2 (ver CLAUDE.md) y reiniciar.

## Estilo comun (pegar al principio de cada pedido)

> Pixel art de videojuego, estilo de las tarjetas ilustradas de un RPG de Minecraft: colores
> saturados, contornos marcados, iluminacion dramatica, lectura clara en tamano chico (se va a ver
> a unos 70 x 50 pixeles). Sin texto, sin letras, sin marco, sin bordes. Una sola escena que llene
> todo el cuadro. Fondo exterior magenta puro #FF00FF solo si sobra espacio.

## 1. Oceano Astral (Portales, pagina 2)

> Escena submarina profunda y magica: ruinas de columnas de piedra cubiertas de coral violeta y
> rosa, una gran almeja abierta con una perla celeste brillante en el centro, rayos de luz que bajan
> desde la superficie, burbujas, algas que se mueven, peces pequenos. Paleta: azul profundo,
> turquesa, violeta y toques de rosa coral. Sensacion de mundo entero bajo el agua y algo de peligro
> (sombra de una criatura grande al fondo). Formato apaisado 3:2.

## 2. Mazmorra del End - nave astral (Portales, pagina 2, proximamente)

> Una nave espacial gigante varada en el vacio del End, construida con bloques violetas y rosados,
> con lineas de luz blanca y dorada que la recorren como venas. Vista desde afuera, flotando sobre
> islas de piedra del End, cielo negro con estrellas y polvo violeta. Una entrada iluminada deja ver
> un pasillo largo de paredes rosadas con paneles de luz amarilla. Atmosfera misteriosa, de algo que
> todavia no se puede visitar. Formato apaisado 3:2. Diseno original, no copiar construcciones de
> otros autores.

## 3. Bosque Astral (Minas, pagina 2)

> Un bosque frondoso de robles y abetos altos, con un claro donde hay un tocon recien talado y un
> hacha clavada, troncos apilados y aserrin. Luz calida de tarde entre las hojas, pequenas
> particulas brillantes violetas flotando (toque astral). Paleta: verdes vivos, marron de madera,
> dorado de la luz. Formato apaisado 16:9.

## Si Gemini devuelve una hoja con varias

Pedir las tres en una sola hoja (fila de izquierda a derecha: oceano, nave del End, bosque) sobre
fondo magenta, y recortarlas a mano a los tres archivos de arriba.
