# Decoraciones persistentes del Oceano Astral

AstralOceano 1.5.0 guarda decoraciones fuera del mundo, en
`plugins/AstralOceano/decor/<nombre>/`. Cada carpeta contiene `estructura.nbt`
y `meta.yml` con las coordenadas originales. Respaldar esta carpeta junto con
la configuracion del plugin. No subirla al repositorio publico si contiene barcos de terceros.

Pone los barcos, parate en el oceano y marca las dos esquinas con WorldEdit
(`//wand`, o `//pos1` y `//pos2`). Inclui todo el barco, los hologramas y el agua
que queres conservar. Ejecuta `/oceano decor guardar barco1`; listo.
Requiere OP o `astral.oceano.admin`. WorldEdit es opcional.

Sin WorldEdit, desde consola o como administrador:

```text
oceano decor guardar barco1 x1 y1 z1 x2 y2 z2
oceano decor lista
oceano decor poner barco1
oceano decor poner
oceano decor quitar barco1
```

Las seis coordenadas son bloques absolutos del mundo `oceano`, incluyendo ambas
esquinas. `poner` sin nombre restaura todas. `quitar` elimina el registro guardado;
conserva la construccion actual, que desaparecera en la siguiente regeneracion.
Para actualizar una decoracion, quitar su registro y guardar de nuevo la zona completa.
No superponer volumenes: se aplican en orden alfabetico y el ultimo gana.

Se guardan bloques (incluyendo aire, agua e inventarios), text displays,
item displays, marcos, cuadros, armor stands, barcos y vagonetas. Retira mobs,
objetos sueltos y entidades ajenas antes de guardar. Los jugadores no se guardan.
Las entidades reciben `astral.oceano.decor.<nombre>`: al restaurar se eliminan
las anteriores con ese tag en los chunks cargados y se recrean una sola vez.
Dejar los barcos decorativos quietos, dentro del volumen guardado.

No existe el limite de 48 bloques de los structure blocks. El limite administrativo
es 4.000.000 de bloques y 2048 por lado horizontal para evitar bloquear el servidor.
Guardar zonas ajustadas: el volumen entero se restaura, tambien sus cofres y menas.
No guardar el mapa entero ni usar `/oceano plantilla` para estas decoraciones.
La regeneracion sigue renovando los recursos fuera de los volumenes registrados.

Cada regeneracion de 72 horas restaura todas las decoraciones despues de cargar
el mundo y los chunks necesarios. No se reaplican automaticamente en cada arranque:
un reinicio normal conserva el mundo actual. `poner` permite recuperarlas manualmente.
Los avisos actuales del repositorio son menu/titulo/chat; no hay hologramas del
oceano generados por el repo que deban recrearse con otro comando. El texto que
ya pusiste a mano debe quedar incluido en una seleccion guardada.

Instalar el JAR requiere apagar y reiniciar. Guardar/poner/quitar no requiere
reinicio ni `mm reload`. Nunca sustituir mundos ni usar Worlds > Upload en `world`.
La implementacion usa la [Structure API de Paper](https://jd.papermc.io/paper/26.1.2/org/bukkit/structure/Structure.html).
