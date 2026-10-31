# Texture pack de referencia — 31/10/2026

Preparado localmente. Esta version todavia no se publico en GitHub ni se instalo en Aternos.

- `build/AstralRPG-Textures.zip`: pack completo para Minecraft 26.1.2.
- `build/Menu-style-preview.png`: simulacion del menu de pausa, no captura del juego.
- `build/HUD-preview.png`: corazones, escudos, comida y burbujas de la lamina; barra inferior vanilla.
- `build/Items-reference-preview.png`: 24 iconos de armadura y 30 armas/herramientas extraidos
  directamente de la referencia, sin suavizado ni redibujo. Solo se quita el fondo gris.
- `build/Armor-vanilla-preview.png`: render con el atlas real y el volumen vanilla. Las armaduras
  puestas son una adaptacion propia; no contienen modelos de Armored Legacy ni requieren mods.

El menu usa arte ilustrado preparado a partir de la captura en `pack-source/ref/escape-art.png`.
Los botones de volver/desconectar usan glifos bitmap para dibujar personajes, cofres y el pergamino
fuera del rectangulo normal; conservan sus zonas de clic. Las traducciones se limitan a esos dos
rotulos. El boton Guia AstralRPG sigue viniendo de `astral:guia` y del tag `pause_screen_additions`
del datapack, y aparece en la segunda fila derecha de la vista previa.

La barra de objetos, seleccion, mano secundaria, XP, salto, recarga y barras de jefes se heredan
de Minecraft. El constructor filtra las texturas antiguas para que no vuelva la barra morada.
No se cambian bloques ni las armas, objetos y armaduras de los tiers RPG.

Los iconos de cuero sin tinte usan un modelo sin la capa y el tinte marron vanilla, para conservar
el dibujo de la referencia dentro del juego. Los objetos tenidos conservan un icono coloreable.
Los trims se mantienen en la armadura puesta; el icono de cuero muestra el dibujo de referencia.

## Regenerar

Desde la raiz del repositorio, con la carpeta de GUI original extraida del cliente:

```text
python datapack-src/gui_textures.py .local/vanilla-gui --client-jar <26.1.2.jar>
python datapack-src/reference_style.py --client-jar <26.1.2.jar>
python datapack-src/build_pack.py datapack-src/pack-source
python datapack-src/verify.py --client-jar <26.1.2.jar>
```

Verificado: rutas y medidas de los 59 sprites del HUD contra el cliente, 54 iconos 16x16,
16 capas de armadura 64x32, proveedores de fuente y traducciones. Los recortes de iconos
se compararon pixel por pixel con la lamina original. Falta comprobar el menu con el pack
cargado en un cliente real, especialmente el espacio inferior en las distintas escalas GUI.

SHA1 del ZIP: `52ae8e58d3105d6d68009911eeeccdb64b1c8d47`.
