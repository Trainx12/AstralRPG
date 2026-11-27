# Momia y ancestrales del Survival: escala inicial (27/11/2026)

Preparado localmente; NO instalado ni comprobado con cliente remoto.

El generador creaba el modelo BetterModel y luego cambiaba `minecraft:scale`.
Ese cambio posterior permite que piezas animadas y quietas usen transformaciones
de escalas distintas, compatible con la cabeza flotante reportada. Se corrige el
orden para los cinco `AST_MODEL_*_ancestral_mundo`, tanto en spawn como en carga.
No se cambia el tamaño configurado, las animaciones, los colores ni el balance.

La momia local tiene `head` como hijo de `body`, pivote Y24, torso hasta Y24 y
cabeza desde Y24. Ninguna animación traslada `head` de forma independiente.
`astral:mob/jefe_mundo` y `ancestral_evento.py` no vuelven a modificar scale.
La causa del incidente remoto queda pendiente de confirmar: la lectura oficial
del log de Empower falló (HTTP 400); no se pudo verificar la versión cargada de
AstralTamanos ni reproducir el síntoma con un cliente.

## Archivos de esta tarea

- `datapack-src/mobs/mythic.py`: orden de atributos antes del modelo, sólo ancestrales del Survival.
- `build/mythicmobs/skills/astral.yml`: salida regenerada; cinco modelos reordenados.
- `datapack-src/test_ancestral_modelo.py`: regresiones de orden, onSpawn/onLoad y cuello.
- `datapack-src/mobs/preview_momia_ancestral.py`: generador de comparación CPU.
- `build/previews/momia_ancestral_cabeza.png`: arte local idéntico antes/después; NO captura del fallo ni prueba remota.
- Este documento.

Los cambios previos de `MULT_APARICION` en mythic.py se conservan en el árbol
local y se excluyen del commit. No se tocó ni publicó AstralTamanos.java/JAR,
ya modificados por otra tarea. No cambia ningún resource pack ni datapack ZIP;
no corresponde subir packs a R2 ni actualizar SHA-1 por este arreglo.

## Verificaciones

Desde `datapack-src/`, con Python y las dependencias Pillow/PyYAML del proyecto:

```text
python mobs/mythic.py
python -m mobs.preview_momia_ancestral
python -m unittest test_ancestral_modelo test_modelos_efectos test_yeti_bastones_guia
```

19 pruebas aprobadas. Auditoría adicional de la fuente aislada para publicar:
genera exactamente el YAML de entrega; comparada con HEAD sólo cambia el orden
de cinco skills y conserva idénticos sus comandos y valores. Las demás skills
son idénticas. `git diff --check` sin problemas.

También se ejecutó `test_esqueletos_tamano`: su comparación histórica falla con
`KeyError: ZOGLIN` porque la tabla vieja no contempla el tipo actual; no se
modificó esa prueba ni los tipos de criatura. Ese fallo no depende del arreglo.

## Entrega exacta para Claude

| Archivo local | Destino en el servidor |
|---|---|
| `build/mythicmobs/skills/astral.yml` | `/plugins/MythicMobs/skills/astral.yml` |

SHA-256 del YAML:
`7ec70a986847fcf9531de680b810c4765b847ba00d40ffc44c549accadc682ae`.

No subir randomspawns, mascotas ni los ZIP locales: contienen trabajo previo.
No subir la imagen de revisión al servidor. No reemplazar mundos.

1. Antes de instalar, verificar en consola `version AstralTamanos` y `tamanos`.
   El ajuste posterior de cajas de AstralTamanos sigue existiendo: para ese caso
   hace falta el redibujado de 1.1.0 preparado en la tarea anterior. Si todavía
   está en 1.0.0, completar esa entrega separada en el reinicio autorizado.
   El JAR local previo es `build/tamanos/AstralTamanos.jar`, destino de esa otra
   entrega `/plugins/update/AstralTamanos.jar`, SHA-256
   `44a8101ce7ec742d77bf77b1922ef42f2859e67ba03aaae5d54d531cb414abde`.
   No se certificó aquí su instalación remota.
2. Respaldar el YAML remoto y subir únicamente el YAML de la tabla.
3. Sólo esta corrección YAML no requiere apagar ni reiniciar: ejecutar
   `mm reload` cuando Claude proceda al despliegue. NO se ejecutó aquí.
   Actualizar un JAR sí requiere reinicio; no usar PlugMan ni activar reinicios
   por servidor vacío. Respetar el reinicio autorizado/programado.
4. Revisar consola por errores de MythicMobs/BetterModel. Probar una momia
   ancestral NUEVA y los otros cuatro ancestrales, en reposo, caminando y
   atacando; esperar al menos 5 segundos para incluir AstralTamanos y comprobar
   también la recarga del chunk. No considerar entidades ya dibujadas como
   prueba suficiente del nuevo orden.
5. Confirmar cabeza y torso unidos, tamaño y caja de golpe conservados. Si
   persiste, conservar log y versión exacta para revisar el ajuste runtime;
   no dar por cerrado el incidente visual sólo con estas pruebas estáticas.
6. Una vez verificado en vivo, anunciar el arreglo en Discord según CLAUDE.md.
   Texto preparado: «Corregimos la aparición de los jefes ancestrales del
   Survival para evitar que sus partes se vean separadas».

Despliegue, revisión de consola real, cliente y anuncio pendientes de Claude.
