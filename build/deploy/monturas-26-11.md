# Monturas: clic, doma y propietario — 26/11/2026

Implementacion preparada; instalacion y consola remota pendientes de Claude. No subir desde APIs privadas.

AstralDecor 1.24.6 se arma sobre la copia 1.24.5 verificada del 24/11. Solo cambian
`astral/AstralMounts*.class` y la version de `plugin.yml`; los demas bytes internos
se comparan automaticamente. No incluye Gomera ni compila AstralDecor 1.25.x.

Antes de instalar, comparar el JAR que actualmente espera en `/plugins/update`:
SHA-256 base `a735f465310892a53d13d85003fcc503d866ac1e778b3dc98fc269c8122d245d`. Si difiere, **no reemplazarlo**: descargar la base actual
y revisar su delta antes de preparar otro parche. Esta copia local no verifica el estado remoto de hoy.

| Archivo local | Destino remoto | SHA-1 |
|---|---|---|
| `build/monturas/AstralDecor.jar` | `/plugins/update/AstralDecor.jar` | `316d89364c530b1cda783f1bc95e73f5214ec5b0` |
| `.local/terceros/AstralRPG-privado/build/entregas/monturas-26-11/mobs/astral.yml` | `/plugins/MythicMobs/mobs/astral.yml` | `62ebc03914d00fedaf7fd99c505d2f7039ef1509` |

El YAML privado conserva todos los bloques de su base y sustituye solo las seis monturas.
Base de YAML local: `.local/terceros/AstralRPG-privado/build/mythicmobs/mobs/astral.yml`.
SHA-256 base YAML: `3ba78f45751479bdb8dd6d8e725c1f73721a8c84f06e80a8ab9cb17e79748ab2`.
Comparar tambien ese archivo con el remoto antes de sustituirlo. Si difiere, descargar
el remoto a `.local/` y regenerar con `--mobs-base <archivo>` para preservar los otros cambios.
`skills/astral.yml` no cambia y no necesita subirse. No instalar el YAML publico encima del privado.

Requiere reinicio completo; `mm reload` solo no activa Java. Dejar el JAR en update para
el reinicio diario de las **05:00** autorizado en el pedido. No activar `reiniciopendiente`
ni apagar antes. Para evitar una mezcla de versiones, instalar el YAML con el servidor
apagado durante esa ventana y arrancar; el inicio carga ambos y no requiere recarga adicional.
No cambia datapack ni resource pack. No sustituir mundos ni usar Worlds > Upload.

Despues del inicio: verificar AstralDecor 1.24.6, MythicMobs sin errores y probar las seis
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

Discord, publicar solo cuando este en vivo:
> Arreglamos las monturas: ahora podes ensillarlas y subirte haciendo clic en su modelo.
> Al poner el huevo ya quedan domadas y a tu nombre. Otros jugadores no pueden usarlas.
> Tambien corregimos el acceso a las monturas voladoras y las terrestres quedan tranquilas al bajarte.
