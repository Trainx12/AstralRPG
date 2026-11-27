# Slimes: herencia al dividirse (27/11)

Preparado, sin desplegar. AstralProgression 1.6.1; abierto a todos por ser un arreglo autorizado.

Paper 26.1.2 copia los tags en ConversionType.convertCommon, incluido astral.seen;
Slime.remove convierte al hijo y luego setSize restablece vida base y dano. SPLIT se emite
despues de setSize y antes de insertar los hijos. La marca heredada impide mob/roll.
Correccion 1.6.1: captura bases y modificadores al morir (EntityDeathEvent LOWEST),
antes de la espera de division. En el conjunto local, el padre ya llega a SPLIT con bases
por defecto; copiarlo ahi ocultaba el error en la prueba anterior. La instantanea conserva
los valores previos a la muerte y se consume en SPLIT (o caduca en 100 ticks si no divide).
Sin muerte registrada usa la captura en SPLIT como respaldo. Con esos valores,
los aplica en SPLIT, en CreatureSpawnEvent SLIME_SPLIT y nuevamente al tick siguiente.
La ultima aplicacion termina despues de la insercion y los listeners de spawn sincronicos;
restaura primero bases/modificadores y despues llena la vida. No depende de que el padre
siga vivo; retira cada hijo pendiente al tick siguiente, incluso si se cancelo su aparicion.
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
Para actualizar desde 1.6.0, subir SOLO el JAR: el Skript no cambio.
El Skript de la tabla es requisito acumulado si aun no se instalo la entrega anterior.
Preparar antes del proximo reinicio diario autorizado; verificar el horario vigente en el panel. No activar reinicio por vacio.
El reinicio completo carga JAR y Skript; no hace falta apagar para preparar plugins/update.
Alternativa: con el servidor apagado reemplazar el JAR en plugins/ y arrancar.
Si se prepara el Skript con el servidor encendido: `skript reload astral_economia` (consola),
pero no considerar terminado hasta cargar tambien el JAR mediante reinicio completo.
No usar PlugMan ni /reload general. No requiere datapack, texturas, R2 ni reemplazar mundos.
Aternos no permite subir plugins propios fuera de su catalogo: sin AstralProgression disponible
alli, la instalacion queda bloqueada; continuar en el hosting que permita este JAR (Empower).

Comprobar consola: AstralProgression 1.6.1 activo y Skript sin errores. Matar slimes/magma cubes
escalados nuevos: cada hijo debe tener la misma vida maxima, llena, tier y elite que el padre.
Comprobar ambas generaciones, dano y pagos con cuenta de prueba; minijuegos y mascotas intactos.
Las divisiones anteriores ya ocurridas no se pueden reconstruir: probar entidades nuevas.
Nunca subir SlimeSplitProbe, configuraciones locales de Paper ni mapas del ensayo.

Reproducir: `python datapack-src/deploy_slimes.py --java <java25> --server <Paper-local>`;
`python tools/probar_slimes_paper.py --java <java25> --source <Paper-local>`.
Ensayo nativo y ensayo con `--reset-bases`: ambos verifican bases, modificadores, valor
final y vida llena a +1, +5 y +20 ticks; incluyen dos generaciones, slime/magma, elites,
exclusiones, contacto diminuto, XP y plata. Caso remoto: Size:2 (Bukkit 3), base 9,
astral:tier +24 => 225; el inyector de prueba cambia bases a 20/1/0.2 durante spawn
conservando el modificador y reproduce 500 de vida maxima con 1.6.0. La prueba compara
contra valores capturados ANTES de morir, no contra el padre ya alterado en SPLIT.
El ensayo nativo tambien detecta el cambio del padre durante su muerte en el conjunto
local. El inyector simula adicionalmente un reseteo tardio del hijo; no identifica que
componente remoto lo causa ni replica todos los plugins/datapacks del servidor. Con 1.6.1 vuelve a 225 al tick siguiente y permanece.
Para demostrar la regresion de 1.6.0: agregar `--baseline --reset-bases --jar <jar-1.6.0>
--work <directorio-local-distinto>`. Los logs e inyectores quedan solo en el ensayo local.

Validacion local 27/11: Paper 26.1.2, Java 25; 1.6.1 sin fallos en ensayo nativo
(1767 comprobaciones) y con reseteo tardio (1733 comprobaciones). 1.6.0 reproduce
la regresion al comparar contra el padre antes de morir (210 fallos con inyector).
La cantidad varia por la cantidad aleatoria de hijos. El JAR mantiene config/recursos;
solo cambian clases AstralProgression y version. El Skript generado queda identico.
39 pruebas de progresion, tiers, economia y minijuegos aprobadas.
Suite ampliada (47): dos fallos ajenos a esta tarea en test_gameplay (requisito de defensa
vs Combate de armaduras, y click_requirement de titulos); no se modificaron sus fuentes
ni salidas. No se declara aprobada la suite completa. Verificacion remota pendiente.

Discord, publicar solo al quedar en vivo: Corregimos los slimes y cubos de magma: al dividirse,
sus hijos conservan la vida completa, el tier y el dano del original. Sus premios de combate
quedan controlados para evitar multiplicaciones de plata y XP.

SHA-256 de los archivos de esta entrega:
- `build/runtime/AstralProgression.jar`: `f2a0f227647cf6b404f91a97d4ef195e2944656abfee111a18df61e1edb2b6d2`
- `build/economia/Skript/scripts/astral_economia.sk`: `13b1dbf8ff24695311c9dff901f07058ebf38773b0755ef23196222642d74e6d`
