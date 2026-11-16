# Tanda XP, cuchillo, ballestas, mochilas y botones — 16/11/2026

Preparada localmente. Despliegue remoto pendiente; no se accedio a Aternos/Empower ni se subio a R2.
Paper 26.1.2 / Java 25. La documentacion identifica Empower como principal desde el 07/11; Aternos es copia.
Confirmar el panel y la version del pack actualmente instalado antes de aplicar. No sustituir mundos; nunca Worlds > Upload en world.

## Comportamiento

XP vanilla directa: frasco 550 puntos y barril 5.500. Stack 16; clic usa uno, Shift + clic todos los de esa mano. Un frasco lleva aproximadamente del nivel 0 al 20 (la barra usa redondeo flotante).
Manzana comible incluso con hambre llena: cinco minutos reales, persiste al desconectar/reiniciar, otra renueva. No altera Luck vanilla ni permisos de OP. AstralDecor guarda el vencimiento en PDC y muestra segundos en actionbar/astral.suerte.
CrazyCrates: tres tablas normales y tres de garantia, mas sus seis variantes _suerte. Pesos de raros/epicos/legendarios x1,5, normalizados: comun 55,81395%, poco comun 23,25581%, raro 15,34884%, epico 4,88372%, legendario 0,69767%. La garantia conserva 87,5% epico / 12,5% legendario. El runtime toma suerte al comprar el lote y la conserva para sus llaves diferidas. El menu y la vitrina normal anuncian probabilidades base; las variantes incluyen su chance individual en la ruleta.
Fuentes: las tres gachas (frasco poco comun, barril epico; manzana rara solo Cosmeticos); todos los cofres de jefe (8% frasco, 1% barril, 3% manzana, tiradas independientes y mismo cooldown existente); podios semanales (1: barril+3 frascos+manzana; 2: 2 frascos+manzana; 3: frasco+manzana); eventos ancestrales existentes (20% frasco, 2,5% barril); Infinita VI+ cada 5 min presentes (8% frasco, 1% barril).
Tienda: frasco_xp_gigante $25,000, barril_xp $220,000, manzana_esmeralda $60,000. EconomyShopGUI gratuito abre un menu DeluxeMenus propio con Vault y espacio libre.
Cuchillos T1-T10: Combate, 53% del dano de espada y velocidad 3,0: DPS 1,59 frente a 1,60. Se ajusto el 55% orientativo porque daria mas DPS que la espada. Costos/requisitos de la espada, mejora exige cuchillo anterior. Forja, mesa cuando cabe y guia incluidos.
Ballestas T1-T10: 1,20 / 1,05 / 0,90 / 0,65 / 0,20 / 0,18 / 0,16 / 0,14 / 0,12 / 0,10 s. Punteria por tier; perforacion hasta IV y multidisparo desde IV; municion normal gratis desde V. Las armaduras de Arquero y los arcos ya tienen 10 tiers. No hay una familia de flechas Astral por tier: la municion vanilla escala con Punteria, sin hueco que completar.
Mochilas: un cuerpo 3D comun con cuerpo, bolsillo, tapa y correas; seis texturas. El runtime cambia solo item_model de cabezas con expendablebackpacks:backpack_uuid y backpack_tier 1..6. Conserva UUID, contenido y el resto de los componentes.
Lobby: Velocidad II. Botones: iconos provisorios en los slots existentes; no se movieron ventanas salvo Infinita VI-X+ (pasa de 36 a 54 slots, usa el marco y tarjetas del selector bajo; Volver 45, Cerrar 53). Los Proximamente comparten modelo. No se hizo arte final. Test de botones: sin excepciones clickeables; los rellenos y cabezas reales sin acciones pueden seguir vanilla.

## Instalacion (servidor apagado)

1. Apagar desde el panel y respaldar solo los archivos de esta lista que se reemplazan.
2. Subir los siguientes archivos locales a sus destinos. No tocar regiones ni mapas.

