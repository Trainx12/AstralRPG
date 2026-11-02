# Armas especiales independientes

Implementacion local del 02/11/2026. No publicadas en Aternos.
Se forjan en Guia AstralRPG → Especiales y aparecen en `admin/kit_especiales`.
Ninguna exige una clase ni forma parte de los kits Berserker, Arquero o Mago.

| Arma / ID | Habilidad | Mana | Recarga |
|---|---|---:|---:|
| Filo de la Tormenta / `espada_tormenta` | 25% por golpe cuerpo a cuerpo aceptado: rayo visual y 6 de dano en radio 2 | 0 | — |
| Danza del Ender / `espada_sombras` | Clic derecho: selecciona hasta 6 enemigos distintos a 12 bloques y salta junto a cada uno, con un golpe de 10; un salto cada 5 ticks, secuencia de 1,5 s a 20 TPS | 40 | 5 s |
| Filo del Destello / `espada_destello` | Clic derecho: 3 bloques siguiendo la mirada, tambien verticalmente | 10 | Ninguna |
| Hacha del Sismo / `hacha_terremoto` | Clic derecho: 10 de dano en radio 3; doce fragmentos del suelo suben y bajan durante 0,8 s | 30 | 6 s |
| Varita del Estallido / `varita_estallido` | Clic derecho: disparo instantaneo hasta 16 bloques; explota contra un bloque o enemigo. Tambien explota al golpear cuerpo a cuerpo. Radio 2, dano 6 | 20 por uso | Disparo: 1 s |

Los valores son puntos de vida, antes de armadura/resistencia (2 puntos = 1 corazon).
El mana se consume con `SkillsUser.consumeMana`, sobre el saldo real de AuraSkills.
La varita hace su golpe fisico normal aunque no alcance el mana para la explosion.
Los costos y danos adicionales elegidos son un balance inicial ajustable.

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
- No hay habilidades en lobby. Los dos teletransportes siguen desactivados en las seis
  mazmorras, conforme a las reglas de movilidad existentes.
- Los saltos comprueban el volumen completo del jugador cada 0,2 bloques, paredes,
  borde del mundo y peligros. El salto Ender exige linea de vision, suelo y un destino
  lateral libre; omite enemigos muertos, lejanos o inaccesibles. Cambiar de arma,
  desconectarse, morir o cambiar de mundo corta la secuencia.
- Un teletransporte de Destello cancelado devuelve los 10 de mana.
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

1. Instalar **skript-reflect 2.6.3** desde el catalogo de plugins de Aternos. Necesita
   Skript 2.14 o superior; se probo con Skript 2.17.1 y AuraSkills 2.4.0.
2. Subir `build/gameplay/astral_armas_especiales.sk` a `plugins/Skript/scripts/`.
3. Instalar el datapack y resource pack regenerados siguiendo `GUIA.md`.
   Cambiar URL y SHA-1 juntos. No reemplazar el mundo completo.
4. Reiniciar tras instalar el complemento; luego `skript reload astral_armas_especiales`.
5. Dar una copia de cada arma con `loot give <jugador> loot astral:item/<id>` o
   `execute as <jugador> run function astral:admin/kit_especiales`.

Sin el script o skript-reflect, los objetos y recetas cargan, pero sus habilidades
no funcionan. No se necesita un plugin Java propio ni mods del cliente.

La prueba local usa Paper 26.1.2 build 74, dos clientes de protocolo locales,
AuraSkills 2.4.0, Skript 2.17.1 y skript-reflect 2.6.3. Se comprobaron carga sin
errores, mana insuficiente y debito exacto, desplazamiento repetido de tres bloques,
paredes, seis victimas distintas, recargas, dano a mobs, exclusion de jugadores
fuera de arena y limpieza de displays. Falta evaluar visualmente las animaciones
y el balance en el cliente real, y comprobar las regiones de WorldGuard en Aternos.
Tambien se comprobo dano real entre los dos jugadores dentro de arena, cancelacion
externa de dano y devolucion de mana ante teletransporte cancelado.

Referencias tecnicas: [API de AuraSkills](https://wiki.aurelium.dev/auraskills/api),
[skript-reflect](https://github.com/SkriptLang/skript-reflect),
[API de Paper](https://jd.papermc.io/paper/26.1.2/org/bukkit/World.html).
