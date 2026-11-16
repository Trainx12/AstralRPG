# Balance de especiales y agua — 16/11/2026

Implementacion local posterior a la tanda XP/cuchillo. Sin acceso remoto ni subida a R2. Empower es el principal segun docs/SERVIDOR.md; Aternos queda como copia. Confirmar panel/version instalada.

## Daño real sin mejoras

| Item | Tier | Antes → ahora |
|---|---:|---:|
| `espada_destello` | 2 | 2.000 → 500 |
| `espada_tormenta` | 3 | 2571,43 → 2.500 |
| `espada_sombras` | 4 | 2857,14 → 12.500 |
| `hacha_terremoto` | 3 | 3142,86 → 3.600 |
| `varita_estallido` | 4 | 1714,29 → 18.750 |
| `varita_curacion` | 3 | 285,71 → 285,71 |
| `asura_espada` | 4 | 12.500 → 13.750 |
| `lanza_1` | 1 | 60,61 → 90 |
| `lanza_2` | 2 | 353,1 → 450 |
| `lanza_3` | 3 | 2000 → 2.250 |
| `lanza_4` | 4 | 10582,01 → 11.250 |
| `lanza_5` | 5 | 57291,66 → 56.250 |
| `lanza_6` | 6 | 292968,74 → 281.250 |
| `lanza_7` | 7 | 1493566,18 → 1.406.250 |
| `lanza_8` | 8 | 7595486,11 → 7.031.250 |
| `lanza_9` | 9 | 38548519,74 → 35.156.250 |
| `lanza_10` | 10 | 207519531,25 → 175.781.250 |

Lanzas: 90% de la espada de su tier, ataque 1,1 y alcance/estocada vanilla. La columna anterior estima el golpe directo normal sin carga ni efectos; el daño de embestida depende de velocidad. Empalar/Poder Astral se retiran del equipo nuevo para evitar multiplicarlo dos veces. Los encantamientos se conservan al migrar; Empalar/Poder Astral antiguos dejan de multiplicar al detectar spear_balance:1.

## Habilidades y fichas

Sismo causa x2 el atributo de ataque actual y el factor real de mejora +N del Herrero; radio 5, maná 100, recarga 6 s. Danza usa el daño T4; Estallido el daño del bastón T4 (18.750). Varita de Curación conserva su balance. Se interpretó “el bastón” como Varita del Estallido; no hay confirmación del dueño de otra identidad.
Asura: daño base +10% respecto de Espada del Coloso T4; cada cuarto golpe directo al mismo enemigo en una ventana de 5 s causa +50% y cura 5% de vida máxima. Cambiar de objetivo corta la secuencia. Carnívora: +5% de defensa por pieza respecto de T3 neutro (redondeo por pieza); 4/4 cura 3% de vida máxima al matar un mob.
Talismanes: Vida, Furia, Viento y Roca I/II/III dan 5/10/20%. No existen niveles T6–T10. Roca aplica además su porcentaje a la Defensa Astral calculada por el datapack.
Espada de las Mareas: proyectil de 3186, maná 90, recarga 1.1 s. Hacha: +25% en golpes directos bajo el agua. Arco: conserva flechas vanilla y compensa el rozamiento acuático al del aire. Pico: atributo +0,8 sobre base 0,2 = 1,0, sin penalidad acuática. Set: aire ilimitado, eficiencia acuática 1, nado horizontal sostenido x1,5 calibrado con travelInWater de Paper; no se cambia Gracia del Delfín. Visión sin partículas ni icono solo con 4/4 sumergido; se retira al salir o desequipar; respeta efectos ajenos.
Casco: cuerpo cerrado azul oscuro y aletas desde los píxeles del icono; no usa la cabeza/orejas del mod. Vista local frente/costado: `build/Servicios-preview/casco_agua.png` (derivado privado, EXCLUIDO del commit). El resto del set se conserva. Se incluyen tambien los recursos propios del menu Efectos/Bosque ya publicados en a2bfd72; las demas entradas previas se verifican byte por byte.

