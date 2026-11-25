# Salir del pozo de Minas — 25/11/2026

Despliegue remoto pendiente. La documentacion actual del proyecto identifica
Empower como servidor activo y Aternos como copia. Confirmar el destino con el
dueno antes de instalar. No toca mundos, datapacks, resource pack ni moldes.

## Archivo y recarga

| Archivo local | Destino relativo en el servidor |
|---|---|
| `build/minas/Skript/scripts/astral_minas.sk` | `plugins/Skript/scripts/astral_minas.sk` |
| `build/lobby/TAB/secciones-config.yml` (solo las claves indicadas abajo) | `plugins/TAB/config.yml` |

Conservar un respaldo del script remoto y de TAB, y todas
las variables de Skript. La copia local conserva la ventana privada de Renacer
que ya estaba preparada antes de esta tarea.
El commit publica solo la mejora de salida: los cambios previos de esa ventana
y sus dependencias siguen locales, fuera del commit. Para desplegar sobre la
ventana ya instalada, usar el Skript del arbol local de esta entrega; no
sustituirlo por la version de Git sin integrar primero la ventana vigente.

Con el archivo verificado, subirlo y ejecutar en consola:

```text
skript reload astral_minas
minassubir privado
tab reload
```

Revisar la consola: la recarga debe finalizar sin errores. Basta recargar este
script; no requiere apagar ni reiniciar el servidor.

En TAB combinar solo `scoreboard.scoreboards.minas.lines` y agregar
`conditions.am_subir_row` desde el archivo local. Conservar las demas claves
del config remoto. La fila `%condition:am_subir_row%` va despues de Regeneracion;
se retira el encabezado redundante Minas para conservar el limite de 15 filas
incluyendo Party. La condicion usa `%objective_score_{am_subir}%=1`.
Skript crea y actualiza ese objetivo al cargar, entrar/cambiar de mundo y
cambiar `/minassubir publico|privado`; fuera de Minas vale 0.

## Prueba privada

1. Ejecutar `minassubir privado` desde consola y entrar con ByTrainx a una mina.
2. Bajar al pozo y ejecutar `/subir`: debe volver a la plataforma con sonido
   suave y barra de accion.
3. Repetir dentro de 3 segundos: debe impedir el segundo uso. Fuera del pozo,
   en una mina cerrada o en otro mundo, no debe trasladar al jugador.
4. A menos de 3 bloques del fondo (`PIT.y1 + 3`, hoy Y < 76), comprobar
   el aviso `&e⬆ Usa &f/subir &epara volver arriba`. En Y 76 o mas no debe
   aparecer; en Y 75 si. No debe repetirse antes de 5 minutos por jugador,
   aunque salga y vuelva al fondo dentro de ese intervalo. Cumplidos los
   5 minutos, debe volver a aparecer si sigue dentro de la zona.
   En privado, un jugador comun no debe recibir avisos ni usar `/subir`.
5. Probar pico, taladro y Minero de Vetas: deben conservar la proteccion del mapa.
6. Regenerar esa mina con `/minasreset N` y comprobar que `/subir` sigue
   funcionando. No ejecutar `/minasmoldes` para instalar esta mejora.
7. ByTrainx debe ver `⬆ Salir del pozo /subir` despues de Regeneracion; un
   jugador comun no la ve en privado. Verificar tambien cambio de mundo y
   reconexion. Al alternar el interruptor, el panel debe actualizarse.
8. Cada 10 minutos de actividad del script, solo jugadores en `astral_minas`
   autorizados reciben un mensaje: `⬆ Con /subir apareces arriba, en la
   plataforma de tu mina.` En privado solo ByTrainx; en publico todos los
   de Minas. No es un temporizador individual desde la entrada.

Solo despues del OK del dueno:

```text
minassubir publico
```

Desde entonces todos los jugadores de Minas pueden usar `/subir` y recibir sus
avisos. `/minassubir privado` vuelve a limitarlos a ByTrainx. El interruptor no
modifica bloques ni regenera las minas.
Nunca sustituir mundos ni usar Worlds > Upload en la fila world.

## Ajuste del aviso de barra de accion (25/11/2026)

Esta revision solo cambia el limite de altura y el intervalo individual del
aviso: `y < PIT.y1 + 3` (hoy Y < 76) y 5 minutos. El mensaje de chat cada
10 minutos, TAB y `/subir` conservan su comportamiento.
Si la mejora de salida ya esta instalada, actualizar unicamente
`build/minas/Skript/scripts/astral_minas.sk` en
`plugins/Skript/scripts/astral_minas.sk` y ejecutar `skript reload astral_minas`.
Conservar el estado actual de `minassubir`; no hace falta tocar TAB ni sus
interruptores para este ajuste. No requiere apagar ni reiniciar.

## Verificacion local de esta revision

- Regenerado con `python minas.py`; TAB y los demas archivos generados no cambian.
- 22 pruebas aprobadas: 5 de `test_minas_subir` y 17 de `test_economia`.
- Skript aislado para Git: carga y recarga correctas en Paper 26.1.2 / Java 25,
  sin errores de Skript. ExcellentEnchants informa la falta del proveedor de
  tooltips (PacketEvents o ProtocolLib) en el entorno local.
- Salida aislada comparada con el generador, usando la economia local previa.
  Limitacion anterior a esta tarea: el `minas.py` de HEAD importa constantes
  `MINAS_SUBA`, `MINAS_FORTUNA` y `MINAS_COSTO_FACTOR` todavia ausentes en la
  economia publicada. Una regeneracion desde un clon limpio queda pendiente
  de publicar esa tarea por separado. La prueba aislada del panel requiere
  tambien las regiones locales privadas; no se publican.
- Cambios previos de Renacer y economia conservados y excluidos del commit.
- Sin instalacion ni comandos remotos. Prueba del dueno y despliegue pendientes.
