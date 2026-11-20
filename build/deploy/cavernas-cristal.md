# Cavernas de Cristal Astrales (tanda 7e) - 19/11/2026

Hecho por Claude directo (sin Codex). **DESPLEGADO 19/11 23:44** (commit 9dd5487, pack FINAL d19e121a = base del proximo pack; mundo creado con los comandos de abajo). Incluye las ventanas nuevas del 19/11 (abajo).
Fuente unica: `datapack-src/cavernas.py` (precios y premios en `economia.py`: `CAVERNAS_PRECIO`, `CAVERNAS_COMISION`).
Plugin propio nuevo: `datapack-src/runtime/AstralCavernas.java` (modelo: AstralOceano).

## Que hay
- Mundo `cavernas_cristal`: caverna cerrada (techo de roca, sin cielo), borde 1.000 x 1.000, galeria de ~40 bloques
  de alto con columnas, tuneles debajo del piso y luces propias (sin antorchas). 5 zonas:
  | Zona | Donde | Gemas | Tier de mobs |
  |---|---|---|---|
  | Jardin de Amatista | norte | Amatista | 4 |
  | Grietas de Jade | este | Jade | 4 |
  | Forja de Rubi | sur | Rubi y Topacio | 4 |
  | Lago de Zafiro | oeste (con agua) | Zafiro | 4 |
  | Corazon de Opalo y Onix | centro, radio 150, hasta ~50 bloques mas hondo | Opalo y Onix | 5 |
- Campamento (spawn) en 0, 12, -300: **atril** = comisiones, **barril** = venta. No se rompe ni se construye.
- Vetas: bloque de nota en campana (bell, notas 0-15). Cada gema tiene veta comun y honda (debajo de Y 0, mejor
  calidad). Calidad (Cruda/Pulida/Impecable): comun 88/10/2, honda 72/22/6; con **Polvo de Cristal** 76/19/5 y
  58/32/10 (bajadas el 20/11). Se pican con **taladro de Rubi (tier 4) o mejor**, a mano o en area; con otro taladro no sueltan nada.
- Menas para vender en el barril: Cristal Astral en bruto **45.000$** y Geoda Estelar **400.000$** (solo hondas).
- Mobs (MythicMobs `cavernas.yml`, los aparece el plugin; no hay apariciones naturales): golem de cada zona y Arana
  de Cristal. Un **guardian por zona** (barra de jefe, vida de jefe del mundo) cada ~8 min si hay alguien en la
  zona: suelta gemas Pulida/Impecable, Polvo y Geoda. Todos pagan plata por tier (AST_PLATA_*).
- Comisiones: 3 por dia y por jugador (cambian a medianoche, hora argentina). Pagan 2M / 4M / 8M y 1-3 Polvos.
  Cuentan las vetas picadas (a mano y con taladro en area), golems, aranas, mobs del Corazon y guardianes.
- Polvo de Cristal: clic derecho = 10 min de mejor calidad en las vetas (se suma si se usan varios).
- Entrada: Portales -> casilla 48 "Cavernas de Cristal" (ventana de aviso) o `/cavernas entrar`. Requisito: haber
  ganado la **Tumba** (permiso `astral.fragmento.arena`) o tener equipo **tier 4**.
- Se regenera cada 3 dias con avisos (10, 5 y 1 min antes). Morir ahi pierde la mitad de la plata (como survival).
- Comandos: `/cavernas` (estado), `entrar`, `comisiones`, `vender`. OP: `regenerar`, `plantilla`, `jefe [zona]`,
  `medir [chunks]`, `crear` (crea el mundo sin Multiverse), `mapa` (planta y cortes en la carpeta del plugin).
- Gemas en el cofre de mazmorra segun la nota (pedido del dueno, queda fijo): F 0 %, D 5 %, C 10 %, B 18 %,
  A 30 %, S 45 % de una gema al reclamar; con A o S la calidad usa la tabla del tier siguiente
  (`gemas.DROP_COFRE`, `DROP_BONUS_TIER`, `DROP_CALIDAD`).

## Plata por hora (cuenta en cavernas.py)
Densidad medida en Paper (100 chunks, franja de 6 bloques de piso/paredes/techo): Cristal 0,76 %, Geoda 0,02 %,
gemas 0,18 %. Buscando vetas a la vista (~800 Cristales y ~15 Geodas por hora) = **~42M/h**, entre Minas II
Diamante (39M/h) y Minas II Restos ancestrales (69M/h). Picando todo a ciegas con taladro 2x2 = ~6M/h.
Las comisiones suman ~6-24M por dia.

## Arte y ventanas nuevas (19/11, disenos del dueno + Gemini)
Recortes de las referencias del dueno (`arte_19_11.py`, `ventanas_19_11.py --importar`) y piezas rehechas con Gemini
sobre magenta (`gemini_19_11.py`; hojas en `.local/gemini/refs-19-11/gemini/`). Piezas finales en `pack-source/arte-19-11/`.
- **Cavernas**: 16 vetas 32x32 y 3 objetos 64x64 (Gemini); ventana de entrada (ilustracion + ENTRAR/VOLVER) y tablero de
  Comisiones de 6 filas (insignia de estado, icono, barra de avance y COBRAR por tarjeta).