## Durabilidad

Causa: desgaste vanilla max(1, daño/4) por pieza; el daño escalado lo hace enorme. AstralDecor limita cada evento de desgaste positivo a 1. Se elimina el desgaste probabilístico anterior. Armaduras: al menos 2.401 puntos por pieza; se conservan los máximos mayores T1–T10. Oficios/Agua/Carnívora reciben el mismo mínimo. Armas y utilidades con durabilidad: mínimo 7.201 (salvo indestructibles previas). Presupuesto conservador: 200 golpes recibidos por mazmorra ×12=2.400; armas 600 usos ×12=7.200. Es una estimación para todas las copias/Bosque–Santuario/Infinita, no un conteo de partidas humanas ni garantía para Infinita sin límite.
ITEM_VERSION 23 usa la migración por slot existente al entrar/equipar/inventario: actualiza max_damage, atributos y ficha, conservando desgaste, encantamientos, mejoras +N y demás componentes.

## Archivos y despliegue

| Local | Destino remoto |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` |
| `build/oceano/AstralOceano.jar` | `plugins/AstralOceano.jar` |
| `build/gameplay/astral_armas_especiales.sk` | `plugins/Skript/scripts/special_weapons.sk` (reemplazar, sin duplicado) |
| `build/mazmorras/astral_mazmorras_copias.sk` (si falta tanda previa) | `plugins/Skript/scripts/astral_mazmorras_copias.sk` |
| `build/infinita/astral_infinita.sk` (si falta tanda previa) | `plugins/Skript/scripts/astral_infinita.sk` |
| `build/rankings/astral_rankings.sk` (si falta tanda previa) | `plugins/Skript/scripts/astral_rankings.sk` |

FINAL privado nuevo: `.local/terceros/AstralRPG-privado/build/entregas/balance-especiales-agua/AstralRPG-Textures.zip`; SHA-1 **`99ca716f64a5be9dfa18fb05ab192814c6a4663a`**. Base preservada `build/entregas/tanda-xp-cuchillo/AstralRPG-Textures.zip` (posterior al pack tiers 6–10), mas `build/disenos-menu/recursos-menu.zip` de a2bfd72. No instalar el ZIP público.
Apagar antes de reemplazar JAR y datapack. No subir config.yml de AstralOceano: contiene la fecha de regeneración y ajustes existentes. Los números de combate van dentro del JAR. Subir el FINAL a R2 con `python tools/subir_pack_r2.py ".local/terceros/AstralRPG-privado/build/entregas/balance-especiales-agua/AstralRPG-Textures.zip"`; verificar descarga pública y recién entonces actualizar `resource-pack-sha1` en server.properties. Conservar URL fija. Iniciar Java 25; reinicio completo obligatorio. No sustituir mundos ni usar Worlds > Upload en world.
Si solo cambia un Skript: `skript:skript reload special_weapons`, `skript:skript reload astral_mazmorras_copias`, `skript:skript reload astral_infinita`, `skript:skript reload astral_rankings`. El reinicio ya los carga. MythicMobs no cambia en esta tarea; si se instala la tanda previa: `mm reload` y revisar consola.
Carteles: defaults y comando por mundo ya corregidos en la tanda previa; actualizaciones de Infinita/Trainx siguen activas. Borrar solo los dos del lobby desde consola:
```text
execute in minecraft:lobby run minecraft:kill @e[type=minecraft:text_display,tag=astral_rank_infinita,x=180.5,y=101.5,z=182.5,distance=..3]
execute in minecraft:lobby run minecraft:kill @e[type=minecraft:text_display,tag=astral_rank_trainx,x=186.5,y=101.5,z=182.5,distance=..3]
```
Limpieza: copias e Infinita conservan lo ya implementado; Fosa ahora elimina items/flechas/tridentes cuando queda vacía. No borra displays ni cofres de recompensa mientras hay jugadores.

## Verificaciones y pendientes

Suite completa: 300 pruebas, mas contrato final de movilidad. Ensayo Paper: nado horizontal medido 1,49999999x / 1,50000050x; 200 golpes reales T5 con set T5 consumen 200 de durabilidad; visión propia/ajena y proyectil 3.186 verificados. Skript y MythicMobs cargan; revisar el resultado final del ensayo y auditoría en el resumen de entrega. El ensayo de limpieza ejecuta los comandos por dimensión; no simula una partida completa con party. La prueba de daño usa un jugador NMS sin cliente y un mob T5. No se verificó instalación remota. Falta validación visual con cliente real del casco, proyectil, nado con obstáculos/corrientes y sensaciones de combate. Revisar consola al instalar: sin errores de funciones, loot, modificadores ni Skript.

## Equipo con ficha (270)

`agua_arco`, `agua_boots`, `agua_chestplate`, `agua_espada`, `agua_hacha`, `agua_helmet`, `agua_leggings`, `agua_pico`, `arco_1`, `arco_10`, `arco_2`, `arco_3`, `arco_4`, `arco_5`, `arco_6`, `arco_7`, `arco_8`, `arco_9`, `arquero_10_boots`, `arquero_10_chestplate`, `arquero_10_helmet`, `arquero_10_leggings`, `arquero_1_boots`, `arquero_1_chestplate`, `arquero_1_helmet`, `arquero_1_leggings`, `arquero_2_boots`, `arquero_2_chestplate`, `arquero_2_helmet`, `arquero_2_leggings`, `arquero_3_boots`, `arquero_3_chestplate`, `arquero_3_helmet`, `arquero_3_leggings`, `arquero_4_boots`, `arquero_4_chestplate`, `arquero_4_helmet`, `arquero_4_leggings`, `arquero_5_boots`, `arquero_5_chestplate`, `arquero_5_helmet`, `arquero_5_leggings`, `arquero_6_boots`, `arquero_6_chestplate`, `arquero_6_helmet`, `arquero_6_leggings`, `arquero_7_boots`, `arquero_7_chestplate`, `arquero_7_helmet`, `arquero_7_leggings`, `arquero_8_boots`, `arquero_8_chestplate`, `arquero_8_helmet`, `arquero_8_leggings`, `arquero_9_boots`, `arquero_9_chestplate`, `arquero_9_helmet`, `arquero_9_leggings`, `asura_espada`, `ballesta_1`, `ballesta_10`, `ballesta_2`, `ballesta_3`, `ballesta_4`, `ballesta_5`, `ballesta_6`, `ballesta_7`, `ballesta_8`, `ballesta_9`, `baston_1`, `baston_10`, `baston_2`, `baston_3`, `baston_4`, `baston_5`, `baston_6`, `baston_7`, `baston_8`, `baston_9`, `berserker_10_boots`, `berserker_10_chestplate`, `berserker_10_helmet`, `berserker_10_leggings`, `berserker_1_boots`, `berserker_1_chestplate`, `berserker_1_helmet`, `berserker_1_leggings`, `berserker_2_boots`, `berserker_2_chestplate`, `berserker_2_helmet`, `berserker_2_leggings`, `berserker_3_boots`, `berserker_3_chestplate`, `berserker_3_helmet`, `berserker_3_leggings`, `berserker_4_boots`, `berserker_4_chestplate`, `berserker_4_helmet`, `berserker_4_leggings`, `berserker_5_boots`, `berserker_5_chestplate`, `berserker_5_helmet`, `berserker_5_leggings`, `berserker_6_boots`, `berserker_6_chestplate`, `berserker_6_helmet`, `berserker_6_leggings`, `berserker_7_boots`, `berserker_7_chestplate`, `berserker_7_helmet`, `berserker_7_leggings`, `berserker_8_boots`, `berserker_8_chestplate`, `berserker_8_helmet`, `berserker_8_leggings`, `berserker_9_boots`, `berserker_9_chestplate`, `berserker_9_helmet`, `berserker_9_leggings`, `carnivora_arco`, `carnivora_azada`, `carnivora_baston`, `carnivora_boots`, `carnivora_cana`, `carnivora_chestplate`, `carnivora_escudo`, `carnivora_espada`, `carnivora_guadana`, `carnivora_hacha`, `carnivora_helmet`, `carnivora_lanza`, `carnivora_leggings`, `carnivora_martillo`, `carnivora_pala`, `carnivora_pico`, `cuchillo_1`, `cuchillo_10`, `cuchillo_2`, `cuchillo_3`, `cuchillo_4`, `cuchillo_5`, `cuchillo_6`, `cuchillo_7`, `cuchillo_8`, `cuchillo_9`, `espada_1`, `espada_10`, `espada_2`, `espada_3`, `espada_4`, `espada_5`, `espada_6`, `espada_7`, `espada_8`, `espada_9`, `espada_destello`, `espada_heroe_errante`, `espada_sombras`, `espada_tormenta`, `gancho`, `gancho_realista`, `guadana_1`, `guadana_10`, `guadana_2`, `guadana_3`, `guadana_4`, `guadana_5`, `guadana_6`, `guadana_7`, `guadana_8`, `guadana_9`, `guadana_umbria`, `guantes_meteoro`, `hacha_1`, `hacha_10`, `hacha_2`, `hacha_3`, `hacha_4`, `hacha_5`, `hacha_6`, `hacha_7`, `hacha_8`, `hacha_9`, `hacha_terremoto`, `lanza_1`, `lanza_10`, `lanza_2`, `lanza_3`, `lanza_4`, `lanza_5`, `lanza_6`, `lanza_7`, `lanza_8`, `lanza_9`, `mago_10_boots`, `mago_10_chestplate`, `mago_10_helmet`, `mago_10_leggings`, `mago_1_boots`, `mago_1_chestplate`, `mago_1_helmet`, `mago_1_leggings`, `mago_2_boots`, `mago_2_chestplate`, `mago_2_helmet`, `mago_2_leggings`, `mago_3_boots`, `mago_3_chestplate`, `mago_3_helmet`, `mago_3_leggings`, `mago_4_boots`, `mago_4_chestplate`, `mago_4_helmet`, `mago_4_leggings`, `mago_5_boots`, `mago_5_chestplate`, `mago_5_helmet`, `mago_5_leggings`, `mago_6_boots`, `mago_6_chestplate`, `mago_6_helmet`, `mago_6_leggings`, `mago_7_boots`, `mago_7_chestplate`, `mago_7_helmet`, `mago_7_leggings`, `mago_8_boots`, `mago_8_chestplate`, `mago_8_helmet`, `mago_8_leggings`, `mago_9_boots`, `mago_9_chestplate`, `mago_9_helmet`, `mago_9_leggings`, `minero_boots`, `minero_chestplate`, `minero_helmet`, `minero_leggings`, `motosierra_astral`, `motosierra_avanzada`, `motosierra_basica`, `motosierra_industrial`, `motosierra_infernal`, `talador_boots`, `talador_chestplate`, `talador_helmet`, `talador_leggings`, `taladro_amatista`, `taladro_diamante`, `taladro_divan`, `taladro_gemas`, `taladro_jaspe`, `taladro_mitril`, `taladro_rubi`, `taladro_titanio`, `taladro_topacio`, `talisman_furia_1`, `talisman_furia_2`, `talisman_furia_3`, `talisman_roca_1`, `talisman_roca_2`, `talisman_roca_3`, `talisman_vida_1`, `talisman_vida_2`, `talisman_vida_3`, `talisman_viento_1`, `talisman_viento_2`, `talisman_viento_3`, `varita_curacion`, `varita_estallido`
