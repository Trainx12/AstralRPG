# Tienda, nombres de NPC, alas y peluches

Generado por `datapack-src/deploy_tienda.py`. Preparado; no desplegado. El servidor activo figura como Empower en docs/SERVIDOR.md.

## Archivos exactos

| Local | Destino |
|---|---|
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/models/astral_npc_comerciante.bbmodel` | `plugins/BetterModel/models/astral_npc_comerciante.bbmodel` |
| `build/mythicmobs/skills/tanda3c.yml` | `plugins/MythicMobs/skills/tanda3c.yml` |
| `.local/terceros/AstralRPG-privado/build/entregas/tienda-modelo/mythicmobs/mobs/astral.yml` | `plugins/MythicMobs/mobs/astral.yml` |
| `.local/terceros/AstralRPG-privado/build/entregas/tienda-modelo/mythicmobs/skills/astral.yml` | `plugins/MythicMobs/skills/astral.yml` |

Pack FINAL: `.local/terceros/AstralRPG-privado/build/entregas/tienda-modelo/AstralRPG-Textures.zip` -> R2 con `python tools/subir_pack_r2.py .local/terceros/AstralRPG-privado/build/entregas/tienda-modelo/AstralRPG-Textures.zip`.
Actualizar `resource-pack-sha1=18107d6003a7f9f190d604e67a9cdf6b6096e02f` solo despues de verificar la descarga publica.
Base instalada `9c181ed2a097ea27021f761346714ca04416e24f`; 25 entradas cambiadas, ninguna eliminada; 5219 referencias verificadas.

El ZIP publico no contiene el arte privado. No instalarlo como FINAL. No subir DecorProbe.jar ni configuraciones del Paper local.

## Instalacion y reinicio

1. Avisar y esperar sin jugadores; respaldo de los seis archivos/properties que se reemplazan. Apagar el servidor.
2. Subir los archivos de la tabla. Conservar las configuraciones locales de plugins. AstralDecor genera su config nueva; si ya existe, integrar los mapas del config.yml incluido en el JAR.
3. Subir el FINAL a R2, verificar su descarga y actualizar server.properties. No cambiar mundos, regiones ni mapas.
4. Encender, esperar Done y BetterModel listo; revisar consola de MythicMobs, BetterModel y AstralDecor. No requiere recargas adicionales despues del arranque.
5. Comprobar el nombre visible sin apuntar, el clic en Tienda y los guardianes ocultos. Si se recargan YAML con el servidor encendido: `mm reload`; modelos: `bettermodel reload`. El JAR requiere reinicio, no /reload.

## Rehacer solo la Tienda si hace falta

La recuperacion de modelos no requiere volver a spawnear. Estas lineas son opcionales, solo si falta o debe rehacerse el NPC:

```text
rg flag -w lobby __global__ mob-spawning allow
mm mobs kill astral_npc_tienda
mm mobs spawn astral_npc_tienda 1 lobby,182.5,101,152.678,0,0
rg flag -w lobby __global__ mob-spawning deny
```

Si queda una entidad vanilla sin registrar, inspeccionar su UUID y usar `minecraft:kill <UUID>` solo sobre esa entidad. No matar todos los aldeanos ni borrar copias de Portales de otros mundos.

## Coordenadas elegidas el 11/11

| NPC | x y z | yaw |
|---|---|---|
| expediciones | 178.492 103 237.476 | 180.4 |
| minas | 146.511 102 237.506 | 270.1 |
| cronista | 189.454 102 218.495 | 90.7 |
| arena | 167.548 102 218.504 | -89.6 |
| portales | 211.434 105 237.492 | 90.0 |
| venta | 174.5 101 152.678 | 0 |
| bazar | 178.637 101 152.678 | -1.7 |
| herrero | 198.657 100 181.429 | 92.1 |
| subastas | 205.466 100 175.476 | 2.7 |
| viajero | 178.0 98 190.0 | 180 |
| tienda | 182.5 101 152.678 | 0 |

Los listados de lobby y tanda3c reflejan estas posiciones; no ejecutar todo comandos.txt para esta actualizacion.

## Alas y peluches

- Alas en segunda mano (F o inventario), con cualquier pechera. Sacarlas de esa mano las oculta. Sin proteccion ni vuelo; caen o se conservan segun las reglas de muerte/tumbas del servidor. El runtime nunca consume ni entrega copias. Los items viejos se actualizan a v15 al entrar.
- Display pasajero, offset local detras de hombros, rotacion del cuerpo e interpolacion de 2 ticks; baja al agacharse. El objeto no se dibuja en la mano; GUI y suelo conservan su vista.
- Peluches sobre superficies con colision (incluye losas y alfombras). Espacio libre de 0,9 bloques; mensajes al faltar apoyo, permiso, espacio o ante interaccion bloqueada. Conserva cancelaciones ajenas.
- Lobby: no permite colocar peluches, tampoco con OP o bypass. Mensaje: Aca no se pueden poner peluches. No otorgar permisos para decorar lobby. La recogida conserva la consulta de WorldGuard.
- WorldGuard y WorldEdit usados en la prueba local; Bolt, Essentials y AxGraves no estan cargados alli. Si otro plugin bloquea, revisar su permiso en remoto; no desactivar protecciones globalmente.

## Calidad y limites

- Cuatro vueltas renderizadas, con comparacion frontal, ambos tres cuartos, costado y espalda. Evidencia privada en `.local/tienda-review/vuelta1.png` a `vuelta4.png`.
- Vuelta 1: lentes muy altos, guantes como barra larga; se bajaron lentes, se achicaron y juntaron manos.
- Vuelta 2: bigote recto y nariz escondida, abrigo corto; se inclinaron mechones, se adelanto nariz y alargaron solapas/faldones.
- Vuelta 3: faltaban hebilla ancha, bajo del chaleco, cuello y detalle posterior; se agregaron.
- Vuelta 4: comprobados calva, patillas, lentes turquesa, bigote mas ancho que cabeza, abrigo rojizo con oro, chaleco verde, guantes juntos, botas oscuras e idle. Escala y pixelado usan el rig de los otros nueve NPC.
- Diferencias finales: antiparras simetricas, detalles del abrigo y bigote simplificados en bloques, hebilla octogonal; las manos se juntan segun el pedido. La referencia usa perspectiva y sombreado pintado diferentes; no es una copia pixel a pixel.
- `build/previews/npc-tienda-comparacion.png` contiene referencia y queda local. `npc-todos.png` solo incluye modelos propios.
- Render de alas Asura y Carnivora con pechera, frente/espalda/costado: `.local/terceros/AstralRPG-privado/build/entregas/tienda-modelo/previews/alas-pechera.png` (solo privado).
- Paper con jugador NMS simulado verifica estado, protecciones y reinicio; no certifica suavidad visual de caminar/correr/saltar ni el clic del menu con cliente real. Revisar esas acciones y las tumbas al desplegar. No hay captura de cliente ni despliegue remoto.

Reproduccion: generar datapack/lobby/MythicMobs y `python mobs/preview_tanda3c.py npc`; compilar build_runtime.py; ejecutar `tools/probar_decor_paper.py` con Java25/Paper local; `python datapack-src/deploy_tienda.py --assets <Paper>/plugins/BetterModel/build/assets`; luego `python build_pack.py pack-source` desde datapack-src.

## Verificacion local comprobada

- Suite completa: 214 pruebas aprobadas.
- Paper 26.1.2 / BetterModel 3.6.0 / MythicMobs 5.13.0 / WorldGuard 7.0.18: 230 comprobaciones, cero fallos, incluido reinicio.
- Recuperacion sin duplicados: Tienda, maquinas, Venta rapida, NPC de Expediciones, guardian oculto y guia de salida. Nombre/tracker acompanan /tp.
- Alas: pasajero unico, pechera simultanea, altura real 1,45 b, giro corporal y altura agachado 1,2 b.
- Peluches: clic nativo Paper, proteccion WG y bypass OP; piedra, losa y alfombra en supervivencia/creativo; una sola devolucion.
- Logs completos y referencias conservados solo en .local. Falta la revision visual con cliente real y el despliegue remoto.
