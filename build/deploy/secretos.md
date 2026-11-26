# Secretos de Astral (7c / plan E3) — 18/11/2026

Hecho por Claude directo. Generador `datapack-src/secretos.py`, cifras en `economia.py`. **DESPLEGADO 19/11 (1e2c61d): `skript reload astral_secretos` OK, sin reinicio.**
No cambia el pack ni el datapack. Todavia NO hay secretos colocados: los elige el dueno.

## Como se usa
- OP, mirando un cartel (o cualquier bloque) a menos de 5 bloques: `/secreto crear [pista]`. Si es cartel le escribe
  "✦ Secreto ✦ / de Astral / Clic derecho / para reclamar". Queda guardado en el server y el chat muestra una linea
  para copiar a `SECRETOS` en `secretos.py` (asi queda en el repo; pasarmela y la agrego).
- `/secreto borrar` (mirandolo) y `/secreto lista`. Los secretos no se pueden romper (salvo borrandolos).
- Jugadores: clic derecho lo reclama UNA vez por cuenta (guardado por UUID). `/secretos`: cuantos encontraste de cuantos hay.

## Premio (ruleta invisible)
- 2%: una pieza de equipo (arma o armadura) de 1 tier mas que la mejor arma Astral que lleva (puntaje `astral.wt`
  del datapack; sin equipo Astral = tier I, sale tier II). Anuncio en el chat de todos.
- 38%: plata = 5% a 20% de la que lleva encima, minimo 10.000 y maximo 5.000.000.
- 60%: 2 tiradas del pool de premios de cofre de su tier (materiales Astral, frascos, diamantes...).
Todo se anota en `plugins/Skript/logs/astral-secretos.log`.

## 10 lugares propuestos (NO colocados)
| # | mundo | idea | coordenadas aprox. |
|---|---|---|---|
| 1 | `lobby` | Detras del Cronista, entre las columnas | 189 102 221 |
| 2 | `lobby` | Abajo del puente del tren, junto al agua | 112 96 192 |
| 3 | `lobby` | Arriba del edificio de Portales Astrales | 211 112 240 |
| 4 | `world` | Cueva cerca del spawn del survival | a elegir en el juego |
| 5 | `bosque` | Bosque Sombrio: escondido en el Claro corrompido | 1504 107 1504 |
| 6 | `tumba` | Tumba: en el Pasaje de los sellos | -175 88 203 |
| 7 | `cumbre_hielo` | Cumbre Helada: atras de la Plaza de la fuente | a elegir en el juego |
| 8 | `forja_volcano` | Corazon de la Forja: junto al Nucleo | 82 52 -55 |
| 9 | `oceano` | Oceano Astral: en el fondo, cerca de la entrada a la Fosa | a elegir en el juego |
| 10 | `astral_minas` | Minas Astrales: en la sala de espera de la primera mina | a elegir en el juego |

Ojo con las mazmorras: tienen 6 copias (`bosque`, `bosque_2`...). Un secreto se pone en UN mundo; para que lo
encuentren en cualquier copia habria que crearlo en las 6 (cuentan como secretos distintos) o dejarlo en la copia 1.

## Archivos a subir
| Local | Server |
|---|---|
| `build/secretos/astral_secretos.sk` (NUEVO; usa `pz_tirada` de astral_puntaje.sk, ya en el server) | `plugins/Skript/scripts/` |

Despues: `skript reload astral_secretos` (no `sk reload`: es de AuraSkills).

## Pruebas
- `test_secretos.py` (6): generado al dia, cifras de economia, una vez por jugador (se marca antes de tirar la ruleta,
  variables persistentes), equipo +1 tier que existe en el datapack para tiers 1-10, premios del cofre, comandos y proteccion.
- `tools/probar_economia_paper.py`: Paper local con los 4 scripts: "All scripts loaded without errors".
- Falta con cliente: crear un secreto, reclamarlo, ver que no deje dos veces y `/secretos`.

## 26/11/2026: premios de plata mejorados (EN VIVO 26/11 18:43, skript reload OK)
Pedido del dueno. Ahora cada secreto da plata SIEMPRE segun el tier del jugador (su mejor arma Astral), entre 1x y 2x
de 300 mobs Astral de ese tier (~1 hora de farmeo): T1 450k-900k, T2 900k-1,8M, T3 1,8M-3,6M, T4 3,6M-7,2M,
T5 7,5M-15M ... T10 240M-480M. 10% de "secreto dorado" x3 con aviso a todos. Ademas 3% equipo +1 tier o 2 tiradas del cofre.
Antes: 38% plata (5-20% de lo que llevaba encima, 10k-5M). Subir `build/secretos/astral_secretos.sk` a
`plugins/Skript/scripts/` y `skript reload astral_secretos` (en vivo, sin reinicio). Anunciar en Discord al quedar en vivo.
