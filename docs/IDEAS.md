# Ideas para implementar (08/11/2026)

Lista del dueño. Las cosas grandes se hacen con Codex (plan de Claude, ver `docs/CLAUDE_CODEX.md`);
las chicas las puede ir haciendo Claude. Lo marcado **a mano** lo hace el dueño.

## Orden por trabajo (de más a menos, sin las tareas a mano)

| # | Tarea | Estado |
|---|---|---|
| 1 | Renacimiento: reinicio de progreso, tiers VI a X, dificultad personal y deseo | Definido (faltan detalles, ver abajo) |
| 2 | Jefe final: el dueño, para 4 jugadores | Definido (arma y armadura por ver) |
| 3 | Final del Santuario al vencer a los 6 jefes | Por definir |
| 4 | Bosque para motosierras (árboles que vuelven a crecer, como las Minas Astrales) | Falta el mapa |
| 5 | Fragmentos: llave para renacer (entregarlos al aldeano tras matar al jefe final) | Definido (va con el 1) |
| 6 | Pistas/acertijos al entrar a una expedición para encontrar al aldeano de la mazmorra | Definido |
| 7 | Más mapas de parkour (mínimo 1 más de la torre espiral) | Pendiente |
| 8 | Ranking de parkour por mapa (más rápidos) | Definido |
| 9 | Premio y deseo lite al terminar la historia del Cronista | Definido |
| 10 | Saltador (gancho viejo) y Gancho (gancho real) | Hecho en el repo (08/11), falta subir |
| 11 | Arreglar el cofre de los jefes al terminar la mazmorra (WorldGuard bloqueaba el clic) | Hecho en el repo (08/11), falta correr los comandos en el server |
| 12 | Decorar a cada aldeano que no tenga puesto | Pendiente |
| 13 | Skins para los aldeanos | Pendiente |
| 14 | Spawns de las arenas de pelea | Pendiente |
| 15 | Arreglar la momia que camina al revés (tenía los brazos para atrás) | Hecho en el repo (08/11), falta subir |

## A mano (las hace el dueño)
- Terminar las mazmorras de Forja, Santuario, Bosque y Cumbre.
- Santuario: un mini parkour en cada plataforma donde aparece cada jefe, o cambiar de mapa.
- Balancear el dinero de la tienda, las minas y los bosques.
- Probar las mazmorras.

## 1. Renacimiento
- Se ofrece al jugador que terminó **todas las mazmorras**. Es opcional.
- **Los fragmentos son la llave:** al matar al jefe final (el dueño) sale el mensaje de que pueden
  llevar los fragmentos al aldeano. Al entregarlos, el aldeano ofrece renacer y elegir el deseo.
  Como el renacimiento reinicia las mazmorras, los fragmentos se vuelven a conseguir en cada vuelta.
- Al renacer se reinicia su progreso (mazmorras, minas, historia, etc.).
- **Conserva:** skills (AuraSkills), cosméticos, monturas, mascotas y el equipo de tier V.
- **Tiers VI a X:** se desbloquean después del primer renacimiento. Hay que crearlos para todas las
  clases (armas, armaduras, texturas, Forja, escala). Es la parte más pesada. Ojo con los topes de
  atributos (`spigot.yml`, vida máxima de mobs) porque la escala es ×5 por tier.
- **Sin límite** de renacimientos.
- **El dinero vuelve a 0.**
- Dificultad **solo para ese jugador**: vida y daño de los mobs ×3 en el primer renacimiento (+200%)
  y después +100% por cada uno: renacimiento 1 = ×3, 2 = ×4, 3 = ×5 (renacimiento N = ×(N+2)).
  - Se suma al tier que ya elige cada mob según el jugador más cercano (`docs/ESCALA_TIERS.md`).
  - Con jugadores de distinto renacimiento cerca, y en mazmorras en grupo, se usa **el más alto**.
- Ajuste por skills: cada nivel de skill de más (sobre un "nivel esperado" para quien terminó todas
  las mazmorras) suma dificultad extra.
- **Dinero de los mobs: +100%** por renacimiento.
- Al renacer **pide un deseo** que cumple el dueño:
  - El jugador lo escribe en un menú; queda en una lista y al dueño le llega el aviso aunque esté
    desconectado. `/deseos` muestra los pendientes para aprobar o rechazar.
  - **Permitido:** un arma que ya existe, dinero (con tope), subir 1 tier, un arma personalizada con límite.
  - **Prohibido:** creativo, volver a desbloquear todas las mazmorras, desbloquear todos los tiers o subir skills.
  - Arma personalizada (propuesta): daño de su tier +1 como máximo, una sola habilidad de las que ya
    existen, nombre a elección y aspecto entre modelos ya hechos.
- **Falta definir:**
  - Tope de dinero del deseo: el dueño lo define después de revisar cuánto da cada mina y los
    precios nuevos de la tienda.

## 2. Jefe final (el dueño)
- Criatura de MythicMobs con la skin del dueño. Arma y armadura: por ver.
- Muy fuerte y con mucha vida: pensado para 4 jugadores.
- Entrada: con menos de 4 jugadores sale una advertencia; si igual entran, el jefe recibe ×1,5.

## 6. Pistas para encontrar las mazmorras
Apenas el jugador entra a una expedición, recibe pistas o acertijos sobre dónde está el aldeano que
lleva a la mazmorra.

## 8. Ranking de parkour
- En cada mapa, antes de la salida, una tabla con los más rápidos.
- Más adelante: al cerrar la semana, premio para los 3 primeros.
- **Descartado:** ranking de asesinatos en las arenas PvP (se podrían dejar matar para sumar).

## 9. Final de la historia del Cronista
- **Premio:** Brújula de mazmorras (apunta a la que todavía no hizo), título **Astral** y una mejora
  permanente (por ejemplo +10 de vida, +5 de daño, +4 de resistencia).
- **Deseo lite** (elige uno):
  - 10 tiradas gratis de cada gacha.
  - Dinero igual al precio de su próxima mina; si ya tiene todas, 500M.

## 10. Saltador y Gancho
- El gancho viejo (`gancho`, impulso por mirada) pasa a llamarse **Saltador** y su skin pasa a ser
  una bola de slime (después se le hace una propia).
- El gancho real (`gancho_realista`) pasa a llamarse **Gancho** y se queda con la skin del gancho.
- Ver `docs/TAB_Y_GANCHOS.md`.

## Bosque para motosierras
- Paga lo mismo que vale la madera de cada árbol.
- Falta elegir el mapa y cómo se arma.

## Por definir
- **Final del Santuario** al vencer a los 6 jefes (animación, premio).
