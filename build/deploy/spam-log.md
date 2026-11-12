# Spam de funciones de salas — 12/11/2026

Preparado localmente; despliegue remoto pendiente. El servidor activo documentado
es Empower (Paper 26.1.2); Aternos queda como copia. Esta tarea no accedio a ninguno.

## Correccion

`datapack-src/mobs/tanda2.py` agregaba a los 14 controladores una llamada de consola
MythicMobs a `astral:tanda2/<mazmorra>/<sala>/tick` cada **20 ticks** (un segundo,
no cada tick), incluso en salas inactivas. La consola informa esas ejecuciones.

Ahora `astral:loop/t20`, ya programado por el datapack, llama una sola vez a
`astral:tanda2/tick`. Este selecciona controles ARMOR_STAND por nombre existente,
en su dimension y con `<mazmorra>.on`, y ejecuta el mantenimiento como cada control
y en su posicion. No fuerza chunks ni necesita reemplazar los controles existentes.
Se conserva el intervalo de 20 ticks; la fase respecto del timer de Mythic puede
variar hasta 19 ticks. Las funciones de cola, topes, oleadas, muerte de jefe,
reset y premio conservan su contenido. Santuario no cambia.

Solo dos entradas difieren dentro del ZIP: `loop/t20.mcfunction` y la nueva
`tanda2/tick.mcfunction`. En los cinco YAML solo se retiran las 14 llamadas repetidas.
No se desactiva globalmente el feedback ni se ocultan errores del servidor.

## Instalacion exacta

Apagar completamente; respaldar los seis archivos actuales y reemplazarlos juntos.
Conservar los demas datapacks, plugins y configuraciones.

SHA-256 del ZIP preparado:
`b0d13b874efbbb80b60964e68b4415f27a185b00e192b93e8b057435e6d927d4`.

| Archivo local | Destino relativo a la raiz del servidor |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/mythicmobs/mobs/mazmorra.yml` | `plugins/MythicMobs/mobs/mazmorra.yml` |
| `build/mythicmobs/mobs/bosque.yml` | `plugins/MythicMobs/mobs/bosque.yml` |
| `build/mythicmobs/mobs/tumba.yml` | `plugins/MythicMobs/mobs/tumba.yml` |
| `build/mythicmobs/mobs/cumbre.yml` | `plugins/MythicMobs/mobs/cumbre.yml` |
| `build/mythicmobs/mobs/forja.yml` | `plugins/MythicMobs/mobs/forja.yml` |

Iniciar y revisar consola. El arranque carga datapack y MythicMobs: no requiere
`minecraft:reload` ni `mm reload` adicionales. Una recarga aislada de MythicMobs
sin instalar el datapack detendria el mantenimiento de colas: no hacerlo.
No subir los auxiliares SpamProbe/UrgenteProbe ni carpetas `.local`.
No cambiar el resource pack, SHA-1, mapas ni mundos; nunca Worlds > Upload sobre world.

Verificacion remota pendiente: entrar a una sala, completar oleadas y jefe, abrir
el cofre, abandonar y volver para comprobar reset. Mirar al menos un minuto de
consola con salas cargadas: no deben repetirse `Running function .../tick` ni
`Function .../tick returned ...`. Los eventos puntuales wave/reset pueden informar
su ejecucion. Si se vuelve atras, restaurar juntos el ZIP y los cinco YAML y reiniciar.

## Verificaciones locales

- Generadores: `python datapack-src/build.py` y `python datapack-src/mobs/mazmorra.py`.
- Nueva regresion: `python -m unittest discover -s datapack-src -p test_spam_log.py`.
  Comprueba las 14 salas, una unica llamada desde t20, mundo/contexto/filtro activo,
  ausencia del timer de consola y conservacion de inicio/reset/victoria de Mythic.
- `test_ajustes_menu_oleadas.py`: 4 pruebas OK.
- Suite relevante conjunta: **19 pruebas OK** (`test_spam_log`,
  `test_oleadas_tanda2.OleadasTests`, `test_oleadas_tanda2.ModelSizeTests`,
  `test_tanda3a`, `test_ajustes_menu_oleadas`).
- `test_oleadas_tanda2.py`: 8 pruebas OK y una comprobacion historica de hashes
  de Santuario desactualizada. El archivo que falla es identico a HEAD anterior
  (`da200e8d618d8e8a4c8f806a1c1c5f096b51f20d`); no se altera para esta tarea.
- `python tools/verificar_terceros.py`: sin arte privado ni rutas privadas versionadas.
- `git diff --check`: OK. Trabajo previo no versionado conservado y excluido.

Ensayo reproducible (JDK 25 y un Paper local detenido con los plugins requeridos):

```text
python tools/probar_spam_paper.py --java <java25.exe> --base .local/tanda4a-paper --baseline da200e8d618d8e8a4c8f806a1c1c5f096b51f20d
python tools/probar_spam_paper.py --java <java25.exe> --base .local/tanda4a-paper
```

Cada ejecucion crea otra carpeta privada `.local/spam-paper-*`; no modifica la base.
Usa un jugador NMS simulado, mata enemigos para avanzar y confirma el estado de
muerte del jefe para probar la aparicion del cofre. No prueba combate con cliente,
cobro economico ni cooldown del premio. Los mapas no se copian ni publican.
Comparacion definitiva en Paper 26.1.2 + MythicMobs 5.13.0 + BetterModel 3.6.0:

| Version | Comprobaciones del auxiliar | Mensajes de mantenimiento `/tick` |
|---|---|---|
| Anterior, `da200e8` | 7 OK, 0 fallos | 89 |
| Corregida | 7 OK, 0 fallos | 0 |

Se comprobo sala inactiva, avance automatico del reloj, las dos oleadas, inicio
de otra partida, reset al abandonarla activa, cofre con muerte confirmada y reset
de la sala final. Logs privados: `.local/spam-paper-ne6kvwe1/probe.log` (anterior)
y `.local/spam-paper-5tmq0w2m/probe.log` (corregida). Ambos ensayos emiten tres
`No key layers in MapLike[{}]` al crear mundos planos de prueba con configuracion
por defecto; no hay fallos de carga de las funciones de salas. No se certifica
que toda la consola este libre de avisos ajenos a esta correccion.

## Otros mensajes revisados

- `Set [aq.clock] for #epoch`: `misiones.py`, skill `AQ_CLOCK`, llamada desde el
  Cronista cada 200 ticks y al aparecer. Requiere `<utils.epoch>` de Mythic para
  mantener dias reales; no se reemplaza por tiempo del mundo ni se suprime el reloj.
- `Added tag astral.menu.test`: `estrella_menu.py`, consulta de identidad de un slot
  desde Skript. Elimina y agrega la etiqueta para comprobar custom_data. No se
  reemplaza por nombre/lore ni por ejecutar como jugador OP.
- La clase `CommandMechanic` del MythicMobs local no expone opcion `silent`.
  Resolver esos dos puentes sin feedback requiere otro mecanismo de comunicacion
  (y ensayos de misiones/seguridad de inventario); queda pendiente. No son llamadas
  por segundo por cada sala vacia como el origen principal corregido aqui.

## Publicacion y despliegue

Commit/push autorizados para esta tarea. El hash se comunica en el resultado del
puente; este documento queda dentro del mismo commit. Despliegue remoto pendiente
de Claude con acceso al navegador; no se afirma instalacion ni validacion remota.
