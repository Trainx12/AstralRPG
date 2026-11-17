# Monturas, criaturas hostiles y Basura — 17/11/2026

Preparado localmente. Instalacion y consola remota pendientes de Claude con navegador.
Servidor principal documentado: Empower (Paper 26.1.2 / Java 25); Aternos es copia.
No usar APIs privadas ni reemplazar mundos. Esta entrega conserva el pack FINAL vigente y su SHA-1.
Se integra al apagado/reinicio de pendiente-17-11.md; AstralDecor 1.16.0 sustituye 1.15.0.

## Archivos exactos

| Local | Destino | SHA-256 |
|---|---|---|
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` | `3b291857f20be91dac475ae72955a0d78c41ae7ed28b61eba7fc8d5e0257298d` |
| `.local/terceros/AstralRPG-privado/build/entregas/monturas-17-11/mythicmobs/mobs/astral.yml` | `plugins/MythicMobs/mobs/astral.yml` | `7ddd707ffbcaae3a44538c0c86c348a3029316aebf1fbe5830416de9ef49f5d7` |
| `.local/terceros/AstralRPG-privado/build/entregas/monturas-17-11/mythicmobs/skills/astral.yml` | `plugins/MythicMobs/skills/astral.yml` | `0ab59e787ecd0f19fd6a76201045c2e17c851dce541e9f6eb33a676fb444fb65` |
| `build/lobby/CrazyCrates/crates/gacha_monturas.yml` | `plugins/CrazyCrates/crates/gacha_monturas.yml` | `4a52517cc570c785af252a40e88fec4c36e85c6a9e9f347a758018f24bc82f57` |
| `build/lobby/CrazyCrates/crates/gacha_monturas_suerte.yml` | `plugins/CrazyCrates/crates/gacha_monturas_suerte.yml` | `5876dac48c1de045e8ea1768680aaddce4c9d1f9fae8016b25d8b48463121aea` |
| `build/lobby/CrazyCrates/crates/gacha_monturas_garantia.yml` | `plugins/CrazyCrates/crates/gacha_monturas_garantia.yml` | `dfdd25f18914b8b78b56f09aa3cca9149e5fd062ffd4a2b298e797e2bf75b149` |
| `build/menus/DeluxeMenus/gui_menus/gacha_monturas.yml` | `plugins/DeluxeMenus/gui_menus/gacha_monturas.yml` | `aa3f66da8c08286dec2e3b2c4607cba091a6309b6f99046743d0485c19d6f1f8` |
| `build/mythicmobs/mobs/tanda3a.yml` | `plugins/MythicMobs/mobs/tanda3a.yml` | `ede2d5cde0d18f02ad9e9c0299b6ce9dac222d8a65992f4e59e2b3507ef7bb7f` |

Los dos YAML de MythicMobs son las copias de la entrega privada: conservan modelos de vendedores,
Goblin y Grub. No instalar encima las skills publicas de reserva. Randomspawns, modelos, texturas,
datapack y scripts no cambian por esta tarea. El datapack y gameplay vigentes deben estar activos
para mob/roll y dano por tier; sus actualizaciones previas siguen en la entrega acumulada.

## Instalacion

1. Guardar copias de los ocho archivos de destino. Apagar el servidor.
2. Reemplazar solo esos archivos. Conservar configuracion y datos de AstralDecor y los mundos.
3. Iniciar: reinicio completo obligatorio por AstralDecor.jar. No PlugMan.
4. El arranque carga los YAML; comprobar AstralDecor 1.16.0, MythicMobs, BetterModel y Skript sin errores.
   Para recargas posteriores solo de configuraciones: `mm reload`, `crates reload`, `dm reload`.
   Ninguna recarga de YAML reemplaza el reinicio del JAR.
5. Con cliente en survival: huevo, silla y WASD/salto de Grillo, Chocobo, Escarabajo y Lagarto;
   probar tambien creativo y otro jugador (no roba la propiedad). Verificar silla y posicion del jinete.
   Las naturales nacen domadas sin dueno; el primer usuario las reclama. Las creadas con huevo
   reciben UUID del usuario del evento, tambien en creativo; no se usa NearestPlayer.
6. Lagarto: agua profunda, W y mirada arriba/abajo, espacio para ascender, Shift para bajar del animal;
   respiracion mientras esta sumergido. Comparar distancia con nado a pie, comprobar corriente/paredes.
7. Mapache y Pinguino: huevos en survival, persecucion y golpes con tier; Pinguino aplica Lentitud
   durante 2,5 s, copos y frio visual 1 s sin dano adicional por congelacion. Los mobs antiguos ya
   cargados mantienen su tipo anterior: comprobar con huevos nuevos; no borrar indiscriminadamente entidades.
8. Verificar Gran Ave/Pterodactilo, vitrina (Basura al final), iconos, bota gastada y compras normales,
   con suerte y con garantia. Falta el ensayo de mass-open del JAR remoto de CrazyCrates.

## Estatuas del Santuario

El octavo archivo (`mobs/tanda3a.yml`) tambien se puede instalar solo, sin apagar:
subirlo, `mm reload` y `mm mobs kill astral_estatua_cangrejo`. Comandos individuales
de spawn en [pendiente-17-11.md](pendiente-17-11.md#estatuas-del-santuario-instalable-por-separado-sin-reinicio).
Conservar la Forja existente. Todas usan IRON_GOLEM y modelo a s=2.0.
Alturas geometricas locales: Coloso 5,76; Chaman 5,38; Momia 4,10; Yeti 7,00; Forja 6,90 bloques.
El Coloso conserva su escala de jefe y entra en el rango de las otras estatuas.
La comparacion visual en pedestales y persistencia al descargar chunks quedan para el cliente remoto.

## Balance

| Rareza | Normal | Con suerte | Garantia |
|---|---:|---:|---:|
| Basura | 55% | 51,16279% | 0% |
| Comun | 20% | 18,60465% | 0% |
| Poco comun | 10% | 9,30233% | 0% |
| Raro | 11% | 15,34884% | 0% |
| Epico | 3,5% | 4,88372% | 87,5% |
| Legendario | 0,5% | 0,69767% | 12,5% |

Basura tiene diez premios equiprobables (5,5% cada uno). No reinicia el pity; la garantia
sigue cada 40 tiradas y excluye Basura. Armas y Cosmeticos conservan sus archivos y tablas.

Animales/mascotas reales: **35.81596046%** por tirada normal, **17.90798023 en 50**
(sin aplicar las tiradas de garantia). Cuenta: 20×70/92 + 10×20/34 + 11×60/60 +
3,5×34/37 + 0,5×22/22. La estimacion ~30% del plan no coincide con su tabla explicita;
se conservaron los pesos pedidos. Sin Basura, el catalogo actual daba 75,07427%.

## Verificacion y limites

Pruebas reproducibles: `python -m unittest discover -s datapack-src -p test_monturas_1711.py`,
regresiones de gacha/mascotas/gameplay, `python tools/verificar_terceros.py`.
Ensayo Paper: `python tools/probar_monturas_paper.py --java <JDK25/bin/java.exe> --base .local/testsrv`.
No instalar MountProbe.jar ni publicar sus logs/mundo. Evidencia y limites finales se registran en el resultado.
Verificado el 17/11: 42 pruebas relevantes aprobadas; suite completa 360/361.
El unico fallo preexistente es `test_special_weapons.test_every_weapon_has_a_resolved_animated_model`
por `varita_curacion`: sus fuentes y test son identicos a HEAD y quedan fuera de esta tarea.
Paper 26.1.2, MythicMobs 5.13.0, BetterModel 3.6.0 y Skript 2.17.1: 51 comprobaciones
aprobadas, incluyendo dueños de huevos, control nativo, una sola silla al morir, direcciones A/D,
vector de nado, respiracion, persecucion por tier, hielo y cinco estatuas persistentes en Pacifico.
Las seis cajas de Armas/Cosmeticos son identicas byte a byte al checkout de HEAD; su generador coincide.
Java 25 compila con dos avisos de deprecacion anteriores; auditoria de terceros aprobada.
El jugador NMS simulado no envia movimiento de vehiculo: el desplazamiento observado fue cero.
Por eso 0,65 bloques/tick es velocidad solicitada; no hay medicion real de nado sin cliente.
El ensayo sin cliente no certifica la posicion visual ni las restricciones del conjunto remoto de
WorldGuard/ClearLag/AstralProgression. Mantener CUSTOM y clearlag_exclude, y la prohibicion de montar
en mazmorras del gameplay. El modelo rosa no se identifica con certeza: la captura original no fue
adjuntada a esta invocacion; no alcanza su descripcion para asignarle una especie.
