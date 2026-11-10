# Tanda 3a: Coloso, planta y cinco estatuas

**Estado: preparacion local. No desplegado.** Aprobar las vistas antes de publicar/subir.

## Archivos y destinos exactos

| Archivo local | Destino en el servidor |
|---|---|
| `build/models/astral_coloso_musgoso.bbmodel` | `plugins/BetterModel/models/astral_coloso_musgoso.bbmodel` |
| `build/models/astral_bosque_planta.bbmodel` | `plugins/BetterModel/models/astral_bosque_planta.bbmodel` |
| `build/mythicmobs/mobs/mazmorra.yml` | `plugins/MythicMobs/mobs/mazmorra.yml` |
| `build/mythicmobs/skills/mazmorra.yml` | `plugins/MythicMobs/skills/mazmorra.yml` |
| `build/mythicmobs/skills/bosque.yml` | `plugins/MythicMobs/skills/bosque.yml` |
| `build/mythicmobs/mobs/tanda3a.yml` | `plugins/MythicMobs/mobs/tanda3a.yml` |
| `build/mythicmobs/skills/tanda3a.yml` | `plugins/MythicMobs/skills/tanda3a.yml` |
| `build/AstralRPG-Textures.zip` | R2, objeto `AstralRPG-Textures.zip` |

Pack: **17,524,400 bytes**, SHA-1 **`0f83316b419912602abb0b03a033b29a80766cf0`**.
Comparado con HEAD inicial: +33 archivos, ninguno quitado ni modificado; +77.852 bytes.

Las estatuas usan los bbmodels existentes: `astral_cangrejo`, `astral_chaman`, `astral_momia`, `astral_yeti`, `astral_golem_forja`, todos a s=2.0. Conservar esos cinco en BetterModel.
**Datapack:** se regenero y se compararon todas las entradas del ZIP con HEAD: contenido identico. No requiere reemplazar `AstralRPG-Items.zip`.

## Instalacion por Claude, tras la aprobacion visual

1. Usar el servidor vigente de docs/SERVIDOR.md (Empower; Aternos es copia). Respaldar los archivos a reemplazar.
2. Sin jugadores en las salas de Minas/Bosque, apagar el servidor. Subir los dos bbmodels y los cinco YAML de la tabla.
3. Ejecutar `python tools/subir_pack_r2.py build/AstralRPG-Textures.zip`. Verificar descarga publica y SHA-1. Poner la URL fija de R2 y el SHA-1 de arriba en `server.properties`.
4. Verificar `spigot.yml` → `settings.attribute.maxHealth.max: 1000000000.0` (ya informado en produccion). Sin este tope el jefe queda limitado a 1.024.
5. Iniciar. El reinicio carga modelos, pack y YAML; no hacen falta recargas adicionales. Si se prueba por recargas antes del reinicio: `bettermodel reload`, despues `mm reload`; el cambio de pack/propiedades requiere reiniciar.
6. Revisar consola: modelos nuevos cargados, sin errores de Molang ni skills desconocidas. Reconectar un cliente, aceptar el pack y probar ambos modelos.

## Controladores y entidades

Recrear el controlador de oleadas del Bosque para eliminar el estado de oleadas anterior. Hacerlo con la sala vacia; si quedaran plantas de una prueba previa, retirarlas primero:

```text
mm mobs kill astral_bosque_planta
mm mobs kill astral_bosque_control_sala1
execute in minecraft:bosque run kill @e[tag=ad.bosque.sala1]
data remove storage astral:tanda2/bosque/sala1 queue
mm mobs spawn astral_bosque_control_sala1 1 bosque,1468.5,101,1570.5
```

No recrear controladores de Santuario. El controlador de Minas no cambia: el proximo `astral_mina_guardian` usa el Coloso. Para una instancia anterior: terminar/resetear esa sala vacia y verificar el proximo jefe. No usar `mm mobs kill` sobre un jefe en combate ni conceder premios por borrarlo.

Estatuas: solo definidas, **ninguna colocada**. Comandos manuales en docs/MAZMORRAS.md.

## Planta: cantidades y posiciones

