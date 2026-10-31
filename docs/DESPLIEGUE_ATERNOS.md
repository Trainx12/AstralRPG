# Despliegue de pruebas en Aternos

Codigo y pack publicados en main: a00265d. Mapas de terceros y respaldos privados excluidos del repo.
Resource pack SHA1: 5d2e77ba1810393e27f94032bdfe43ec77217474.

Instalados: datapack, configuraciones MythicMobs de historia/diarias/mascotas/mazmorras y menu principal.
Mundos creados: bosque, tumba, cumbre, forja, santuario, arena. Regiones cargadas por Files con servidor apagado.
No se reemplazaron world, lobby ni mina. La Forja contiene solo el volcan sur.

Montaje ejecutado: plataformas iniciales de las copias nuevas, 13 controladores de salas, terraza de expediciones,
7 arcos tematicos y guardianes, arco de acceso junto al Viajero, puestos de bazar/subastas/herrero y Cronista.
Bazar, Subastas, Herrero y Viajero recreados para actualizar ubicaciones o interacciones.
PvP activo solo en arena; inventario conservado en nuevos mundos; reaparicion al lobby.
Chunks de montaje descargados en los mundos nuevos; zona del lobby permanece cargada para NPC/reloj.

Comprobado en Aternos: arranque completo, 105 mobs cargados, datapack habilitado, construcciones verificadas
por bloques, cada controlador y NPC confirmados por MythicMobs, reloj #today aq.clock positivo, 9 menus cargados.
No aparecieron errores de funciones ni configuracion AstralRPG durante el arranque y montaje.
Hay avisos previos de dos tiendas QuickShop sin inventario y dialogos de ejemplo de MythicMobs; no se borraron tiendas.

Pendiente de prueba real: aspecto del HUD, combates completos, transiciones entre salas, premios con economia real,
y muerte en arena con AxGraves. Las ubicaciones siguen siendo propuestas para revisar en Minecraft.
Guia y comandos: PROBAR_ATERNOS.md.

Respaldos privados: .local/backups/lobby-antes-ambientacion.zip y config-antes-despliegue.json.
Captura del servidor online: .local/backups/aternos-despliegue.jpg.

Reubicacion solicitada con capturas: Herrero lobby 198.657 100 181.429 (yaw 92.1);
Subastas lobby 205.466 100 175.476 (yaw 2.7). Teletransportados los NPC existentes y posiciones verificadas.

Borde del lobby ampliado de 190 a 360 bloques (centro existente 178,192) para incluir la galeria.
Holograma astral.amb.subastas movido a 205.5 104.3 183.2, sobre la entrada de la casa.

Holograma astral.amb.herrero movido a 196.5 104.3 181.5, sobre el frente del nuevo puesto elegido por el dueno.

Bazar reubicado a 178.637 101 152.678 (yaw -1.7); holograma a 178.637 105.5 154.8.
Subastas: holograma adelantado de Z=183.2 a Z=186.5 porque quedaba oculto por la fachada.
Hologramas Bazar y Subastas con see_through, brillo 15 y view_range 1.5 para legibilidad.

Viendo desde la plaza: Venta rapida izquierda (174.5,101,152.678), Bazar centro, Tienda derecha (182.5,101,152.678).
Tres hologramas alineados a Y=104.5, Z=161.5: Venta X=174.5, Bazar X=178.637, Tienda X=182.5.
Subastas atrasado exactamente 2 bloques hacia la casa: posicion final 205.5 104.3 184.5.

31/10: Viajero movido a lobby (178.0,98.0,190.0), yaw 180. Se verificaron los cuatro bloques
chiseled_stone_bricks en X=177/178, Z=189/190, Y=97 y la posicion exacta del NPC por NBT.
Minas conserva el acceso de la galeria (204.5,100,278.5), cartel (204.5,105.8,275.5).
Se retiro el aldeano duplicado de (171.5,100,224.5) y su cartel antiguo; save-all confirmado.
El generador de montaje inicial deja de crear ese segundo acceso; ese cambio de montaje queda
en el ZIP para futuras instalaciones y no requiere ejecutar de nuevo el montaje en este servidor.

Mascotas: instalados y releidos ambos mascotas.yml, recargado MythicMobs (105 mobs, 298 skills),
recreado solo astral_mascotas_control y recargado menu mascotas (DeluxeMenus: 9 menus).
Se quitaron el guardado automatico en lobby/arena y las restricciones de invocacion de esos mundos.
Todos los bonus, marca del Cuervo y rescate del Fenix verifican el mundo del dueno contra las seis mazmorras.
WorldGuard mob-spawning allow y spawn_mobs=false en lobby/arena, conservando las otras protecciones.
Prueba local Paper/MythicMobs: el mismo mecanismo world con lista separada por comas aplica Fuerza
cuando incluye world y no aplica efectos con la lista real de mazmorras desde world.
El seguimiento de mascotas entre mundos y el recorrido completo requieren prueba del jugador.

Fallo visual reportado en inventario: hacha al arrastrar y objetos cerca del cursor en shulker.
Revisado el pack: no contiene shaders ni reemplazos de modelos/texturas vanilla de herramientas.
Resaltados de casillas conservan medidas, alpha y metadatos de Minecraft 26.1.2.
Pendiente la prueba comparativa sin resource pack antes de atribuir una causa o publicar una correccion.
