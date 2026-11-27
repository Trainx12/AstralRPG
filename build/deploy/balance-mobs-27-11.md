# Vida y skill de slimes; tier de jefes (27/11/2026)

AstralProgression 1.6.3. Esta entrega reemplaza el balance de la entrega historica de slimes 1.6.1.

Slimes y cubos de magma: grandes conservan su vida escalada por tier; cada division
reduce la vida maxima a la mitad, con vida llena al nacer. Naturales medianos y pequenos
usan base 8 y 4 frente a 16 del grande vanilla. La XP de skill conserva tier, elite,
penalizaciones y reparto existentes: tamano grande 100%, mediano 45%, pequeno 20%.
No cambia dinero, loot, dano, velocidad, mascotas ni minijuegos excluidos.

Los jefes de mundo toman el tier exacto del mejor arma/baston o armadura del inventario,
incluido equipo puesto y mano secundaria; herramientas y accesorios excluidos.
El evento ancestral usa al jugador elegido aunque haya otro mas cerca de la aparicion.
Sin equipo/jugador cercano: minimo T1. Se conservan los tiers propios de mazmorras y Santuario.
Vida normal de jefe: 25 x VIDA_REF[tier]; ancestral conserva multiplicador x5.
MythicMobs restablece la vida base despues de sus comandos onSpawn: se reprodujo el cangrejo
con 5000 de vida aun con astral.jm10. El runtime restaura por la API nativa la base del tier guardado
dos ticks despues de MythicMobSpawnEvent. La tabla world-boss-health.txt se genera desde escala.py.
Tambien actualiza la base HEALTH del registro de estadisticas de MythicMobs: ese registro
reaplicaba 1000 de base y devolvia el ancestral a 5000 incluso tras corregir el atributo nativo.
No usa NBT para restaurar ni recalcula el tier durante esa restauracion. Solo una vez
al nacer; no al cargar chunks ni por reloj.
La XP reconoce astral.jmN antes del tier fijo de la especie; el dano usa la condicion nativa
de Skript para consultar cada etiqueta sin fallar al haber multiples tags.

## Instalacion aislada

Servidor activo: Empower; Aternos quedo como copia y no permite subir este plugin propio.
No reemplazar AstralRPG-Items.zip ni mundos, ni regenerar/subir texturas.

`build/balance-mobs/balance-mobs-instalar.zip` contiene solo:

| Ruta en el archivo (relativa a /home/container) | Uso |
|---|---|
| `plugins/update/AstralProgression.jar` | Paper reemplaza el JAR al reiniciar |
| `plugins/Skript/scripts/astral_gameplay.sk` | Solo diez condiciones de tags de jefes |
| `plugins/Skript/scripts/astral_ancestral.sk` | Identifica al jugador del evento |
| `world/datapacks/zz-AstralRPG-BalanceMobs.zip` | Tres funciones; prioridad posterior al datapack base |

Subir y descomprimir el archivo en la raiz. Conservar configuraciones y datos del plugin.
No usar PlugMan, /reload general ni activar reinicio por vacio. Cargar conjuntamente en
el proximo reinicio diario autorizado. Comprobar AstralProgression 1.6.3, scripts sin errores
y datapack habilitado con prioridad posterior a AstralRPG-Items. Si se necesita ordenar
manualmente: deshabilitar el parche y habilitarlo con `last` mediante comandos `datapack`.
Cuando se actualice el datapack base con estas mismas funciones, retirar el parche para
que no oculte cambios futuros en esas tres funciones.

Las entidades ya divididas no se reconstruyen. Probar criaturas nuevas; la restauracion
de jefes tampoco sana jefes antiguos en combate.

## Regenerar y verificar

Compilar: `python datapack-src/deploy_slimes.py --java <java25> --server <Paper-local> --jar-only`.
Generar parche y entrega: `python datapack-src/deploy_balance_mobs.py`.
El generador completo se ejecuta en `.local/`, sin reemplazar el build acumulado de otras tareas.
Solo se extraen mob/roll, mob/jefe_mundo y mob/jefe_vida; no incluye arte privado.

Ensayos: `tools/probar_slimes_paper.py` (nativo y `--reset-bases`) y
`tools/probar_balance_mobs_paper.py`. Nunca subir plugins, mundos ni cuentas de ensayo.
El ensayo de jefes usa vida y comandos reales del cangrejo, sin su modelo visual.
Los errores ajenos de upgrade/slot del datapack acumulado local no se incluyen en el parche.

Discord, solo cuando quede activo: "Corregimos la vida y la experiencia de slimes y cubos de magma:
los medianos tienen la mitad de vida y dan el 45% de experiencia; los pequenos tienen un cuarto
de vida y dan el 20%. Los jefes de mundo ahora ajustan vida, dano y experiencia a su tier,
segun el mejor arma o armadura del inventario del jugador. Corregido el cangrejo ancestral de 5000 de vida."

Validacion: 11 pruebas unitarias de progresion, requisitos y probabilidad aprobadas.
Paper 26.1.2: 2011 comprobaciones de slime/magma con reseteo tardio, dos generaciones,
vida/atributos a +1/+5/+20 ticks, XP 100/45/20, elites, contacto y dinero; cero fallos funcionales.
Tambien paso el ensayo nativo previo (2183 comprobaciones). El ensayo final detecto un error
ajeno al consultar actualizaciones de Paper y claves de Yggdrasil por red (servidor local offline):
se excluyen solo esos avisos del verificador.
Jefes: arma T1, armadura T5 guardada junto a arma T1 y herramienta T10, baston T10;
vida, dano con multiples tags, XP del tier real, cangrejo ancestral T10 estable y sin curacion
posterior. El log de jefes se verifico con --verify-log; el lanzador original esperaba
incorrectamente la firma [Server] del mensaje emitido por el cangrejo; corregido el verificador.
Se reprodujo antes el ancestral de 5000, incluso despues de cambiar solo el atributo nativo;
actualizar HEALTH en el registro de MythicMobs resuelve la regresion.

Publicado: commit 11e9644ae89b713de5b4d4c5a536c0d3536ff37a, push y rama remota verificados.
Instalado EN DISCO en Empower el 27/11/2026, aproximadamente 20:46-20:48 AR, desde el navegador.
Los cuatro archivos fueron descargados desde sus destinos y comparados byte por byte con la entrega:
plugin en plugins/update, ambos scripts y parche del datapack correctos. El datapack base no se reemplazo.
Consola consultada: AstralProgression 1.6.2 todavia activo. No se reinicio ni recargo el servidor.
La activacion de 1.6.3 y la comprobacion en vivo quedan pendientes del reinicio diario autorizado.
Aternos no fue modificado: servidor activo documentado y verificado es Empower.
Discord pendiente hasta quedar activo; texto listo arriba. No se promete aviso automatico.

SHA-256 verificados en los destinos remotos:


- `build/runtime/AstralProgression.jar`: `a8e4b2b054293a2f4407c097e82a7ab649dcd5a2b6702b219f701aac60d3dea0`
- `build/gameplay/astral_ancestral.sk`: `bc25b49565f030f90467aa0e8b6a207db2104ef52b9b87307c3fcc7e767df297`
- `build/balance-mobs/astral_gameplay.sk`: `fc6e17912ad2347f71e87919c6f3064caabc8e7eaacbb539dcf158d5efe0a24b`
- `build/balance-mobs/zz-AstralRPG-BalanceMobs.zip`: `50f07c92324d5cb8d61df0549a7a16e6fbbf4aca34fa61b5df583ee875e9a753`
