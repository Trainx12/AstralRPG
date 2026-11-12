# Contenidos privados - tanda 4a

Santuario Azeroth: `Spires of Azeroth.zip` y sus regiones convertidas son de terceros.
Original intacto en Downloads; etapas, regiones y vistas CPU exclusivamente en
`.local/santuario-azeroth/`. No publicar mapas, schematics ni las vistas derivadas.
Codigo/configuracion propios y entrega se publican: [santuario-azeroth.md](../build/deploy/santuario-azeroth.md).
El mapa no se incorpora al resource pack ni necesita cambiar el FINAL privado.

## Tren del lobby (preparado, sin desplegar)

`tren_lobby.py` conserva el ZIP original Steam Train Coaster en `ASTRAL_PRIVADO/x/tren/`
y sus derivados solo en `ASTRAL_PRIVADO/build/entregas/tren-lobby/`.
Convierte paper/CMD viejo a item_model 26.1 y atlas item, sin override vanilla.
El FINAL se basa exclusivamente en la entrega Alas/casco y conserva cada entrada previa.
Codigo, referencias de modelos y configuracion de tren propia se publican sin arte;
el auditor incluye el ZIP anidado original. No publicar capturas del arte licenciado.
Los pastes originales no se pudieron recuperar (HTTP 403); offsets de asientos y escala
deben cotejarse en cliente. Lista de instalacion: [tren-lobby.md](../build/deploy/tren-lobby.md).

## Continuacion: tanda 4b

Carnivora T3, Asura T4 (cinco monedas), seis peluches y correccion de contornos
de mascotas siguen este mismo circuito de dos packs. El arte de `x/carnivoret`,
`x/asura` y `x/peluches` se convierte con `tanda4b_privado.py` al ejecutar
`build_privado.py --prepare`; originales intactos. Las vistas `tanda4a.png` y
`tanda4b.png` quedan exclusivamente en el build privado. Esta ultima se regenera
con `python datapack-src/preview_tanda4b.py`; es una vista estatica, no una captura en juego.

`AstralDecor.jar` es codigo propio publico (`datapack-src/runtime/AstralDecor.java`),
compilado para Paper 26.1.2 / Java 25 con `build_runtime.py`. Resuelve muebles
protegidos por WorldGuard, alas cosmeticas, generacion/proteccion de mena y
la tienda de peluches de $2.500 mediante Vault. EconomyShopGUI gratuito abre
la tienda propia desde su seccion Peluches, porque componentes/comandos de
compra son funciones Premium.

Lista exacta, reproduccion, estado reservado del note_block, efectos secundarios,
reinicio y pruebas pendientes con jugador: [tanda4b.md](../build/deploy/tanda4b.md).
El pack FINAL de 4b reemplaza al FINAL de 4a; no usar el SHA-1 anterior al instalar
ambas juntas. No se desplego esta tanda.

El codigo, los balances y los menus son propios y se publican. El arte de terceros y todas sus salidas derivadas se conservan en el repositorio privado. No integrar Game Stations. Esta tanda no modifica Santuario.

## Reproduccion sin red

1. Ejecutar los generadores publicos desde `datapack-src`: `python build.py`, `python mobs/mascotas.py`, `python mobs/mythic.py`, `python lobby.py`, `python menus.py` y `python build_pack.py pack-source`.
2. Configurar `ASTRAL_PRIVADO` apuntando al clon privado (por defecto `.local/terceros/AstralRPG-privado`, desde la raiz del proyecto). Debe contener `x/` con los originales. Sin el clon, `build_privado.py` termina sin modificar archivos. Las mascotas nuevas usan temporalmente el modelo propio del lobo, Goblin usa zombie vanilla, los vendedores siguen aldeanos y la espada usa diamante vanilla.
3. Desde la raiz: `python datapack-src/build_privado.py --prepare`. Produce 20 modelos adaptados, la espada Java, tres YAML de integracion, medidas y una vista previa dentro de `ASTRAL_PRIVADO/build/`.
4. En un Paper local con BetterModel 3.6.0, colocar TODOS los `build/models/*.bbmodel` publicos y superponer los `ASTRAL_PRIVADO/build/models/*.bbmodel` en `plugins/BetterModel/models/`. Usar la config `datapack-src/mobs/bettermodel_config.yml` y arrancar. No copiar la salida a pack-source publico.
5. `python datapack-src/build_privado.py --assets <servidor-local>/plugins/BetterModel/build/assets`. Combina la salida completa del plugin y el item privado con el ZIP publico. Falla si falta un modelo nuevo. Resultado FINAL: `ASTRAL_PRIVADO/build/AstralRPG-Textures.zip` y `pack.sha1`.
6. `python tools/verificar_terceros.py`: audita los archivos versionados del repo publico, ZIP anidados, PNG por bytes y pixeles, modelos y texturas embebidas. Requiere el clon privado para comparar. Ejecutarlo despues de agregar las rutas explicitas al indice y antes de commitear.
7. Commit y push separados: codigo/salidas propias al repo publico; `build/` derivado al repo privado. Nunca agregar `.local/` al publico.
8. Para publicar el pack durante el despliegue: `python tools/subir_pack_r2.py <ASTRAL_PRIVADO>/build/AstralRPG-Textures.zip`. El argumento posicional ya admite el ZIP privado; `--dry-run` calcula su SHA-1 sin red ni claves. Actualizar propiedades solo tras verificar la descarga. Lista de instalacion: `build/deploy/tanda4a.md` (regenerar con `python datapack-src/deploy_tanda4a.py`).

## Mascotas y obtencion

