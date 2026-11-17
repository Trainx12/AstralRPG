# Entrega acumulada del 16/11/2026 — Empower

Preparacion verificada sobre main `5e09d01`. Servidor Empower `44d1ad66`, Paper 26.1.2 / Java 25.
La API documentada del panel confirmo el servidor encendido y el pack instalado
`4322b8ca706b692d7d0d4f750312d079a5e7653a`; la descarga publica de R2 coincide.
Esta comprobacion no acredita todavia la instalacion de esta entrega.

## Archivos preparados

Lista exacta acumulada: [archivos locales y destinos](deploy-16-11-archivos.md),
[manifest con SHA-256](deploy-16-11-archivos.json). Son 104 reemplazos, tres
integraciones selectivas y seis retiros de menus obsoletos. El manifest resuelve
duplicados por destino y usa las tres configuraciones privadas actuales de MythicMobs.
No instalar las reservas publicas de `mobs/astral.yml`, `skills/astral.yml` ni `skills/mascotas.yml`.

FINAL privado local:
`.local/terceros/AstralRPG-privado/build/entregas/modelos-3d-efectos/AstralRPG-Textures.zip`.
SHA-1: `6421c6d38ec1303051a44b3f42b52a2b3f3dcb42`.
Base Fable comprobada: `d19862c596d7c26506ec08931ccbb9c286514127`, sobre arte
`90c90b745bce97490550d8d22a8a1cc4011be8e1`, que ya conserva la cadena anterior.
7258 referencias del FINAL auditadas. Todas las entradas de Fable fuera del delta
explicito se conservaron byte por byte, sin borrar entradas. El ZIP publico no sirve para instalar.
El dueno autorizo incluir Crop & Kettle en este FINAL de R2; esa decision reemplaza
los bloqueos historicos de distribucion de las entregas anteriores.

Datapack privado CNK actual:
`.local/terceros/AstralRPG-privado/build/entregas/crop-kettle/CropAndKettle-Astral.zip`,
SHA-1 `c40b2295f96a7e5f648fce6cde44581d257dd96c`. Se instala una sola vez en
`world/datapacks/`, junto a Astral, nunca una copia por dimension.

## Correcciones al revisar el conjunto

- El armador del FINAL ya no calcula su contenido contra HEAD: despues del merge
  podia omitir efectos y borrar huesos del Fenix. Ahora usa los recursos actuales
  de una lista limitada y suma los seis PNG finales sin pisar arte privado.
- Se regeneraron ambos ZIP del merge y los generadores publicos actuales, los
  modelos privados de mochilas/cuchillos/Trainx y los plugins propios aplicables.
- AstralEfectos evita generar dibujos en chunks descargados, los marca no persistentes
  y elimina sus entidades invalidas. El ensayo reprodujo dibujos huerfanos antes
  de esta correccion y verifico su eliminacion despues.
- Consumibles pasa al slot 44: el slot 43 remoto ya lo ocupa Oficios; 44 estaba libre.
- El pan producido por CNK recibe `custom_data.astral_cnk.cocina`; conserva material,
  alimento y aspecto. Evita revender como pan vanilla el trigo cocinado. Solo cambia
  esa loot table del datapack CNK adaptado, sin cambiar precios de las tiendas.
  Conservar `match-item-meta: true` y no agregar `custom_data` a los NBT ignorados.
- El probe historico XP ahora comprueba el catalogo vigente: ballestas III–V presentes,
  I–II y VI–X ausentes. No se reintroducen las retiradas.

## Verificaciones locales

339 pruebas Python aprobadas. Compilaciones Java 25 de AstralDecor 1.13.0,
AstralOceano 1.4.0, AstralEfectos 1.1.0 y AstralPortales aprobadas.
La compilacion dentro del sandbox mostro una restriccion de acceso a dependencias;
se repitio con acceso autorizado y sin esa excepcion.

Paper 26.1.2 aislado:

