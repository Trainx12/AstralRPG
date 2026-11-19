# Reforja de gemas (tanda 7d) — 19/11/2026

Hecho por Claude directo (sin Codex). **Preparado, SIN commit, SIN push y SIN desplegar** (falta el OK del dueno).
Fuente unica: `datapack-src/gemas.py` (costos en `datapack-src/economia.py`: `GEMA_PONER_TIER`, `GEMA_CALIDAD_MULT`,
`GEMA_EXTRAER_MULT`). Entrega armada con `python datapack-src/deploy_gemas.py --base-pack <FINAL economia-e1>`.

## Que hace
- 7 gemas (Rubi, Zafiro, Jade, Topacio, Amatista, Opalo, Onix) x 5 calidades (Cruda, Pulida, Impecable, Perfecta, Estelar).
  Perfecta y Estelar agregan un efecto secundario chico.
- Ranuras segun el tier del equipo: T1-T3 1, T4-T7 2, T8-T10 3. No se repite el tipo en una misma pieza.
- Herrero: boton **GEMAS** (casillas 51-52) abre la ventana **Reforja de gemas** (`/astralreforja`). Ahi:
  shift+clic en el equipo y en la gema; **ENGARZAR** cobra plata; si la pieza ya tiene ese tipo o no hay lugar,
  reemplaza (la vieja se DESTRUYE, pide un segundo clic: CONFIRMA). Clic en una ranura la elige; **EXTRAER** la saca
  sana al recuadro GEMA (cuesta x3). Boton **FORJA** vuelve al Herrero.
- Sin dupes: el equipo y la gema quedan guardados en variables y vuelven al cerrar, salir, entrar o recargar Skript
  (mismo esquema que el Herrero). Los cambios se hacen sobre una copia: si algo falla, no se toca nada.
- La gema es un encantamiento `astral:gema_<tipo>_<arma|armadura>_<calidad>`: se ve en el item con icono, nombre y
  efecto, y sobrevive a la actualizacion automatica de items.
- OP: `/astralgema dar <jugador> <rubi|zafiro|jade|topacio|amatista|opalo|onix|azar> <calidad 1-5> [cantidad]`.
  Kits: `function astral:admin/kit_gemas` y `kit_gemas_altas`.
- **Drop raro TEMPORAL** (hasta las Cavernas de Cristal, 7e): al reclamar el cofre de mazmorra con nota A (3%) o
  S (8%) sale una gema al azar; calidad por tier de la mazmorra (T1-2 Cruda; T3 hasta Pulida; T4-5 hasta Impecable).
  Se configura en `gemas.py` (`DROP_COFRE`, `DROP_CALIDAD`); para sacarlo: borrar las 2 lineas `astralgema cofre` de
  `mazmorras_puntaje.py`. Queda en el log `astral-gemas`.

## Donde se aplica cada efecto (una sola vez)
| Efecto | Lugar |
|---|---|
| Dano (Rubi, secundarios de Zafiro y Opalo) | encantamiento, efecto de dano del arma |
| Vida, velocidad de ataque/movimiento, empuje, dano del arma (armadura) | encantamiento, atributos `add_multiplied_base` (no se multiplican con mejoras ni talismanes) |
| Defensa (Opalo armadura) | `player/def` -> `gemas/defensa`, despues del Talisman de Roca |
| Suerte (Topacio) | `drop/give` -> `gemas/suerte`: chance de duplicar el drop Astral (solo corre cuando cae un drop) |
| Mana y critico (Zafiro, Amatista) | plugin `AstralGemas.jar`: modificadores de AuraSkills (se borran al salir o apagar) |
| Dano a elites y jefes (Opalo arma) | `AstralGemas`: elites, jefes del mundo y TODO mob de MythicMobs con barra de jefe (jefes de mazmorra incluidos) |
| Robo de vida (Onix arma) | `AstralGemas`: 40% por golpe de curar 1 / 1,25 / 1,5 / 2 / 2,5% de tu vida maxima; maximo una cura cada 0,5 s. Tambien en PvP |
| Espinas (Onix armadura) | `AstralGemas`: 10% por golpe recibido y por pieza, % de la vida del atacante (mitad a elites/jefes). Tambien en PvP |
| Plata (Topacio) | `AstralGemas` deja etiquetas `astral.gp0..5` una vez por segundo; `astral_economia.sk` solo las lee. **Ningun comando por baja** |

