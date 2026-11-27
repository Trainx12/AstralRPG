# Soporte excluido del tier - 27/11

Pendiente de instalacion por Claude. No se accedio al servidor remoto.

| Local | Destino |
|---|---|
| `build/tier-soporte-27-11/AstralRPG-TierSoporte.zip` | `world/datapacks/z-AstralRPG-TierSoporte.zip` |
| `build/tier-soporte-27-11/AstralProgression.jar` | `plugins/update/AstralProgression.jar` |

Conservar el datapack principal instalado y los complementos existentes. Este ZIP solo contiene
`pack.mcmeta` y `data/astral/function/player/lvl.mcfunction`; no contiene mapas ni items nuevos.
Comprobar que no haya otro complemento posterior que reemplace esa funcion.
Conservar `plugins/AstralProgression/config.yml` y el nombre del JAR instalado;
el mecanismo plugins/update requiere el mismo nombre. Si difiere, usar ese nombre.

Subir ambos antes del reinicio diario autorizado de las 05:00. No activar reinicio por vacio.
Alternativa con el servidor apagado: sustituir el JAR en `plugins/` y arrancar.
No usar PlugMan, `/reload`, ni reemplazar mundos. No requiere R2 ni resource pack.
Si el complemento no esta activo con prioridad, ejecutar en consola:
`datapack enable "file/z-AstralRPG-TierSoporte.zip" last`.
Comprobar `datapack list enabled`, AstralProgression 1.5.0 sin errores y ejecutar como jugador
`function astral:player/lvl`; con espada T2, varita en inventario y talisman en secundaria,
`scoreboard players get <jugador> astral.wt` debe dar 2 (sin equipo superior).
Matar mobs nuevos T2 con Combate de nivel 10 debe conservar XP completa con varita en mano.
No instalar SupportTierProbe ni configuraciones del ensayo en remoto.
Aternos no permite subir este plugin propio si no esta en su catalogo: no instalar a medias ni eludir restricciones.

La exclusion central corrige mobs (`wt`), elites (`lvl`), dano/PvP (`ht`) y premios de secretos que leen `wt`.
Economia no lee esos scores; conserva sus reglas. Stellarity conserva su etiquetado de equipo.
El tier de XP sigue siendo el de la skill acreditada, con las penalizaciones legitimas existentes.
La varita ya no puede elegir Hechiceria por requisitos heredados; el golpe directo usa Combate
como sin arma Astral, salvo un hechizo real marcado `astral.caster`.

Reproducir: `python datapack-src/deploy_tier_soporte.py --java <java25> --server <Paper-local>`;
`python datapack-src/test_tier_soporte.py`;
`python tools/probar_tier_soporte_paper.py --java <java25> --source <Paper-local>`;
`python tools/verificar_terceros.py`.

Verificado localmente: compilacion JDK 25, 3 pruebas unitarias, 26 comprobaciones Paper
(sin fallos): wt/lvl=2 con espada T2 y los soportes; 132 XP de Combate en los tres
casos sin varita, varita en inventario y varita en mano, factor 1. Auditoria de terceros OK.
La espada Astral T2 exige Combate 16: el ensayo de XP a nivel 10 usa espada vanilla
para evitar ese bloqueo, y conserva la espada Astral T2 para las pruebas de scores.
Estas pruebas locales con jugador simulado no sustituyen la comprobacion remota.

Aviso sugerido para Claude cuando este en vivo: La Varita de Curacion y los talismanes
ya no suben el tier de los mobs ni alteran la skill de tus golpes.