| Ensayo | Resultado |
|---|---|
| XP/suerte/mochilas, dos arranques | `XP RESULT failures=0` en ambos |
| Balance/agua/durabilidad | `BAL RESULT failures=0` |
| XP x4, mercader neutral/agresor, golems/tier/limite | `CORR RESULT failures=0` |
| Retiro/llaves/marcadores, dos arranques | `RET RESULT failures=0` en ambos |
| CNK: olla, cultivo y aislamiento survival/Nether | `CNK RESULT failures=0` |
| Items, Fenix, Trainx, golems y efectos | `FX RESULT failures=0`; 32 dibujos y cero vivos tras 4 s |
| Economia con plugin/config actuales | `FX RESULT failures=0`; rechaza masa/pan CNK y frasco Astral; pan vanilla $3,94 y patata venenosa $15 conservados |

Logs, respaldos, mapas, originales y derivados licenciados quedan exclusivamente en `.local/`.
Los probes no se instalan en produccion. Los ensayos sin cliente no certifican el render,
el agarre de armas, la ruleta real, compras con dos jugadores ni las protecciones de claims.

## Instalacion y recuperacion

Respaldo previo: `.local/respaldo-server-16-11/`, con los archivos existentes y
`respaldo.json` de las 148 rutas comprobadas. Se respaldaron tambien las tiendas
anidadas y la descarga R2 anterior en `.local/deploy-16-11/R2-anterior.zip`.
No borrar variables de Skript ni reemplazar `plugins/AstralOceano/config.yml`.

Apagar desde Empower, comprobar estado offline, aplicar el manifest y las tres
integraciones. Actualizar gui_menus conservando registros ajenos y retirando solo
los seis obsoletos del manifest. Agregar `cnk` a structure-namespaces y verificar
AstralProgression activo y survival correcto. Mantener ClearLag CUSTOM y los topes
de atributos en spigot.yml en `1.0E12`.

Con el servidor apagado, publicar el FINAL:

```text
python tools/subir_pack_r2.py ".local/terceros/AstralRPG-privado/build/entregas/modelos-3d-efectos/AstralRPG-Textures.zip"
```

Verificar SHA-1 publico y modificar solo `resource-pack-sha1` en server.properties.
No escribir si la lectura esta vacia/incompleta: el respaldo verificado contiene 69 claves.
Mantener URL fija, puertos y las demas claves. Reinicio completo obligatorio por los JAR,
datapacks y modelos. Nunca reemplazar mundos/regiones ni usar Worlds > Upload en world.
Si falla antes de iniciar: restaurar solo los archivos respaldados y el pack R2 anterior,
con el servidor apagado; no restaurar mundos ni datos de jugadores.

Tras iniciar, con la entrada oceanica cargada, ejecutar una vez (sin barra):

```text
execute in minecraft:oceano run minecraft:kill @e[tag=oceano.aurora,distance=0..]
datapack list enabled
dm list
oceano estado
```

La limpieza Aurora solo afecta su tag en Oceano; si su chunk no estaba cargado,
visitar la entrada y repetir. No usar killall. Las cinco mascotas retiradas no deben
aparecer en menus ni gachas; la compensacion la hace el script una sola vez por UUID/mascota.
Si solo se corrige YAML posteriormente: `mm reload`, `dm reload`, `crates reload`,
`tab reload`, `sreload`; para scripts, `skript:skript reload special_weapons`,
`astral_infinita`, `astral_rankings`, `astral_mascotas_retiro`, `astral_servicios`
y `astral_duelos` (cada nombre como comando completo). No usar /reload general.
El arranque normal carga todo sin repetir estas recargas.

## Estado remoto

Instalacion, subida R2 del nuevo FINAL, cambio de properties y consola posterior:
pendientes de completar tras la publicacion del codigo. Economia verificada con
EconomyShopGUI 7.3.4 y las tiendas actuales descargadas del panel; sus precios reales
por unidad incluyen el ajuste stack-size del YAML. El proveedor Vault del ensayo es
un doble local; no se modifico dinero de jugadores ni se compro/vendio en produccion.

Con cliente probar: cuatro frascos (uno/Shift/mano secundaria), manzana y expiracion,
cuchillos I–X, mochilas (UUID/contenido/mejora), materiales VI–X, Saltador/Gancho,
Fenix y bonus, seis ventanas/Descansar, golems e Infinita, mercader con dos jugadores,
gachas normales/suerte/garantia, cocina y ventas, claims, efectos Bajo/Medio/Alto y
ausencia de Aurora al cargar su entrada.
