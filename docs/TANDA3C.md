# Tanda 3c: máquinas de Mini juegos, NPC en 3D y mejoras de jefes

Instalación y comandos exactos: [lista de instalación](../build/deploy/tanda3c.md)
(`python -m mobs.entrega_tanda3c` desde `datapack-src/`).

## Qué hay

- **Máquinas de Mini juegos** (`astral_maquina_arcade`, `astral_maquina_capsulas`): diseño propio con la
  paleta Astral. Son `VILLAGER` quietos e invencibles con el modelo encima; las dos abren `dm open parkour`.
  Pantalla, marquesina, neón, luces y cúpula van a brillo 15 con `brightness{pid=...}`.
- **Diez personajes** (`astral_npc_<nombre>`): mago, herrero, subastas, bazar, cronista, minero,
  caballero, hechicero, bruja y comerciante (Tienda). Qué NPC usa cada uno está en `NPC_MODELOS` de `mobs/tanda3c.py`.
  Las entradas escondidas de mazmorra usan la bruja y el guía del final el mago; Santuario queda en espera.
  Las gachas y el aldeano viejo de Mini juegos no cambian. Venta rápida sigue con el modelo privado.
- **Jefes mejorados** (propios): yeti rehecho, golem de la forja, momia, chamán y cangrejo; retoques al
  Coloso Musgoso y a la planta. Esqueletos y Creeper Nuclear no se tocaron (sus modelos están fijados por prueba).

## Dónde se edita

| Qué | Archivo |
|---|---|
| Máquinas y motor de pintura por cara (`PixelModel`) | `datapack-src/mobs/creatures_tanda3c.py` |
| Personajes | `datapack-src/mobs/npc_tanda3c.py` |
| Mobs/skills de MythicMobs y reparto de modelos | `datapack-src/mobs/tanda3c.py` |
| Vistas previas | `datapack-src/mobs/preview_tanda3c.py` (`python preview_tanda3c.py` y `... npc`) |
| Jefes | `datapack-src/mobs/creatures.py` (`FurModel` pinta el pelo liso del yeti) |

## Cosas que nos mordieron

- **Nombre encima del modelo:** BetterModel 3.6.0 solo dibuja el nombre del mob si el modelo tiene un hueso
  cuyo nombre empieza con `mtag_`. `PixelModel` agrega `mtag_nombre` solo; al vendedor privado se lo pone
  `build_privado.py`. Sin ese hueso el nombre no se ve aunque el mob tenga `AlwaysShowName: true`.
- **Siempre visible y reinicio (11/11):** AstralDecor 1.1 consulta los NPC activos una vez por segundo.
  Si BetterModel ya tiene el renderer pero falta el tracker, ejecuta la skill original (incluye luces).
  No recrea trackers existentes. Activa `ModelNametag.alwaysVisible(true)` en el hueso, que es
  independiente del flag de MythicMobs. Los cinco guardianes escondidos conservan texto vacio.
  El mismo hueso sigue al NPC al teletransportarlo: no crea entidades extra ni rotulos duplicados.

Entrega de Tienda, coordenadas actuales y pruebas: [tienda-modelo.md](../build/deploy/tienda-modelo.md).
- **Animaciones:** BetterModel no lee números con muchos decimales (`0.7142857142857143`). `bbmodel.swing`
  redondea la velocidad a 4 decimales.
- **Vista previa espejada:** `build_models.preview3d` dibuja espejado. En el juego `+X` queda a la izquierda
  de quien mira el frente; `preview_tanda3c.py` da vuelta la imagen para que coincida.
- **Vidrio de la máquina de cápsulas:** las cápsulas van antes que el vidrio y en el mismo hueso, para que
  se dibujen primero. Falta confirmarlo en el juego.
- Las comparaciones `build/previews/npc-*-comparacion.png` incluyen la referencia de terceros: son solo
  locales y no van al repo público. Sí van `npc-todos.png`, `maquinas-minijuegos.png` y `mejoras-3c-*.png`.
