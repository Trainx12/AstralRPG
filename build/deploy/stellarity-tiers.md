# Stellarity por tiers — entrega privada del 26/11/2026

Estado: preparado localmente. No se subio ni se comprobo el servidor remoto.
El servidor principal documentado es Empower (Paper 26.1.2 / Java 25); Aternos es la copia.
Claude continua la instalacion mediante navegador autorizado. No usar APIs privadas ni sustituir mundos.

## Versiones y alcance

AstralStellarity 1.0.0 + AstralMesa 1.5.3, sobre Stellarity 5.4.2 original
(SHA-256 6c42ac245cecd3882ec3fc160d2fdf31a74d88b16a29a6332cd52d3bb8fa498c).
No reemplazar ese ZIP. No cambia el resource pack; no subir R2 ni cambiar SHA-1.
No subir el ZIP compartido AstralRPG-Items.zip de este workspace: contiene trabajo anterior ajeno a esta tarea.
La compatibilidad va en un complemento separado con SOLO player/def de Astral.
El generador principal build.py incorpora la misma correccion para futuras compilaciones completas.

Tabla unica: datapack-src/stellarity_tiers.py (150 objetos: equipo con tier y consumibles con precio).
Prismatic Punch se compara con ballesta, Kaleidoscope con espada, Tamaris con espada,
Fluffy Hammer con hacha; The End es spirit_dagger y la espada antigua alpha_wooden_sword.
Las herramientas conservan la regla vigente: no elevan el tier del mundo; armas y armaduras si.
Los libros de esta version no infligen dano fijo: Luz da Regeneracion, proporcional por astral_gameplay.sk.
Prismember y Starless Scythe calculan su habilidad desde el atributo: no se multiplican otra vez.
Penetracion Kohara sin atacante directo se atribuye solo si hay UN jugador con kohara.attacker en ese mundo.

## Instalacion exacta

Todas las rutas y SHA-256 estan en [manifest.json](../stellarity/manifest.json).
Cada entrada enumera archivo local y destino completo en el servidor (incluidos los 138 menus).

- build/stellarity/AstralStellarity.jar -> plugins/AstralStellarity.jar (primera instalacion).
  Para actualizar una instalacion existente: plugins/update/AstralStellarity.jar.
