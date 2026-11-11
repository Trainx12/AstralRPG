# Correccion de escala de mobs 3D

Generado por `datapack-src/deploy_esqueletos.py`. Despliegue remoto pendiente.
Sustituye las escalas y cajas ensanchadas de d51e4de y la indicacion s=20/7 de la entrega anterior. Cumbre usa s=2.0, igual al Ancestral.

## Archivos a instalar

| Local | Destino |
|---|---|
| `.local/terceros/AstralRPG-privado/build/entregas/esqueletos-tamano/mythicmobs/skills/astral.yml` | `plugins/MythicMobs/skills/astral.yml` |
| `build/mythicmobs/skills/mazmorra.yml` | `plugins/MythicMobs/skills/mazmorra.yml` |
| `build/mythicmobs/skills/tanda3a.yml` | `plugins/MythicMobs/skills/tanda3a.yml` |
| `build/mythicmobs/skills/tanda3b.yml` | `plugins/MythicMobs/skills/tanda3b.yml` |

El astral.yml privado conserva las skills de NPC/modelos privados de la entrega anterior; goblin y abejorro usan las medidas de sus modelos privados. Antes de instalar, comparar con la copia vigente del servidor y conservar cualquier cambio posterior ajeno a escalas. Los otros tres YAML son publicos.

## Aplicacion

1. Confirmar instancia: la documentacion vigente indica Empower; Aternos es una copia antigua. Respaldar los cuatro archivos y esperar a que las salas queden vacias.
2. Reemplazar solo los cuatro YAML. No cambiar mundos, datapack, JAR, modelos ni resource pack. Nunca Worlds > Upload en world.
3. Ejecutar `mm reload` en consola. No requiere apagar ni reiniciar para estos YAML. Si hubo muchas recargas o hay errores de memoria, reiniciar de forma normal.
4. Revisar consola por errores de YAML, skills/modelos ausentes y comandos de atributos. Probar mobs nuevos y descargados/cargados: onSpawn/onLoad reaplica la escala. Una recarga no garantiza corregir entidades ya cargadas: vaciar/resetear las salas por su ciclo normal o descargar/cargar los chunks; no matar controladores ni mascotas globalmente.
5. Comparar arquero, escudero, guardian, nigromante y esqueleto montado sobre arana con jugador. Verificar Cumbre y Ancestral iguales. Probar melee, flecha y baston; los brazos pueden quedar fuera de la caja, como antes de d51e4de.

## Escalas minecraft:scale

Las columnas historicas reproducen las formulas de `git show d51e4de^:datapack-src/mobs/tamanos.py` y `git show d51e4de:datapack-src/mobs/tamanos.py`. Geometria de modelos sin cambios en esta tarea. Para Cumbre: s historico 4.0, d51e4de 20/7 y nuevo 2.0.

