# Tier de XP por requisitos reales — 27/11

AstralProgression 1.6.2. Activo en Empower el 27/11 tras el reinicio realizado por el dueno.

| Skill | Niveles T1 a T10 |
|---|---|
| fighting | 4 / 16 / 20 / 25 / 30 / 35 / 40 / 45 / 50 / 55 |
| sorcery | 0 / 14 / 20 / 26 / 32 / 37 / 42 / 47 / 52 / 57 |
| archery | 8 / 14 / 20 / 25 / 30 / 35 / 40 / 45 / 50 / 55 |

Fuente unica: items.py/items_t6_10.py; skill_tiers.py regenera el bloque Java antes de compilar.
Cada muerte usa la skill acreditada; en party, cada miembro conserva su skill y nivel.
Sin cambios en recompensas base, permisos de bonus, penalizaciones, loot, claims ni slimes.
Por debajo del primer requisito sigue T1; skills desconocidas no aplican factor de tier.

Instalar solo build/runtime/AstralProgression.jar en plugins/update/AstralProgression.jar
(mismo nombre que el instalado); conservar plugins/AstralProgression/config.yml.
Carga al reiniciar; el dueno realizo el reinicio de esta entrega. No reiniciar por cuenta propia,
usar PlugMan ni reemplazar mundos. No requiere datapack ni resource pack.
Servidor vigente segun CLAUDE.md: Empower; Aternos es la copia historica.
Verificar version 1.6.2 en consola y XP real con Combate 16/19/20 y Magia 14/19/20.

Verificado: compilacion JDK25, 13 pruebas unitarias (skills, soporte y tanda5a),
139 comprobaciones Paper con cero fallos: limites T2-T10 de las tres skills,
penalizaciones legitimas, bonus superior, independencia entre skills y XP real
con/sin Varita de Curacion. Paper aviso que no pudo obtener la clave publica de
Mojang; el ensayo offline no depende de ella. Cualquier otro ERROR hace fallar el ensayo.
Auditoria de terceros OK; recursos/config del JAR conservados respecto de la base 1.6.1.
Ensayo: tools/probar_tier_soporte_paper.py --java <java25> --source <Paper-local>
--progression build/runtime/AstralProgression.jar.

Empower: archivo en plugins/update/AstralProgression.jar, 66.68 KB. Se descargo
de nuevo desde el panel y coincidio su SHA-256 con el local. Tras el reinicio del
dueno: servidor Online, version 1.6.2 consultada en consola, registro con Enabling
AstralProgression v1.6.2 y XP por tier activo; ningun ERROR en el arranque revisado.
No se usaron recargas ni se reemplazaron mundos. Prueba jugando con cliente real
pendiente del dueno. Aviso publicado en Discord (HTTP 204) el 27/11.

SHA-256: 3d8a903ece98f2efa8fcfdec3af6464a767f94cd847d112f504cacb2d0d24d87

Reproducir: deploy_skill_tiers.py --java <java25> --server <Paper-local>.
Aviso publicado: Corregimos la XP de combate y magia: ahora tu tier sigue
el nivel requerido por el equipo de cada habilidad, sin penalizaciones adelantadas.
