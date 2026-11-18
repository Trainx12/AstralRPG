# Party, panel y reaparicion - 17/11/2026

Preparado localmente; R2 y servidor NO modificados. La documentacion identifica Empower como principal y Aternos como copia. Claude debe verificar el panel y los archivos vigentes antes de instalar. Contexto del pedido: instalado hasta 0f0d23a, AstralDecor 1.18.0; esta entrega no reemplaza AstralDecor.

## Implementado

- AstralParty 1.0.0: party solo en memoria, maximo seis; comandos existentes, crear y disolver. El lider que sale/desconecta disuelve, igual que antes. Invitaciones de 60 segundos, sin addons Skript.
- /party abre inventario: cabezas, invitaciones aceptar/rechazar, candidatos paginados (mismo mundo primero), invitar, salir/disolver, clic del lider en una cabeza para echar. Menu Astral: Party en slot 33 con icono propio.
- Expansion interna de PlaceholderAPI (no descargar eCloud): %astral_party_en%, lider, cantidad, miembros, linea, titulo, fila1..fila3 y tab1..tab3. Todos conservan el prefijo astral_party_. El puente de consola mantiene {-party.lider::*} y {-party.miembros::*}; mazentrar e Infinita conservan party_miembros().
- Todos los tableros TAB tienen Party: lider y tres parejas compactas, nombres de cinco caracteres y porcentaje de vida, rojo <=30%, muerto con segundos. Maximo 15 lineas. El footer muestra los seis nombres completos y vida actual/maxima, incluso entre mundos. Se usa la alternativa de footer del plan; no se cambia el orden global de jugadores.
- En copias e Infinita, dano letal con party se cancela y pasa a espectador sin drops. La muerte real (/kill) tambien conserva objetos/XP y fuerza respawn dentro. 30 segundos en oleadas/Infinita, 15 en sala de jefe; constantes en party.py. Camara inicial del companero vivo mas cercano; Shift o /party mirar abre cabezas para elegir y Mirar libre. Action bar inferior y titulo con cuenta regresiva. Mirar libre queda a <=16 bloques de un companero vivo; se bloquea el cambio de mundo, cofres e interacciones.
- Reaparece junto al companero observado (o uno vivo), modo anterior, vida completa e inmunidad real de 40 ticks. Sin vivos: todos espectador tres segundos, titulo La mazmorra los conquisto / Todos cayeron, sonido y lobby. Al desconectarse muerto se restaura modo/lobby; una marca persistente permite recuperar tras reinicio inesperado.
- Los espectadores no suman vivos ni escala de oleadas. Permanecen fisicamente en su copia durante la espera para conservar la reserva y evitar reasignarla/resetearla; despues de la derrota la liberacion sigue el flujo existente. Quien espera al ganar revive y puede reclamar su cofre normal (cooldown individual existente); no se castiga su botin. Sin party se mantiene el flujo previo. No se agrego transferencia de liderazgo (opcional en el plan).

## Archivos exactos congelados

| Local | Destino | SHA-256 |
|---|---|---|
| `.local/terceros/AstralRPG-privado/build/entregas/party-17-11/tarea/runtime/AstralParty.jar` | `plugins/AstralParty.jar` | `c967de7ef16b0d32e14e545cc307d205b79c2982de7e7bc3eae22a9b3a0634b4` |
| `.local/terceros/AstralRPG-privado/build/entregas/party-17-11/tarea/mazmorras/astral_mazmorras_copias.sk` | `plugins/Skript/scripts/astral_mazmorras_copias.sk` | `3336e532f8e40600ecc0cca4bf87dfbcf23eafd74fc9be0cd459bf850338987a` |
| `.local/terceros/AstralRPG-privado/build/entregas/party-17-11/tarea/infinita/astral_infinita.sk` | `plugins/Skript/scripts/astral_infinita.sk` | `2852f1d4431823a843545be4e269558c1126e77675f3f218ad0e5909e2b726f5` |
| `.local/terceros/AstralRPG-privado/build/entregas/party-17-11/tarea/menus/DeluxeMenus/gui_menus/principal.yml` | `plugins/DeluxeMenus/gui_menus/principal.yml` | `d64783a156c3d60ab100f2ae4510e36c01463c2d5a5afac155afbf04ab19dd67` |
| `.local/terceros/AstralRPG-privado/build/entregas/party-17-11/tarea/lobby/TAB/secciones-config.yml` | `plugins/TAB/config.yml (combinar secciones)` | `11af8bd9e929310d1fd36cc846992fef9dc3353453d606837067972ccd9bd98f` |
| `.local/terceros/AstralRPG-privado/build/entregas/party-17-11/AstralRPG-Textures.zip` | `R2: AstralRPG-Textures.zip` | `3db1ee9a39c3989e752044abd05ebfc68b81cccecf3d47e5c7719a0826efc458` |

