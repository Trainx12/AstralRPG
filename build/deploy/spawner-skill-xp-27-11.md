# Combat de spawners — 27/11/2026

AstralProgression 1.6.5: los mobs de spawner y trial spawner dan el 50% de XP
de fighting (Combate). Sorcery, archery y otras habilidades conservan su XP.
El factor se aplica al premio con sus bonus/penalizaciones de tier y reparto
de party. Los multiplicadores superiores siguen en x4 (+1) y x10 (+2 o mas).
Ejemplo sin otros bonus: base del jugador 30, premio normal 30/120/300,
premio de spawner 15/60/150. La XP nativa de entidades sin tier tambien se reduce.

El origen se conserva en conversiones y divisiones sucesivas, con la misma
marca persistente de AstralSpawnerXp. Ese plugin independiente de orbes vanilla
no se modifica ni se incluye en esta entrega.

Fuente: datapack-src/runtime/AstralProgression.java.
Generar: deploy_spawner_skill_xp.py --java <java25> --server <Paper-local>.
Salida aislada: build/spawner-skill-xp/AstralProgression.jar.
Conserva recursos del JAR publicado y defaults x4/x10 de la entrega anterior.
No instalar el JAR historico build/runtime/AstralProgression.jar para esta tarea.

Destino: plugins/update/AstralProgression.jar en Empower (servidor activo).
Conservar plugins/AstralProgression/config.yml. No requiere cambiar datapack,
resource pack ni mundos. Carga al proximo reinicio; no reiniciar por cuenta propia.

Validado con JDK25, 3 pruebas unitarias y 165 comprobaciones Paper sin fallos.
XP real (incluye bonus nativo del jugador de prueba): normal/spawner
143/71.5 (mismo tier), 572/286 (+1), 1430/715 (+2 y +3).
Tambien se verificaron fuentes nativas sin tier, otras habilidades y herencia
del origen. No hubo ERROR en el ensayo final; PacketEvents aviso que no pudo
comprobar actualizaciones, sin impedir la prueba. Auditoria de archivos de esta
tarea: sin arte privado ni credenciales.

SHA-256: e4f72b8ab45c34158126ec16e7499c4df9ba154387668485214cdd1bd622b882.
Estado de instalacion: pendiente de subida.
Aviso listo para cuando cargue: Los mobs de spawners ahora dan la mitad de XP
de Combate. Los bonus x4 y x10 se mantienen sobre esa nueva recompensa.
