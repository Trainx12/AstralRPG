# Guia Astral: Stellarity, Comida y Crafteos

Preparado, sin instalacion remota verificada. Empower, Paper 26.1.2 / Java 25.
Stellarity 5.4.2; no instalar 6.0.1. CNK 1.3.12 se describe como preparado,
sin confirmar su presencia actual. No se instala ni modifica Stellarity o CNK.

## Version y conservacion

Base descargada del R2 publico, SHA-1 `e2eafeb55caddd8cb4661a2e1b05a61e4f44f516`. Esto comprueba la version
publicada del pack; no certifica el SHA-1 actual en server.properties remoto.
FINAL privado: `.local/terceros/AstralRPG-privado/build/entregas/guia-stellarity-comida-crafteos/AstralRPG-Textures.zip`.
SHA-1 nuevo: `d994958669b02a57b95fd7a1c5c985b820a024b7`.
Estado de R2: **Subido a R2 y descarga publica verificada por tools/subir_pack_r2.py.**
Conserva 22420 entradas de la base fuera del delta de fuentes y fondos de Guia.
No incluye texturas locales de gomera/bazar/renacer ni otras tareas sin publicar.
Los ZIP compartidos build/AstralRPG-Items.zip y build/AstralRPG-Textures.zip,
build/runtime/guia_fuente.json y build.py conservan el trabajo previo.
La captura usada fue HEAD:build/runtime/guia_fuente.json; solo cambia la ampliacion.

## Archivos y destinos

| Local | Destino / accion |
|---|---|
| Cada YAML listado abajo en build/guia-stellarity/gui_menus/ | plugins/DeluxeMenus/gui_menus/ con el mismo nombre |
| build/guia-stellarity/config-guia.yml | Fusionar las entradas dentro de gui_menus en plugins/DeluxeMenus/config.yml; no sustituir el archivo completo |
| FINAL privado indicado arriba | R2, mediante tools/subir_pack_r2.py; no subir el ZIP publico de assets como pack completo |
| SHA-1 indicado arriba | resource-pack-sha1 en server.properties, solo tras verificar descarga publica |

Son 143 YAML (140 nuevos) y el fragmento de registro.
build/guia-stellarity/GuiaAstral-Assets.zip y font-providers.json son insumos publicos
del generador, no packs completos ni archivos para plugins.
No se necesita subir datapack a world/datapacks, JAR, Skript, mapas ni mundos:
esta tarea agrega consultas a DeluxeMenus y fondos al resource pack.

## Instalacion y prueba reservada

1. Comprobar que el resource-pack remoto corresponda a la base. Si el pack publicado
   cambio, volver a generar con `python datapack-src/deploy_guia_stellarity.py --download-base`.
   No usar un FINAL local mas nuevo de otra tarea por su fecha.
2. Subir el FINAL con `python tools/subir_pack_r2.py ".local/terceros/AstralRPG-privado/build/entregas/guia-stellarity-comida-crafteos/AstralRPG-Textures.zip"`.
   El comando compara el SHA-1 de la descarga publica. Registrar el resultado antes
   de actualizar server.properties desde el panel.
3. Instalar los YAML listados y fusionar config-guia.yml. Conservar el resto de menus.
   Consola: `dm reload`; revisar errores de YAML, requisitos, modelos y menus faltantes.
4. Consola: `lp user ByTrainx permission set astral.guia.ampliacion true`.
   Las ventanas exigen ese permiso Y nombre ByTrainx. No darlo al grupo default.
5. Cargar el nuevo SHA-1 con reinicio completo. Los YAML solos admiten dm reload sin apagar;
   el cambio de pack/propiedades requiere reinicio y reconexion del cliente.
   El pedido de reiniciar sin jugadores lo continua Claude desde el panel: antes usar
   `list` en consola y comprobar cero conectados; no asumirlo por falta de datos.
6. ByTrainx: `/modo admin`, `/sala`, abrir `/guiaastral`, Comida (pagina 1),
   Crafteos y Stellarity (pagina 3). Probar volver/anterior/siguiente/cerrar,
   cantidades, textos al pasar el cursor y colores del fondo. Otro jugador debe
   recibir el aviso de prueba al intentar abrir estas ventanas.
7. Abrir al publico requiere OK del dueno y cambiar el generador que construye
   open_requirement; regenerar la entrega. No quitar requisitos a mano en build.

No reiniciar ni recargar el servidor desde esta tarea. No usar Worlds > Upload,
no reemplazar mundos y no ejecutar /reload de Bukkit para cambiar datapacks.
tools/empower_api.py admite `--yes command "list"` con la clave existente del panel,
pero no devuelve la salida de consola: solo confirma el envio. No sirve para
certificar el numero de conectados; Claude debe leer la consola del panel.
No se usa API privada de Aternos ni se eluden restricciones.

## Verificacion y limites

20 pruebas de test_guia_cofre.py y test_guia_atlas.py: ingredientes, enlaces,
indexado, forma, cantidades, modelos, fuente sin mutacion y recetas sin boton Forja.
Verificar tambien el manifiesto y la auditoria tools/verificar_terceros.py antes del commit.
No se ejecuto el antiguo ensayo Paper de dialogos: el datapack no cambia y ese
ensayo no carga DeluxeMenus. La carga real del plugin y cliente siguen pendientes.

build/previews/guia-stellarity contiene un plano PNG por ventana nueva; son
vistas de casillas y nombres con el fondo real, sin renders de arte de terceros,
sin simular capturas de Minecraft. La revision visual con cliente es obligatoria.
Informe completo privado: .local/coordination/stellarity-informe.md (no publicar).
Datos de la Guia: datapack-src/guia_stellarity.json, 150 objetos y 116 recetas.
El informe incluye efectos, botin condicionado, biomas, estructuras y anexo CNK.

