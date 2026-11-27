# XP de skills por mobs superiores — 27/11/2026

AstralProgression 1.6.4. Un mob +1 tier paga la XP base del tier de la skill x4;
un mob +2 o mas paga x10 (tope +2). Antes era x5/x25.
Se conserva el minimo de XP normal del mob, el permiso astral.xp.tierbonus,
la skill acreditada, sus requisitos reales, las penalizaciones x0,15/x0,03,
los bonus de elite/jefe, los factores de tamano de slime y el reparto en party.
No cambia dano, vida, loot, dinero ni requisitos de niveles.

## Archivo

- `build/xp-tiers/AstralProgression.jar`
- SHA256: `488d95f3bebb8fc6a8125e274c8f7d4a12b113971a8b98a385eedcce9312f66a`
- Fuente y recursos base: `11e9644ae89b713de5b4d4c5a536c0d3536ff37a`, que ya incorpora
  el cambio del calculo de esta tarea y los arreglos publicados de slimes/jefes.
  La tabla de escala y las pruebas se completan en esta entrega.
- Regenerar: `python datapack-src/deploy_xp_tiers.py --revision 11e9644ae89b713de5b4d4c5a536c0d3536ff37a --java <java25> --server <Paper-local>`.
  El generador lee una revision de Git para excluir trabajo local concurrente.

## Instalacion pendiente

El servidor activo documentado es Empower; Aternos es la copia anterior.
La revision automatica rechazo abrir gp.empowerservers.com por falta de autorizacion
especifica para ese origen. No se instalaron archivos ni se reinicio el servidor.

Antes de subir, verificar la version activa y respaldar su JAR. Si hay una version
posterior o trabajo adicional ya instalado, integrar primero para no revertirlo.
Reemplazar unicamente `plugins/AstralProgression.jar`; no subir plugins de prueba.
Conservar la configuracion existente. El runtime usa x4/x10 como defaults incluso
si todavia existe `tier-bonus: 5`. Si existe `tier-bonus-multipliers`, comprobar
que tenga `'1': 4` y `'2': 10`.

Requiere reinicio completo: respetar el reinicio diario de las 05:00; no reiniciar
por cuenta propia ni activar reinicio por servidor vacio. No usar PlugMan ni reload.
Revisar consola al arrancar: AstralProgression 1.6.4, sin errores.
No requiere datapack, resource pack ni cambios en el mundo.

## Verificacion

- Compilacion Java 25 aprobada (aviso de API deprecada preexistente).
- 14 tests aprobados: tanda5a, skill_tiers, tier_soporte y tier_probabilidad.
- Comparacion automatica del config del JAR contra la base: solo cambia la tabla
  del bonus; los demas valores y recursos auxiliares son identicos.
- Ensayo Paper aprobado: `T5A RESULT failures=0`. Verifica x4/x10 y tope +2
  en fighting, sorcery y archery, config anterior con defaults, tier 0, falta de
  permiso, limites de nivel, penalizaciones y XP real con equipo de soporte.
  Log local: `.local/tier-soporte-paper/paper.log`.

## Aviso al quedar activo

Pendiente; no anunciar como instalado antes de verificarlo.
Texto: "Ajuste de experiencia: derrotar mobs un tier por encima ahora da x4 de XP
de skill; dos tiers por encima da x10."