## Balance (numeros reales de escala.py)
- Zombi T5: 262.500 de vida. Espada T5: 62.500 -> 5 golpes. Con Rubi Estelar (+22%) 4 golpes; con Mejora +10 y Rubi Estelar 3.
  Jefe del mundo T5: 6,5 millones -> 105 golpes (86 con Rubi Estelar). Mobs y armas suben x5 por tier, asi que el %
  pesa igual en todos los tiers: el Rubi Estelar es como una Mejora +7 extra, no mata de un golpe.
- Robo de vida: jugador T5 con set completo 8.000 de vida; un mob T5 pega 1.000 (167 despues de la Defensa).
  Espada (~1,6 golpes/s) con Onix Estelar: ~0,64 curas/s x 2,5% = ~128 de vida por segundo, menos que un mob T5 solo.
  La espera de 0,5 s evita que los cuchillos (3 golpes/s) sean inmortales.

## Tabla de gemas
| Gema | Calidad | En arma | En armadura (por pieza) |

|---|---|---|---|

| Rubí | Cruda | +4% daño | +1,5% vida máxima |

| Rubí | Pulida | +7% daño | +2,5% vida máxima |

| Rubí | Impecable | +11% daño | +3,5% vida máxima |

| Rubí | Perfecta | +16% daño, +1% vida máxima | +5% vida máxima, +1% daño del arma |

| Rubí | Estelar | +22% daño, +2% vida máxima | +6,5% vida máxima, +2% daño del arma |

| Zafiro | Cruda | +4% maná máximo, +5% regeneración de maná | +3% regeneración de maná |

| Zafiro | Pulida | +7% maná máximo, +8% regeneración de maná | +5% regeneración de maná |

| Zafiro | Impecable | +11% maná máximo, +12% regeneración de maná | +8% regeneración de maná |

| Zafiro | Perfecta | +16% maná máximo, +18% regeneración de maná, +2% daño | +11% regeneración de maná, +2% maná máximo |

| Zafiro | Estelar | +22% maná máximo, +25% regeneración de maná, +3% daño | +15% regeneración de maná, +4% maná máximo |

| Jade | Cruda | +3% velocidad de ataque | +1% velocidad |

| Jade | Pulida | +5% velocidad de ataque | +1,5% velocidad |

| Jade | Impecable | +8% velocidad de ataque | +2% velocidad |

| Jade | Perfecta | +11% velocidad de ataque, +1% velocidad | +2,5% velocidad, +1% velocidad de ataque |

| Jade | Estelar | +15% velocidad de ataque, +2% velocidad | +3,5% velocidad, +2% velocidad de ataque |

| Topacio | Cruda | +5% plata por baja | +1% de duplicar drops Astral |

| Topacio | Pulida | +8% plata por baja | +2% de duplicar drops Astral |

| Topacio | Impecable | +12% plata por baja | +3% de duplicar drops Astral |

| Topacio | Perfecta | +17% plata por baja, +1% de duplicar drops Astral | +4% de duplicar drops Astral, +2% plata por baja |

| Topacio | Estelar | +25% plata por baja, +2% de duplicar drops Astral | +5% de duplicar drops Astral, +3% plata por baja |

| Amatista | Cruda | +2% prob. crítica | +3% daño crítico |

| Amatista | Pulida | +3% prob. crítica | +5% daño crítico |

| Amatista | Impecable | +5% prob. crítica | +7% daño crítico |

| Amatista | Perfecta | +7% prob. crítica, +5% daño crítico | +10% daño crítico, +0,5% prob. crítica |

| Amatista | Estelar | +10% prob. crítica, +10% daño crítico | +14% daño crítico, +1% prob. crítica |

| Ópalo | Cruda | +6% daño a élites y jefes | +3% Defensa de la pieza |

| Ópalo | Pulida | +10% daño a élites y jefes | +5% Defensa de la pieza |

| Ópalo | Impecable | +15% daño a élites y jefes | +8% Defensa de la pieza |

| Ópalo | Perfecta | +21% daño a élites y jefes, +2% daño | +11% Defensa de la pieza, +5% resistencia al empuje |

| Ópalo | Estelar | +28% daño a élites y jefes, +3% daño | +15% Defensa de la pieza, +10% resistencia al empuje |

| Ónix | Cruda | 40% de curar 1% de tu vida al golpear | devuelve 0,2% de la vida del atacante |

| Ónix | Pulida | 40% de curar 1,25% de tu vida al golpear | devuelve 0,35% de la vida del atacante |

| Ónix | Impecable | 40% de curar 1,5% de tu vida al golpear | devuelve 0,5% de la vida del atacante |

