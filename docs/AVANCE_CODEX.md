# Cambios locales del 30/10/2026

## Correccion del Cronista (31/10/2026)

Publicada en GitHub e instalada en Aternos el 31/10. La prueba con jugador detecto ademas
prioridades repetidas entre variantes del mismo slot: DeluxeMenus descartaba opciones y
mostraba espacios vacios (o el aviso de espera). Cada variante ahora tiene prioridad unica.
ScoreboardObjectives ya estaba activa; se comprobo con `papi list` y la lectura de scores.

- Historia, las tres dificultades y el premio de armadura usan pantallas propias. Los clics abren
  el menu correspondiente; ya no dependen de refrescar la condicion oculta `aq.page`.
- El objeto central muestra objetivo, dinero, premios extra y progreso al pasar el cursor.
  Al hacer clic, cierra la ventana y muestra el objetivo en el chat con el comando para volver.
- Verde permite aceptar o comprobar/cobrar. Rojo permite rechazar o abandonar: pausa el conteo
  y conserva avances, sin pagar ni consumir materiales. Las diarias se borran a medianoche como antes.
- Retomar Jinete actualiza la referencia de distancia para no contar recorridos hechos durante la pausa.
- Si faltan datos, aparecen un aviso y Actualizar. Las pestañas y la ayuda siguen visibles aunque
  no funcione la expansion; las acciones siguen validando los objetivos desde el datapack.
- Faltaba incluir `ScoreboardObjectives` en los pasos de instalacion. Es necesaria para las
  condiciones y el progreso del menu: https://github.com/PlaceholderAPI/Expansion-ScoreboardObjectives.

Para volver a instalar esta correccion:

1. Con el servidor apagado, reemplazar `world/datapacks/AstralRPG-Items.zip` por el ZIP de `build/`.
2. Copiar los cinco archivos `build/menus/DeluxeMenus/gui_menus/misiones*.yml` a
   `plugins/DeluxeMenus/gui_menus/`. Agregar las cinco entradas de misiones de
   `build/menus/DeluxeMenus/config-gui_menus.yml` en `gui_menus:` del config existente.
3. Reemplazar `plugins/MythicMobs/skills/misiones.yml` con `build/mythicmobs/skills/misiones.yml`.
4. Arrancar y ejecutar en consola `papi ecloud download ScoreboardObjectives`, `papi reload`,
   `dm reload` y `mm reload`. Si ya esta instalada, basta con verificar que este cargada.
5. Como jugador, `/papi parse me %objective_score_{aq.state}%` debe devolver un numero.
   Abrir al Cronista y probar las tres pestañas, detalle, aceptar, abandonar, retomar y cobrar.
   Las entregas se cobran junto al NPC indicado en el objetivo. No recrear el Cronista.

Verificado en PC: `python -m unittest test_misiones` (historia, 14 diarias, falta de expansion,
acciones y navegacion) y `python verify.py` (JSON y referencias de funciones/loot/skills).
Pendiente: prueba visual con jugador y plugins completos; no se modifico el resource pack.

Estos cambios estan preparados en la PC. **No se subieron a Aternos, no se hizo commit ni push.**
La historia, las diarias, los nuevos accesos y el HUD necesitan una prueba con jugador antes de publicarse.

## HUD

- `hud_rpg.py` conserva el estilo piedra, oro y violeta, con runas e indicadores de recarga del ataque.
- Ahora exporta a las medidas nativas de Minecraft. El dibujo interno sigue a 4x.
- `gui_textures.py --hud-only` regenera solo el HUD y conserva las ventanas que ya funcionan.
- `--client-jar` comprueba las 88 rutas y dimensiones contra el cliente 26.1.2 antes de escribir.
- Las texturas nuevas son PNG RGBA estaticos, sin metadatos de animacion o escalado heredados.
- No se encontro en los logs disponibles una causa confirmada del rosa/negro anterior. Esta es una version
  compatible para probar, no una reparacion visual confirmada dentro del juego.
- No se agregaron barras falsas de mana, retratos ni durabilidad numerica: esos datos y posiciones del ejemplo
  necesitan otro sistema de HUD o mods; el pack actual cambia los elementos que Minecraft ya dibuja.

Vista previa: `build/HUD-preview.png`. Pack: `build/AstralRPG-Textures.zip`.
SHA1 de esta version: `5d2e77ba1810393e27f94032bdfe43ec77217474`.

## Historia y diarias

`datapack-src/misiones.py`, integrado con `build.py`, genera las funciones y `build/mythicmobs/skills/misiones.yml`.
Usa los plugins existentes. No hace falta instalar un plugin nuevo de misiones.

- Viajero: clic normal conversa/entrega el capitulo; **shift + clic conserva el viaje al mundo**.
- Herrero: explica el primer equipo y la Forja final; mantiene sus mejoras originales.
- Cronista: muestra las tres diarias del dia y cobra las completadas. Las entregas se hacen en Tienda,
  Herrero, Bazar o Cronista segun la mision.