Limitaciones del original: Frost Cloud enumera cinco ingredientes pero exige seis;
el Altar Maldito necesita comprobar activacion porque Astral retira al dragon;
bell_flower y chorus_petal carecen de modelo en el RP disponible (base vanilla).
El RP de traducciones local es 6.0.1, distinto del datapack 5.4.2; los numeros y
recetas se leen del datapack, no se infieren de esas traducciones.

## Texto para Discord — solo despues de abrir al publico

🆕 La Guia Astral suma Comida, Crafteos y Stellarity.
Ahora podes consultar para que sirve cada sistema y ver las recetas del End,
sus materiales y donde se preparan. Tambien vas a encontrar armas, armaduras,
libros, peces y jefes. La cocina Crop & Kettle aparece como preparada hasta
confirmar que este habilitada. Abrilo desde la Guia del Menu Astral.

No publicado en Discord: la ampliacion sigue reservada al dueno.

## Lista exacta de YAML

Cada ruta local siguiente se copia a plugins/DeluxeMenus/gui_menus/ con su mismo nombre:

- `build/guia-stellarity/gui_menus/g_atlas_seccion_cocina.yml`
- `build/guia-stellarity/gui_menus/g_atlas_seccion_crafteos.yml`
- `build/guia-stellarity/gui_menus/g_atlas_seccion_stellarity.yml`
- `build/guia-stellarity/gui_menus/g_guia_comida_cnk.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_altares.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_armor_1.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_books_1.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_food_1.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_food_2.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_jefes.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_materials_1.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_materials_2.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_mundo_1.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_mundo_2.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_potions_1.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_potions_2.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_book_of_conveyance.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_book_of_jinx.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_champion_boots.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_champion_chestplate.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_champion_helmet.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_champion_leggings.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_chorus_plating.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_crest_of_the_end.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_enderite_smithing_template.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_endonomicon.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_floral_boots.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_floral_chestplate.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_floral_helmet.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_floral_leggings.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_hallowed_boots.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_hallowed_chestplate.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_hallowed_helmet.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_hallowed_leggings.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_sandstorm_trident.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_satchel_of_voids.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_shulker_axe.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_shulker_boots.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_shulker_chestplate.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_shulker_helmet.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_shulker_hoe.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_shulker_leggings.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_shulker_pickaxe.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_shulker_shovel.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_shulker_spear.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_shulker_sword.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_spectral_fury.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_altar_tamaris.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_blind_rage_potion_70.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_blind_rage_potion_ext_71.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_candied_chorus_fruit_60.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_chorus_juice_69.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_chorus_pie_64.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_chorus_stew_57.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_ender_dirt_96.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_ender_grass_block_98.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_endurance_potion_72.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_endurance_potion_ext_73.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_endurance_potion_ii_74.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_entanglement_potion_75.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_entanglement_potion_ext_76.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_entanglement_potion_ii_77.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_fried_chorus_fruit_61.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_frost_cloud_potion_78.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_frozen_carpaccio_63.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_golden_chorus_fruit_59.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_grilled_enderman_flesh_62.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_hellfire_treader_potion_79.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_hellfire_treader_potion_ext_80.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_hellfire_treader_potion_ii_81.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_lifeforce_potion_82.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_lifeforce_potion_ext_83.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_lifeforce_potion_ii_84.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_luck_potion_89.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_minecraft_experience_bottle_58.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_pho_65.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_poseidons_nectar_90.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_prismatic_sushi_68.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_red_potion_91.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_regeneraga_92.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_regeneraga_ii_93.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_rooted_ender_dirt_97.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_royal_jelly_94.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_royal_jelly_ii_95.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_shepherds_pie_66.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_spelunker_potion_85.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_spelunker_potion_86.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_spelunker_potion_ext_87.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_spelunker_potion_ii_88.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_caldero_sushi_67.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_black.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_blue.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_brown.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_cyan.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_gray.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_green.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_light_blue.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_light_gray.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_lime.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_magenta.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_orange.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_pink.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_purple.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_red.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_water.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_white.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_elytra_yellow.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_minecraft_dispenser.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_minecraft_dropper.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_minecraft_end_crystal.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_minecraft_end_rod.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_minecraft_glass.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_minecraft_leather.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_minecraft_lever.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_minecraft_observer.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_minecraft_piston.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_minecraft_purple_dye.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_minecraft_slime_ball.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_minecraft_spectral_arrow.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_stellarity_chorus_plant_from_fruit.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_stellarity_glass_from_end_stone.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_stellarity_gunpowder_from_popped_chorus_blasting.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_stellarity_gunpowder_from_popped_chorus_campfire.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_stellarity_leather_from_membranes.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_stellarity_papyrus.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_stellarity_purple_dye_from_chorus_flower.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_stellarity_slime_ball_from_ender_eye.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_stellarity_spectral_arrow_alt.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_stellarity_sugar_from_chorus_fruit.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_stellarity_suspicious_stew_from_chorus_fruit.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_stellarity_suspicious_stew_from_pink_petals.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_r_stellarity_suspicious_stew_from_pitcher_pod.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_recetas_1.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_recetas_2.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_recetas_3.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_recetas_4.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_recetas_5.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_recetas_6.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_tools_1.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_trinkets_1.yml`
- `build/guia-stellarity/gui_menus/g_guia_stellarity_weapons_1.yml`
- `build/guia-stellarity/gui_menus/guia_astral.yml`
- `build/guia-stellarity/gui_menus/guia_astral_3.yml`
