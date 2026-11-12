# Disenos pendientes y retiro de alas — preparado, sin desplegar

Empower / Paper 26.1.2 / Java 25. Aternos es la copia antigua. No se accedio al servidor ni se publico R2.
Generar: `python datapack-src/deploy_disenos.py`, despues de regenerar menus, portales, lobby, datapack y pack publico, y compilar AstralDecor.
Base FINAL instalada indicada por el plan: `ad66e732862b13f8042c3b7e0e93844839d55607`. Base publica fija: `a1fe4f2a960396a720728edfcfd9a891c693597d`.
La base privada incluye el tren ya presente en ad66e73: sus entradas se conservan, pero no se regeneran ni se publican los cambios pendientes del tren.

## Archivos exactos y destinos

| Local | Destino |
|---|---|
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/menus/DeluxeMenus/gui_menus/arenas.yml` | `plugins/DeluxeMenus/gui_menus/arenas.yml` |
| `build/menus/DeluxeMenus/gui_menus/bazar.yml` | `plugins/DeluxeMenus/gui_menus/bazar.yml` |
| `build/menus/DeluxeMenus/gui_menus/cofre_bosque.yml` | `plugins/DeluxeMenus/gui_menus/cofre_bosque.yml` |
| `build/menus/DeluxeMenus/gui_menus/cofre_cumbre.yml` | `plugins/DeluxeMenus/gui_menus/cofre_cumbre.yml` |
| `build/menus/DeluxeMenus/gui_menus/cofre_forja.yml` | `plugins/DeluxeMenus/gui_menus/cofre_forja.yml` |
| `build/menus/DeluxeMenus/gui_menus/cofre_mina.yml` | `plugins/DeluxeMenus/gui_menus/cofre_mina.yml` |
| `build/menus/DeluxeMenus/gui_menus/cofre_santuario.yml` | `plugins/DeluxeMenus/gui_menus/cofre_santuario.yml` |
| `build/menus/DeluxeMenus/gui_menus/cofre_tumba.yml` | `plugins/DeluxeMenus/gui_menus/cofre_tumba.yml` |
| `build/menus/DeluxeMenus/gui_menus/comandos.yml` | `plugins/DeluxeMenus/gui_menus/comandos.yml` |
| `build/menus/DeluxeMenus/gui_menus/cosmeticos.yml` | `plugins/DeluxeMenus/gui_menus/cosmeticos.yml` |
| `build/menus/DeluxeMenus/gui_menus/cosmeticos_sombreros.yml` | `plugins/DeluxeMenus/gui_menus/cosmeticos_sombreros.yml` |
| `build/menus/DeluxeMenus/gui_menus/dropper_facil.yml` | `plugins/DeluxeMenus/gui_menus/dropper_facil.yml` |
| `build/menus/DeluxeMenus/gui_menus/dropper_h4rs.yml` | `plugins/DeluxeMenus/gui_menus/dropper_h4rs.yml` |
| `build/menus/DeluxeMenus/gui_menus/expediciones.yml` | `plugins/DeluxeMenus/gui_menus/expediciones.yml` |
| `build/menus/DeluxeMenus/gui_menus/fragmentos.yml` | `plugins/DeluxeMenus/gui_menus/fragmentos.yml` |
| `build/menus/DeluxeMenus/gui_menus/gacha_cosmeticos.yml` | `plugins/DeluxeMenus/gui_menus/gacha_cosmeticos.yml` |
| `build/menus/DeluxeMenus/gui_menus/gacha_monturas.yml` | `plugins/DeluxeMenus/gui_menus/gacha_monturas.yml` |
| `build/menus/DeluxeMenus/gui_menus/gacha_rpg.yml` | `plugins/DeluxeMenus/gui_menus/gacha_rpg.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_bombardero.yml` | `plugins/DeluxeMenus/gui_menus/mascota_bombardero.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_brujita.yml` | `plugins/DeluxeMenus/gui_menus/mascota_brujita.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_canonero.yml` | `plugins/DeluxeMenus/gui_menus/mascota_canonero.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_desierto.yml` | `plugins/DeluxeMenus/gui_menus/mascota_desierto.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_encapuchado.yml` | `plugins/DeluxeMenus/gui_menus/mascota_encapuchado.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_frondoso.yml` | `plugins/DeluxeMenus/gui_menus/mascota_frondoso.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_ghastito.yml` | `plugins/DeluxeMenus/gui_menus/mascota_ghastito.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_hondero.yml` | `plugins/DeluxeMenus/gui_menus/mascota_hondero.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_honguito.yml` | `plugins/DeluxeMenus/gui_menus/mascota_honguito.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_jungla.yml` | `plugins/DeluxeMenus/gui_menus/mascota_jungla.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_llamita.yml` | `plugins/DeluxeMenus/gui_menus/mascota_llamita.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_micelio.yml` | `plugins/DeluxeMenus/gui_menus/mascota_micelio.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_nieve.yml` | `plugins/DeluxeMenus/gui_menus/mascota_nieve.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_pantano.yml` | `plugins/DeluxeMenus/gui_menus/mascota_pantano.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_pradera.yml` | `plugins/DeluxeMenus/gui_menus/mascota_pradera.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_sabana.yml` | `plugins/DeluxeMenus/gui_menus/mascota_sabana.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_saqueador.yml` | `plugins/DeluxeMenus/gui_menus/mascota_saqueador.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascotas.yml` | `plugins/DeluxeMenus/gui_menus/mascotas.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascotas_2.yml` | `plugins/DeluxeMenus/gui_menus/mascotas_2.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascotas_3.yml` | `plugins/DeluxeMenus/gui_menus/mascotas_3.yml` |
| `build/menus/DeluxeMenus/gui_menus/mazmorras.yml` | `plugins/DeluxeMenus/gui_menus/mazmorras.yml` |
| `build/menus/DeluxeMenus/gui_menus/parkour.yml` | `plugins/DeluxeMenus/gui_menus/parkour.yml` |
| `build/menus/DeluxeMenus/gui_menus/portales.yml` | `plugins/DeluxeMenus/gui_menus/portales.yml` |
| `build/menus/DeluxeMenus/gui_menus/principal.yml` | `plugins/DeluxeMenus/gui_menus/principal.yml` |
| `build/menus/DeluxeMenus/gui_menus/subastas.yml` | `plugins/DeluxeMenus/gui_menus/subastas.yml` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos.yml` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos_garantia.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos_garantia.yml` |
| `.local/terceros/AstralRPG-privado/build/entregas/disenos-pendientes/AstralRPG-Textures.zip` | R2: objeto `AstralRPG-Textures.zip` |

FINAL SHA-1: `d7310b324b82bf0c060e70f9febeb152c446a1a2`. 5291 referencias auditadas; 240 entradas nuevas/cambiadas, 8 retiradas. Manifiesto privado: `build/entregas/disenos-pendientes/procedencia.json`.
El ZIP publico contiene reservas propias y vanilla. NO instalarlo como FINAL.

## Instalacion pendiente

1. Respaldar los destinos y server.properties. Esperar sala vacia y APAGAR el servidor.
2. Reemplazar los archivos de la tabla. JAR 1.6.0 y datapack requieren reinicio completo. No instalar plugins de prueba ni copiar configuraciones del Paper local.
3. Eliminar `plugins/DeluxeMenus/gui_menus/cosmeticos_alas.yml` y solo la entrada `gui_menus.cosmeticos_alas` de config.yml. Conservar los demas registros. Referencia generada: `build/menus/DeluxeMenus/config-gui_menus.yml`.
4. AstralDecor integra su catalogo de gorros y retira cosmetics.alas sin reemplazar las configuraciones de NPC. Conservar datos de LuckPerms y playerdata: habilitan la compensacion.
5. Publicar el FINAL solo al desplegar y verificar su descarga publica:

```text
python tools/subir_pack_r2.py .local/terceros/AstralRPG-privado/build/entregas/disenos-pendientes/AstralRPG-Textures.zip
```

Luego fijar `resource-pack-sha1=d7310b324b82bf0c060e70f9febeb152c446a1a2` y conservar la URL R2. No ejecutar esta subida como parte de esta entrega.
6. Encender y revisar Done, AstralDecor 1.6.0 y ausencia de errores nuevos de recetas, modelos, menus o cajas. El arranque carga YAML y datapack; no hace falta /reload.
7. Si despues solo se ajustan YAML: `dm reload` y `crates reload`. Nunca PlugMan ni recarga global para cambiar el JAR.
8. No reemplazar mundos ni regiones; nunca Worlds > Upload en world. Solo sustituir el ZIP del datapack en su carpeta.

El holograma de la gacha debe decir «Titulos y gorros». No ejecutar todo build/lobby/comandos.txt para cambiar una linea: preservar posicion y vendedores existentes.

## Comportamiento y compensacion

- Asura y Carnivora salen de catalogo, gacha normal y garantia, navegacion y seguimiento de AstralDecor. Tambien se retira el seguimiento de los items de segunda mano: era el mismo sistema.
- Se retiran sus recetas. Los IDs fisicos antiguos siguen resolviendo a una pluma vanilla como recuerdo, sin vuelo, atributos ni geometria de alas. Los nuevos llevan nombre/lore de recuerdo; no se destruyen ni reconstruyen objetos antiguos, por lo que conservan nombres personalizados y componentes.
- Compensacion permanente sin cobro: permiso antiguo de alas Carnivora habilita Sombrero Carnivora; permiso de alas Asura habilita Cuernos de Diablo. No se gastan ni revocan permisos. Abrir /cosmeticos y elegir el gorro. Las posesiones fisicas se conservan como recuerdo; no se convierten en dinero.
- Gorros: el sistema anterior ocultaba el ItemDisplay al portador y usaba un anclaje/escala independientes de la cabeza. Ahora se envia equipo visual HEAD de Minecraft al portador y observadores, sin modificar inventario, armadura ni defensa. Visible en tercera persona; un casco real tiene prioridad. No se afirma un diagnostico remoto: no hubo acceso al servidor real.
- /cosmeticos tiene botones propios GORROS y TITULOS. Los gorros usan el mismo marco ilustrado. Las 23 mascotas tienen el mismo detalle de nivel, experiencia, mejoras, invocar y descansar; las 17 nuevas vuelven a su pagina correcta.

## Iconos y vistas

Principal: Fragmentos reutilizaba Habilidades y Duelos reutilizaba Arenas. Ahora tienen dibujos propios; Cosmeticos muestra un gorro. Se conservan los otros iconos propios.
Submenus: se reemplazan las reservas vanilla de navegacion, comandos, cofres, gacha y minijuegos por iconos de servicio propios. Mochilas, Proteccion y Recetas tienen accesos en Comandos. Tren y Santuario incluyen icono propio preparado: no se inventa un boton /tren ni se modifica el tren pendiente; Santuario conserva su tarjeta ilustrada.
Inventario exacto antes/despues de todos los botones accionables: `build/previews/disenos/auditoria-iconos.json`. Los premios de misiones conservan su objeto vanilla porque representan el premio real. Flechas/cerrar/candados comparten simbolo de navegacion deliberadamente.
Vistas publicas antes/despues de cada menu cambiado: `build/previews/disenos/`. Los detalles nuevos, las paginas 2/3 y gorros con arte licenciado estan exclusivamente en el privado, `build/entregas/disenos-pendientes/previews/`. Son renders CPU de glifos y sprites; las reservas vanilla se indican con su inicial, no son capturas de juego. Los retratos salen de los modelos 3D adaptados, sin ImageGen ni copia al pack publico.

## Verificacion y limites

Compilacion Java 25 correcta. verify.py: JSON, funciones/loot, sprites, IDs de misiones y secuencias de mazmorras correctos. Auditoria del FINAL valida todas las referencias.
Paper local con dos jugadores NMS simulados: 14 comprobaciones aprobadas, paquetes HEAD a portador/observador, casco real intacto, reaparicion al quitar casco, quitar gorro, compensacion Asura, persistencia y ausencia de displays/pasajeros. Dependencias de encantamientos incluidas. No valida render de cliente ni integraciones remotas.
Suite completa: 245 pruebas, 242 aprobadas y tres fallos historicos de test_alas_casco (comparacion con 75f49c4), test_oleadas_tanda2 (hashes de Santuario) y test_urgente (rutas anteriores de Santuario). Los tres se reproducen tambien en la copia del commit inicial a1fe4f2; no se modifican esos tests ni sus fuentes por esta tarea. Las 93 regresiones focalizadas de las areas modificadas pasan.
Antes de dar conformidad visual: dos clientes vanilla con este FINAL aceptado, probar sin casco y con casco, tercera persona propia y desde observador, equipar/quitar los 20 gorros, cambio de mundo/reconexion/muerte y AxGraves; recorrer /menu, submenus, /mascotas paginas 1–3 y todos los detalles, gacha normal/garantia. Registrar capturas privadas y consola real. Despliegue y estas pruebas siguen pendientes.