Los archivos bajo tarea contienen exclusivamente esta implementacion. El script publicado de copias se obtuvo aplicando la migracion a HEAD, sin el cambio previo fresh del usuario. La copia acumulada local `.local/terceros/AstralRPG-privado/build/entregas/party-17-11/acumulado/mazmorras/astral_mazmorras_copias.sk` conserva ese trabajo previo; SHA-256 `95127b8c71c9d9287d3d03270a00a5bc5c5cfd7bbff9606c59000f0bfd5f24fe`. Si Claude instala tambien la tanda anterior de Chaman/hitboxes, usar esta acumulada para copias en lugar de la de tarea. Comparar con el script instalado para no retroceder correcciones. Los otros cambios previos (datapack, MythicMobs, modelos y AstralDecor) permanecen fuera del commit de Party.

## FINAL y puesta en marcha

FINAL basado en `.local/terceros/AstralRPG-privado/build/entregas/menu-efectos-17-11/AstralRPG-Textures.zip`, SHA-1 `beb0d6d3b8fb1269e18d5910c0bc953518cc9abc`. Nuevo SHA-1 FINAL: `f676a363568343998f0badc4511e577312e9be65`. Solo cinco rutas propias: icono Party (PNG/modelo/item) y las dos partes del marco del menu. Todo el resto del FINAL se conserva byte por byte. El ZIP publico es de codigo/arte propio y NO se instala en R2.

1. Apagar el servidor: se agrega un plugin y cambia resource-pack-sha1. Conservar Java 25 y todos los mundos.
2. Subir los cinco archivos congelados de la tabla a sus destinos. TAB es un fragmento: combinar header-footer, scoreboard y las otras claves generadas con config.yml, conservando las entradas ajenas. Mantener Skript 2.17.1 y PlaceholderAPI 2.12.3 (versiones ensayadas). El menu principal ya esta registrado; no se registra un menu DeluxeMenus nuevo.
3. Publicar el FINAL: `python tools/subir_pack_r2.py ".local/terceros/AstralRPG-privado/build/entregas/party-17-11/AstralRPG-Textures.zip"`. Comprobar SHA-1 de la descarga publica; no se publico desde esta tarea.
4. En server.properties conservar resource-pack y poner `resource-pack-sha1=f676a363568343998f0badc4511e577312e9be65`. Iniciar de nuevo y revisar consola. El arranque carga scripts, expansion, TAB y menus.
5. Si se ajustan configs tras iniciar: `skript:skript reload astral_mazmorras_copias`, `skript:skript reload astral_infinita`, `astralpartyinternal sync`, `dm reload`, `tab reload`. No usar /reload ni PlugMan para el JAR; su cambio siempre requiere reinicio. No hacen falta mm reload, bettermodel reload ni cambiar el datapack por esta tarea.
6. Probar con dos clientes: /menu -> Party, invitar/aceptar, vida baja, TAB entre mundos; entrar juntos, caer en oleadas/jefe, cambiar camara con Shift, esperar 30/15 s, victoria con uno caido, derrota conjunta tres segundos, desconectar caido y volver. Revisar ausencia de errores/excepciones en consola.
Nunca sustituir mundos ni usar Worlds > Upload en la fila world.

## Verificacion

Paper 26.1.2 / Java 25: 54 comprobaciones aprobadas, Skript sin errores y sin excepciones del plugin. Incluye expansion real PAPI, sync real con Skript/mazentrar, dano real, muerte real, inventario, 30/15 s, derrota, camaras, confinamiento, desconexion/recuperacion y bloqueo de extraccion del menu. El reloj se adelanta en el ensayo para comprobar los bordes sin esperar todos los tiempos reales.
Ademas: seis tests de generacion, YAML, limite de lineas, metadata y delta del FINAL; auditoria de referencias de ambos packs y verificacion de bytes conservados. Las vistas party_menu_astral.png y party_interfaz_panel.png son renders locales/representativos, no capturas de un cliente.
Falta prueba visual con clientes y conjunto completo de plugins remoto (TAB, WorldGuard y MythicMobs). El ensayo NMS local no acredita ese despliegue ni la apariencia/teclas en cliente.

Reproducir: `python datapack-src/party.py --java <Java25/bin/java.exe> --server .local/testsrv --papi <PlaceholderAPI.jar>`; `python datapack-src/deploy_party.py`; `python -m unittest discover -s datapack-src -p test_party.py`; `python tools/probar_party_paper.py --java <Java25/bin/java.exe> --base .local/testsrv --papi <PlaceholderAPI.jar>`.
