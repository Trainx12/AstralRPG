# Entrega: Tiers 6 a 10 (14/11/2026)

Armaduras elegidas por el dueño (casco 3D + cuerpo plano), armas, materiales, escala hasta T10 y Mazmorra Infinita
hasta X+. Detalle de números: `docs/ESCALA_TIERS.md` (sección Tiers 6 a 10).

Pack FINAL privado: `<ASTRAL_PRIVADO>/build/entregas/tiers6-10/AstralRPG-Textures.zip`
(base `oficios` bfb2b1e3 + cambios públicos + armaduras). Se arma con `python datapack-src/deploy_tiers6_10.py`.
sha1 en `pack.sha1` de esa carpeta (53cabb357fd94cf19ce209175d0d4421bfc7b315).

## Archivos
| Local | Servidor |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/runtime/AstralProgression.jar` | `plugins/AstralProgression.jar` |
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` |
| `build/tanda5a/AstralProgression/config.yml` | `plugins/AstralProgression/config.yml` |
| `build/gameplay/astral_gameplay.sk`, `astral_armas_especiales.sk` | `plugins/Skript/scripts/` |
| `build/infinita/astral_infinita.sk`, `build/rankings/astral_rankings.sk` | `plugins/Skript/scripts/` |
| `build/menus/DeluxeMenus/gui_menus/infinita_tier.yml`, `infinita_tier_alto.yml` | `plugins/DeluxeMenus/gui_menus/` |
| `build/menus/DeluxeMenus/config-gui_menus.yml` | sumar la entrada `infinita_tier_alto` al `config.yml` de DeluxeMenus |
| `build/lobby/TAB/secciones-config.yml` | condiciones `pm_inf_tier*` del `config.yml` de TAB |

## Pasos
1. `spigot.yml`: `settings.attribute.maxHealth.max: 1.0E12` y `settings.attribute.attackDamage.max: 1.0E12`
   (T10: espada 195 M, mobs hasta 15.600 M en jefes de mundo).
2. Subir el pack FINAL: `python tools/subir_pack_r2.py <zip final>`, verificar la descarga y poner el sha1 en
   `resource-pack-sha1` (comprobar que `server.properties` no quede vacío).
3. Subir los archivos de la tabla y reiniciar (datapack, jars y pack nuevos).
4. Después: `tab reload`, `dm reload`.

## Probado
- 286 tests. Paper local (`tools/probar_tiers6_10_paper.py`): zombi T10 con 625.000.000 de vida y cartel
  `[T10] Zombie ❤ 625.000.000`; élite Astral T10 `❤ 3.124.999.000` (cartel en miles); `#pct` 100/99;
  `loot` de Espada del Fin de los Tiempos, Yelmo del Destructor, Túnica del Glaciar y Corazón del Fin.

## Falta probar en el juego (con jugador)
- Casco 3D en la cabeza y en el inventario (rotaciones nuevas de 26.1, sobre todo Glaciar) y texturas 256x128.
- Golpe real de un arma T10 a un mob T10 y el hechizo de un bastón T7+.
- Ventana `infinita_tier_alto` y la subida a X+.
- Armas T6-T10 se ven como las T5 (temporal). Berserker T6 y Arquero T8/T9 se ven como el T5 de su clase.
