# Nucleo de Venta Automatica — privado, 27/11/2026

Estado: implementado localmente; no instalado ni recargado en servidor remoto.
Sin arte nuevo, sin cambios de resource pack, sin Guia ni Discord.

## Archivos y despliegue por Claude

La documentacion identifica Empower como servidor principal y Aternos como copia.
Confirmar el servidor de destino antes de instalar. Nunca sustituir mundos ni usar Worlds > Upload.

Instalacion recomendada, limitada a esta tarea:

1. Descargar una copia del `plugins/Skript/scripts/astral_minas.sk` realmente instalado.
2. Desde la raiz: `python datapack-src/deploy_autoventa.py --server-script RUTA_A_LA_COPIA.sk`.
   El generador exige la funcion `am_give` anterior exacta y rechaza un script ya parcheado.
   Produce `build/autoventa/astral_minas.sk` conservando todo el resto del archivo remoto.
   Si rechaza la copia, comparar manualmente con `build/autoventa/astral_minas-autoventa.patch`;
   no reemplazar el script remoto por la version acumulada local a ciegas.
3. Subir `build/autoventa/AstralRPG-Autoventa.zip` a
   `world/datapacks/AstralRPG-Autoventa.zip`. SHA-256:
   `fdfb664929973f672d354a622ef089216cbf5fb2cb08009cbe01d626533cb0f1`.
   Solo contiene pack.mcmeta, loot_table/item/autoventa.json y function/autoventa/identify.mcfunction.
4. Subir la copia parcheada `build/autoventa/astral_minas.sk` a
   `plugins/Skript/scripts/astral_minas.sk`, conservando respaldo y variables de Skript.
5. El datapack requiere reinicio completo segun las reglas del proyecto: coordinar la instalacion
   con el reinicio diario o uno autorizado. No ejecutar `reload` global, `minasmoldes`, `minasactivar`
   ni comandos de instalacion/mapas. No hace falta apagar para transferir estos archivos;
   el reinicio es para cargarlos. Con el datapack ya cargado, solo cambios posteriores del script:
   `skript reload astral_minas`.
6. Comprobar consola sin errores de Skript/datapack y `datapack list enabled`.
   Si el pack queda deshabilitado: `datapack enable "file/AstralRPG-Autoventa.zip" last`.
   Dependencias existentes: Skript, Vault/EssentialsX, AstralMinasLimite, AuraSkills,
   PlaceholderAPI y DeluxeMenus. Verificar `papi parse ByTrainx %auraskills_mining%` numerico.

Alternativa acumulada: `build/AstralRPG-Items.zip` -> `world/datapacks/AstralRPG-Items.zip`
y `build/minas/Skript/scripts/astral_minas.sk` -> `plugins/Skript/scripts/astral_minas.sk`.
**No usar los acumulados locales sin revisar los cambios previos**: el workspace conserva trabajo
ajeno pendiente (incluidos Renacer y Nudillos). El commit de esta tarea separa sus propios hunks
y su ZIP publico de esos cambios. La entrega aditiva evita arrastrarlos al servidor.
No instalar dos scripts de Minas activos. No requiere JAR nuevo, texturas ni R2.

## Comandos de consola

Dar uno al dueno conectado:

`minecraft:loot give ByTrainx loot astral:item/autoventa`

Efecto privado (tambien es el estado por defecto si no existe la variable):

`autoventa privado`

Abrir el efecto SOLO cuando el dueno lo autorice:

`autoventa publico`

El interruptor solo controla el efecto; **la receta sigue desactivada**.
Para habilitar la receta en una futura publicacion autorizada, importar `RECIPE` de `autoventa.py`
y ejecutar `RECIPES.append(RECIPE)` en `build.py` antes de `prepare_mesa`; regenerar datapack,
menus y runtime segun docs/GUIA.md. Esa apertura debera incorporar su entrada a la Guia.
`receta-desactivada.json` es la especificacion de la receta reservada; NO se sube como receta vanilla.

## Receta final reservada (9 ingredientes; no consume equipo)

| Ingrediente | Cantidad |
| --- | ---: |
| Cristal Arcano Refinado | 16 |
| Bloque de netherita (compacto de la mina mas alta) | 64 |
| Bloque de diamante (compacto anterior) | 64 |
| Esencia del Nether | 16 |
| Estrella del Nether | 2 |
| Bloque de esmeralda | 32 |
| Ojo de ender | 16 |
| Netherita Reforzada | 16 |
| Nucleo de Furia | 16 |

Sin mochila para no consumir inventarios de ExpendableBackpacks. Las 64 unidades de netherita
incluyen y superan las cuatro adicionales de la propuesta. Sin limite de nueve unidades de mesa:
la futura receta corresponde a la Forja Astral.

## Funcionamiento y prueba pendiente del dueno

Corazon del mar vanilla con brillo, no apilable, PDC AuraSkills Mineria 100.
Compara ID real por custom_data en hotbar, inventario y secundaria; no admite un item renombrado.
Solo Minas Astrales, solo ByTrainx por defecto. Consulta Mineria fresca mediante el mismo puente
DeluxeMenus/PAPI existente en armas especiales; sin dato numerico no vende. Aviso una vez por bloqueo.
Enfriamiento en memoria de dos segundos. Reutiliza `am_sell_value(p, true)` y acredita Vault;
conserva precios, recorte, multiplicador y Renacer actuales. PDC invisible no impide vender.
Recupera exclusivamente drops nuevos de ese picado y conserva su PDC; si no entran, vuelven al piso.
Si hubo venta, barra de accion y sonido suave; sin venta conserva el aviso de inventario lleno.

Prueba remota pendiente: llenar inventario con minerales, probar Mineria 99/100, secundaria,
jugador ajeno en privado, publico solo con permiso del dueno, equipo/objetos con nombre,
inventario sin vendibles y PDC real de AstralMinasLimite. Confirmar saldo y consola.

## Regeneracion y verificaciones

Desde datapack-src: `python build.py`, `python minas.py`, `python deploy_autoventa.py`.
Pruebas: `python -m unittest test_autoventa test_minas_subir -v`.
Ensayo aislado: `python tools/probar_autoventa_paper.py --java RUTA_JAVA25 --base RUTA_PAPER_LOCAL`.
El ensayo usa un doble local de DeluxeMenus/PAPI; la expansion real y el cliente deben comprobarse remotamente.
No se afirma ningun despliegue remoto.

Verificado el 27/11: ambos generadores y la entrega corren sin error; 9 pruebas Python aprobadas.
Paper 26.1.2-74 + Skript 2.17.1: carga sin errores y 31 comprobaciones funcionales aprobadas
(saldo real de Essentials igual a Venta rapida, slots 0/10/35/secundaria, PDC recuperado,
drops ajenos, nombre/lore protegidos, enfriamiento, Mineria 99, lectura ausente,
sin vendibles, item renombrado, visitante privado/publico y fuera de Minas).
Auditoria acotada a los 13 archivos de la tarea con `tools/verificar_terceros.py`: sin arte privado.
El ensayo registra avisos de actualizacion de Skript y del proveedor opcional de tooltips de
ExcellentEnchants; no impiden cargar ni ejecutar las pruebas. Los logs quedan privados en `.local/`.
