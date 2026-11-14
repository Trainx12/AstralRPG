# Jefe final Trainx, Renacimiento, Deseos y Rankings (14/11/2026)

## Jefe final: Trainx (oleada 6 del Santuario)
- Generador: `datapack-src/mobs/trainx.py`. Modelo 3D con la skin del dueno (cuenta ByTrainx, sacada de
  SkinsRestorer), la **Espada del Dios de la Guerra** en la mano derecha y el **Baston Astral** en la izquierda,
  de unos **5 bloques** de alto. La skin y el modelo son privados (`<ASTRAL_PRIVADO>/originales/trainx/skin.png`,
  `build/models/astral_trainx.bbmodel`): `python mobs/trainx.py` lo regenera.
- Arriba: **"✦ Tier V+ ✦ Trainx ❤ vida"** (funcion `astral:mob/nombre_vplus` del datapack) y barra violeta.
- Pelea (numeros arriba del generador): vida = jefe de la Forja x 5,2 (4 jugadores x 1,3); de cerca combo de
  espada y barrido con aviso; de lejos rayos del baston; lluvia de estrellas (marca en el piso, cae a ~1 s);
  embestida al mas lejano. Fases a 60 % y 30 %. Si nadie esta cerca 30 s, se cura y vuelve al centro.
  Con menos de 4 jugadores avisa que va a ser muy duro (la vida no baja).
- Al morir: cada participante (supervivencia/aventura) recibe `astral.trainx.vencido`, un texto poetico sobre
  juntar los fragmentos, renacer y pedir un deseo, y el boton [Ver mis fragmentos]. El tiempo va al ranking.

## Fragmentos y Renacimiento
- `/fragmentos` (cofre_mazmorra.py) tiene el boton **RENACER**. Pide los 7 fragmentos + Trainx vencido;
  si falta algo, dice que. Abre la confirmacion (`renacer`): que se pierde y que se conserva.
- Al renacer (`renacimiento.py`, `astral_renacimiento.sk`): se quitan fragmentos, Trainx vencido y esperas
  de cofres; se reinicia la historia del Cronista (no las diarias), las Minas Astrales vuelven a la primera,
  plata a 0. Se conservan skills, cosmeticos, monturas, mascotas y equipo. Sufijo `✦N` y meta
  `astral_renacimiento` de LuckPerms.
- Dificultad personal: mobs x(N+2) de vida y dano (se usa el renacimiento mas alto a 32 bloques).
- Tiers VI a X: todavia no existen ("se estan forjando").
- Pendiente: +100 % de plata de los mobs por renacimiento.

## Deseos
- Renacimiento -> ventana `deseo` (marco de mazmorras). Fin de la historia del Cronista -> `deseo_lite`
  (ventana azul del Cronista). Se elige categoria y se escribe en el chat (`cancelar` vuelve).
- Topes de plata: lo que cuesta la ultima mina (hoy **25.000.000$**) y 1/4 para el lite (**6.250.000$**);
  salen de `minas.py`.
- Reglas en el libro de la ventana; todos los deseos los revisa el Admin.
- **/deseos** (permiso `astral.admin.deseos`): pendientes con [Aprobar] [Rechazar]. Aprobar no entrega nada:
  se cumple a mano. Rechazar devuelve el deseo para que pida otro. `/deseos historial`. Avisos al entrar.
- `/deseo`: el jugador reabre su ventana si tiene un deseo sin pedir.

## Rankings (`rankings.py`, `astral_rankings.sk`)
| Ranking | Mide | Cartel |
|---|---|---|
| Parkour Spiral / Spiral 2 / Paradise 3 | menor tiempo (largada al salir 3 bloques de la llegada) | atras de la llegada |
| Mazmorra Infinita | nivel mas alto aguantado 2 min | lobby |
| Santuario vs Trainx | menor tiempo del grupo | lobby y llegada del Santuario |
| Minas Astrales | bloques picados en la semana | junto al NPC de Minas |
| Bosque | troncos en la semana | llegada del Bosque |

- Carteles: text_display (`build/rankings/comandos.txt`), se actualizan cada 30 s. Moverlos: `/ranking cartel <id>`.
- **Metas de parkour**: un OP parado en la meta: `/ranking meta parkour_spiral` (y spiral2, paradise3).
  Sin meta no cuenta tiempos (el cartel dice "Meta sin fijar").
- `/ranking`: resumen. Cierre: **lunes 00:00 (Argentina)**; `/ranking cerrar` lo fuerza (admin).
- Premios top 3 (constantes arriba de `rankings.py`): 1.000.000$ / 500.000$ / 250.000$, tiradas de gachas,
  Chispas o Gema, **titulos que solo salen de rankings** (oro, plata, bronce; se equipan con `/trofeos`) y al
  1° el **Aura de Campeon** (`/trofeos aura`). El 1° de parkour gana el **Fenix** (o 10 tiradas de Monturas).
  Desconectados: se entrega al entrar.