- **Perla Abisal y Coral Astral**: objetos 64x64 y menas planas 32x32 (Gemini).
- **Portales**: tarjetas Nether, End, Cavernas (abre su aviso) y Vacio Estelar ("proximamente"). Mini juegos, Oceano y
  Arenas pasan a las casillas 48-50.
- **Forja**: Herrero y Reforja con botones con icono (Gemini): MEJORAR/ENGARZAR 38-42, REPARAR/EXTRAER 46-49,
  GEMAS/FORJA 50-52, flecha 45 y X 53.
- **Efectos**: fila 1 Bajo/Medio/Alto (tarjeta elegida con borde dorado), filas 2-6 las 5 categorias con
  ACTIVADO/DESACTIVADO (Gemini). "Volver" no entra (un cofre tiene 6 filas como maximo): ESC.
- **Banco Astral**: 6 vistas (principal, depositar, retirar, mejorar cuenta, movimiento realizado, cuenta maxima) con
  carteles y dibujos de Gemini; TODO/MITAD eligen y CONFIRMAR mueve; importes en vivo al pasar el mouse.
- **Taladros y motosierras en la mano**: la punta hacia adelante (arreglo de la sesion de iconos, `iconos_19_11.py`).

## Archivos y orden de instalacion (un reinicio)
| # | Archivo local | Destino | SHA-1 (12) |
|---|---|---|---|
| 1 | `.local/deploy-cavernas/AstralRPG-Items.zip` (datapack del server + Cavernas) | `/world/datapacks/AstralRPG-Items.zip` | c26c1408b2fd |
| 2 | `build/cavernas/AstralCavernas.jar` | `/plugins/AstralCavernas.jar` | 43e087c2eddd |
| 3 | `build/mythicmobs/mobs/cavernas.yml` | `/plugins/MythicMobs/mobs/cavernas.yml` | b76a66c92566 |
| 4 | `build/menus/DeluxeMenus/gui_menus/{cavernas_aviso,portales,configuraciones}.yml` | `/plugins/DeluxeMenus/gui_menus/` | 701759f4bc35 / 22dc452c09cf / 5e7aa3d343f6 |
| 5 | DeluxeMenus `config.yml`: en `gui_menus:` agregar `cavernas_aviso:` / `file: cavernas_aviso.yml` | `/plugins/DeluxeMenus/config.yml` | - |
| 6 | `build/economia/Skript/scripts/astral_economia.sk` (Banco nuevo y perdida en las Cavernas) | `/plugins/Skript/scripts/` | 6ec05c88ff6f |
| 7 | `build/gemas/astral_gemas.sk`, `build/services/astral_servicios.sk` (Forja), `build/mazmorras/astral_puntaje.sk` (gemas por nota) | `/plugins/Skript/scripts/` | ff0092782c81 / 566c3e8d5e92 / 157ced1449a9 |
| 8 | Pack FINAL `.local/terceros/AstralRPG-privado/build/entregas/cavernas-cristal/AstralRPG-Textures.zip` (base iconos-19-11 16f93b5c) | R2 + `resource-pack-sha1` | ver `pack.sha1` |

9. Reiniciar. Despues, en consola (`build/cavernas/comandos.txt`): `mv create cavernas_cristal normal -g AstralCavernas`,
   gamerules, borde de 1.000 y `rg flag -w cavernas_cristal __global__ pvp deny`.
10. Probar con OP: Portales -> Cavernas; atril y barril del campamento; Herrero y Reforja; /menu -> Efectos; Banco.

## Pruebas hechas
- `python -m unittest test_cavernas` (y los de gemas/economia/puntaje/secretos/pack_1711): todo OK.
- `python tools/probar_cavernas_paper.py --java <java25>` (Paper local, datapack + MythicMobs): el mundo se crea,
  genera ~10-20 chunks por segundo; una veta de Rubi con taladro de Rubi suelta "Rubi Crudo", con taladro de
  Diamante no suelta nada; la de Cristal suelta "Cristal Astral en bruto"; el golem aparece como [T4] y el
  guardian con su vida de jefe. (Las habilidades AST_* que avisa el ensayo estan en el astral.yml del server.)
- **No probado** (necesita jugador): picar con el taladro en area, el atril/barril, comisiones, Polvo, aparicion
  automatica de mobs y guardianes, regeneracion.

## Vistas previas
`build/previews/cavernas_planta.png` (planta 1 px = 2 bloques), `cavernas_corte_x.png` / `cavernas_corte_z.png`
(cortes por el centro), `cavernas_vetas.png` (texturas de vetas e items).

## Arte
Vetas: roca dibujada por codigo + cristales de las gemas de Gemini (sin texturas vanilla; `cavernas.texturas()`).
Items: Cristal (amatista Cruda aclarada), Geoda (opalo Perfecta), Polvo (dibujado). Provisorio: se puede pasar por
Gemini como las gemas.

## Regenerar
```
cd datapack-src
python build.py
python cavernas.py --jdk <bin JDK 25>
python economia.py; python menus.py
python deploy_cavernas.py --base-pack ../.local/terceros/AstralRPG-privado/build/entregas/reforja-gemas/AstralRPG-Textures.zip
```
