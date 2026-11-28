# Spawners sin experiencia vanilla

Correccion del 28/11/2026: la entrega local del 27/11 no se habia publicado
ni instalado. La inspeccion del servidor activo encontro AstralProgression
1.6.5, pero ningun AstralSpawnerXp.jar.

AstralSpawnerXp 1.0.0 suprime solo los orbes vanilla de SPAWNER y
TRIAL_SPAWNER. Conserva el origen mediante PDC en conversiones y divisiones
sucesivas. No modifica drops de items, configuraciones ni recompensas de
AuraSkills/AstralProgression. En particular conserva la reduccion de Combate
de la tarea anterior y sus multiplicadores de tier.

Fuentes: `datapack-src/runtime/AstralSpawnerXp.java` y
`datapack-src/spawner_xp.py`. Generar desde la raiz:

```text
python datapack-src/spawner_xp.py --java <java25>
python tools/probar_spawner_xp_paper.py --java <java25>
```

La prueba usa un servidor local separado y un jugador NMS, con chunks
forzados para que avancen las animaciones de muerte. Espera 30 ticks antes
de contar orbes y descendientes. Nunca instalar SpawnerXpProbe en remoto.

Resultado: 28 comprobaciones Paper aprobadas. Spawner y trial: 0 orbes y
71.5 XP real de Combate con la configuracion del ensayo. Natural, custom,
huevo y cria: los 7 puntos vanilla fijados por el probe y 143 XP de Combate.
Dos generaciones reales de slimes heredan la supresion de orbes.
PacketEvents aviso de un fallo HTTP 403 en su comprobador de actualizaciones,
sin impedir las pruebas.

Instalar solo `build/spawner-xp/AstralSpawnerXp.jar` en
`plugins/AstralSpawnerXp.jar` del servidor activo de Empower. Es un plugin
nuevo: requiere reinicio completo. No usar `/reload` ni carga dinamica.
No reemplazar mundos, datapack, resource pack ni AstralProgression.

SHA-256: `2ba72c601da7b2c5c4701e439a7f77bfc1740030dcfed9039da9652bd4220be2`.

Comprobar consola: `Enabling AstralSpawnerXp v1.0.0` sin errores; despues
probar una baja de spawner y una natural en el servidor real.

Aviso para publicar cuando se confirme la carga: Los mobs de generadores
ya no dan experiencia de Minecraft para encantar. Siguen dando experiencia
de habilidades. Los mobs que aparecen normalmente conservan su experiencia.

## Despliegue verificado el 28/11/2026

Publicado el codigo y el JAR en GitHub (533c575f). Subido unicamente
`plugins/AstralSpawnerXp.jar` en Empower y descargado de nuevo para verificar
el SHA-256 identico. `plugins/update` estaba vacio antes del reinicio.
Se reinicio el servidor para cargar el plugin nuevo; no se cambiaron mundos,
datapacks, resource pack ni otros plugins.

Registro remoto: `Enabling AstralSpawnerXp v1.0.0`, seguido de
`Done (280.399s)!`, sin errores de AstralSpawnerXp. Los horarios del registro
son 13:58:37 y 14:00:07 (UTC), respectivamente. Aviso publicado en el canal
de novedades de Discord (HTTP 204).

La validacion de bajas y orbes fue en Paper local; falta la comprobacion
jugando del dueno en el servidor real. El plugin ya esta cargado y activo.