- build/mesa/AstralMesa.jar -> plugins/update/AstralMesa.jar (conservar una sola copia activa).
- build/stellarity/tiers.json -> plugins/AstralStellarity/tiers.json.
- build/stellarity/config.yml -> plugins/AstralStellarity/config.yml SOLO la primera vez: publico: false.
- build/stellarity/AstralStellarity-Compat.zip -> world/datapacks/AstralStellarity-Compat.zip.
- Cada build/stellarity/menus/*.yml -> plugins/DeluxeMenus/gui_menus/<mismo nombre>.
  Son menus ya registrados; conservar config.yml de DeluxeMenus y su permiso privado.

Antes de instalar el complemento, comparar el player/def del datapack remoto con la base SHA-256 indicada
abajo. Si difiere, fusionar SOLO las dos exclusiones astral.stellarity por pieza (barra visual y talisman),
regenerar y verificar antes de subir: no pisar una funcion remota mas nueva con esta base.
En futuras entregas completas que ya tengan el hook de build.py, retirar este complemento para que no
oculte una version posterior de player/def. No retirar Stellarity-5.4.2.zip.

AstralMesa: NINGUNA clave nueva para fusionar. Lee las bases base-arma/base-armadura YA cargadas del servidor;
utilidades cuestan 50% de arma, armaduras/alas/caballo usan base-armadura, materiales/comida/pociones tabla fija.
No subir build/mesa/config.yml. Conservar los valores remotos x2, los interruptores y las demas opciones.
La linea es una vista por paquetes: no modifica consumibles ni su apilado y contempla subastas sin convertir.

JARs y alta del datapack requieren REINICIO COMPLETO. Preparar para el reinicio diario autorizado de las 05:00;
no ejecutar stop, reiniciopendiente ni otro reinicio por cuenta propia. No hace falta apagar para preparar
plugins/update; no reemplazar un JAR cargado en plugins/ mientras corre el servidor. Instalar el JAR nuevo
antes del reinicio y comprobar su carga despues. Nunca Worlds > Upload ni subir carpetas de mundos.

Despues de arrancar, comprobar plugins y consola, luego desde consola:

```text
stellarity publico no
datapack list enabled
```

Si el complemento no queda con prioridad sobre AstralRPG-Items (es necesario que player/def sea el suyo):

```text
datapack disable "file/AstralStellarity-Compat.zip"
datapack enable "file/AstralStellarity-Compat.zip" last
```

Estos comandos recargan datos; revisar consola. No ejecutar /reload de Bukkit ni PlugMan.
Las siguientes actualizaciones de SOLO tablas se cargan con stellarity recargar (config.yml + tiers.json);
al cambiar numeros, aumentar VERSION en la fuente unica antes de regenerar para migrar equipo existente.
Menus solos: dm reload. Config de Mesa (si el dueno la cambia): astralmesa reload.
Skript no cambia en esta entrega; necesita el astral_gameplay.sk vigente para Defensa, regeneracion y PvP.

## Prueba del dueno en /sala (sin abrir al publico)

Usar /modo admin y /sala. Respaldar inventario/niveles del dueno antes de pruebas de requisitos;
no cambiar permanentemente sus niveles para probar el bloqueo. Un OP no evita nuestros requisitos.
Dar por consola (usa los originales del datapack):

```text
loot give ByTrainx loot stellarity:item/weapon/dragonblade
loot give ByTrainx loot stellarity:item/weapon/prismember
loot give ByTrainx loot stellarity:item/armor/shulker/chestplate
loot give ByTrainx loot stellarity:item/armor/elytra/dragon_wings
```

Con cada objeto en mano: /stellarity ver. Dragonblade: T5, dano base 62.500, Combate 30.
Prismember: T6, dano base 312.500, Combate 35. Pechera Shulker: T5, Defensa 200, vida +1.975.
No confundir atributo base con golpe final: AuraSkills, encantamientos y habilidades conservan sus bonus.
Equipar pechera sin el nivel la devuelve al inventario; si esta lleno, el sobrante cae con propietario.
Comprobar salud, Defensa, lore, precio sugerido y subasta real mas barata con publicaciones ya existentes.
En survival, el mejor equipo debe elevar astral.wt; las herramientas solas no lo elevan.
Probar Dragonblade contra mob T5, giro Prismember y su penetracion contra T6, arcos, escudos en secundaria,
vuelo de las tres alas, libros y los bonus de set en un cliente real. No invocar ni reactivar el dragon.
Comprobar que otro jugador no convierte equipo y que un prestamo privado vuelve a sus atributos originales.
Probar PvP solo en arena. Revisar consola por errores de AstralStellarity, Skript y datapacks.

## Apertura posterior (solo con OK del dueno)

```text
stellarity publico si
```

Para volver a privado: stellarity publico no (restaura los atributos en inventarios de otros jugadores al revisar).
El permiso de la Guia y la visibilidad de precios de Mesa son interruptores separados: no abrirlos como parte
de esta prueba; revisar su aprobacion antes de cambiar astral.guia.ampliacion o astralmesa precios publico.
El equipo ya convertido usa atributos propios persistentes: conservar el plugin activo para restaurar al
volver a privado. No desinstalar el JAR mientras haya equipo convertido repartido sin restaurarlo antes.

Atencion de balance para la prueba: Ancient Wooden Sword conserva la velocidad +2133 del autor por instruccion
del plan. Aunque su dano sea T7, su DPS es extraordinario. No certificar el balance publico de ese objeto sin
la decision del dueno. Las habilidades originales, criticos, crecimiento de Harvester y efectos de set se
conservan; requiere prueba visual y de sensacion de juego con el conjunto remoto completo.

## Verificaciones locales realizadas

6 tests de tabla/precios y 23 regresiones de Guia aprobados. Compilacion Java 25 aprobada.
Paper real con Stellarity 5.4.2, AuraSkills, Skript, ExcellentEnchants y PacketEvents:
conversion privada y restauracion, atributos y velocidad del autor, Prismember T6, dano T5,
habilidad fija y penetracion Kohara, funcion ORIGINAL de giro Prismember sin doble factor,
Defensa 200 y etiquetas binarias, vida +1.975, tier del mundo, requisitos y limite PvP de arenas.
El ensayo de subastas verifica tambien la mezcla de originales y convertidos y la visibilidad privada.
Skript cargo sin errores. NightCore intento descargar idiomas externos sin exito; los ensayos no
certifican esos textos ni sustituyen la comprobacion de consola/cliente del servidor remoto.

## Verificacion reproducible

```text
python -m unittest discover -s datapack-src -p test_stellarity.py
python -m unittest discover -s datapack-src -p test_guia_cofre.py
python -m unittest discover -s datapack-src -p test_guia_atlas.py
python datapack-src/stellarity_balance.py --jdk <jdk25-bin> --menus
python datapack-src/mesa_encantamientos.py --jdk <jdk25-bin>
python tools/probar_stellarity_paper.py --java <java25> --base .local/testsrv --node <node> --node-modules .local/asw-test/node_modules --stellarity <Stellarity-5.4.2.zip>
python tools/verificar_terceros.py
```

No subir la config de Mesa regenerada por ese comando. La prueba Paper usa carpetas nuevas locales y dos
clientes de protocolo; no certifica visuales, vuelo ni el panel remoto. Los logs quedan exclusivamente .local.

## Discord preparado, sin publicar

Titulo: Equipo del End por tiers
Las armas, armaduras y accesorios de Stellarity ahora acompanian la progresion de Astral.
Cada equipo muestra su tier, sus estadisticas y el nivel necesario para usarlo.
Tambien podes consultar su precio sugerido y la subasta mas barata desde el inventario.
Se conservan las habilidades especiales de los objetos y los bonus de sus conjuntos.
Publicar solo cuando se abra a los jugadores; esta entrega privada no se anuncia.

Base player/def SHA-256: `7f42107a3e5f538f738c817415984b8014fa9cf241814d33a7d572691f85ee93`.