Oleada 1: ninguna. Oleada 2: dos. Oleada 3: tres. Son adicionales a la composicion vanilla, pero comparten su tope de seis vivos. La skill las invoca antes de armar la cola; sus tags de sala bloquean el avance hasta morir y permiten borrarlas en RESET. Los refuerzos por jugadores extra siguen siendo vanilla; no multiplican las plantas fijas.

| Oleada | Puntos (x, y, z) |
|---|---|
| 2 | (1448.5, 102, 1564.5); (1478.5, 102, 1561.5) |
| 3 | (1448.5, 102, 1564.5); (1478.5, 102, 1561.5); (1457.5, 97, 1579.5) |

## Geometria e hitbox

Minecraft escala uniformemente la caja vanilla: se iguala el alto, siguiendo la seccion 6 del plan. El ancho no puede coincidir simultaneamente con una silueta asimetrica usando solo `minecraft:scale`.

| Modelo | s | Modelo ancho × alto × fondo (bloques) | Scale | Caja vanilla ancho × alto |
|---|---:|---|---:|---|
| `astral_coloso_musgoso` | 2 | 4.950 × 6.000 × 2.013 | 2.222222 | 3.111 × 6.000 |
| `astral_bosque_planta` | 1 | 1.346 × 1.792 × 0.831 | 0.918889 | 0.551 × 1.792 |

## Revision visual y autoria

- Coloso: bloques claros con juntas originales y marcos labrados; torso ancho y pies cuadrados; corona asimetrica abierta y gema vertical turquesa, un ojo turquesa con brillo claro; musgo en hombros, pecho y cintura, raices marrones colgantes y enroscadas en brazo levantado, cuatro flores amarillas frontales y una en cada brazo. Animaciones idle, walk y golpe de ambos brazos.
- Planta: base de cuatro raices con flores rosas, tallo oliva escalonado inclinado, boca verde con mandibula abierta, dientes intercalados, cavidad y lengua rojas, tres capullos magenta con espirales originales en relieve y cuatro hojas turquesa con nervaduras. Balanceo, mordida y escupida.
- Estatuas: se reutiliza sin modificar cada modelo original del proyecto, con idle, sin IA, invulnerable, sin gravedad, colision, drops, BossBar ni habilidades de combate.
- No se importaron texturas ni geometria de las referencias. Se compararon frente, costado y 3/4. La planta tiene una disposicion mas simetrica que la referencia; el Coloso tiene relieves propios. La aprobacion de parecido corresponde al dueno.

Vistas: `build/previews/coloso-musgoso-comparacion.png`, `planta-carnivora-comparacion.png` (ambas solo locales e ignoradas: contienen la referencia de terceros); `build/previews/estatua-<jefe>-comparacion.png` y `build/previews/tanda3a.png` (modelos propios, jugador de 1,8 bloques al lado, escala comun).

Regenerar: `python mobs/build_models.py`, `python mobs/preview_tanda3a.py`, `python mobs/mythic.py`, `python mobs/mazmorra.py`; convertir con Paper + BetterModel, copiar assets propios a `pack-source/bettermodel/assets`, `python build_pack.py pack-source`, `python -m mobs.entrega_tanda3a` desde datapack-src.

## Verificacion y pendientes

Pasaron **158 pruebas** (`python -m unittest discover -p "test_*.py"`) y `python verify.py`. Ademas, carga real en Paper 26.1.2 con BetterModel 3.6.0 (28 modelos) y MythicMobs 5.13.0 (114 mobs y 347 skills). Escala real comprobada por consola: planta 0.918889, Coloso 2.222222; vida del Coloso 72.000 con el tope de produccion. La planta conserva NoAI, NoGravity y velocidad 0. Validar en juego las mordidas/proyectiles con un jugador, dano por tier con el Skript de produccion, render y animaciones desde un cliente, y las oleadas completas. La consola local sin ExcellentEnchants informa errores de recetas ajenas a esta tanda; no es una prueba completa del servidor.

Pendientes: aprobacion visual, publicacion segun aprobacion y acceso de red, subida R2, instalacion en el servidor y comprobacion de consola/juego. No se reemplaza ningun mundo.
