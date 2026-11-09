# Armas especiales independientes

Instaladas en Aternos el 02/11/2026 (datapack + script `special_weapons.sk`).
Se forjan en Guia AstralRPG → Especiales y aparecen en `admin/kit_especiales`.
Ninguna exige una clase ni forma parte de los kits Berserker, Arquero o Mago.

| Arma / ID | Habilidad | Mana | Recarga |
|---|---|---:|---:|
| Filo de la Tormenta / `espada_tormenta` | 25% por golpe cuerpo a cuerpo: rayo visual que hace el 30% del dano del golpe (minimo 1) en radio 2 | 0 | — |
| Danza del Ender / `espada_sombras` | Clic derecho: hasta 6 enemigos a 12 bloques; salta junto a cada uno con estela, lo mira y golpea 10. Un salto cada 4 ticks (1,2 s). Se puede usar en mazmorras | 15 | 5 s |
| Filo del Destello / `espada_destello` | Transmisión Instantánea: teletransporta hasta 12 bloques según la mirada (también vertical) y da +50% de velocidad por 3 segundos. No se puede en mazmorras; en el lobby sí | 50 | Ninguna |
| Varita de Curación / `varita_curacion` | Curación: cura el 5% de la vida máxima por segundo durante 5 s, a vos y a los jugadores a 7 bloques. No se acumula (reinicia el tiempo). Anda en el lobby | 60 | 1 s |
| Hacha del Sismo / `hacha_terremoto` | Clic derecho: onda de 5 anillos (hasta 5 bloques); cada anillo levanta el suelo y golpea 10 a lo que alcanza, con empuje hacia arriba | 10 | 6 s |
| Varita del Estallido / `varita_estallido` | Clic derecho: disparo instantaneo hasta 16 bloques; explota contra un bloque o enemigo. Tambien explota al golpear cuerpo a cuerpo. Radio 2, dano 6 | 5 por uso | Disparo: 1 s |

Los valores son puntos de vida, antes de armadura/resistencia (2 puntos = 1 corazon).
El mana se lee con `dm execute <jugador> [console] asw_mana %player_name% %auraskills_mana_int%`
(DeluxeMenus resuelve el placeholder con los datos del jugador) y se descuenta con
`auraskills:mana remove`. Antes se usaba `mm test cast` desde consola, que leia el mana del
servidor: por eso ninguna habilidad con mana funcionaba. Costos bajados porque el mana
base de AuraSkills es 20. Funcionan en supervivencia, aventura y creativo (no espectador). No hace falta ningun addon de Skript.
La varita hace su golpe fisico normal aunque no alcance el mana para la explosion.
Los costos y danos adicionales elegidos son un balance inicial ajustable.

Colores en DamageIndicator (cada habilidad usa su tipo de dano): golpe normal blanco,
rayo cian (`lightning`), explosion de la varita naranja (`entity_explosion`), sismo
amarillo (`falling_block`). Config en `build/plugins-basicos/DamageIndicator/config.yml`;
se aplica al reiniciar (el plugin no tiene comando de recarga).

## Protecciones

- Jugadores excluidos de todas las habilidades fuera de la dimension `minecraft:arena`.
  Dentro se exige que atacante y victima esten en el mismo mundo, y la victima en
  supervivencia o aventura. El portador nunca se lastima con su propia habilidad.
- Se respetan invulnerabilidad y cancelaciones de dano de Bukkit. El dano se atribuye
  al jugador; no se usa `/damage` para saltear los eventos de los plugins.
  WorldGuard no estuvo instalado en la prueba local: resta verificar sus regiones en Aternos.
- Se excluyen soportes de armadura, aldeanos, NPC invulnerables, entidades domesticables
  y tipos habituales de montura. Una entidad adicional puede excluirse con metadata
  Bukkit `asw.protected`. Las mascotas actuales de MythicMobs son invulnerables.
- En el lobby solo anda la Transmisión Instantánea (no hace daño); las demás avisan
  "no se usan en el lobby" en vez de no hacer nada (09/11/2026). Los dos teletransportes siguen desactivados en las seis
  mazmorras, conforme a las reglas de movilidad existentes.
