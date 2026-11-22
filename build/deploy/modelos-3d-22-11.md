# Modelos 3D y animaciones (22/11/2026)

**Estado:** DESPLEGADO el 22/11 a las 14:31 (hora local; 17:31 del server). Pack `2df2bf6a` en R2 y en
`server.properties`, jar 5b3a2f05, modelos, `players/astral_poses`, `nave.yml` (mobs y skills) y config de BetterModel
con `player-animation: true`. Arranque limpio (Done 245 s, BetterModel sin avisos, Skript sin errores).
Respaldos de lo reemplazado en `.local/deploy-modelos-22-11/respaldo/`. **Sin commit.**

## Que cambia en el juego

- **Taladros I-IX y motosierras (5):** modelos 3D esculpidos siguiendo los iconos del dueno (no el dibujo ensanchado).
  Segunda pasada (pedido del dueno): broca suave con dos surcos en helice, collar con rebordes y 8 tornillos, anillo
  de engranaje con muescas, puerto redondo atras con aro del tier y barra de carga, manometro, mira con lente,
  palanca, canos, emblema; motosierra con eslabones, dientes en L, pinon en la punta, puas, tapa de arranque,
  visor y barra de nafta, filtro, bujia, interruptor, cebador, tapa de aceite y franja de advertencia. Lo que se ve
  en 1ra persona (costado izquierdo, atras y arriba) tiene detalle propio.
  Taladro: broca en espiral con brillo que corre, collar con anillo de luz, carcasa redonda con tapas de engranaje y la
  gema que brilla a los dos lados, aletas, luces atras, mango de pistola con vendas y remaches, gatillo y manguera.
  Cada tier con lo suyo (placas de mitril, cristales de amatista, rejilla de fuego del rubi, oro del topacio, vetas
  del jaspe, broca arcoiris y cristales de gemas, oro y chispas del divino).
  Motosierra: barra con ranura, cadena que se mueve con dientes, nariz redondeada, motor con rejillas que brillan,
  tapa del pinon, guardamano, asa, tirador, escape y mango; infernal con dientes de fuego, astral con cristales.
  En el inventario se ven de costado (como el icono); en la mano se agarran del mango y apuntan adelante.
- **Gomera:** horquilla de madera 3D con vendas, soga, gomas y la bolsita con la piedra. Tres modelos: quieta,
  tensando y tensada (en 1ra persona se apunta mirando por el medio de la horquilla).
- **Libros del Invocador (6):** Grimorio Podrido (ojo verde, hongos), del Muneco Maldito (botones, costuras,
  alfileres), del Evocador (colmillos, esmeralda, marcador), de Piel de Dragon (escamas, ojo, cuernos),
  Necronomicon (calavera, cadenas, candado, runas) y Dorado (sol con gema, rubies, runas flotando).
- **Capitan del Vacio rehecho con el dibujo del dueno:** calavera (cuencas hundidas con cejas enojadas, pupilas que
  brillan, nariz, pomulos y dientes arriba y abajo) con corona dorada y racimo de **amatistas** facetadas, seis
  brazos con brazaletes dorados y manos **todas de hueso** (tres falanges y nudillos), costillas con la estrella de
  luz a la vista (el esternon termina arriba), hombreras y **tunica en tres capas** con bordes y puntas doradas,
  tabardo y capa atras. Lo que brilla (ojos, estrella, corona, puntas de la tunica) va en huesos `glow_`.
  Animaciones: idle, caminar, combo de garras, **Barrido del Vacio** (nuevo: gira 360 con los seis brazos, radio 7,
  dano 26, cada ~9 s si hay alguien cerca), lanzamiento, salto, furia, pulso, aparecer y muerte (se le cae la corona).
  Ojo Vigia: el ojo ahora brilla.
