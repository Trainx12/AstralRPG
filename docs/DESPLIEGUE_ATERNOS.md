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