| Mob | Antes de d51e4de | En d51e4de | Nueva |
|---|---:|---:|---:|
| astral_mapache | 1.437500 | 4.785638 | 1.437500 |
| astral_pinguino | 2.223214 | 3.676361 | 2.223214 |
| astral_espantapajaros | 2.578125 | 4.723818 | 2.578125 |
| astral_espantapajaros_elite | 3.480469 | 6.377154 | 3.480469 |
| astral_abejorro | 1.296875 | 7.457113 | 1.296875 |
| astral_abejorro_elite | 1.750781 | 10.067102 | 1.750781 |
| astral_arana | 1.083333 | 1.539551 | 1.083333 |
| astral_arana_elite | 1.462500 | 2.078394 | 1.462500 |
| astral_cara | 3.350000 | 3.725000 | 3.350000 |
| astral_cara_elite | 4.522500 | 5.028751 | 4.522500 |
| astral_momia | 2.102564 | 6.564451 | 2.102564 |
| astral_momia_ancestral | 2.102564 | 6.564451 | 2.102564 |
| astral_yeti | 3.181818 | 4.339701 | 3.181818 |
| astral_yeti_ancestral | 3.181818 | 4.339701 | 3.181818 |
| astral_golem_forja | 2.555266 | 3.437860 | 2.555266 |
| astral_golem_forja_ancestral | 2.555266 | 3.437860 | 2.555266 |
| astral_cangrejo | 3.138889 | 3.903165 | 3.138889 |
| astral_cangrejo_elite | 2.118750 | 2.634637 | 2.118750 |
| astral_cangrejo_ancestral | 3.138889 | 3.903165 | 3.138889 |
| astral_chaman | 2.788358 | 8.087792 | 2.788358 |
| astral_chaman_ancestral | 2.788358 | 8.087792 | 2.788358 |
| astral_yeti_cumbre | 6.363636 | 6.199573 | 3.181818 |
| astral_golem_forja_mazmorra | 10.221063 | 13.751438 | 10.221063 |
| astral_mina_guardian | 2.131710 | 5.299882 | 2.131710 |
| astral_bosque_planta | 1.255412 | 5.378173 | 1.255412 |
| astral_esq_arquero | 1.132341 | 3.234623 | 1.132341 |
| astral_esq_escudero | 1.028853 | 3.871179 | 1.028853 |
| astral_esq_guardian | 1.117045 | 4.126690 | 1.117045 |
| astral_esq_nigromante | 1.169081 | 5.609874 | 1.169081 |
| astral_goblin (modelo privado instalado) | 1.226764 | 2.875748 | 1.226764 |
| astral_abejorro (modelo privado instalado) | 1.390881 | 11.495796 | 1.390881 |
| astral_abejorro_elite (modelo privado instalado) | 1.877690 | 15.519325 | 1.877690 |

Las filas sin aclaracion usan modelos publicos. Las tres filas privadas corresponden a la entrega instalable. Las variantes por sala y los jinetes reutilizan las mismas skills; montar no agrega un multiplicador aqui.

## Cumbre y alcance

Mismo modelo astral_yeti, s=2.0, altura geometrica de reposo 7 b y scale=3.181818 en Cumbre y Ancestral. La altura geometrica no certifica el aspecto final de BetterModel con un cliente. Se conservan ataques, radios, dano, fases y posiciones. Las pruebas de terreno verifican la caja en -101.8 30 56.9, en -54.9 30 6.5 y desplazamientos cortos de la sala. No se agregan apoyos.

La tabla y las pruebas numericas no sustituyen capturas de cliente. No desplegado ni consola remota verificada.

## Verificaciones reproducibles

Desde datapack-src: `python mobs/mythic.py`, `python mobs/mazmorra.py`, `python deploy_esqueletos.py`. Pruebas: `python -m unittest discover -p "test_*.py"`.
Smoke local: `python tools/probar_tamanos_paper.py --java <java25.exe> --server .local/tanda4a-paper` desde la raiz. Nunca instalar TamanosProbe en remoto.

Paper 26.1.2 / BetterModel 3.6.0 / MythicMobs 5.13.0: 10 spawns, 24 comprobaciones aprobadas (escala, displays y montaje). Cuatro esqueletos a pie y montados en arana; Cumbre y Ancestral con scale=3.181818 y altura real de entidad 7 b. Log privado en `.local/tamanos-probe/paper.log`.

Capturas con cliente en `build/previews/`: pendientes, no se dispuso de un cliente grafico conectado. Falta probar golpes/flechas y revisar consola en la instancia remota.

Suite versionada mas test_esqueletos_tamano: 217 pruebas aprobadas. Incluye comparacion contra la formula ejecutada desde git show d51e4de^ y terreno/alcance de Cumbre. Descubrimiento completo anterior: 217/218 aprobadas; unico fallo ajeno en test_cosmeticos_nuevos (archivo previo sin versionar), esperaba 20 claves y encontro 21. Ese trabajo se conserva sin editar ni publicar.
