# Slimes: herencia al dividirse (27/11)

Preparado, sin desplegar. AstralProgression 1.6.0; abierto a todos por ser un arreglo autorizado.

Paper 26.1.2 copia los tags en ConversionType.convertCommon, incluido astral.seen;
Slime.remove convierte al hijo y luego setSize restablece vida base y dano. SPLIT se emite
despues de setSize y antes de insertar los hijos. La marca heredada impide mob/roll.
El arreglo usa EntityTransformEvent SPLIT en el plugin existente, copia atributos y modificadores,
vida llena, efectos, nombre, tags y score astral.mt. Conserva el tamano y ambas especies.
Tambien recupera el contacto de slimes diminutos (vanilla no los deja atacar aunque tengan dano).
Solo procesa padres escalados; excluye minijuegos de minijuegos.parkour_worlds, mascotas,
invocaciones marcadas astral.pet e invulnerables. No modifica los Size:0 de las salas.

Los hijos pagan XP de AuraSkills como un mob normal de su tier, sin bonus de elite;
conservan factores por tier del jugador y reparto de party. La plata de survival/Infinita
queda limitada al valor de un mob normal del tier por hijo; las oleadas pagan su valor
normal, sin extra de elite para hijos. Se usa la condicion nativa `has scoreboard tag`
de Skript para reconocer tier, marca y rutas de pago aun con multiples tags:
[documentacion oficial](https://docs.skriptlang.org/conditions.html#CondHasScoreboardTag).
La prueba anterior con `scoreboard tags ... contain` obtenia T1 y omitía el tope al
agregar la segunda etiqueta. Infinita queda excluida del pago survival para no cobrar doble.
Cada muerte vuelve a exigir combatir toda la vida heredada. No se cambia
el loot de elite, los avances ni la XP vanilla; cada slime tiene como mucho dos generaciones
desde Size:3 vanilla (4 -> 2 -> 1 en Bukkit).

| Archivo local | Destino |
|---|---|
| `build/runtime/AstralProgression.jar` | `plugins/update/AstralProgression.jar` |
| `build/economia/Skript/scripts/astral_economia.sk` | `plugins/Skript/scripts/astral_economia.sk` |

Conservar nombre exacto del JAR instalado para plugins/update; conservar config y datos del plugin.
Subir ambos antes del reinicio diario autorizado de las 05:00. No activar reinicio por vacio.
El reinicio completo carga JAR y Skript; no hace falta apagar para preparar plugins/update.
Alternativa: con el servidor apagado reemplazar el JAR en plugins/ y arrancar.
Si se prepara el Skript con el servidor encendido: `skript reload astral_economia` (consola),
pero no considerar terminado hasta cargar tambien el JAR mediante reinicio completo.
No usar PlugMan ni /reload general. No requiere datapack, texturas, R2 ni reemplazar mundos.
Aternos no permite subir plugins propios fuera de su catalogo: sin AstralProgression disponible
alli, la instalacion queda bloqueada; continuar en el hosting que permita este JAR (Empower).

Comprobar consola: AstralProgression 1.6.0 activo y Skript sin errores. Matar slimes/magma cubes
escalados nuevos: cada hijo debe tener la misma vida maxima, llena, tier y elite que el padre.
Comprobar ambas generaciones, dano y pagos con cuenta de prueba; minijuegos y mascotas intactos.
Las divisiones anteriores ya ocurridas no se pueden reconstruir: probar entidades nuevas.
Nunca subir SlimeSplitProbe, configuraciones locales de Paper ni mapas del ensayo.

Reproducir: `python datapack-src/deploy_slimes.py --java <java25> --server <Paper-local>`;
`python tools/probar_slimes_paper.py --java <java25> --source <Paper-local>`.
Para comparar con el JAR anterior: agregar `--baseline --jar <jar-anterior> --work <directorio-local-distinto>`.

Discord, publicar solo al quedar en vivo: Corregimos los slimes y cubos de magma: al dividirse,
sus hijos conservan la vida completa, el tier y el dano del original. Sus premios de combate
quedan controlados para evitar multiplicaciones de plata y XP.

SHA-256 de los archivos de esta entrega:
- `build/runtime/AstralProgression.jar`: `f9ed79900503fc15558d3d4ea11eb9bf9cf0167b12c193d782d110a76f819243`
- `build/economia/Skript/scripts/astral_economia.sk`: `13b1dbf8ff24695311c9dff901f07058ebf38773b0755ef23196222642d74e6d`