| Ónix | Perfecta | 40% de curar 2% de tu vida al golpear, +1% vida máxima | devuelve 0,7% de la vida del atacante, +1% vida máxima |

| Ónix | Estelar | 40% de curar 2,5% de tu vida al golpear, +2% vida máxima | devuelve 1% de la vida del atacante, +2% vida máxima |


## Costos (plata)
| Tier | Ranuras | Cruda (engarzar / extraer) | Pulida (engarzar / extraer) | Impecable (engarzar / extraer) | Perfecta (engarzar / extraer) | Estelar (engarzar / extraer) |

|---|---|---|---|---|---|---|

| 1 | 1 | 10.000$ / 30.000$ | 20.000$ / 60.000$ | 40.000$ / 120.000$ | 80.000$ / 240.000$ | 150.000$ / 450.000$ |

| 2 | 1 | 25.000$ / 75.000$ | 50.000$ / 150.000$ | 100.000$ / 300.000$ | 200.000$ / 600.000$ | 375.000$ / 1.125.000$ |

| 3 | 1 | 50.000$ / 150.000$ | 100.000$ / 300.000$ | 200.000$ / 600.000$ | 400.000$ / 1.200.000$ | 750.000$ / 2.250.000$ |

| 4 | 2 | 100.000$ / 300.000$ | 200.000$ / 600.000$ | 400.000$ / 1.200.000$ | 800.000$ / 2.400.000$ | 1.500.000$ / 4.500.000$ |

| 5 | 2 | 200.000$ / 600.000$ | 400.000$ / 1.200.000$ | 800.000$ / 2.400.000$ | 1.600.000$ / 4.800.000$ | 3.000.000$ / 9.000.000$ |

| 6 | 2 | 400.000$ / 1.200.000$ | 800.000$ / 2.400.000$ | 1.600.000$ / 4.800.000$ | 3.200.000$ / 9.600.000$ | 6.000.000$ / 18.000.000$ |

| 7 | 2 | 700.000$ / 2.100.000$ | 1.400.000$ / 4.200.000$ | 2.800.000$ / 8.400.000$ | 5.600.000$ / 16.800.000$ | 10.500.000$ / 31.500.000$ |

| 8 | 3 | 1.200.000$ / 3.600.000$ | 2.400.000$ / 7.200.000$ | 4.800.000$ / 14.400.000$ | 9.600.000$ / 28.800.000$ | 18.000.000$ / 54.000.000$ |

| 9 | 3 | 2.000.000$ / 6.000.000$ | 4.000.000$ / 12.000.000$ | 8.000.000$ / 24.000.000$ | 16.000.000$ / 48.000.000$ | 30.000.000$ / 90.000.000$ |

| 10 | 3 | 3.500.000$ / 10.500.000$ | 7.000.000$ / 21.000.000$ | 14.000.000$ / 42.000.000$ | 28.000.000$ / 84.000.000$ | 52.500.000$ / 157.500.000$ |


Reemplazar cuesta lo mismo que engarzar. Extraer = x3.

## Archivos y orden de instalacion (un reinicio)
Apagar el server antes (encantamientos nuevos del datapack y plugin nuevo).

| # | Archivo local | Destino en el server | SHA-1 (12) |
|---|---|---|---|
| 1 | `.local/deploy-gemas/AstralRPG-Items.zip` (= datapack del server de economia-e1 + SOLO lo de gemas; lista en `datapack-cambios.txt`) | `/world/datapacks/AstralRPG-Items.zip` | bad2ec86f992 |
| 2 | `build/gemas/AstralGemas.jar` | `/plugins/AstralGemas.jar` | 6dfb820e7440 |
| 3 | `build/gemas/astral_gemas.sk` | `/plugins/Skript/scripts/astral_gemas.sk` | 914192f011b8 |
| 4 | `build/services/astral_servicios.sk` | `/plugins/Skript/scripts/astral_servicios.sk` | c3609d40ecfa |
| 5 | `build/economia/Skript/scripts/astral_economia.sk` | `/plugins/Skript/scripts/astral_economia.sk` | b65ac0f3bafc |
| 6 | `build/mazmorras/astral_puntaje.sk` | `/plugins/Skript/scripts/astral_puntaje.sk` | a3d2c76ea418 |
| 7 | Pack FINAL `.local/terceros/AstralRPG-privado/build/entregas/reforja-gemas/AstralRPG-Textures.zip` (base economia-e1 `ecba9321` + 464 archivos nuevos + fondo del Herrero + fuente) | R2 con `python tools/subir_pack_r2.py <FINAL>`, verificar descarga y `resource-pack-sha1` | de8fd0d4915878e028352f6a71894e75b834803c |

