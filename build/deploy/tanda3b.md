# Tanda 3b: entrega sin desplegar

Servidor vigente: Empower (Aternos es copia). No desplegado. Requiere las tandas 2 y 3a compatibles.

## Archivos exactos

| Archivo local | Destino |
|---|---|
| `build/models/astral_esq_arquero.bbmodel` | `plugins/BetterModel/models/astral_esq_arquero.bbmodel` |
| `build/models/astral_esq_escudero.bbmodel` | `plugins/BetterModel/models/astral_esq_escudero.bbmodel` |
| `build/models/astral_esq_nigromante.bbmodel` | `plugins/BetterModel/models/astral_esq_nigromante.bbmodel` |
| `build/models/astral_esq_espadachin.bbmodel` | `plugins/BetterModel/models/astral_esq_espadachin.bbmodel` |
| `build/models/astral_esq_guardian.bbmodel` | `plugins/BetterModel/models/astral_esq_guardian.bbmodel` |
| `build/models/astral_creeper_fantasma.bbmodel` | `plugins/BetterModel/models/astral_creeper_fantasma.bbmodel` |
| `build/mythicmobs/mobs/mazmorra.yml` | `plugins/MythicMobs/mobs/mazmorra.yml` |
| `build/mythicmobs/mobs/bosque.yml` | `plugins/MythicMobs/mobs/bosque.yml` |
| `build/mythicmobs/mobs/tumba.yml` | `plugins/MythicMobs/mobs/tumba.yml` |
| `build/mythicmobs/mobs/cumbre.yml` | `plugins/MythicMobs/mobs/cumbre.yml` |
| `build/mythicmobs/mobs/tanda3b.yml` | `plugins/MythicMobs/mobs/tanda3b.yml` |
| `build/mythicmobs/skills/tanda3b.yml` | `plugins/MythicMobs/skills/tanda3b.yml` |
| `build/gameplay/astral_tanda3b.sk` | `plugins/Skript/scripts/astral_tanda3b.sk` |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/AstralRPG-Textures.zip` | R2: objeto `AstralRPG-Textures.zip` |

Pack: 17705571 bytes. SHA-1: **`d35a026942e85bd056b1682b9c409500cd594a95`**.

## Actualizacion v2 sobre 3b ya instalada

De la tabla anterior, reemplazar solamente los seis `.bbmodel`, los dos `tanda3b.yml`, `astral_tanda3b.sk` y el resource pack. Actualizar `resource-pack-sha1` y reiniciar. No requiere cambiar datapack, archivos de mazmorras ni recrear controladores. La lista completa y los controladores siguientes aplican si 3b aun no fue instalada.

## Instalacion por el responsable del navegador

1. Revisar `docs/TANDA3B.md` y vistas previas. Salas de Bosque/Minas/Tumba/Cumbre vacias y sin combate.
2. Respaldar los archivos de la tabla. Apagar para reemplazar el datapack. No reemplazar mundos ni usar Worlds > Upload.
3. Subir los archivos de la tabla. Conservar el resto de modelos, YAML y Skripts.
4. Subir el pack con `python tools/subir_pack_r2.py build/AstralRPG-Textures.zip`; verificar la descarga publica y su SHA-1. En `server.properties`, conservar la URL fija R2 y poner el SHA-1 de esta entrega en `resource-pack-sha1`.
5. Iniciar. El reinicio carga el datapack, modelos y MythicMobs. Comprobar consola. Si se ajusta durante una prueba: `bettermodel reload`, `mm reload`, `skript:skript reload astral_tanda3b`. El cambio de propiedades/pack y esta instalacion requieren reinicio.
6. Recrear los controladores siguientes con las salas vacias. Evita retener skills antiguas. Los comandos borran entidades etiquetadas de esas salas, incluida una instancia de jefe: nunca ejecutarlos durante una partida.
7. Reconectar un jugador, aceptar pack y probar cada clase, oleadas completas, spawn natural y creeper. Comprobar protecciones de explosion existentes de Tanda 2; potencia 6 y multiplicador de dano x2.

## Controladores (solo salas vacias)

```text
mm mobs kill astral_mina_control_sala1
execute in minecraft:mina run kill @e[tag=ad.mina.sala1]
data remove storage astral:tanda2/mina/sala1 queue
mm mobs spawn astral_mina_control_sala1 1 mina,10.5,-45,-124.5
mm mobs kill astral_mina_control_sala2
execute in minecraft:mina run kill @e[tag=ad.mina.sala2]
data remove storage astral:tanda2/mina/sala2 queue
mm mobs spawn astral_mina_control_sala2 1 mina,19.5,-39,-158.5
mm mobs kill astral_mina_control_sala3
execute in minecraft:mina run kill @e[tag=ad.mina.sala3]
data remove storage astral:tanda2/mina/sala3 queue
mm mobs spawn astral_mina_control_sala3 1 mina,43.5,-24,-201.5
mm mobs kill astral_mina_control_sala4
execute in minecraft:mina run kill @e[tag=ad.mina.sala4]
data remove storage astral:tanda2/mina/sala4 queue
mm mobs spawn astral_mina_control_sala4 1 mina,36.5,24,-248.5
mm mobs kill astral_bosque_control_sala1
execute in minecraft:bosque run kill @e[tag=ad.bosque.sala1]
data remove storage astral:tanda2/bosque/sala1 queue
mm mobs spawn astral_bosque_control_sala1 1 bosque,1468.5,101,1570.5
mm mobs kill astral_bosque_control_sala2
execute in minecraft:bosque run kill @e[tag=ad.bosque.sala2]
data remove storage astral:tanda2/bosque/sala2 queue
mm mobs spawn astral_bosque_control_sala2 1 bosque,1604.5,101,1382.5
mm mobs kill astral_tumba_control_sala1
execute in minecraft:tumba run kill @e[tag=ad.tumba.sala1]
data remove storage astral:tanda2/tumba/sala1 queue
mm mobs spawn astral_tumba_control_sala1 1 tumba,-148.5,60,-98.5
mm mobs kill astral_tumba_control_sala2
execute in minecraft:tumba run kill @e[tag=ad.tumba.sala2]
data remove storage astral:tanda2/tumba/sala2 queue
mm mobs spawn astral_tumba_control_sala2 1 tumba,-175.5,88,203.5
mm mobs kill astral_tumba_control_sala3
execute in minecraft:tumba run kill @e[tag=ad.tumba.sala3]
data remove storage astral:tanda2/tumba/sala3 queue
mm mobs spawn astral_tumba_control_sala3 1 tumba,0.568,72,0.512
mm mobs kill astral_cumbre_control_sala1
execute in minecraft:cumbre_hielo run kill @e[tag=ad.cumbre.sala1]
data remove storage astral:tanda2/cumbre/sala1 queue
mm mobs spawn astral_cumbre_control_sala1 1 cumbre_hielo,-25.6,33,-23.4
mm mobs kill astral_cumbre_control_sala2
execute in minecraft:cumbre_hielo run kill @e[tag=ad.cumbre.sala2]
data remove storage astral:tanda2/cumbre/sala2 queue
mm mobs spawn astral_cumbre_control_sala2 1 cumbre_hielo,-101.8,30,56.9
```

No recrear controladores de Santuario ni Forja. No subir configs de prueba completas.

## Modelos y caja vanilla

| Modelo | s | Modelo ancho x alto x fondo (b) | scale entidad |
|---|---:|---|---:|
| `astral_esq_arquero` | 1 | 1.553 x 2.122 x 1.182 | 1.06633 |
| `astral_esq_escudero` | 1 | 1.669 x 2.047 x 0.759 | 1.028853 |
| `astral_esq_nigromante` | 1 | 2.540 x 2.326 x 0.656 | 1.169081 |
| `astral_esq_espadachin` | 1 | 2.073 x 2.010 x 0.576 | 1.010008 |
| `astral_esq_guardian` | 1 | 1.945 x 2.223 x 0.674 | 1.117045 |
| `astral_creeper_fantasma` | 1 | 0.500 x 1.625 x 0.625 | 1 |

## Reproduccion y pendientes

Desde `datapack-src`: `python mobs/build_models.py`, `python mobs/mythic.py`, `python mobs/mazmorra.py`, `python build.py`, `python mobs/preview_tanda3b.py`. Convertir los seis modelos con BetterModel 3.6.0 local (docs/GUIA.md seccion 4), copiar los assets de estos seis modelos de `plugins/BetterModel/build/assets` a `pack-source/bettermodel/assets`, conservando los demas. `python build_pack.py pack-source`; `python -m mobs.entrega_tanda3b`.

Validacion: `python -m unittest discover -p "test_*.py"` y `python verify.py`. Las pruebas reales y sus limites, el detalle por modelo, paleta y diferencias finales estan en `docs/TANDA3B.md`.

Pendientes: revision visual del dueno; prueba visual en cliente Minecraft 26.1.2 de transparencia/animaciones y combate; subida R2, instalacion y consola de produccion. No se afirma despliegue. Se conserva el fantasma: Minecraft 26.1 soporta translucidez en modelos de item y BetterModel usa item_display (fuentes en docs/TANDA3B.md). Alfa 115-153 en el hielo, destellos blancos opacos, brillo 15/15 y polvo celeste. Esto confirma la viabilidad tecnica; no reemplaza la comprobacion visual en cliente. No se regenero el datapack ni cambiaron controladores en v2: los de la tabla corresponden a la instalacion completa sobre tandas 2/3a. Si ya esta instalada 3b, actualizar solo seis modelos, mobs/skills tanda3b.yml, astral_tanda3b.sk, pack y SHA-1; no recrear controladores.
