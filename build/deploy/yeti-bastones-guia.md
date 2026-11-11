# Yeti, bastones, guias y peluches: entrega conjunta con Tienda

Generado por `datapack-src/deploy_yeti.py`. Incluye tienda-modelo de 2714f24. NO desplegado. Servidor activo documentado: Empower; Aternos es la copia antigua.

## Archivos exactos

| Local | Destino |
|---|---|
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/models/astral_npc_comerciante.bbmodel` | `plugins/BetterModel/models/astral_npc_comerciante.bbmodel` |
| `.local/terceros/AstralRPG-privado/build/entregas/yeti-bastones-guia/mythicmobs/mobs/astral.yml` | `plugins/MythicMobs/mobs/astral.yml` |
| `.local/terceros/AstralRPG-privado/build/entregas/yeti-bastones-guia/mythicmobs/skills/astral.yml` | `plugins/MythicMobs/skills/astral.yml` |
| `build/mythicmobs/skills/tanda3a.yml` | `plugins/MythicMobs/skills/tanda3a.yml` |
| `build/mythicmobs/skills/tanda3b.yml` | `plugins/MythicMobs/skills/tanda3b.yml` |
| `build/mythicmobs/skills/tanda3c.yml` | `plugins/MythicMobs/skills/tanda3c.yml` |
| `build/mythicmobs/skills/mazmorra.yml` | `plugins/MythicMobs/skills/mazmorra.yml` |
| `build/mythicmobs/skills/bosque.yml` | `plugins/MythicMobs/skills/bosque.yml` |
| `build/mythicmobs/skills/tumba.yml` | `plugins/MythicMobs/skills/tumba.yml` |
| `build/mythicmobs/skills/cumbre.yml` | `plugins/MythicMobs/skills/cumbre.yml` |
| `build/mythicmobs/skills/forja.yml` | `plugins/MythicMobs/skills/forja.yml` |

Pack FINAL conjunto: `.local/terceros/AstralRPG-privado/build/entregas/yeti-bastones-guia/AstralRPG-Textures.zip` (mismo contenido que Tienda, SHA-1 `18107d6003a7f9f190d604e67a9cdf6b6096e02f`). No usar el ZIP publico.
Comando para Claude: `python tools/subir_pack_r2.py .local/terceros/AstralRPG-privado/build/entregas/yeti-bastones-guia/AstralRPG-Textures.zip`. Verificar descarga publica antes de fijar `resource-pack-sha1=18107d6003a7f9f190d604e67a9cdf6b6096e02f`.

## Instalacion: un solo reinicio

1. Sala vacia, respaldar archivos de la tabla y server.properties. Apagar el servidor.
2. Reemplazar solo los archivos de la tabla. Conservar configs y mundos. Si AstralDecor/config.yml ya existe, integrar npc-models, npc-skills y hidden-npcs del config.yml incluido en el JAR (los mismos de Tienda).
3. Publicar el FINAL en R2 y verificar su SHA-1; actualizar server.properties. No subir plugins de prueba, logs ni mapas.
4. Encender y esperar Done, catalogo BetterModel y MythicMobs listos. Revisar consola de AstralDecor, datapack y ambos plugins. El JAR requiere reinicio; no usar /reload.
5. No cambian controladores ni sus posiciones: no recrearlos. Dejar vacias las salas para que su RESET quite cofres/guias anteriores; la siguiente victoria genera los nuevos. Si la sala ya estaba finalizada, vaciarla y comprobar RESET antes de entrar.
6. El arranque carga todo. Solo para ajustes posteriores: `mm reload` (YAML), `bettermodel reload` (modelos); datapack con servidor apagado y reinicio. No ejecutar listados completos de lobby ni comandos de pegado de mapas.
Nunca sustituir mundos ni usar Worlds > Upload en world. No instalar configuraciones completas del Paper local.

## Guias

| Mazmorra | Cofre x y z | Guia x y z |
|---|---|---|
| mina (mina) | (36.5, 24, -248.5) | (38.5, 24, -248.5) |
| bosque (bosque) | (1604.5, 101, 1382.5) | (1606.5, 101, 1382.5) |
| tumba (tumba) | (0.5, 72, 0.5) | (2.5, 72, 0.5) |
| cumbre (cumbre_hielo) | (-101.8, 30, 56.9) | (-99.8, 30, 56.9) |
| forja (forja_volcano) | (-7.9, 47, -21.1) | (-5.9, 47, -21.1) |

Cinco pisos naturales comprobados en las regiones locales: distancia 2 b, tres bloques libres. Sin bloques de apoyo. Mago de Tanda3c, nombre visible, mismo menu Expediciones, mira al jugador cercano. LIMPIA elimina copias y RESET retira cofre/guia. Santuario permanece en espera.

## Modelos y caja de combate

Yeti Ancestral: 7 b; Cumbre: 10 b (Ancestral +3), s=20/7. El arte y las animaciones se conservan.
Se evaluaron las subcajas b_/ob_ de BetterModel: https://github.com/toxicity188/BetterModel/wiki/Configuring-custom-hitbox . Se elige ampliar la entidad base para compartir la caja entre melee, flechas y selector vanilla del baston sin entidades intermediarias ni cambiar assets.
Caja vanilla cuadrada conservadora: cubre todos los vertices de reposo para cualquier yaw. El radio incluye profundidad y brazos; al escalar uniformemente puede sobrar altura. No es una caja por hueso ni una malla exacta de las animaciones.

Volumen de aparicion revisado en las cinco regiones locales: Mina, Bosque, Cumbre y Forja sin bloques dentro de la caja; Tumba contiene solo un bloque minecraft:light en 0 79 0 (sin colision). No se modifico el terreno.

Se reemplazo la condicion execute unless dimension por astral:in_sanctuary: la anterior no aplicaba atributos si faltaba alguno de los dos mundos en el registro. El predicado conserva la exclusion de Santuario sin exigir cargarlo.

| Mob | Modelo ancho/alto/profundidad b | scale | Caja ancho/alto b |
|---|---|---|---|
| astral_mapache | 0.762 / 1.006 / 2.353 | 4.785638 | 2.871 / 3.350 |
| astral_pinguino | 0.950 / 1.556 / 0.831 | 3.676361 | 1.471 / 2.573 |
| astral_espantapajaros | 1.562 / 2.062 / 1.006 | 4.723818 | 1.890 / 3.779 |
| astral_espantapajaros_elite | 2.109 / 2.784 / 1.358 | 6.377154 | 2.551 / 5.102 |
| astral_abejorro | 1.805 / 1.038 / 1.863 | 7.457113 | 2.983 / 5.966 |
| astral_abejorro_elite | 2.436 / 1.401 / 2.514 | 10.067102 | 4.027 / 8.054 |
| astral_arana | 1.700 / 0.975 / 1.256 | 1.539551 | 2.155 / 1.386 |
| astral_arana_elite | 2.295 / 1.316 / 1.696 | 2.078394 | 2.910 / 1.871 |
| astral_cara | 1.400 / 1.675 / 0.969 | 3.725 | 3.353 / 1.863 |
| astral_cara_elite | 1.890 / 2.261 / 1.308 | 5.028751 | 4.526 / 2.514 |
| astral_momia | 2.188 / 4.100 / 2.250 | 6.564451 | 3.939 / 12.801 |
| astral_momia_ancestral | 2.188 / 4.100 / 2.250 | 6.564451 | 3.939 / 12.801 |
| astral_yeti | 6.300 / 7.000 / 4.463 | 4.339701 | 8.462 / 9.547 |
| astral_yeti_ancestral | 6.300 / 7.000 / 4.463 | 4.339701 | 8.462 / 9.547 |
| astral_golem_forja | 3.225 / 6.899 / 3.550 | 3.43786 | 4.813 / 9.282 |
| astral_golem_forja_ancestral | 3.225 / 6.899 / 3.550 | 3.43786 | 4.813 / 9.282 |
| astral_cangrejo | 2.800 / 2.825 / 3.450 | 3.903165 | 5.464 / 3.513 |
| astral_cangrejo_elite | 1.890 / 1.907 / 2.329 | 2.634637 | 3.688 / 2.371 |
| astral_cangrejo_ancestral | 2.800 / 2.825 / 3.450 | 3.903165 | 5.464 / 3.513 |
| astral_chaman | 2.862 / 5.437 / 2.890 | 8.087792 | 4.853 / 15.771 |
| astral_chaman_ancestral | 2.862 / 5.437 / 2.890 | 8.087792 | 4.853 / 15.771 |
| astral_yeti_cumbre | 9.000 / 10.000 / 6.375 | 6.199573 | 12.089 / 13.639 |
| astral_golem_forja_mazmorra | 12.900 / 27.597 / 14.200 | 13.751438 | 19.252 / 37.129 |
| astral_mina_guardian | 6.580 / 5.756 / 2.520 | 5.299882 | 7.420 / 14.310 |
| astral_bosque_planta | 2.225 / 2.448 / 1.407 | 5.378173 | 3.227 / 10.487 |

Bastones: spell/ray intersecta la AABB completa con dx/dy/dz en pasos de .5 b; tolerancia .5 b. Mantiene filtro de NPC NoAI, bloqueo por paredes, alcance y un solo impacto.

## Peluches y pendientes visuales

Los seis usan NONE, escala maxima .8 b, base alineada a la superficie y caja Interaction por altura. El frente apunta al colocador. Los antiguos se migran una sola vez al habilitar el plugin o cargar el chunk; conservan UUID, item guardado y cantidad. No hace falta recogerlos ni ejecutar un comando.
Lobby bloqueado para todos, incluso OP/bypass: Aca no se pueden poner peluches. No otorgar worldguard.region.bypass.lobby para esta tarea. Recoger sigue respetando WorldGuard.
Vista CPU propia: build/previews/yeti-tamano.png. No equivale a una captura de Minecraft. Capturas de cliente de los seis peluches de frente/costado y prueba visual remota siguen pendientes; no hay cliente grafico usado en esta entrega.
Vista CPU privada de los seis peluches, frente/costado: `.local/terceros/AstralRPG-privado/build/entregas/yeti-bastones-guia/previews/peluches-derechos-CPU.png`. Pez tropical: rotacion X=-90 adicional porque el original esta acostado. No publicar esta vista en GitHub.
Las pruebas Paper con jugador simulado verifican estado, selectores y ray tracing; no sustituyen swings de cliente, vuelos reales de flecha ni consola remota. Resultados locales comprobados al final.

## Verificaciones locales

- Suite Python: 214 pruebas aprobadas. Incluye piso natural de guias, cajas a 72 orientaciones por mob y vertices transformados de los seis peluches.
- Paper 26.1.2 / BetterModel 3.6.0 / MythicMobs 5.13.0 / WorldGuard: 230 comprobaciones aprobadas, incluido reinicio.
- Bastones: pies/centro/cabeza visibles, a 1.5 y 18 b del borde de la caja; zombi, esqueleto 3D, Cumbre, pez, aranita, Momia, Golem, Coloso y Ancestral. Ray tracing Paper horizontal sobre esas alturas; no son disparos reales de flecha.
- Peluches: seis transformaciones, frente al colocador, alturas por modelo, lobby OP bloqueado sin consumir y seis antiguos migrados tras reiniciar sin perderlos.
- Logs solo en .local. Falta revision con cliente y despliegue remoto.
