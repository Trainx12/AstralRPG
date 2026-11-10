# Tanda 2d: recoleccion de motosierra del Bosque

Correccion sobre la tanda 2c (393f641): las siete referencias del bucle de
objetos usan `loop-dropped item` para evitar la ambiguedad con el bucle de jugadores.
La condicion de la marca usa `scoreboard tags ... contains "ab.saw"`, compatible
con Skript; la forma anterior `"ab.saw" is in ...` tambien fallaba al cargar.
Fuente: `datapack-src/bosque_talar.py`; regenerar con `python bosque_talar.py`
desde `datapack-src/`.

## Actualizacion del servidor existente

| Archivo local | Destino |
|---|---|
| `build/bosque/astral_bosque.sk` | `plugins/Skript/scripts/astral_bosque.sk` |

Reemplazar solo ese script. Desde consola ejecutar:

```text
skript:skript reload astral_bosque
```

No requiere apagar ni reiniciar. No cambia el datapack ni el resource pack.
No ejecutar `bosquegenerar` ni `bosquereset`; conservar mundo, arboles y moldes.
Confirmar recarga exitosa sin errores en consola. Probar tala con motosierra,
inventario lleno y dos jugadores cercanos; comprobar que los drops manuales no
se recolectan por este bloque ni se duplican objetos.

## Verificacion local

`python -m unittest test_skript_loops test_tanda2c` desde `datapack-src/`.
La prueba recorre todos los `.sk` de `build/`, detecta referencias genericas
ambiguas en bucles anidados y reproduce el error anterior mediante mutacion.
El analisis reconoce selectores explicitos de entidades; no infiere tipos de
listas de variables. La validacion de carga en Paper complementa esta prueba.

Resultado: 11 pruebas aprobadas y los 12 Skript generados revisados. Paper local
26.1.2 confirmo `Successfully reloaded astral_minas.sk` y
`Successfully reloaded astral_bosque.sk`; se detuvo normalmente tras la prueba.
La carga local no sustituye las pruebas de juego indicadas arriba.

Despliegue pendiente: esta entrega no modifica el servidor de produccion.
