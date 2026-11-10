# Tanda 2c: Forja y Bosque Astral

Generado por `datapack-src/tanda2c_entrega.py`. Preparado localmente, SIN desplegar.
El servidor activo documentado es Empower; Aternos es la copia anterior. Confirmar el
panel y la versión a actualizar con Claude. Esta entrega requiere la Tanda 2 instalada.

## Archivos locales y destinos exactos

| Archivo local | Destino del servidor |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/minas/Skript/scripts/astral_minas.sk` | `plugins/Skript/scripts/astral_minas.sk` |
| `build/bosque/astral_bosque.sk` | `plugins/Skript/scripts/astral_bosque.sk` |
| `build/mythicmobs/mobs/astral.yml` | `plugins/MythicMobs/mobs/astral.yml` |
| `build/mythicmobs/mobs/forja.yml` | `plugins/MythicMobs/mobs/forja.yml` |

`build/bosque/instalacion.txt` es una guía local; en un bosque existente usar solo
el bloque final de actualización de NPC, no crear el mundo ni ejecutar bosquegenerar.
Nunca sustituir mundos ni usar Worlds > Upload sobre world.

## Instalación

Apagar el servidor y reemplazar exclusivamente los cinco archivos anteriores. Iniciar
de nuevo: el reinicio es necesario para el datapack según el procedimiento del proyecto.
El arranque carga MythicMobs y Skript. Si hace falta recargar por separado, desde consola:

```text
mm reload
skript:skript reload astral_minas
skript:skript reload astral_bosque
```

Cargar Minas antes de Bosque: comparten `am_sale_menu` y `am_give`. No hace falta
`dm reload`: se reutiliza la interfaz de Minas, sin archivos nuevos de DeluxeMenus.
Después instalar los dos aldeanos (se eliminan solo instancias de esos dos tipos):

```text
rg flag -w astral_bosque __global__ mob-spawning allow
mm mobs kill astral_npc_bosque_venta
mm mobs spawn astral_npc_bosque_venta 1 astral_bosque,-1.5,65,56.5,90,0
mm mobs kill astral_npc_bosque_viaje
mm mobs spawn astral_npc_bosque_viaje 1 astral_bosque,-7.5,65,56.5,-90,0
rg flag -w astral_bosque __global__ mob-spawning deny
```

## Cambios y comprobaciones pendientes en servidor

- Forja: cuatro funciones ahora usan summon vanilla. Magma `Size:0` no se divide;
  escala 4 conserva el tamaño del cubo grande, vida base 16 y ataque base 6 antes de
  `mob/roll`. Conserva tags de sala/oleada/vanilla, Glowing y resistencia al fuego.
  Se retiran las dos definiciones MythicMobs de magma que ya no se usan.
- Consola: confirmar que cargan spawn12/spawn13 de sala1/w1 y spawn11/spawn12 de
  sala2/w2 sin Unknown or incomplete command. Completar ambas oleadas: no debe haber hijos.
- Bosque: comprobar ambos aldeanos en pasto, mirando al spawn; viaje a Minas y Lobby.
- Venta: comparar saldo previo, vista previa y saldo final; solo maderas, conservar
  minerales, equipo con nombre/lore y estrella. Repetir Minas para descartar regresiones.
- Tala: herramienta normal y motosierra, Fortuna, pila completa sin espacio, dos jugadores,
  tirar madera manualmente cerca del corte (no debe entrar al recolector), desconexión y
  vuelta antes de recoger. Verificar ausencia de duplicados, pérdida y componente ab_saw
  en los objetos recibidos. Revisar errores de Skript y comandos data en consola.

Precios pendientes (sin inventar, no se venden): stripped_cherry_log, stripped_cherry_wood, stripped_mangrove_log, stripped_mangrove_wood.
Solicitar los cuatro precios reales de EconomyShopGUI y actualizar el catálogo antes de
habilitar esas variantes. Las otras 36 variantes tienen precio fijo.

## Pack y verificaciones locales

- Resource pack SIN cambios: SHA-1 `7a99922fb1734f4f80c64cee3f363a7b4d2404cb`. No subir pack, ni cambiar URL/SHA.
- Datapack de esta entrega: SHA-1 `2db5c1f4b7f16d88081468c325709c95cc3e17c2`.
- Ejecutar desde datapack-src: `python build.py`, `python bosque_talar.py`,
  `python minas.py`, `python mobs/mythic.py` y `python tanda2c_entrega.py`
  (este último genera forja con `mob_yml` y esta guía).
- `python -m unittest discover -p "test_*.py"` y `python verify.py`.
- Resultado local: 148 pruebas aprobadas; verify.py aprobado (avisos de obsolescencia de Pillow).
- Prueba nueva recorre todos los mcfunction del ZIP y directorio generado; rechaza
  comandos ajenos a Minecraft, también dentro de execute/return. verify.py la incluye.
  Es una validación de raíces: no equivale a Brigadier ni prueba la sintaxis completa.
  No existe un lector completo de comandos de Minecraft entre las herramientas versionadas.
- No hubo prueba en Paper/cliente real ni revisión de la consola del servidor en esta tanda.
  Santuario y modelos 3D no se modifican.