- **Animacion del cuerpo (BetterModel, modelo `players/astral_poses`): solo en la Cosecha** (giro de 360 agachado
  con la guadana estirada y anillo de almas, 1 s). Durante ese segundo no se ve la armadura: BetterModel solo sabe
  dibujar armaduras vanilla (baja las texturas de Minecraft), no las nuestras. Por eso el dueno pidio que no pase
  en cada golpe.
- **Efectos sueltos (modelo `models/astral_fx_clases`), no tapan al jugador:** tajo de almas adelante en el barrido
  del Segador y circulo de invocacion con runas que suben al invocar.

## Archivos a instalar

| Local | Server |
|---|---|
| `build/clases/AstralClases.jar` (sha1 5b3a2f05) | `plugins/AstralClases.jar` (agrega las poses; resto igual al 7655856a) |
| `build/models/astral_capitan_vacio.bbmodel`, `astral_ojo_vigia.bbmodel`, `astral_fx_clases.bbmodel` | `plugins/BetterModel/models/` |
| `build/players/astral_poses.bbmodel` | `plugins/BetterModel/players/` (carpeta nueva) |
| `build/mythicmobs/mobs/nave.yml`, `build/mythicmobs/skills/nave.yml` | `plugins/MythicMobs/Mobs/` y `Skills/` (**comparar antes con los del server**: solo deberia sumar NAVE_CAP_BARRIDO) |
| `plugins/BetterModel/config.yml` del server | `module.player-animation: true` (igual que `datapack-src/mobs/bettermodel_config.yml`) |
| FINAL privado `entregas/modelos-22-11/AstralRPG-Textures.zip` (sha1 **2df2bf6a1b3e99f03f3066a1e9ebd78b24692089**) | R2 con `tools/subir_pack_r2.py` + `resource-pack-sha1` |

El FINAL se arma encima del instalado `clases-22-11` (76fc66d9) con `python datapack-src/deploy_modelos_22_11.py`
(lee los assets que BetterModel genero en el Paper local). Saca los assets del Capitan viejo y suma las piezas del
cuerpo del jugador (`bettermodel/*/player_limb`). Es la base del proximo pack.

Requiere reinicio (jar nuevo + pack). Despues: `mm reload` no hace falta (reinicia), verificar en consola que
BetterModel carga `astral_poses` sin avisos.

## Como se rearma

```
cd datapack-src
python herramientas3d.py        # -> build/previews/taladros_3d.png, motosierras_3d.png
python gomera3d.py              # -> build/previews/gomera_3d.png, gomera_3d_quieta.png
python libros3d.py              # -> build/previews/libros_3d.png
python mobs/capitan_vacio.py    # -> build/models + build/previews/capitan_vacio.png
python poses_jugador.py         # -> build/players/astral_poses.bbmodel + build/models/astral_fx_clases.bbmodel
python clases.py --jdk <bin JDK25>
python ../tools/probar_modelos_22_11.py --java <bin JDK25>    # Paper local + bot
python deploy_modelos_22_11.py
python build_pack.py pack-source                              # pack publico
```

## Probado

- Paper 26.1.2 local + BetterModel 3.6.0 + MythicMobs 5.13 + AstralClases: 31 de 31 comprobaciones
  (`tools/probar_modelos_22_11.py`): el limb `astral_poses` (guadana_giro) y el modelo de efectos (tajo, invocar)
  cargan, el Capitan y el Ojo cargan con todas sus animaciones, el Capitan aparece por MythicMobs con su modelo y
  reproduce cada estado, y con un bot jugador: guadana_giro en su cuerpo y los dos efectos en el piso junto a el,
  sin errores. BetterModel sin avisos de parseo.
- Pack FINAL auditado (`pack_audit`): todas las referencias de modelos y texturas existen.
- Vistas previas por software: inventario, mano en 3ra persona y 1ra persona (cuenta de ItemInHandLayer).

## Falta

- Mirar con cliente real: agarre de taladros/motosierras/libros/gomera en la mano, el Capitan en la Nave y las
  poses del jugador (que el arma quede bien en la mano del modelo).
- Commit (hay archivos mezclados con otras tandas en el arbol).
