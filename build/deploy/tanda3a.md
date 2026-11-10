# Tanda 3a: Coloso, planta y cinco estatuas

**Estado: tanda 3a v2 preparada, publicacion en GitHub autorizada. No desplegado.** El dueno revisa las vistas antes de instalar en el servidor.

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

Pack: **17,552,861 bytes**, SHA-1 **`d05cab11deda98621c5d93b9d83bbfee10af20c6`**.
Assets reconvertidos con BetterModel 3.6.0; el pack incluye la geometria y texturas v2. No subir solamente los bbmodels conservando el pack v1.

Las estatuas usan los bbmodels existentes: `astral_cangrejo`, `astral_chaman`, `astral_momia`, `astral_yeti`, `astral_golem_forja`, todos a s=2.0. Conservar esos cinco en BetterModel.
**Datapack:** no cambia la logica respecto de f82a741. No requiere reemplazar `AstralRPG-Items.zip`.

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
| `astral_coloso_musgoso` | 2 | 6.580 × 5.756 × 2.520 | 2.13171 | 2.984 × 5.756 |
| `astral_bosque_planta` | 1 | 2.225 × 2.448 × 1.407 | 1.255412 | 0.753 × 2.448 |

## Revision visual y autoria

- Coloso: bajo y ancho, piernas cortas, cabeza hundida con mejillas labradas y nariz en bloque; dos marcos huecos, placa y gema vertical, un ojo turquesa y otro oscuro. Brazo derecho alto y doblado con raices gruesas; izquierdo colgante con tres bandas. Pecho con runas, cinturon, musgo irregular en hombros, cintura y piernas, flores de formas y tamanos variados. Idle, marcha pesada y martillazo derecho.
- Planta: base cuadrada verde con enredadera magenta y flores rosas; tallo grueso diagonal con nervaduras y espinas rosas. Boca mayor ladeada con cavidad roja, dientes y tiras verdes, dos capullos cubicos magenta en angulos distintos y tres hojas turquesa anchas. Balanceo, mordida y escupida.
- Estatuas: se reutiliza sin modificar cada modelo original del proyecto, con idle, sin IA, invulnerable, sin gravedad, colision, drops, BossBar ni habilidades de combate.
- Texturas propias: bordes oscuros, luces superiores, ruido por pixel y cara, grietas y nervaduras. Los parches y flores no se copian como stickers. Las referencias se usan solo para revision y cuentagotas; no se importaron sus texturas ni geometria.

### Tres vueltas de comparacion y comprobacion final

1. Render inicial contra la referencia: musgo demasiado fino y repetitivo, raices poco visibles, boca frontal y hojas superiores parejas. Correccion: cortina de anchos y largos variados con bordes escalonados, raices mas gruesas, mandibula inclinada y hoja derecha mas corta.
2. Segundo render: rostro demasiado plano y paleta sin muestreo documentado. Correccion: mejillas hundidas y bordes claros; cuentagotas local incorporado al musgo, raices, tallo, boca, capullos y hojas.
3. Tercer render: puño aun demasiado descubierto y hoja inferior larga. Correccion: raiz cruzando el puño y hoja inferior mas corta y ancha. Se renderizaron otra vez las cuatro vistas para comprobarlo.

Diferencias restantes de la ultima vuelta: las runas, grietas, espirales y recorridos de raices son disenos propios; la iluminacion ortografica local no reproduce el sol, perspectiva y shader de la foto. No se detectaron faltantes estructurales de la lista visual. Falta aprobacion visual del dueno y ver las animaciones desde un cliente Minecraft.

Muestreo sobre referencias locales (x,y; RGB): Coloso musgo (342,485) `#51561c`, raiz (413,81) `#5b4238`; planta tallo (194,429) `#978725`, oliva (327,282) `#4c501e`, rojo (291,345) `#af1f1f`, capullo (208,316) `#b43773`, hoja (199,199) `#377b7d`. Se combinan con los tonos y luces indicados en el plan.

Vistas: `build/previews/coloso-musgoso-comparacion.png`, `planta-carnivora-comparacion.png` (ambas solo locales e ignoradas: contienen la referencia de terceros); `build/previews/estatua-<jefe>-comparacion.png` y `build/previews/tanda3a.png` (modelos propios, jugador de 1,8 bloques al lado, escala comun).

Regenerar: `python mobs/build_models.py`, `python mobs/preview_tanda3a.py`, `python mobs/mythic.py`, `python mobs/mazmorra.py`; convertir con Paper + BetterModel, copiar assets propios a `pack-source/bettermodel/assets`, `python build_pack.py pack-source`, `python -m mobs.entrega_tanda3a` desde datapack-src.

## Verificacion y pendientes

Pasaron **159 pruebas** (`python -m unittest discover -p "test_*.py"`), incluidas las **6 pruebas** de `test_tanda3a` con la regresion adicional de dimensiones/animaciones v2, y `python verify.py`. Ademas, carga real en Paper 26.1.2 con BetterModel 3.6.0 (28 modelos) y MythicMobs 5.13.0 (114 mobs y 347 skills). Las escalas actualizadas se calculan de los modelos y figuran en la tabla anterior; vida del Coloso 72.000 con el tope de produccion. La planta conserva NoAI, NoGravity y velocidad 0. Validar en juego las mordidas/proyectiles con un jugador, dano por tier con el Skript de produccion, render y animaciones desde un cliente, y las oleadas completas. La instancia aislada no incluye todos los plugins de produccion; no es una prueba completa del servidor.

Pendientes: aprobacion visual, subida R2, instalacion en el servidor y comprobacion de consola/juego. No se reemplaza ningun mundo.
