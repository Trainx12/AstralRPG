# Entrega: jefes agresivos, esqueletos menos rigidos y mazmorras de noche (13/11/2026)

No cambia el resource pack (solo animaciones de servidor y configs). No requiere reinicio.

## Archivos a subir (panel Empower -> Files)
| Local | Servidor |
|---|---|
| `build/models/astral_{momia,yeti,golem_forja,cangrejo,chaman,coloso_musgoso}.bbmodel` | `plugins/BetterModel/models/` |
| `build/models/astral_esq_{arquero,escudero,nigromante,espadachin,guardian}.bbmodel` | `plugins/BetterModel/models/` |
| `build/mythicmobs/mobs/{astral,bosque,cumbre,forja,fosa,mazmorra,santuario,tumba}.yml` | `plugins/MythicMobs/mobs/` |
| `build/mythicmobs/skills/{astral,cumbre}.yml` | `plugins/MythicMobs/skills/` |
| `build/mazmorras/astral_mazmorras_copias.sk` | `plugins/Skript/scripts/astral_mazmorras_copias.sk` |

## Consola (en este orden)
```
bettermodel reload
mm reload
sk reload astral_mazmorras_copias
```
Los jefes que ya estan vivos conservan la IA vieja hasta que vuelvan a aparecer (reiniciar la sala o `mm mobs kill <id>`
con la sala vacia).

## Verificado en Paper local (`tools/probar_jefes_paper.py`)
- MythicMobs carga todos los jefes y skills nuevas sin errores de configuracion.
- El golpe al piso no cambia bloques (1681 bloques iguales) ni deja bloques cayendo.
- Skript carga el script de noche sin errores y fija la hora.

## No verificado
- Con un jugador real: que se sienta bien la persecucion, el dano y que los disparos peguen.
- Las animaciones en el juego (BetterModel interpola distinto que la vista previa).
