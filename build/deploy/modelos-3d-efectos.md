# Modelos 3D y efectos — 16/11/2026

Preparada en la rama `claude/modelos-3d-efectos-7878de`. **Sin desplegar**: no se toco Empower, R2 ni GitHub.
Va junto con la tanda de Codex (`cargar-arte-16-11`): al unir las ramas hay que rearmar el FINAL (ver abajo).

## Que cambio

| Pedido | Resultado | Generador |
|---|---|---|
| Mochilas 3D (6 materiales) | Forma de la mochila `explorer` de Wet Backpacks, modificada: tapa que cae al frente, dos correas con hebilla, bolsillo frontal, bolsillos laterales, asa y correas de hombro curvas. Se sacaron el hacha y el rollo del mod. Una textura propia por material (cuero con costuras, cobre con verdin, hierro con placas, oro, diamante facetado, netherite con hebillas doradas). Mismos `astral:mochila_<material>`. | `mochilas3d.py` (privado) |
| Cuchillos T1-T10 | La textura de mod que eligio el dueno por tier, esculpida en 3D (hoja con lomo y filo, mango redondo, brillo/animacion del mod). Plano en el inventario. | `armas_planas3d.py` (privado) |
| Otras armas planas | Espada, Hacha, Pico y Arco (con 3 tensados) de las Mareas pasan a 3D. El resto de armas del FINAL ya era 3D (auditoria de los 231 items planos: lo demas son armaduras, materiales, talismanes, taladros y botones). | `armas_planas3d.py` (privado) |
| Fenix | Modelo nuevo (265 piezas): cuello en S, cresta de 5 llamas, alas en dos tramos que se doblan al aletear, cola de cintas en 3 tramos que ondula, brasas flotando, degrade rojo-naranja-oro. Un solo par de ojos (a los costados). | `mobs/pet_models.py` |
| Efectos de varitas | Rayo laser continuo (4 planos cruzados con luz propia, nucleo blanco y halo del color) + destellos blancos en estrella + chispas del color. Baston de fuego (T4) y Varita de Estallido: bola de fuego que vuela, llamitas en el piso alrededor del mago y un incendio al llegar. Electrico (T5) en zigzag; Vacio (T10) con un segundo rayo oscuro. Colores por elemento: `COLOR_BASTON` en `efectos.py`. | `efectos.py`, `runtime/AstralEfectos.java`, `build.py` |
| Explosiones (referencia verde) | Hongo de 12 cuadros con cupula blanca, bandas onduladas, nucleo blanco y patas; manchas en el piso, onda expansiva, llamitas que suben y medialunas. | `efectos.py` |
| Jefes | Golpe al piso: onda doble, destello, hongo grande y corona de hongos (Alto); el fuego deja incendio. Disparos: fogonazo al lanzar, estela dibujada (`astralfx estela`) y explosion mas grande al pegar. | `mobs/jefes_combate.py` |
| Trainx | Animaciones rehechas (idle, walk, attack, combo, barrido, cast, lluvia, dash) y nuevas `aparece` (cae del cielo y aterriza de rodillas) y `furia` (cambio de fase). Efectos en el combo, la embestida, las fases, la aparicion y la muerte. | `mobs/trainx.py` |
| Armas especiales | Varita de Estallido (bola de fuego), Hacha del Sismo (golpe de piedra), Heroe Errante (golpe de luz), Curacion y Transmision (estallidos). | `special_weapons.sk` |

**Niveles:** Bajo = igual que antes (solo `witch` + `end_rod` en el rayo, ningun dibujo). Medio = rayo fino, 2 destellos,
un hongo y una onda por golpe. Alto = todo. Cada dibujo es un `item_display` que solo ven los jugadores de ese nivel;
tope de 320 dibujos en todo el server (los adornos se cortan a 220). Ensayo local: un golpe de jefe + 4 rayos + estallido = 35 dibujos, todos borrados en menos de 3 s.

## Instalar (reinicio completo)