| Archivo local | Destino |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/infinita/astral_infinita.sk` | `plugins/Skript/scripts/astral_infinita.sk` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos.yml` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos_garantia.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos_garantia.yml` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos_garantia_suerte.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos_garantia_suerte.yml` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos_suerte.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos_suerte.yml` |
| `build/lobby/CrazyCrates/crates/gacha_monturas.yml` | `plugins/CrazyCrates/crates/gacha_monturas.yml` |
| `build/lobby/CrazyCrates/crates/gacha_monturas_garantia.yml` | `plugins/CrazyCrates/crates/gacha_monturas_garantia.yml` |
| `build/lobby/CrazyCrates/crates/gacha_monturas_garantia_suerte.yml` | `plugins/CrazyCrates/crates/gacha_monturas_garantia_suerte.yml` |
| `build/lobby/CrazyCrates/crates/gacha_monturas_suerte.yml` | `plugins/CrazyCrates/crates/gacha_monturas_suerte.yml` |
| `build/lobby/CrazyCrates/crates/gacha_rpg.yml` | `plugins/CrazyCrates/crates/gacha_rpg.yml` |
| `build/lobby/CrazyCrates/crates/gacha_rpg_garantia.yml` | `plugins/CrazyCrates/crates/gacha_rpg_garantia.yml` |
| `build/lobby/CrazyCrates/crates/gacha_rpg_garantia_suerte.yml` | `plugins/CrazyCrates/crates/gacha_rpg_garantia_suerte.yml` |
| `build/lobby/CrazyCrates/crates/gacha_rpg_suerte.yml` | `plugins/CrazyCrates/crates/gacha_rpg_suerte.yml` |
| `build/menus/DeluxeMenus/gui_menus/bazar.yml` | `plugins/DeluxeMenus/gui_menus/bazar.yml` |
| `build/menus/DeluxeMenus/gui_menus/cofre_bosque.yml` | `plugins/DeluxeMenus/gui_menus/cofre_bosque.yml` |
| `build/menus/DeluxeMenus/gui_menus/cofre_cumbre.yml` | `plugins/DeluxeMenus/gui_menus/cofre_cumbre.yml` |
| `build/menus/DeluxeMenus/gui_menus/cofre_forja.yml` | `plugins/DeluxeMenus/gui_menus/cofre_forja.yml` |
| `build/menus/DeluxeMenus/gui_menus/cofre_fosa.yml` | `plugins/DeluxeMenus/gui_menus/cofre_fosa.yml` |
| `build/menus/DeluxeMenus/gui_menus/cofre_mina.yml` | `plugins/DeluxeMenus/gui_menus/cofre_mina.yml` |
| `build/menus/DeluxeMenus/gui_menus/cofre_santuario.yml` | `plugins/DeluxeMenus/gui_menus/cofre_santuario.yml` |
| `build/menus/DeluxeMenus/gui_menus/cofre_tumba.yml` | `plugins/DeluxeMenus/gui_menus/cofre_tumba.yml` |
| `build/menus/DeluxeMenus/gui_menus/comandos.yml` | `plugins/DeluxeMenus/gui_menus/comandos.yml` |
| `build/menus/DeluxeMenus/gui_menus/configuraciones.yml` | `plugins/DeluxeMenus/gui_menus/configuraciones.yml` |
| `build/menus/DeluxeMenus/gui_menus/consumibles.yml` | `plugins/DeluxeMenus/gui_menus/consumibles.yml` |
| `build/menus/DeluxeMenus/gui_menus/deseo.yml` | `plugins/DeluxeMenus/gui_menus/deseo.yml` |
| `build/menus/DeluxeMenus/gui_menus/deseo_lite.yml` | `plugins/DeluxeMenus/gui_menus/deseo_lite.yml` |
| `build/menus/DeluxeMenus/gui_menus/dropper_facil.yml` | `plugins/DeluxeMenus/gui_menus/dropper_facil.yml` |
| `build/menus/DeluxeMenus/gui_menus/dropper_h4rs.yml` | `plugins/DeluxeMenus/gui_menus/dropper_h4rs.yml` |
| `build/menus/DeluxeMenus/gui_menus/expediciones.yml` | `plugins/DeluxeMenus/gui_menus/expediciones.yml` |
| `build/menus/DeluxeMenus/gui_menus/fragmentos.yml` | `plugins/DeluxeMenus/gui_menus/fragmentos.yml` |
| `build/menus/DeluxeMenus/gui_menus/gacha_cosmeticos.yml` | `plugins/DeluxeMenus/gui_menus/gacha_cosmeticos.yml` |
| `build/menus/DeluxeMenus/gui_menus/gacha_monturas.yml` | `plugins/DeluxeMenus/gui_menus/gacha_monturas.yml` |
| `build/menus/DeluxeMenus/gui_menus/gacha_rpg.yml` | `plugins/DeluxeMenus/gui_menus/gacha_rpg.yml` |
| `build/menus/DeluxeMenus/gui_menus/infinita_tier_alto.yml` | `plugins/DeluxeMenus/gui_menus/infinita_tier_alto.yml` |
| `build/menus/DeluxeMenus/gui_menus/mazmorras.yml` | `plugins/DeluxeMenus/gui_menus/mazmorras.yml` |
| `build/menus/DeluxeMenus/gui_menus/misiones.yml` | `plugins/DeluxeMenus/gui_menus/misiones.yml` |
| `build/menus/DeluxeMenus/gui_menus/misiones_1.yml` | `plugins/DeluxeMenus/gui_menus/misiones_1.yml` |
| `build/menus/DeluxeMenus/gui_menus/misiones_2.yml` | `plugins/DeluxeMenus/gui_menus/misiones_2.yml` |
| `build/menus/DeluxeMenus/gui_menus/misiones_3.yml` | `plugins/DeluxeMenus/gui_menus/misiones_3.yml` |
| `build/menus/DeluxeMenus/gui_menus/misiones_4.yml` | `plugins/DeluxeMenus/gui_menus/misiones_4.yml` |
| `build/menus/DeluxeMenus/gui_menus/oceano_aviso.yml` | `plugins/DeluxeMenus/gui_menus/oceano_aviso.yml` |
| `build/menus/DeluxeMenus/gui_menus/oficios.yml` | `plugins/DeluxeMenus/gui_menus/oficios.yml` |
| `build/menus/DeluxeMenus/gui_menus/portales.yml` | `plugins/DeluxeMenus/gui_menus/portales.yml` |
| `build/menus/DeluxeMenus/gui_menus/principal.yml` | `plugins/DeluxeMenus/gui_menus/principal.yml` |
| `build/menus/DeluxeMenus/gui_menus/renacer.yml` | `plugins/DeluxeMenus/gui_menus/renacer.yml` |
| `build/menus/DeluxeMenus/gui_menus/subastas.yml` | `plugins/DeluxeMenus/gui_menus/subastas.yml` |
| `build/minas/Skript/scripts/astral_minas.sk` | `plugins/Skript/scripts/astral_minas.sk` |
| `build/mythicmobs/mobs/astral.yml` | `plugins/MythicMobs/mobs/astral.yml` |
| `build/mythicmobs/mobs/lobby.yml` | `plugins/MythicMobs/mobs/lobby.yml` |
| `build/rankings/astral_rankings.sk` | `plugins/Skript/scripts/astral_rankings.sk` |
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` |
| `build/shop/EconomyShopGUI/sections/Consumibles.yml` | `plugins/EconomyShopGUI/sections/Consumibles.yml` |
| `build/shop/EconomyShopGUI/shops/Consumibles.yml` | `plugins/EconomyShopGUI/shops/Consumibles.yml` |

