# Monturas: etiqueta y seguir/quieta (privado) — 26/11/2026

Implementacion preparada; instalacion y consola remota pendientes de Claude. No subir desde APIs privadas.

AstralDecor 1.24.7 se arma sobre la copia 1.24.5 verificada del 24/11. Solo cambian
`astral/AstralMounts*.class` y la version de `plugin.yml`; los demas bytes internos
se comparan automaticamente. No incluye Gomera ni compila AstralDecor 1.25.x.

Antes de instalar, comparar el JAR que actualmente espera en `/plugins/update`:
SHA-256 base `a735f465310892a53d13d85003fcc503d866ac1e778b3dc98fc269c8122d245d`, o la entrega anterior 1.24.6
`a9e90fff2fb7b702ffc6646c816376dfb4e3ed7070f937652b2f7a4bbc13ac1b` (ba8f51d).
Ambas son compatibles con este parche acumulado. Si difiere de ambas, **no reemplazarlo**: descargar la base actual
y revisar su delta antes de preparar otro parche. Esta copia local no verifica el estado remoto de hoy.

| Archivo local | Destino remoto | SHA-1 |
|---|---|---|
| `build/monturas/AstralDecor.jar` | `/plugins/update/AstralDecor.jar` | `0ea575f26a8740a946574ecd58c265b88f0de177` |
| `.local/terceros/AstralRPG-privado/build/entregas/monturas-26-11/mobs/astral.yml` | `/plugins/MythicMobs/mobs/astral.yml` | `8ab9cd85d80405900722c3559ede5cd18c56e7a5` |

El YAML privado conserva todos los bloques de su base y sustituye solo las seis monturas.
Base de YAML local: `.local/deploy-26-11-monturas/remoto-mobs-1795717581.yml`.
SHA-256 base YAML: `ce56fc92fb0b74fa886c250ba02cc2d1bd38cc52d5f0634359a264725486d1e0`.
Tambien se acepta como base remota el YAML de ba8f51d (SHA-1
`62ebc03914d00fedaf7fd99c505d2f7039ef1509`), sobre el que solo cambia la
condicion del temporizador de IA de las dos voladoras.
Comparar tambien ese archivo con el remoto antes de sustituirlo. Si difiere, descargar
el remoto a `.local/` y regenerar con `--mobs-base <archivo>` para preservar los otros cambios.
`skills/astral.yml` no cambia y no necesita subirse. No instalar el YAML publico encima del privado.

Requiere reinicio completo; `mm reload` solo no activa Java. Dejar el JAR en update para
el reinicio diario de las **05:00** autorizado en el pedido. No activar `reiniciopendiente`
ni apagar antes. Para evitar una mezcla de versiones, instalar el YAML con el servidor
apagado durante esa ventana y arrancar; el inicio carga ambos y no requiere recarga adicional.
No cambia datapack ni resource pack. No sustituir mundos ni usar Worlds > Upload.

Despues del inicio: verificar AstralDecor 1.24.7, MythicMobs sin errores y probar las seis
monturas con cliente real, en survival y creativo: huevo, silla, clic en el modelo, WASD,
espacio, Shift, otro jugador, vuelo y Lagarto sumergido. Revisar asiento y animacion de caminar.
Si se retoca luego solo YAML, comando de consola `mm reload`; evitar recargas repetidas.

Reproduccion desde la raiz (JDK 25 y dependencias Python Pillow/PyYAML):
```
python datapack-src/deploy_monturas_2611.py --java <java25> --server .local/testsrv --base .local/deploy-24-11-recetas-todas/verif-1795554672.jar
python tools/probar_monturas_paper.py --java <java25> --base .local/testsrv
cd datapack-src
python -m unittest test_monturas_1711 -v
```

El ensayo usa eventos Bukkit de clic y el evento de BetterModel con hitboxes reales,
sin depender de ejecutar astralmount por consola. Comprueba conductor nativo, atributos,
migracion, propiedad, antirrobo, sillas, controlador FLY, lobby y vectores de nado.
Es un jugador NMS simulado: no acredita desplazamiento de cliente, asiento ni animacion
visual. Esas verificaciones quedan pendientes en el servidor remoto.

Nuevo en 1.24.7, oculto: solo ByTrainx puede nombrar con etiqueta de yunque y alternar
SEGUIR/QUIETA con **Shift + clic derecho**, sin silla ni etiqueta en la mano.
Clic normal sigue montando. El nombre consume una etiqueta en survival, no en creativo.
Nombre y modo se guardan en PDC; texto separado no persistente se reconstruye al cargar.
Seguimiento cada 10 ticks sobre lista propia; no cruza mundos. Lista positiva:
`world`, `world_nether`, `world_the_end`, `sala_dueno`. Desconectado = quieta.
TP a mas de 20 bloques solo si hay piso y volumen despejado cerca, dentro del borde.
Sin lugar seguro espera. El texto flotante y vuelo necesitan revision visual del dueno.
No abrir al publico ni conceder permisos: esta entrega usa el filtro directo ByTrainx.

Discord para la funcion NUEVA (guardar, publicar solo cuando el dueno la abra):
> Ahora podes ponerle nombre a tu montura con una etiqueta.
> Con Shift + clic podes elegir si te sigue o se queda quieta; te avisa por el chat.

Discord del arreglo PUBLICO anterior, solo cuando quede en vivo:
> Arreglamos las monturas: ahora podes ensillarlas y subirte haciendo clic en su modelo.
> Al poner el huevo ya quedan domadas y a tu nombre. Otros jugadores no pueden usarlas.
> Tambien corregimos el acceso a las monturas voladoras y las terrestres quedan tranquilas al bajarte.
