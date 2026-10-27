# Balance de AstralRPG

Valores de referencia (daño por segundo aproximado contra un mob sin armadura).

| Clase | Tier I | Tier III | Tier V |
|---|---|---|---|
| Berserker (espada + set) | ~10 | ~17 | ~27 (hasta ~38 con poca vida) |
| Mago (bastón + set) | ~4,4 a distancia | ~10 | ~20 a distancia |
| Arquero (arco + set) | ~7 | ~14 | ~25 (con 0,4 s de enfriamiento) |
| Lanza (Combate) | ~9 | ~13 | ~19 + área + ejecución |

Cambios hechos al revisar:

- **Mago**: los hechizos pegaban demasiado (el bastón V hacía ~37 de daño por segundo). Ahora: daño 5/6/7/8,5/10 y recarga 1,25 s → 1 s.
- **Berserker V**: la armadura y la espada V multiplicaban la Furia entre sí (hasta x2,1). La armadura ahora tiene Furia I (+15% máx.) y la espada mantiene Furia II.
- **Arquero**: con carga casi instantánea se podía disparar sin parar. Los arcos III/IV/V tienen 0,2/0,3/0,4 s de enfriamiento, y bajaron los multiplicadores (arco V x1,30, set V x1,25).

## Dificultad progresiva

Cada mob hostil nuevo puede volverse élite. La amenaza cerca de un jugador es:

`amenaza = mejor tier Astral que tiene equipado (0-5) + 1 cada 7 días de mundo (máx. +3)`

- Probabilidad de élite: 6% + 5% por punto de amenaza (6% al empezar, 46% en endgame).
- Tier del élite: 1 + azar(0..amenaza)/2, máximo 5.

| Tier | Nombre | Vida | Daño | Extra | Drops |
|---|---|---|---|---|---|
| I | Veterano | +40% | +15% | | Esencia de Élite 50% |
| II | Élite | +90% | +30% | | Esencia x1-2 |
| III | Campeón | +160% | +50% | inmune al fuego | Esencia x2, Alma Corrupta 35% |
| IV | Pesadilla | +260% | +75% | + Resistencia I | Alma x1-2, Esencia x2 |
| V | Astral | +400% | +110% | + Regeneración | Chispa Astral 60%, Alma x2, Esencia x3 |

Se suma a LevelledMobs, que ya sube el nivel de los mobs según la distancia al spawn.

Los materiales nuevos sirven para los **Talismanes** (mano secundaria: vida, daño, velocidad y armadura, 3 niveles) y la línea de **Lanzas** (Combate, 5 niveles).
