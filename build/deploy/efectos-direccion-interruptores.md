# Bastones: requisitos, direccion e interruptores de efectos — 17/11/2026

Preparado para Empower (servidor vigente); despliegue remoto pendiente.
AstralEfectos 1.2.0, Paper 26.1.2, Java 25. Conservar PacketEvents instalado.

## Archivos exactos

| Local (desde la raiz del repo) | Destino en el servidor | SHA-256 |
|---|---|---|
| `build/runtime/AstralEfectos.jar` | `plugins/AstralEfectos.jar` | `ad7685d81bf03844792bb4d44cbbfbd11072a12e13e29ebe914b63e29b3b0557` |
| `build/menus/DeluxeMenus/gui_menus/configuraciones.yml` | `plugins/DeluxeMenus/gui_menus/configuraciones.yml` | `e51c83103d02179fb624d479f15c91cd8cc38bec06d946f33a4d6e5c905d47a3` |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` | `b9bc34f9401b1f40e1a9751eff4333068ec1c1472601a4c2b26503aaa684f785` |
| `build/gameplay/astral_armas_especiales.sk` | `plugins/Skript/scripts/special_weapons.sk` | `8565a46741dd03d9756a8efe4be7672230161c4b5352e888d1a09d9cbd76a93c` |

## Instalacion

1. Respaldar los cuatro archivos actuales del servidor y verificar Java 25. Apagar el servidor.
2. Reemplazar solamente los cuatro archivos de la tabla. El datapack es la salida completa actual del repositorio; conservar los demas datapacks y archivos del servidor.
   Skript: usar el nombre real activo, special_weapons.sk. Verificar que no haya otra copia activa astral_armas_especiales.sk; conservar desactivada la copia duplicada registrada el 16/11, sin borrar scripts ajenos.
3. Iniciar: hace falta reinicio completo por el JAR y el datapack. No usar PlugMan ni recarga global de Bukkit.
4. En consola: `dm reload`. Si Configuraciones ya esta registrado no cambiar config.yml; si falta, agregar `configuraciones: {file: configuraciones.yml}` dentro de `gui_menus`, conservando las otras entradas, y repetir `dm reload`.
5. Revisar consola: AstralEfectos 1.2.0 activo, DeluxeMenus sin errores y funciones `astral:spell/*` cargadas. Comprobar `/configuraciones` y `/efectos` con cliente.
6. El arranque carga Skript; si se reemplaza con el servidor encendido: `skript:skript reload special_weapons`. No usar el alias sk de AuraSkills. Revisar que informe cero errores.
7. Con jugador conectado: `papi parse <jugador> %auraskills_sorcery%`, y lo mismo con fighting y archery: deben devolver numeros, nunca placeholders literales. Requieren AuraSkills con su preset legacy, PlaceholderAPI y DeluxeMenus activos. Si falta Sorcery, revisar `skills preset load legacy.zip` y `skills reload`, conservando datos y configuracion del servidor.

No hay cambios de MythicMobs: no ejecutar `mm reload`. No cambian texturas ni resource pack: no subir nada a R2 ni cambiar SHA-1.
Nunca sustituir mundos ni usar Worlds > Upload en la fila world. Solo se reemplaza el ZIP del datapack dentro de world/datapacks.
Si se intenta instalar en la copia historica de Aternos, primero confirmar compatibilidad y disponibilidad del JAR por sus vias permitidas; esta entrega no elude sus restricciones.

## Comportamiento y limites

- El rayo usa raytrace desde los ojos hasta 25 bloques y conserva la salida lateral de 0,36 bloques. ItemDisplay nace con yaw/pitch cero; la transformacion aplica la direccion una sola vez.
- `/efectos armaduras|armas|bastones|mascotas|jefes` alterna; agregar `on` u `off` fija. Sin argumentos lista niveles y cinco estados clickeables. Preferencias individuales persistentes en el scoreboard principal.
- Objetivos: `astral.fx.armadura`, `astral.fx.armas`, `astral.fx.bastones`, `astral.fx.mascotas`, `astral.fx.jefes`. 1=true, 0=false; sin score se inicializa a 1 al entrar o al habilitar el plugin con jugadores conectados. Se releen cada 40 ticks; el comando aplica de inmediato.
- Los interruptores apagan solo efectos nuevos: AstralEfectos y particulas de elemento de Medio/Alto. Las particulas de siempre se ven siempre, incluso con Bastones=false (witch, end_rod, large_smoke y dragon_breath).
- El nivel Bajo/Medio/Alto y cada interruptor se combinan: true no fuerza efectos exclusivos de niveles superiores.
- Bastones controla los dibujos nuevos de rayos, fuego e impactos y `/astralfx rayo`. Jefes controla `/astralfx golpe`, `estallido` y `estela`. Las tareas diferidas conservan su categoria.
- Mascotas controla rastro y llamitas de mascotas evolucionadas de AstralEfectos; armaduras controla auras de set completo, armas controla rastros de armas y arcos.
- MythicMobs emite particulas por su propia via, sin una categoria en los paquetes. No se filtran: permanecen poof/invocacion, end_rod, evolucion y subida de mascotas; particulas, bloques falsos y proyectiles de jefes. No se modifica su YAML.
- Avisos de ataque siempre conservados: los dos `particlering` previos al SLAM (`AST_JEFE_SLAM_*`), proyectil ITEM y rastro nativo, indicadores y zonas de dano de las mazmorras (incluido Trainx). El filtro de PacketEvents sigue limitado a reducir damage_indicator; no cancela avisos.
- Configuraciones usa 45 casillas: niveles 11/13/15, interruptores 29..33 y Volver 40. Fondo generico para evitar reutilizar el panel ilustrado de 27 casillas. Conserva el icono del menu principal.
- Bastones I-X: exige Hechiceria 8/14/20/26/32/37/42/47/52/57 antes de cobrar mana y lanzar. Espada de Agua exige Combate 20; Heroe Errante, Combate 16. Valores tomados del PDC generado; especiales sin requisito conservan su uso.
- Lectura fallida de niveles o mana: no lanza ni cobra. Si cambia el arma durante la consulta, cancela el uso. Las variables de lectura son solo memoria y se limpian antes de cada consulta.
- Revision de otros usos: guadanas usan golpes y arcos/ballestas (incluido agua_arco) usan EntityShootBowEvent; AuraSkills RequirementListener.onAttack/onShoot ya controla sus PDC cuando prevent_weapon_use esta activo. No hay un disparo especial por clic que evada esos eventos. use/main solo maneja el gancho sin requisito.

## Verificaciones

Regresion: 45 pruebas de `test_baston_requisito`, `test_efectos_interruptores`, `test_special_weapons`, `test_gameplay`, `test_modelos_efectos`, `test_menu_principal`, `test_retiro_ventanas_1611` y `test_ajustes_menu_oleadas`, aprobadas.
Placeholder confirmado en documentacion oficial: https://wiki.aurelium.dev/auraskills/placeholders (`%auraskills_[skill]%`; no sufijo _level).
Ensayo local de requisitos: `tools/probar_baston_requisito_paper.py` con Paper 26.1.2, Java 25, Skript 2.17.1, AuraSkills 2.4.0 (legacy), PlaceholderAPI y DeluxeMenus 1.14.2-DEV-218. Resultado: 13 comprobaciones, failures=0.
T5 con Hechiceria 20 y mana 500: no lanza y conserva 500; con Hechiceria 32: lanza y pasa de 500 a 300. Se cancela regeneracion solo en el ensayo para medir el debito exacto. Tambien verifica mana insuficiente, lectura ausente, umbrales de Agua/Heroe y especial sin requisito. No instalar ManaProbe.jar ni reqprobe.sk en remoto.
Reproducir: `python tools/probar_baston_requisito_paper.py --java <java25.exe> --base <Paper-local> --papi <PlaceholderAPI.jar> --deluxemenus <DeluxeMenus.jar> --node <node.exe> --node-modules <carpeta-con-minecraft-protocol>`.
Ensayo reproducible con dos jugadores NMS simulados: `python tools/probar_efectos_categorias_paper.py --java <java25.exe> --base .local/testsrv`.
Ejecutado en Paper 26.1.2 / Java 25: 54 comprobaciones aprobadas, `FXCFG RESULT failures=0`, sin errores de carga del datapack.
Comprueba defaults, preferencias individuales, visibilidad de dibujos vivos, ausencia de creacion sin espectadores, toggle/on/argumentos invalidos, Bajo, yaw 90/pitch 30 y raytrace real. No instalar EfectosProbe.jar en remoto.
Pendiente con cliente real: alineacion visual en todas las direcciones y bastones, refresco de iconos sin cerrar el menu, reconexion/reinicio conservando preferencias y particulas recibidas por dos clientes. Revisar tambien los avisos de jefes con Jefes=false.
No se verifico un despliegue remoto ni una sesion de juego visual. Los logs del ensayo quedan solo en .local/.