- `/menu` y la Guia Astral tienen acceso a un diario de consulta. Tambien `/trigger aq.journal`.
- El capitulo se guarda en `aq.state` (0 sin empezar, 1 prologo, 2 campos, 3 Cangrejo, 4 Chaman,
  5 Momia, 6 Minas, 7 Yeti, 8 Golem, 9 epilogo, 10 historia completa).
- Los seis recuerdos estan definidos en `HISTORY_ITEMS`, separados de materiales y sin recetas.
  Se entregan una vez por jugador, durante su capitulo. La victoria personal queda registrada: perder
  el recuerdo no bloquea la historia y comprarlo a otro jugador no permite saltar un capitulo.
- El Viajero conserva narrativamente los ecos de los fragmentos; el epilogo no exige tener otra vez
  cinco objetos fisicos. Los recuerdos quedan como coleccionables.
- Los contadores de las misiones solo registran acciones posteriores al inicio del capitulo/dia.
- La armadura tier I del capitulo de los campos se elige una sola vez con `/trigger aq.reward set N`:
  1-4 Berserker, 5-8 Mago, 9-12 Arquero; dentro de cada clase: casco, pechera, grebas, botas.
- Las 14 diarias se sortean en tres grupos (5 faciles, 5 medias, 4 dificiles); cada dia todos reciben
  la misma seleccion de tres. Reinician a las **00:00 de Argentina (UTC-3)** usando la fecha real
  que aporta MythicMobs, incluso si Aternos estuvo apagado al cambiar el dia.
- La racha requiere cobrar las tres el mismo dia, durante siete dias consecutivos. Da una tirada de armas.
  Un dia omitido corta la racha; completar otra semana da otra tirada.
- Jinete mide 1000 bloques en monturas terrestres mediante la estadistica de cabalgar. No mide vuelo.
- Para Provisiones se entregan 32 panes o 32 carnes cocidas del mismo tipo. No se mezclan tipos.
- La diaria de mejora cuenta un intento de +5 o mas, aunque falle, despues de pagar los materiales.
- La arena y espectadores quedan excluidos de los eventos de progreso.
- Las Minas dan credito de historia al terminar aunque el cofre de materiales este en cooldown.

Instalacion y reloj: `build/misiones/comandos.txt`. El chunk del Cronista debe quedar cargado.
El dinero pendiente usa `aqmoney` (sin puntos, por el parser de placeholders) y se paga con Essentials desde MythicMobs. El titulo usa LuckPerms;
la racha, CrazyCrates. Verificar esas integraciones con un jugador antes de abrirlo al publico.

## Mazmorras y arena

Ver [MAZMORRAS.md](MAZMORRAS.md). El motor sirve para varias mazmorras y conserva todos los IDs de las Minas.
Las nuevas tienen ubicaciones propuestas y entradas **deshabilitadas**, como se acordo para revisarlas en Minecraft.
El Santuario queda como prueba posterior a completar la historia, con cinco Ancestrales seguidos.
La Forja conserva solo el volcan del sur; el volcan del norte queda fuera del recorte, para evitar
recorridos confusos. Se verificaron los limites de los 684 chunks del ZIP preparado.

## Verificacion realizada

- Regeneracion del datapack, pack de texturas, MythicMobs, menus y comandos.
- Paper 26.1.2 local cargo el datapack; MythicMobs cargo las configuraciones nuevas.
- Pruebas de contadores con una entidad de prueba: doble cobro de diaria bloqueado; recuerdo del Cangrejo
  entregado una sola vez; dialogo repetido no duplica el premio; dia nuevo reinicia diarias y conserva historia;
  racha semanal entrega una sola marca de gacha.
- Reloj: `31/10/2026 02:59:59 UTC` pertenece al dia anterior; `03:00:00 UTC` cambia de dia en Argentina.
- La lectura de dinero desde MythicMobs se comprobo con un valor de prueba (1234). El nombre del objetivo
  no lleva puntos porque MythicMobs los interpreta como acceso a metadatos.
- Se leyeron de nuevo todos los chunks exportados de los seis recortes; no quedaron bloques de comandos,
  structure blocks, jigsaw ni spawners en sus paletas.
- Faltan pruebas con jugador: aspecto del HUD, inventarios/entregas, dinero real, titulo, gacha y combate.
  El servidor de prueba no incluye la economia completa de Aternos.

## Regenerar

Desde `datapack-src`:

```text
python build.py
python gui_textures.py --hud-only --client-jar <ruta-a-26.1.2.jar>
python hud_rpg.py
python build_pack.py pack-source
python mobs/mythic.py
python mobs/mazmorra.py
python mobs/mascotas.py
python lobby.py
python menus.py
python verify.py --client-jar <ruta-a-26.1.2.jar>
```

Subir el datapack con el servidor apagado. Las configs correspondientes van en `plugins/MythicMobs/{mobs,skills}`
y los menus en `plugins/DeluxeMenus/gui_menus`. Recargar configs con `mm reload` y `dm reload`.
Si se publica el resource pack, actualizar su SHA1 en `server.properties` despues de publicar el ZIP.
No ejecutar la reconstruccion del lobby ni recrear las Minas para instalar estas novedades.
