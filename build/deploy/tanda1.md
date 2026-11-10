# Tanda 1 + correcciones 1b: preparadas, NO desplegadas

El dueno debe revisar primero las vistas previas `build/previews/mazmorras.png`,
`expediciones.png` y `panel-tab.png`. Son aproximaciones; comprobar despues con cliente real.
No subir archivos privados, logs, mapas ni mundos. Santuario queda en espera.

## Archivos a reemplazar (con servidor apagado)

| Local | Destino relativo a la raiz del servidor |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/menus/DeluxeMenus/gui_menus/mazmorras.yml` | `plugins/DeluxeMenus/gui_menus/mazmorras.yml` |
| `build/menus/DeluxeMenus/gui_menus/expediciones.yml` | `plugins/DeluxeMenus/gui_menus/expediciones.yml` |
| `build/mapas_exploracion/astral_viajes.sk` | `plugins/Skript/scripts/astral_viajes.sk` |
| `build/minas/Skript/scripts/astral_minas.sk` | `plugins/Skript/scripts/astral_minas.sk` |
| `build/gameplay/astral_gameplay.sk` | `plugins/Skript/scripts/astral_gameplay.sk` |
| `build/gameplay/astral_panel.sk` | `plugins/Skript/scripts/astral_panel.sk` |
| `build/mythicmobs/mobs/mazmorra.yml` | `plugins/MythicMobs/mobs/mazmorra.yml` |
| `build/mythicmobs/mobs/bosque.yml` | `plugins/MythicMobs/mobs/bosque.yml` |
| `build/mythicmobs/mobs/tumba.yml` | `plugins/MythicMobs/mobs/tumba.yml` |
| `build/mythicmobs/mobs/cumbre.yml` | `plugins/MythicMobs/mobs/cumbre.yml` |
| `build/mythicmobs/mobs/forja.yml` | `plugins/MythicMobs/mobs/forja.yml` |

## Configuraciones a fusionar, conservando el resto

- `build/lobby/TAB/secciones-config.yml`: reemplazar SOLO `scoreboard` y `conditions`
  de `plugins/TAB/config.yml`; las otras secciones no cambian en esta tanda.
- `build/plugins/BetterHud/config-cambios.yml`: aplicar SOLO `default-hud: []`
  en `plugins/BetterHud/config.yml`. Conservar jar, assets, layouts, fuentes y shader.
  No subir los otros archivos BetterHud regenerados: el pack anterior sigue compatible.
- Para cada uno de los 12 mundos enumerados en `tanda1-explosiones.txt`, fusionar
  `build/deploy/WorldGuard/<mundo>/config-fusionar.yml` en
  `plugins/WorldGuard/worlds/<mundo>/config.yml`, sin reemplazar el archivo entero.
  No cambiar santuario ni santuario_interstellar.

## Alcance de la correccion 1b

Esta correccion NO regenera datapack ni resource pack y NO sube nada al servidor/R2.
Si la tanda 1 ya fue instalada: fusionar solo scoreboard/conditions de TAB y los 12
config-fusionar.yml de WorldGuard; `tab reload` y `wg reload`, revisar consola.
No hace falta apagar ni reiniciar solo por 1b. BetterHud sigue apagado; su texto
corregido `build/plugins/BetterHud/layouts/astral.yml` corresponde a
`plugins/BetterHud/layouts/astral.yml` SOLO si se reactiva en otra tarea.
Si tanda 1 sigue pendiente, aplicar la lista completa y el arranque siguiente.

## Resource pack y arranque

1. Revisar visuales y hacer respaldo verificado. Anunciar mantenimiento y apagar el servidor.
2. Reemplazar los archivos y fusionar las configuraciones indicadas arriba.
3. Ejecutar localmente `python tools/subir_pack_r2.py build/AstralRPG-Textures.zip`
   (requiere boto3 y credenciales locales). Verifica descarga publica y devuelve URL + SHA-1.
   No se ejecuto una subida en esta tanda. `--dry-run` calcula hash sin subir.
4. En `server.properties`, fijar `resource-pack=` a la URL R2 devuelta y
   `resource-pack-sha1=` al hash verificado. La URL R2 conserva el mismo nombre.
5. Encender: hace falta arranque completo para datapack y propiedades del resource pack.
   Revisar consola: datapack, Skript, TAB, MythicMobs y WorldGuard sin errores.
6. El arranque ya carga los archivos. Si se necesitan recargas, este es el orden:

```text
mm reload
skript:skript reload astral_viajes
skript:skript reload astral_minas
skript:skript reload astral_panel
skript:skript reload astral_gameplay
tab reload
dm reload
```

7. Aplicar las lineas de `build/deploy/tanda1-explosiones.txt` en consola.
8. Quitar el HUD persistido de cada jugador conectado con
   `hud hud remove <jugador> astral_panel`. Para desconectados lo quita `astral_panel.sk`
   al entrar. `default-hud: []` evita nuevas altas; no desinstalar BetterHud.
9. Tras `mm reload`, volver a colocar SOLO los aldeanos de entrada de mina, bosque,
   tumba, cumbre y forja en sus posiciones actuales guardadas. Identificadores:
   `astral_npc_mina`, `astral_npc_bosque`, `astral_npc_tumba`, `astral_npc_cumbre`,
   `astral_npc_forja`. Guardar posicion y orientacion antes de quitarlos, no duplicarlos.
   No ejecutar los comandos de creacion de mundos ni los de NPC propuestos del generador.
   El YAML regenerado de Santuario cambia solo AlwaysShowName, pero NO instalarlo ahora.
10. Probar con jugador sin OP: orden y requisitos de expediciones, descubrimientos,
    `/minas` desde mapas y mazmorras, `/sb` dos veces y reconexion, panel propio de minas,
    nombres ocultos tras paredes. Quien gano Mina antes sin Bosque puede destrabarse con
    `lp user <jugador> permission set astral.completada.bosque true`.
11. Probar explosiones sobre bloques prescindibles y dano a jugador/mob sin OP.
    Diagnosticar Forja con `tanda1-volcan.txt`; no mover llegadas ni subir regiones sin evidencia.

## Excepcion de explosiones y pendientes

WorldGuard documenta que `creeper-explosion`, `other-explosion`, `ghast-fireball` y
`wither-damage` controlan dano; `tnt` puede impedir la detonacion. La configuracion
`regions.explosion-flags-block-entity-damage` vale true por defecto. Por la condicion
expresa del plan, NO se generan esos cinco flags deny. Solo `enderdragon-block-damage`
es seguro directamente. Las configuraciones por mundo propuestas bloquean dano a bloques
de TNT, creepers, wither, calaveras y bolas de fuego conservando sus explosiones.
Se agregan mobs.block-fireball-explosions: false y mobs.block-fireball-block-damage: true.
WorldGuard 7 no ofrece claves separadas de dano a bloques para camas, anclas de
reaparicion ni cristales del End: quedan pendientes. other-explosion y
block-other-explosions pueden cancelar tambien dano; no se usan para resolverlo.
Probar impacto y fuego de ghast/blaze en cliente real: esto no bloquea propagacion de fuego. No se aplico ningun cambio al servidor.

Fuentes oficiales consultadas:
- https://worldguard.enginehub.org/en/latest/regions/flags/
- https://worldguard.enginehub.org/en/latest/config/

El panel general recupera el estilo original (14 filas), suma rango/monstruos y usa
`%objective_score_{astraldef}%` para Defensa Astral. BetterHud apagado queda corregido
con `[papi:objective_score_{astraldef}]`. ScoreboardObjectives y LocalTime deben estar
instaladas; si faltan: `papi ecloud download ScoreboardObjectives`,
`papi ecloud download LocalTime`, `papi reload`, `tab reload`.
Comparacion visual: `build/previews/panel-tab-comparacion.png`.

No se cambiaron balance, oleadas, jefes, Duels ni barra roja de la Momia.
Retirar BetterHud del pack puede ahorrar fuentes, pero requiere separar y validar
el shader combinado con Stellarity; se propone para otra tanda, no se hizo ahora.

Herramienta opcional: `tools/empower_api.py` simula por defecto; `--yes` ejecuta.
Operaciones: `list /carpeta`, `read /archivo`, `write local /archivo`,
`upload local /carpeta`, `command "comando"`, `restart`. Todos los pedidos incluyen User-Agent: Mozilla/5.0 AstralRPG-deploy.
En tanda 1b la prueba GET /api/client/servers/44d1ad66 quedo bloqueada antes de
contactar la red: falta completar el campo Clave de la seccion Clave de API del panel
en las credenciales locales. No se escribio ni se mandaron comandos al servidor.

SHA-1 del ZIP local regenerado: `7a99922fb1734f4f80c64cee3f363a7b4d2404cb`.

## Verificacion local realizada

- Tanda 1b: TAB comparado semanticamente con HEAD; solo cambian las filas de astral.
  Minas Astrales, condiciones, tabulador y toggle se conservan.
- Tanda 1b: vistas panel-tab.png y panel-tab-comparacion.png revisadas con colores
  por tramo y degradados. La referencia se recorta al panel, sin interfaz del telefono.
- Tanda 1b: pruebas de User-Agent cubren API y subida firmada sin acceder a la red.
- `python -m unittest discover` desde datapack-src: 137 pruebas aprobadas.
- `python -m unittest discover -s tools -p test_tanda1_tools.py`: 7 aprobadas.
- `python datapack-src/verify.py`: JSON, referencias, arte y mazmorras correctos.
- R2 `--dry-run` y Empower simulacion: correctos, sin contactar servicios.
- Revisadas visualmente las previas de expediciones, mazmorras y panel TAB.
- Comparacion con ZIP anterior: datapack cambia solo `mob/roll.mcfunction`;
  resource pack conserva todas las entradas y sus bytes. El orden lo fijan los
  slots de los menus; el SHA-1 del ZIP cambia por su regeneracion.
- Se corrigieron expectativas antiguas de pruebas sobre doble salto,
  varita de curacion vanilla y Saltador/Gancho, sin cambiar su implementacion.
- No hubo prueba en Paper/cliente real ni consola del servidor en esta tanda.
