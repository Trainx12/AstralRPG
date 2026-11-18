# Puntaje de mazmorras y cofre con ruleta (7b / plan E2) — 18/11/2026

Hecho por Claude directo. Cifras en `datapack-src/economia.py`; Skript en `datapack-src/mazmorras_puntaje.py`.
**DESPLEGADO 18/11 ~19:47 (hora AR)** sin reiniciar (5efdabe): `skript reload` de los 3 scripts sin errores, `dm reload` (70 menus), `mm reload` (196 mobs). No cambia el pack ni el datapack.

## Que cambia para los jugadores
- Al entrar una party nueva a una copia arranca el reloj. Cada muerte o caida (con party, a espectador) suma 1.
- Al ganar (`mazfin`; en la Fosa al morir el Cangrejo) sale la nota con titulo grande y detalle en el chat:
  puntos = 100 - 12 por muerte (tope 60) - 4 por minuto entero sobre el objetivo (tope 40) + 10 si nadie murio.
  S >= 95, A >= 85, B >= 70, C >= 55, D >= 40, F menos. Se guarda la mejor nota por jugador y mazmorra
  (`{pz.mejor::<uuid>::<mazmorra>}`).
- Minutos objetivo (estimados, ajustar en `economia.TIEMPO_OBJETIVO` mirando el "Tiempo" que muestra el chat):
  Bosque 12, Minas 10, Tumba 14, Cumbre 12, Forja 10, Santuario 15, Fosa 10.
- Cofre: muestra la nota (casilla del medio) y cobra UNA vez por victoria y por jugador (mas la espera de 30 min).
  - Plata: ruleta invisible `min + (max-min) * u^k`, sesgada a lo bajo. Tier I: min 2.000, max F 5.000 /
    D 30.000 / C 80.000 / B 150.000 / A 250.000 / S 500.000. Multiplicador: II x3, III x8, IV x18, V x40,
    Santuario x60 (S del Santuario: hasta 30.000.000).
  - Items: tiradas F 1, D 1, C 2, B 2, A 3, S 3 del pool del tier (materiales Astral, frascos, manzana,
    diamantes, netherita, totem...). Mejor nota = mas peso a lo raro; lo comun sigue saliendo.
  - Premio especial solo con A (0,5%) o S (1,5%) por tirada: una pieza de equipo del tier siguiente al azar
    (armas y armaduras Berserker/Mago/Arquero). Anuncio en el chat de todo el server.
  - El fragmento del jefe (primera vez) y la XP del cofre siguen igual.

## Archivos a subir
| Local | Server |
|---|---|
| `build/mazmorras/astral_puntaje.sk` (NUEVO) | `plugins/Skript/scripts/` |
| `build/mazmorras/astral_mazmorras_copias.sk` (2 lineas: inicio y fin del puntaje) | `plugins/Skript/scripts/` |
| `build/economia/Skript/scripts/astral_economia.sk` (arreglo: mundos del Santuario con su nombre real `world_minecraft_santuario_azeroth*`; antes ahi no pagaba la tabla de mazmorra ni descontaba plata al morir) | `plugins/Skript/scripts/` |
| `build/menus/DeluxeMenus/gui_menus/cofre_{bosque,mina,tumba,cumbre,forja,santuario,fosa}.yml` | `plugins/DeluxeMenus/gui_menus/` |
| `build/mythicmobs/mobs/fosa.yml` (el Cangrejo avisa el fin del puntaje) | `plugins/MythicMobs/mobs/` |

## Orden
Subir, despues `skript reload astral_puntaje`, `skript reload astral_mazmorras_copias`, `skript reload astral_economia`
(**no `sk reload`: en este server `/sk` es de AuraSkills**),
`dm reload`, `mm reload` (o reiniciar). Requiere la expansion `objective_score` de PlaceholderAPI (ya la usan las gachas).
Ojo: una party que ya este adentro al subir no tiene reloj; al ganar usa el tiempo objetivo (sin descuento por tiempo).

## Pruebas
- `test_mazmorras_puntaje.py` (12): cuenta de puntos y topes, notas, ruleta (esperanza ordenada, Monte Carlo,
  minimo fijo, multiplicadores), mas peso a lo raro con mejor nota, especial solo A/S, ids en el datapack,
  una ruleta por victoria, ganchos en copias/Fosa, cofre con el cobro nuevo.
- `test_mazmorras.py` y `test_tanda_xp.py` adaptados (el cobro vive en Skript).
- `tools/probar_economia_paper.py`: Paper local con los 3 scripts: "All scripts loaded without errors", se crea
  el puntaje `astral.nota`, `mazpuntaje inicio/fin` responden.
- Falta con cliente: ganar una mazmorra (con y sin muertes), ver la nota en el cofre, cobrar y que no deje cobrar dos veces.