| Archivo | Destino |
|---|---|
| `ASTRAL_PRIVADO/build/entregas/modelos-3d-efectos/AstralRPG-Textures.zip` | R2 con `python tools/subir_pack_r2.py <zip>`; `resource-pack-sha1` |
| `build/runtime/AstralEfectos.jar` (1.1.0) | `plugins/AstralEfectos.jar` (reescribe su `config.yml` solo) |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` (solo cambian `spell/*`) |
| `build/gameplay/astral_armas_especiales.sk` | `plugins/Skript/scripts/special_weapons.sk` |
| `ASTRAL_PRIVADO/build/entregas/modelos-3d-efectos/mythicmobs/skills/astral.yml` | `plugins/MythicMobs/skills/astral.yml` (version privada) |
| `build/mythicmobs/skills/trainx.yml` | `plugins/MythicMobs/skills/trainx.yml` |
| `build/models/astral_pet_fenix.bbmodel` | `plugins/BetterModel/models/` |
| `ASTRAL_PRIVADO/build/entregas/modelos-3d-efectos/models/astral_trainx.bbmodel` | `plugins/BetterModel/models/` |

SHA-1 del FINAL: **`d19862c596d7c26506ec08931ccbb9c286514127`**, armado sobre `cargar-arte-16-11`
(SHA-1 base `90c90b745bce97490550d8d22a8a1cc4011be8e1`). `delta.json` lista lo publico (149: dibujos de efectos y Fenix) y lo privado (92: mochilas, cuchillos y Mareas).
Los assets de BetterModel del Fenix ya estan en `pack-source/bettermodel`; Trainx no cambia de huesos, asi que sus assets siguen sirviendo (solo cambian animaciones, que BetterModel lee del `.bbmodel`).

**Si Codex entrega otro FINAL antes:** `python datapack-src/deploy_modelos_efectos.py --base <ese FINAL>` despues de unir
las ramas y regenerar (`build.py`, `mobs/mythic.py`, `build_pack.py pack-source`). El mismo script rearma la `astral.yml`
privada desde el build publico unido; no usar la de esta entrega si `skills/astral.yml` cambio en la otra rama.

## Vistas previas

- Publicas: `build/Servicios-preview/efectos-antes-despues.png`, `build/Servicios-preview/fenix-antes-despues.png`, `build/previews/efectos_hongo.png`.
- Privadas (arte de mods o la skin del dueno): `ASTRAL_PRIVADO/build/entregas/modelos-3d-efectos/previews/mochilas-3d.png`
  (inventario y en mano), `mochilas-uv.png` (plantilla para repintar con Gemini), `armas-3d.png`; `ASTRAL_PRIVADO/build/previews/trainx.png`.

## Licencias (solo circuito privado)

- Mochilas: Wet Backpacks (Lean, Geremilho), `fabric.mod.json` LGPL-2.1-or-later y `LICENSE` CC0. Se usa la forma del `explorer`.
- Cuchillos: T1 Dagger Mod (r2alsei/oofabo, All Rights Reserved); T2 y T7 Born in Chaos (licencia propia);
  T3-T6 y T8-T10 MC Dungeons Weapons (chronosacaria, licencia propia). El repo publico conserva las provisorias.

## Pruebas

- `python -m unittest discover -s datapack-src -p "test*.py"`: 333 OK (incluye `test_modelos_efectos.py`, 10 pruebas, 3 sobre el FINAL privado).
- `python tools/verificar_terceros.py`: sin arte privado en el repo publico.
- Paper 26.1.2 local (copia de `.local/testsrv`): arranca sin errores nuevos; AstralEfectos 1.1.0 activo; `astralfx golpe/estallido/rayo/estela` y los marcadores `fx.rayo`/`fx.estallido` crean y borran sus dibujos; BetterModel genera los 12 huesos del Fenix; Fenix y Trainx aparecen. Avisos previos: `pet_bonus_probe` (prueba vieja) y `mm test cast` desde consola sin lanzador.
- **Falta con cliente real:** ver los rayos, la orientacion de las manchas/ondas en el piso y el agarre de mochilas y cuchillos en mano.
- `astralfx prueba on|off` (solo consola) genera dibujos sin jugadores para ensayos.
