# Tier de XP por requisitos reales — 27/11

AstralProgression 1.6.2. Preparado; despliegue remoto pendiente.

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
Carga en el reinicio diario autorizado de las 05:00. No reiniciar por cuenta propia,
usar PlugMan ni reemplazar mundos. No requiere datapack ni resource pack.
Servidor vigente segun CLAUDE.md: Empower; Aternos es la copia historica.
Verificar version 1.6.2 en consola y XP real con Combate 16/19/20 y Magia 14/19/20.

SHA-256: 3d8a903ece98f2efa8fcfdec3af6464a767f94cd847d112f504cacb2d0d24d87

Reproducir: deploy_skill_tiers.py --java <java25> --server <Paper-local>.
Aviso al entrar en vivo: Corregimos la XP de combate y magia: ahora tu tier sigue
el nivel requerido por el equipo de cada habilidad, sin penalizaciones adelantadas.