8. Encender. En consola: buscar `Reforja de gemas cargada`, `Gemas cargadas: 20 con AuraSkills, 22 con efectos propios` (AstralGemas 1.1.0) y
   `All scripts loaded without errors`. Si solo cambian los Skript: `skript reload astral_gemas` (nunca `sk reload`).
9. Probar con cliente (OP): `/astralgema dar <yo> rubi 3`, Herrero -> GEMAS, engarzar en un arma, mirar el tooltip,
   reemplazar (pide CONFIRMA), extraer, cerrar con cosas adentro y desconectarse con cosas adentro.

## Pruebas hechas
- `python -m unittest test_gemas test_economia test_mazmorras_puntaje test_secretos`: 54 OK. `test_pack_1711` ajustada
  (el fondo del Herrero ahora tiene GEMAS) y OK.
- Bateria completa: 9 fallas que ya estaban antes y no tocan esta tanda (versiones viejas de AstralDecor en test_mesa,
  Duelos, Guia, menu principal, sidebar, travel_ui, tanda1).
- `python tools/probar_gemas_paper.py --java <java25>` (Paper local con datapack + 4 Skript): carga sin errores;
  engarza Rubi en T2, rechaza una segunda gema (1 ranura) y un Rubi repetido, quita bien; armadura T9 acepta 3 y
  rechaza la cuarta; rechaza talismanes; la gema en la mano se reconoce y la extraida sale como item correcto.
- `python tools/probar_economia_paper.py --java <java25>` (ahora con servicios y gemas): 6 scripts sin errores.
- `tools/verificar_terceros.py`: sin arte privado. Datapack: solo cambian `player/def`, `drop/give`, `admin/todo` y las
  `upgrade/slot/*` (por los items nuevos); el Atlas no se corre (las gemas no entran al Atlas).
- AstralGemas 1.1.0 arranca en Paper junto a AuraSkills 2.4.0 y MythicMobs 5.13.
- **No probado** (necesita jugador): la ventana con clics reales, el mana/critico, robo de vida, espinas, Opalo contra
  jefes, suerte y plata en combate.

## Vistas previas
`build/previews/reforja_gemas.png` (vacia / equipo T5 con gema / reemplazo), `build/previews/herrero_gemas.png`,
`build/previews/gemas_texturas.png`.

## Arte (Gemini, 19/11)
- Gemas: hoja de 7x6 de Gemini (`.local/gemini/gemas/hoja_gemas.jpg`, con la referencia del dueno) recortada por
  `python datapack-src/gemas_arte.py` en 35 PNG de **64x64** (se ven lisas, no pixeladas). La segunda columna de la
  hoja (otra "cruda") no se usa.
- Ventana: marco nuevo de Gemini `pack-source/ref/reforja-frame.png` (cristales celestes, cartel de titulo; el texto
  del cartel se borro y se escribe con la letra del server para que se lea nitido).
- Botones: placas de Gemini sin texto `pack-source/ref/gemini/gem_<verde|verde_off|naranja|azul|gris|marron|violeta>.png`,
  al doble de resolucion (36x36 por casilla) con el texto nitido encima. Ranuras `gem_ranura*.png` en 64x64.
  Hojas originales en `.local/gemini/gemas/` (marco.jpg, botones.jpg). Chat de Gemini: https://gemini.google.com/app/373d3479751dd24b

## Texturas (reemplazables)
`datapack-src/pack-source/assets/astral/textures/item/gemas/<tipo>_<calidad>.png` (64x64; tipo = rubi, zafiro, jade,
topacio, amatista, opalo, onix; calidad 1..5). Para cambiar una: pisar el PNG con el mismo nombre (o una hoja nueva
con `gemas_arte.py <hoja>`), `python datapack-src/gemas.py` y `python datapack-src/deploy_gemas.py` (rearma el FINAL).
Iconos de la ventana: `services_ui.py` (`placa`, `socket`) y `gemas.py` (`BOTONES`).

## Regenerar
```
cd datapack-src
python build.py
python gemas.py --jdk <bin JDK 25>
python economia.py; python mazmorras_puntaje.py
python deploy_gemas.py --base-pack ../.local/terceros/AstralRPG-privado/build/entregas/economia-e1/AstralRPG-Textures.zip
```