- Los saltos comprueban el volumen completo del jugador cada 0,2 bloques, paredes,
  borde del mundo y peligros. El salto Ender exige linea de vision, suelo y un destino
  lateral libre; omite enemigos muertos, lejanos o inaccesibles. Cambiar de arma,
  desconectarse, morir o cambiar de mundo corta la secuencia.
- Destello recorre el rayo desde los ojos en pasos de 0,2 bloques y comprueba el volumen
  del cuerpo durante el trayecto. Se detiene antes de paredes, lava y peligros. Si queda
  menos de un bloque libre, no cobra maná. Conserva yaw/pitch y reinicia la caída.
- Un teletransporte de Destello cancelado devuelve los 17 de maná. El bonus de velocidad
  usa `astral:transmision`, se renueva sin acumular y se elimina a los 60 ticks,
  al entrar/salir y al recargar el script. El límite inferior es -63 en los mundos
  Overworld del servidor y 1 en Nether/End; si se añaden dimensiones con otros límites,
  ajustar `asw_blink` antes de habilitar la movilidad allí.
- El rayo usa `strikeLightningEffect`; solo la rutina filtrada aplica dano.
  La explosion usa sonido y particulas. No hay fuego, TNT ni rotura de bloques.
- El hacha anima `block_display`, sin colisiones ni drops. No modifica el suelo real,
  no copia cofres, y elimina los displays al terminar, recargar o descargar el script.
- Los golpes de habilidad no vuelven a disparar las habilidades al golpear.

## Referencias visuales

Modelos y texturas originales, con brillo animado, en `special_weapons3d.py`.
Las imagenes privadas de `.local/referencias/armas` no se distribuyen.

| Arma | Referencia elegida |
|---|---|
| Tormenta | Espada azul con runas de `espadas_03_fuego_cristal_maza.png`; runas celestes de `hacha_y_martillo_runas_celestes.webp` |
| Ender | Espadon violeta con gemas y piezas flotantes de `espadas_03_fuego_cristal_maza.png` |
| Destello | Cristal turquesa de `espada_y_guadana_cristal_turquesa.png`, en hoja mas estrecha |
| Sismo | Piedra oscura y runas de `mixto_06_sets_por_tema.png` y `hacha_y_martillo_runas_celestes.webp`, en tonos ambar |
| Estallido | Varita roja con cristal de `varitas_03_doce_elementos.webp` |

Vista previa: `build/previews/armas_especiales.gif` y `.png`.

## Generar e instalar

Desde `datapack-src/`:

```text
python build.py
python build_pack.py pack-source
python special_weapons3d.py
python verify.py
```

1. Subir `build/gameplay/astral_armas_especiales.sk` a `plugins/Skript/scripts/` con el
   nombre `special_weapons.sk` (asi se llama en Aternos; no dejar los dos, se duplicarian).
2. Subir `build/mythicmobs/skills/armas_especiales.yml` a `plugins/MythicMobs/skills/` y `mm reload`.
3. Instalar el datapack y resource pack regenerados siguiendo `GUIA.md`.
   Cambiar URL y SHA-1 juntos. No reemplazar el mundo completo.
4. `skript reload special_weapons` (nombre completo: AuraSkills puede capturar `sk`).
5. Dar una copia de cada arma con `loot give <jugador> loot astral:item/<id>` o
   `execute as <jugador> run function astral:admin/kit_especiales`.

Sin el script, los objetos y recetas cargan, pero sus habilidades no funcionan.
No se necesita un plugin Java propio, addons de Skript ni mods del cliente.

La prueba local usa Paper 26.1.2 build 74, dos clientes de protocolo locales,
AuraSkills 2.4.0, Skript 2.17.1 y skript-reflect 2.6.3. Se comprobaron carga sin
errores, mana insuficiente y debito exacto, desplazamiento repetido de tres bloques,
paredes, seis victimas distintas, recargas, dano a mobs, exclusion de jugadores
fuera de arena y limpieza de displays. Falta evaluar visualmente las animaciones
y el balance en el cliente real, y comprobar las regiones de WorldGuard en Aternos.
Tambien se comprobo dano real entre los dos jugadores dentro de arena, cancelacion
externa de dano y devolucion de mana ante teletransporte cancelado.

Referencias tecnicas: [API de AuraSkills](https://wiki.aurelium.dev/auraskills/api),
[API de Paper](https://jd.papermc.io/paper/26.1.2/org/bukkit/World.html).