Agregar en `plugins/DeluxeMenus/config.yml`, dentro de `gui_menus`: `consumibles: {file: consumibles.yml}`. Conservar los registros anteriores; consultar `build/menus/DeluxeMenus/config-gui_menus.yml`.
La seccion EconomyShopGUI Consumibles usa slot 43: comprobar que ese slot este libre en el panel actual antes de instalar; mover solo la nueva seccion si esta ocupado.

## Pack FINAL privado

Base: `build/entregas/armas-mod/AstralRPG-Textures.zip` (SHA-1 `3a710f8ba5ee4bc1238996c62d15e40d6e09e122`); se conservan todas sus entradas y las ballestas privadas III-V. Delta publico contra `ab6accdb42cc474e141c66acfe2264855182349e`: 252 entradas.
Local: `.local/terceros/AstralRPG-privado/build/entregas/tanda-xp-cuchillo/AstralRPG-Textures.zip`. SHA-1: `76644a7adfcca953ce413eb506bb6c8fc527c96f`.
No instalar el ZIP publico: no lleva los modelos elegidos de mods. Este FINAL tampoco se publica en GitHub publico.
Con el servidor apagado: `python tools/subir_pack_r2.py ".local/terceros/AstralRPG-privado/build/entregas/tanda-xp-cuchillo/AstralRPG-Textures.zip"`. Verificar la descarga publica antes de actualizar `resource-pack-sha1` en server.properties. Mantener la URL fija existente.
Si el FINAL instalado es posterior o no coincide con la base indicada, rehacer la combinacion con ese FINAL; no reemplazarlo ciegamente.

