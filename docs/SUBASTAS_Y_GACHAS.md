# Subastas y gachas

Generadores: `datapack-src/market_ui.py`, `menus.py` y `auction_ui.py`.
Vista previa conjunta: `build/Servicios-preview/subastas-y-gachas.png`.
La vista previa compone el arte; los simbolos de los controles pequenos indican
su posicion. Dentro del juego se muestran los objetos e informacion del menu.

## Disenos

- Casa de Subastas: nogal, oro, terciopelo rojo, martillo y monedas.
- Arsenal Arcano (gacha_rpg): obsidiana, espadas, baston y cristales violetas.
- Sendas Salvajes (gacha_monturas): madera, hojas, silla y plumas.
- Galeria Celeste (gacha_cosmeticos): plata, oro rosa, corona y estrellas.

Marcos originales creados con ImageGen integrado, guardados en
`datapack-src/pack-source/ref/{subastas,gacha_rpg,gacha_monturas,gacha_cosmeticos}-frame.png`.
Prompts: marco pixel art frontal 4:5, exterior transparente, centro vacio grande,
borde estrecho, cartel superior sin letras; motivos y materiales de cada tema
listados arriba; sin botones, rejilla, perspectiva ni marcas. Textos, mosaicos,
fuentes y zonas de clic se generan por codigo.

## Interaccion

Los cuatro recuadros de cada menu usan ocho mosaicos de 18 px con la misma
accion en toda su superficie. Los gachas conservan precios, premios, garantia
y tiradas x1/x10/x25/x50. Muestran saldo, progreso de garantia y probabilidades;
la vitrina de premios y la ruleta siguen a cargo de CrazyCrates.
Las aperturas externas esperan tres ticks despues del cierre de DeluxeMenus.

Subastas abre el mercado, las publicaciones propias y los objetos por retirar
en CrazyAuctions. Publicar muestra la instruccion `/ah sell <precio>` para el
objeto en la mano: ese recuadro es ayuda, no publica automaticamente. El Bazar
y el NPC Subastas abren este menu nuevo. `/ah` conserva el catalogo directo.

El marco del catalogo real se aplica a sus tres ventanas de seis filas (mercado,
publicaciones y retiradas); no se aplica al dialogo de compra de otro tamano.
Se consultaron las claves y comandos en las fuentes oficiales:
https://github.com/Crazy-Crew/CrazyAuctions/blob/main/common/src/main/resources/config.yml
https://docs.crazycrew.us/mods/crazyauctions/reference/commands/

## Generar e instalar

Desde `datapack-src`:

```text
python market_ui.py
python menus.py
python auction_ui.py
python build_pack.py pack-source
python mobs/mythic.py
python -m unittest test_market_ui test_bazar
python verify.py --client-jar <26.1.2.jar>
```

Subir `build/AstralRPG-Textures.zip` y actualizar su SHA1 al publicarlo.
Copiar los menus generados de DeluxeMenus y agregar la entrada `subastas`
de `build/menus/DeluxeMenus/config-gui_menus.yml` al registro existente.
Actualizar la configuracion de mobs generada y recargar DeluxeMenus/MythicMobs.
No reconstruir el lobby ni recrear NPCs.

En CrazyAuctions, aplicar SOLO los tres titulos de
`build/menus/CrazyAuctions/titulos.patch.yml` al `Settings` del config existente;
el parche NO reemplaza el archivo completo. Alternativamente, ejecutar
`python auction_ui.py --config <copia-config-servidor.yml>` para preparar una
copia completa en `.local/auction-ui-deploy/config.yml`, conservando los demas
campos y comentarios. Recargar con `/ah reload`. No tocar `data.yml`.

Verificacion local: pruebas de las 96 zonas de tirada, costo unico por clic,
condiciones de garantia, cantidades multiples, rutas del arte, avance cero de
los titulos, limite de 256 px por bitmap y navegacion sin cierre tardio.
Las tres ventanas del catalogo usan el mismo marco, pero cada titulo lleva al
final una marca invisible distinta (``, ``, ``, avance 0):
CrazyAuctions decide la logica de cada clic con `title.contains(...)`, y con
titulos iguales un clic en "Mis publicaciones" pasaria por la del mercado.

Instalado en Aternos el 01/11/2026: pack fijado al commit `70e0d0d`, menus de
las tres gachas y Bazar reemplazados, `subastas.yml` creado y registrado en
`plugins/DeluxeMenus/config.yml`, NPC Subastas actualizado en
`MythicMobs/mobs/astral.yml` y los tres titulos cambiados en
`CrazyAuctions/config.yml`. El servidor arranco con 15 menus y sin errores.
Pendiente: probar con un jugador el aspecto, cobros, premios y compras reales.
