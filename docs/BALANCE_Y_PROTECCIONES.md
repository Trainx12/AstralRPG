# Balance y protecciones de AstralRPG

Cambios solicitados el 01/11/2026. Generadores: items.py, build.py, gameplay.py,
cosmeticos.py, lobby.py y menus.py. No se hicieron commits ni push.

- Armaduras: Defensa 6/10/14/18/22. Durabilidad por tier de la pechera:
  2000/3000/4500/6500/9000; casco 80%, grebas 95%, botas 85%. Se pueden romper.
- Espadas y hachas de combate: Fighting. Bastones: Sorcery. Arcos: Archery.
- Version de objetos 4. La migracion modifica cada objeto en su slot, sin clear
  ni give, y conserva dano, adornos y encantamientos ajenos a los stats base,
  incluidas mejoras +N. Tambien actualiza piezas ya equipadas.
- Taladros/motosierras: Shift omite la rotura adicional. Mirando abajo/arriba
  se sigue la columna vertical; un taladro 3x3 excava dos bloques mas ademas
  del inicial. Se elimina Tunnel del taladro infernal para no superponer areas.
  Las funciones de rotura no se ejecutan en lobby, mazmorras ni mapas de busqueda.
- Recursos extra: se conserva la suerte de AuraSkills. Solo fuentes naturales
  explicitadas en mining.yml y foraging.yml; check_replace=true. No shulkers,
  beacons, cofres ni bloques de diamante/netherita u otros bloques de recursos.
- Tumbas: sin caducidad de tres minutos; guardan objetos hasta recuperarlos.
  Aviso con mundo y coordenadas. AxGraves no actua en mundos protegidos y no
  sobreescribe keep_inventory. Se usa prioridad LOW, que necesita reinicio.
- Seis mazmorras y lobby conservan inventario. Rotura y colocacion denegadas
  en las seis mazmorras, incluso para OP en supervivencia. Administradores
  creativos con astral.mazmorras.editar pueden mantener los mapas.
- Entrada con elitras, perlas, chorus y trampillas bloqueada, sin confiscar.
  Tambien se bloquearon, con aprobacion explicita del dueno: cargas de viento,
  Propulsion (se permiten los tridentes de combate sin ese encantamiento),
  cubos de agua, botes/vagonetas y monturas. Nadar devuelve al ultimo punto
  seco seguro de esa mazmorra; si no existe, al lobby. Equipar elitras dentro
  de una mazmorra devuelve al lobby conservando el objeto.
- Gancho: impulso real segun la mirada, minimo vertical 0.9, fuerza 1.25,
  enfriamiento 2 segundos, sin dano de caida durante ese lanzamiento.
- Segundo salto: soltar y volver a pulsar salto en el aire; solo una vez
  hasta aterrizar. Usa entrada de teclado de Paper, sin conceder vuelo.
  Gancho y doble salto estan desactivados dentro de las seis mazmorras por
  decision explicita del dueno. En mapas de busqueda y supervivencia funcionan.
- Titulos: premios de gacha dan permisos permanentes y no reemplazan el titulo
  activo. /cosmeticos, /titulos o el boton de /menu permiten elegir. /titulo
  <id> vuelve a comprobar la propiedad antes de equipar. /titulo quitar borra
  solo el prefijo de prioridad 100, no los titulos desbloqueados.
  El titulo de historia de prioridad 110 conserva su prioridad independiente.
  Se restituyeron a ByTrainx ASTRAL y Minero, segun su descripcion del problema.

47 pruebas locales pasaron y verify.py verifico JSON y referencias. Los
archivos de plugins se respaldaron en .local/backups antes de editarlos.
La comprobacion de sensacion de salto/gancho, muerte real de jugador y
teletransportes con inventario debe completarse en Minecraft; no se mato ni
se movio automaticamente a ningun jugador para probar.

## Rescate de caidas (02/11/2026, pendiente de instalar)

`gameplay.py` genera el rescate en `build/gameplay/astral_gameplay.sk`.
En supervivencia y aventura, guarda cada tick el ultimo punto con piso solido,
pies y cabeza libres, excluyendo magma, cactus y fogatas. Al caer bajo el limite
del mundo vuelve a ese punto y pone en cero velocidad y distancia de caida.
Valida otra vez el piso antes de regresar; sin punto valido usa `/spawn`.
Los puntos se descartan al cambiar de mundo o morir.

Limites Y absolutos configurables en las opciones `rescate-y-*` del generador:
lobby 60; mina -60 (sus salas estan bajo cero); bosque, tumba, cumbre, forja y
santuario 0. Creativo, espectador y mundos de exploracion quedan fuera.
Para instalar, reemplazar `plugins/Skript/scripts/astral_gameplay.sk` y ejecutar
`skript reload astral_gameplay`. Usar el nombre completo porque AuraSkills puede
capturar el alias `sk`. No requiere reemplazar el datapack.
Referencia de distancia de caida: [documentacion de Skript](https://docs.skriptlang.org/expressions/#ExprFallDistance).

Verificado en Paper 26.1.2 / Skript 2.17.1 local: recarga sin errores, ocho
pruebas Python y nueve comprobaciones con jugador de prueba (rescate automatico,
distancia de caida, piso, obstaculos, peligros, limites y cambio de mundo).
En la copia local se adapto el nombre del lobby a `world_minecraft_lobby`,
porque ese servidor carga los mundos desde dimensiones del datapack.

## Comprobacion en Aternos

Skript recargo astral_gameplay y astral_cosmeticos sin errores. DeluxeMenus
cargo 18 menus. AxGraves recargo correctamente; prioridad LOW se cargo en el
reinicio. Se aplicaron keep_inventory y las protecciones de WorldGuard.
Una prueba con un soporte de armadura temporal ejecuto la migracion real
upgrade/slot/armor_head: version 3 -> 4, Defensa 6, max_damage 1600. Se
conservaron dano 117, mejora_armadura 7, Thorns III y adorno oro/coast. Se
vaciaron sus slots, se elimino el soporte y se retiro la carga temporal.
El dueno abrio /cosmeticos y equipo titulos durante la comprobacion. No se
altero ni se teletransporto su inventario para hacer estas pruebas.