## Inicio y recargas

Iniciar con Java 25: reinicio completo obligatorio por JAR, datapack y hash del resource pack. Revisar consola: AstralDecor 1.11.0, recetas registradas, ningun error de enchantments/loot/functions.
Las configs se cargan al iniciar. Si se corrige solo YAML despues: `crates reload`, `dm reload`, `mm reload`, `sreload`; `skript reload astral_minas`, `skript reload astral_infinita`, `skript reload astral_rankings`. No repetir recargas si ya cargo correctamente al iniciar.

## Pruebas de juego

`loot give JUGADOR loot astral:item/frasco_xp_gigante`, repetir 16 veces; usar clic y Shift + clic y verificar los puntos, tambien con mano secundaria. `loot give JUGADOR loot astral:item/barril_xp`.
`loot give JUGADOR loot astral:item/manzana_esmeralda`; comer, mirar barra de accion y `scoreboard players get JUGADOR astral.suerte`; comer otra tras un minuto: vuelve a 300, no 540. Probar x1/x10, garantia, inventario lleno y efecto que vence durante la animacion.
`execute as JUGADOR run function astral:admin/kit_cuchillos`; probar Combate, Forja, mesa y velocidades. `execute as JUGADOR run function astral:admin/kit_ballestas`; comprobar carga, proyectiles, perforacion, multidisparo y flechas desde T5.
`backpack give JUGADOR leather` (y copper/iron/gold/diamond/netherite): conservar un objeto dentro, mirar mano/inventario, desconectar, mejorar y reiniciar. Entrar/salir del lobby: Velocidad II caduca a los 3 segundos de salir. Revisar todos los botones nuevos y ambas ventanas Infinita.

## Verificacion y limites

Verificado: suite completa de 293 pruebas OK, suite especifica ampliada de 8 pruebas OK; compilacion Java 25 OK; Paper 26.1.2 arranca y reinicia con XP RESULT failures=0 en ambos ciclos. Auditor de terceros OK. Los logs quedan en .local y no se publican. El ensayo usa un jugador NMS y dobles de los comandos CrazyCrates: verifica XP real, consumo, PDC, seleccion de caja y reinicio, no reemplaza un cliente visual, la animacion real de CrazyCrates ni las compras en el panel remoto.
Pendiente remoto: subir archivos, R2, reiniciar, consola y pruebas con cliente. No se afirmo ningun despliegue.

## Texturas provisorias