Las 17 nuevas se obtienen en la Gacha de Monturas, con permiso permanente y compensacion de 1000$ como las mascotas anteriores. No se agregan drops de mundo. Probabilidades por rareza intactas: comun 60%, poco comun 25%, rara 11%, epica 3,5%, legendaria 0,5%; garantia epica/legendaria cada 40 tiradas. Los premios de cada rareza comparten ese porcentaje: las posibilidades individuales anteriores disminuyen al ampliar el catalogo.

Los bonus son acumulativos en niveles 1, 10 y 20, solo en los mundos de bonus ya configurados; nivel 30 conserva evolucion. `/mascotas` tiene tres paginas. Las seis originales conservan su arte; las nuevas usan retratos renderizados desde sus modelos privados en las paginas, detalles y vitrina de CrazyCrates, con estado y permiso. El pack publico conserva iconos vanilla de reserva; los retratos solo se generan en el item-pack privado con build_privado.py --prepare. No se usa MCPets ni se publican retratos del arte licenciado.

| ID | Mascota | Rareza | Nivel 1 | + Nivel 10 | + Nivel 20 |
|---|---|---|---|---|---|
| `ghastito` | Ghastito de Nube | Rara | Caida lenta | Regeneracion I | Suerte |
| `bombardero` | Bombardero Musgoso | Epica | Resistencia I | Fuerza I | Prisa I |
| `canonero` | Canonero de Bolsillo | Rara | Fuerza I | Prisa I | Suerte |
| `encapuchado` | Zorro Encapuchado | Epica | Velocidad I | Vision nocturna | Fuerza I |
| `llamita` | Llamita Viajera | Comun | Salto I | Suerte | Resistencia I |
| `hondero` | Pequeno Hondero | Comun | Prisa I | Velocidad I | Suerte |
| `saqueador` | Saqueador Elegante | Rara | Suerte | Fuerza I | Resistencia I |
| `brujita` | Brujita Estelar | Legendaria | Regeneracion I | Resistencia al fuego | Suerte |
| `desierto` | Cubito del Desierto | Comun | Resistencia al fuego | Prisa I | Resistencia I |
| `jungla` | Cubito de la Jungla | Rara | Salto I | Velocidad I | Fuerza I |
| `frondoso` | Cubito Frondoso | Rara | Regeneracion I | Prisa I | Resistencia I |
| `micelio` | Cubito de Micelio | Epica | Regeneracion I | Suerte | 2 corazones de absorcion |
| `pradera` | Cubito de Pradera | Comun | Velocidad I | Suerte | Regeneracion I |
| `sabana` | Cubito de Sabana | Comun | Prisa I | Resistencia al fuego | Velocidad I |
| `nieve` | Cubito de Nieve | Rara | Velocidad I | Resistencia I | Suerte |
| `pantano` | Cubito de Pantano | Rara | Respiracion acuatica | Regeneracion I | Resistencia I |
| `honguito` | Honguito Errante | Epica | Regeneracion I | Resistencia I | Prisa I |

## Mobs, vendedor y espada

Goblin (`astral_goblin`): zombie rapido, vida base 16, dano 3, velocidad 0,34, escala con `mob/roll`. Solo invocacion manual; sin robo de dinero ni apariciones naturales. La copia privada agrega `idle` desde `pose` y conserva `walk`.

Armored Grub conserva los IDs `astral_abejorro` y `astral_abejorro_elite`, misiones, eventos y drops. Cambian los nombres visibles a Armored Grub y Armored Grub Reina. Se conserva su IA de Vex; `idle` anima el vuelo y no se invoca una animacion de ataque inexistente.

Goblin y Grub incorporan un hueso BetterModel `b_astral_hitbox` calculado desde la caja del modelo estatico, y atributos de altura coherentes con la tanda 3a. La caja no sigue la deformacion de cada fotograma. Las medidas se guardan solo en el build privado.

Los cuatro vendedores siguen siendo VILLAGER NoAI, con sus nombres visibles y acciones originales. Se superpone el modelo privado y una caja BetterModel de jugador (0,6 x 1,8). Rehacerlos segun el manifiesto, conservando cualquier posicion ajustada manualmente.

Espada del Heroe Errante (`espada_heroe_errante`): tier III, mismo dano, velocidad 1,6 y requisito de Combate 20 que Espada Ensangrentada. Sin encantamientos ni habilidad especial, sin receta. Se entrega con `loot give <jugador> loot astral:item/espada_heroe_errante`. El pack privado conserva las transformaciones de mano originales y agrega ajuste para GUI.

## Verificacion y limites

Prueba local con Paper 26.1.2, BetterModel 3.6.0 y MythicMobs 5.13.0: carga de 193 mobs y smoke de todas las incorporaciones. Los avisos de dialogos de ejemplo faltantes son previos; MythicMobs tambien avisa al apagarse con entidades activas. Sin jugador conectado: falta comprobar visualmente en Minecraft texturas, interacciones, seguimiento y bonus. El despliegue remoto y la subida a R2 siguen pendientes.

La correccion urgente del 11/11 actualiza los derivados de Carnivora, Asura y peluches
para el atlas de items 26.x, y verifica las UV 0..16 de la Espada del Heroe Errante.
Goblin y Grub agregan `death` en sus copias adaptadas; los originales quedan intactos.
`deploy_urgente.py` copia solo los productos de esta tarea a
`build/entregas/urgente-mascotas-texturas/` del repo privado. Esa carpeta permite
publicarlos sin incluir los cambios previos del resto de `build/`.
El SHA-1 y los destinos exactos estan en la entrega publica; la imagen GUI privada
sale de `preview_pack_gui.py`, leyendo modelos y PNG del ZIP FINAL.
