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
4. Bajo Y 85, comprobar el aviso `&e⬆ Usa &f/subir &epara volver arriba`
   y que no se repita antes de 60 s.
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

## Verificacion local de esta revision

- Regenerado con `python minas.py`; TAB queda sin cambios.
- 4 pruebas de `test_minas_subir` y 17 de `test_economia` aprobadas.
- Skript local y Skript aislado para Git: carga y recarga correctas en Paper
  26.1.2 / Java 25, sin errores de Skript. ExcellentEnchants avisa que falta un
  proveedor de tooltips (PacketEvents o ProtocolLib) en el entorno de prueba.
- Salida publicada comprobada contra el generador aislado. Los cambios previos
  de Renacer y de economia en la documentacion quedan locales, fuera del commit.
- Sin instalacion ni comandos en el servidor remoto; prueba del dueno pendiente.