Reemplazar estos PNG locales y regenerar `build_pack.py pack-source` y `deploy_tanda_xp.py`. Se crean una sola vez y no se pisan al regenerar. Los nombres de item_model quedan fijos. Cuchillo y ballestas pendientes de mod: tabla `PENDIENTES` en armas_mod.py, valores None.

| Item o boton | PNG local | Tamano esperado |
|---|---|---|
| `ballesta_1` | `datapack-src/pack-source/provisorias/ballesta_1.png` | 32x32 RGBA |
| `ballesta_10` | `datapack-src/pack-source/provisorias/ballesta_10.png` | 32x32 RGBA |
| `ballesta_2` | `datapack-src/pack-source/provisorias/ballesta_2.png` | 32x32 RGBA |
| `ballesta_6` | `datapack-src/pack-source/provisorias/ballesta_6.png` | 32x32 RGBA |
| `ballesta_7` | `datapack-src/pack-source/provisorias/ballesta_7.png` | 32x32 RGBA |
| `ballesta_8` | `datapack-src/pack-source/provisorias/ballesta_8.png` | 32x32 RGBA |
| `ballesta_9` | `datapack-src/pack-source/provisorias/ballesta_9.png` | 32x32 RGBA |
| `barril_xp` | `datapack-src/pack-source/provisorias/barril_xp.png` | 32x32 RGBA |
| `boton_arma` | `datapack-src/pack-source/provisorias/boton_arma.png` | 32x32 RGBA |
| `boton_ayuda` | `datapack-src/pack-source/provisorias/boton_ayuda.png` | 32x32 RGBA |
| `boton_configuraciones` | `datapack-src/pack-source/provisorias/boton_configuraciones.png` | 32x32 RGBA |
| `boton_conservas` | `datapack-src/pack-source/provisorias/boton_conservas.png` | 32x32 RGBA |
| `boton_cosmetico` | `datapack-src/pack-source/provisorias/boton_cosmetico.png` | 32x32 RGBA |
| `boton_efectos_alto` | `datapack-src/pack-source/provisorias/boton_efectos_alto.png` | 32x32 RGBA |
| `boton_efectos_bajo` | `datapack-src/pack-source/provisorias/boton_efectos_bajo.png` | 32x32 RGBA |
| `boton_efectos_medio` | `datapack-src/pack-source/provisorias/boton_efectos_medio.png` | 32x32 RGBA |
| `boton_entrar` | `datapack-src/pack-source/provisorias/boton_entrar.png` | 32x32 RGBA |
| `boton_garantia` | `datapack-src/pack-source/provisorias/boton_garantia.png` | 32x32 RGBA |
| `boton_infinita` | `datapack-src/pack-source/provisorias/boton_infinita.png` | 32x32 RGBA |
| `boton_info` | `datapack-src/pack-source/provisorias/boton_info.png` | 32x32 RGBA |
| `boton_minero_info` | `datapack-src/pack-source/provisorias/boton_minero_info.png` | 32x32 RGBA |
| `boton_minero_set` | `datapack-src/pack-source/provisorias/boton_minero_set.png` | 32x32 RGBA |
| `boton_oceano` | `datapack-src/pack-source/provisorias/boton_oceano.png` | 32x32 RGBA |
| `boton_otro` | `datapack-src/pack-source/provisorias/boton_otro.png` | 32x32 RGBA |
| `boton_personalizada` | `datapack-src/pack-source/provisorias/boton_personalizada.png` | 32x32 RGBA |
| `boton_pierdes` | `datapack-src/pack-source/provisorias/boton_pierdes.png` | 32x32 RGBA |
| `boton_plata` | `datapack-src/pack-source/provisorias/boton_plata.png` | 32x32 RGBA |
| `boton_premio` | `datapack-src/pack-source/provisorias/boton_premio.png` | 32x32 RGBA |
| `boton_probabilidades` | `datapack-src/pack-source/provisorias/boton_probabilidades.png` | 32x32 RGBA |
| `boton_proximamente` | `datapack-src/pack-source/provisorias/boton_proximamente.png` | 32x32 RGBA |
| `boton_reglas` | `datapack-src/pack-source/provisorias/boton_reglas.png` | 32x32 RGBA |
| `boton_sin_datos` | `datapack-src/pack-source/provisorias/boton_sin_datos.png` | 32x32 RGBA |
| `boton_talador_info` | `datapack-src/pack-source/provisorias/boton_talador_info.png` | 32x32 RGBA |
| `boton_talador_set` | `datapack-src/pack-source/provisorias/boton_talador_set.png` | 32x32 RGBA |
| `boton_tema` | `datapack-src/pack-source/provisorias/boton_tema.png` | 32x32 RGBA |
| `boton_tier` | `datapack-src/pack-source/provisorias/boton_tier.png` | 32x32 RGBA |
| `boton_tiradas` | `datapack-src/pack-source/provisorias/boton_tiradas.png` | 32x32 RGBA |
| `cuchillo_1` | `datapack-src/pack-source/provisorias/cuchillo_1.png` | 32x32 RGBA |
| `cuchillo_10` | `datapack-src/pack-source/provisorias/cuchillo_10.png` | 32x32 RGBA |
| `cuchillo_2` | `datapack-src/pack-source/provisorias/cuchillo_2.png` | 32x32 RGBA |
| `cuchillo_3` | `datapack-src/pack-source/provisorias/cuchillo_3.png` | 32x32 RGBA |
| `cuchillo_4` | `datapack-src/pack-source/provisorias/cuchillo_4.png` | 32x32 RGBA |
| `cuchillo_5` | `datapack-src/pack-source/provisorias/cuchillo_5.png` | 32x32 RGBA |
| `cuchillo_6` | `datapack-src/pack-source/provisorias/cuchillo_6.png` | 32x32 RGBA |
| `cuchillo_7` | `datapack-src/pack-source/provisorias/cuchillo_7.png` | 32x32 RGBA |
| `cuchillo_8` | `datapack-src/pack-source/provisorias/cuchillo_8.png` | 32x32 RGBA |
| `cuchillo_9` | `datapack-src/pack-source/provisorias/cuchillo_9.png` | 32x32 RGBA |
| `frasco_xp_gigante` | `datapack-src/pack-source/provisorias/frasco_xp_gigante.png` | 32x32 RGBA |
| `infinita_alto_10` | `datapack-src/pack-source/provisorias/infinita_alto_10.png` | 32x32 RGBA |
| `infinita_alto_11` | `datapack-src/pack-source/provisorias/infinita_alto_11.png` | 32x32 RGBA |
| `infinita_alto_6` | `datapack-src/pack-source/provisorias/infinita_alto_6.png` | 32x32 RGBA |
| `infinita_alto_7` | `datapack-src/pack-source/provisorias/infinita_alto_7.png` | 32x32 RGBA |
| `infinita_alto_8` | `datapack-src/pack-source/provisorias/infinita_alto_8.png` | 32x32 RGBA |
| `infinita_alto_9` | `datapack-src/pack-source/provisorias/infinita_alto_9.png` | 32x32 RGBA |
| `manzana_esmeralda` | `datapack-src/pack-source/provisorias/manzana_esmeralda.png` | 32x32 RGBA |
| `mochila_copper` | `datapack-src/pack-source/provisorias/mochila_copper.png` | 32x32 RGBA |
| `mochila_diamond` | `datapack-src/pack-source/provisorias/mochila_diamond.png` | 32x32 RGBA |
| `mochila_gold` | `datapack-src/pack-source/provisorias/mochila_gold.png` | 32x32 RGBA |
| `mochila_iron` | `datapack-src/pack-source/provisorias/mochila_iron.png` | 32x32 RGBA |
| `mochila_leather` | `datapack-src/pack-source/provisorias/mochila_leather.png` | 32x32 RGBA |
| `mochila_netherite` | `datapack-src/pack-source/provisorias/mochila_netherite.png` | 32x32 RGBA |
