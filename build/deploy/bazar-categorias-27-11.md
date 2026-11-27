# Bazar 1.3.1 — categorías (27/11/2026)

Implementado localmente, sin despliegue ni subida a R2. Sigue `publico: false`.
Incluye la base autorizada 1.3.0 (precios, ventanas e interacciones).

Inicio: 0 Combate, 9 Bosque, 18 Océano, 27 Consumibles, 36 Especiales.
Combate es la selección inicial e incluye ambas Netheritas. Bosque tiene Madera
Estelar y Palo Reforzado; Océano tiene Perla Abisal y Coral Astral. IDs intactos.
SQLite no guarda categorías: no hay que transformar ni reemplazar la base.
El cargador reconoce categorías antiguas; una desconocida cae en Especiales.

| Archivo local | Destino |
|---|---|
| `build/bazar/AstralBazar.jar` | `plugins/update/AstralBazar.jar` |
| `build/bazar/productos.yml` | `plugins/AstralBazar/productos.yml` |
| `.local/terceros/AstralRPG-privado/build/entregas/bazar-categorias-27-11/AstralRPG-Textures.zip` | R2, publicación pendiente de Claude |

SHA-256 JAR: `e885c627d0780a3c15db8a7ede43ac751afb7313e150dd26609f12532dbe85dc`.
SHA-256 productos: `077451559f4a15557fa3fa13e0fdcca9e3812e036a89242cd5e47cbaef004187`.
SHA-1 FINAL: `5abd02f93162204a320123d2d0bc233a399d648c`.
Base exacta: `6fe11d1968fb35cb64931609e72f7037b8fe7798`. Delta verificado: 2 entradas,
solo texturas y fuente del inicio del Bazar. Glifos de hasta 224 px; no exceden 256.
No instalar `build/AstralRPG-Textures.zip`: conserva trabajo ajeno pendiente.
`ventanas.yml` está embebido en el JAR: no reemplazar el archivo operativo.
Conservar config, permisos, SQLite/WAL/SHM, respaldos y datos de jugadores.

1. Antes de instalar: `/bazar admin pausar`. Respaldar juntos AstralBazar,
   Essentials y datos de jugadores; no copiar la base local de ensayo al servidor.
2. Subir JAR a update y productos al destino indicado. Si no se admite update,
   apagar y reemplazar solo `plugins/AstralBazar.jar`. Aternos puede impedir
   instalar JAR propios: no usar APIs privadas ni eludir esa limitación.
   La documentación identifica Empower como principal y Aternos como copia.
3. Claude publica el FINAL a R2 justo antes del reinicio, verifica la descarga
   y pone `resource-pack-sha1=5abd02f93162204a320123d2d0bc233a399d648c` en `server.properties`, conservando su URL.
4. Requiere reinicio completo. Esperar el diario; no activar reiniciopendiente,
   no reiniciar por cuenta propia, no PlugMan ni `/reload` para el JAR.
5. Consola: versión AstralBazar 1.3.1, 88 productos, `publico=false`, sin errores.
   `/bazar admin reanudar`; `/bazar admin recargar` solo recarga configuración,
   no sustituye el reinicio de JAR/catálogo. Probar con ByTrainx en `/modo admin`
   y `/sala`, reingresar para descargar el pack. Otro jugador sigue sin acceso.
6. Dueño: comprobar las cinco etiquetas/clics, Netheritas en Combate, dos productos
   en Bosque y dos en Océano, órdenes previas, crear/cancelar/cobrar una orden.
   No abrir al público hasta su aprobación. Sin anuncio Discord mientras oculto.

Nunca sustituir mundos ni usar Worlds > Upload en la fila world.

Verificación: Paper final: 653 comprobaciones, 0 fallos (ensayo bazar-probe-20261127-003601), dos bots y reapertura real JVM; categorias antiguas/desconocidas, saldos, ordenes y filtros verificados. test_economia.py: 17 pruebas OK. Auditoria de terceros aprobada. Catalogo comparado con base inicial: solo seis campos categoria cambiaron.

Vistas CPU en `build/previews/bazar_inicio_27_11.png`, `bazar_bosque_27_11.png`
y `bazar_oceano_27_11.png`. No sustituyen la prueba visual del cliente.
Se reusan marco, espadas, caña y letras Gemini; árbol pixel en su misma paleta.
Revisión final del arte por el dueño pendiente.

Reproducción: `python datapack-src/ventanas_bazar26.py productos`,
`python datapack-src/bazar.py --solo-categorias --jdk <bin-Java25>`,
`python datapack-src/deploy_bazar_categorias_27_11.py --resultado "<resultado>"`.
Para solo compilar desde catálogo versionado, añadir `--solo-compilar` a bazar.py.
