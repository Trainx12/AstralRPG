"""Regenera las vistas previas y las instrucciones de entrega de la tanda 1."""
from pathlib import Path
import re
import hashlib

from PIL import Image
from adventure_ui import previews
from escape_menu import text
from explosion_protection import WORLDS, commands, BLOCK_CONFIG
from lobby import ASTRAL_ROWS
from mapas_exploracion import DEFINITIONS, installation_commands

ROOT = Path(__file__).resolve().parents[1]


def generate():
    out = ROOT / 'build/deploy'
    out.mkdir(parents=True, exist_ok=True)
    preview_dir = ROOT / 'build/previews'
    previews(preview_dir)
    samples = {
        '%condition:sidebar_world%': 'Tumba del Rey de Arena',
        '%player_health_rounded%': '550', '%player_max_health_rounded%': '550',
        '%player_armor%': '100', '%auraskills_power%': '412',
        '%vault_eco_balance_formatted%': '15,230', '%server_online%': '7',
        '%server_max_players%': '50', '%condition:rango%': 'Veterano',
        '%condition:daily_count_0%': '2/3', '%condition:historia%': '4/9',
        '%statistic_mob_kills%': '1,284',
    }
    image = Image.new('RGBA', (220, 156), '#24252c')
    text(image, 'ASTRAL RPG', (110, 8), color='#D6B4FF')
    for i, row in enumerate(ASTRAL_ROWS):
        for placeholder, value in samples.items():
            row = row.replace(placeholder, value)
        row = re.sub('<[^>]+>', '', row).strip().replace('─', '-')
        text(image, row, (110, 24 + i * 11), color='#F0E6FF')
    image.resize((880, 624), Image.Resampling.NEAREST).save(preview_dir / 'panel-tab.png')
    (out / 'panel-tab-lineas.txt').write_text('\n'.join(ASTRAL_ROWS) + '\n', encoding='utf-8')
    (out / 'tanda1-explosiones.txt').write_text(
        '# Solo el flag que no anula dano a entidades. Ver tanda1.md para los demas.\n'
        + '\n'.join(cmd for world in WORLDS for cmd in commands(world)) + '\n', encoding='utf-8')
    for world in WORLDS:
        folder = out / 'WorldGuard' / world
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'config-fusionar.yml').write_text(BLOCK_CONFIG, encoding='utf-8')
    # Solo instrucciones publicas, sin abrir ni preparar mapas de terceros.
    for key, definition in DEFINITIONS.items():
        dest = ROOT / 'build/mapas_exploracion' / key / 'comandos.txt'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(installation_commands(key, definition), encoding='utf-8')
    (out / 'tanda1-volcan.txt').write_text('''# Diagnostico, sin modificar el mundo. Sustituir <jugador>.
mv info forja
# Debe existir y estar cargado como forja. Si falta, revisar worlds.yml y consola antes de importar.
execute in minecraft:forja run forceload query 1536 1900
# Informa carga forzada, NO confirma que el chunk tenga terreno.
execute in minecraft:forja run forceload add 1536 1900
# Esperar unos segundos; guardar si ya estaba forzado para no retirarlo despues.
execute in minecraft:forja if block 1536 221 1900 minecraft:air run say FORJA: piso es aire
execute in minecraft:forja unless block 1536 221 1900 minecraft:air run say FORJA: piso no es aire
# Aire: no viajar en supervivencia. No aire: revisar tipo de bloque, techo y alrededores.
execute in minecraft:forja if block 1536 222 1900 minecraft:air if block 1536 223 1900 minecraft:air run say FORJA: espacio libre
# Sin mensaje: hay un obstaculo o fallo la dimension; revisar consola.
# Solo si el jugador acepta y ya esta en creativo:
execute in minecraft:forja run minecraft:tp <jugador> 1536.5 222 1900.5
# Inspeccionar F3, terreno y bloques bajo los pies. No inferir piso solo del peso de las regiones.
execute in minecraft:forja run forceload remove 1536 1900
# Quitar solo si no estaba forzado antes. Retornar al lobby con spawn <jugador>.
# El repo usa forja 1536.5 222 1900.5 y NPC 1536.5 222 1901.5.
# La mazmorra usa forja_volcano 82.5 52 -55.5; es otro mapa, no cambiar la expedicion.
# docs/MAZMORRAS.md conserva una llegada historica Y=224; tambien documenta piso
# de piedra en Y=221 y aire Y=222..226. Ambas alturas sirven en ese recorte.
# No hay evidencia en el repo de la causa actual; revisar carga y bloques reales.
''', encoding='utf-8')
    files = [
        ('build/AstralRPG-Items.zip', 'world/datapacks/AstralRPG-Items.zip'),
        ('build/menus/DeluxeMenus/gui_menus/mazmorras.yml', 'plugins/DeluxeMenus/gui_menus/mazmorras.yml'),
        ('build/menus/DeluxeMenus/gui_menus/expediciones.yml', 'plugins/DeluxeMenus/gui_menus/expediciones.yml'),
        ('build/mapas_exploracion/astral_viajes.sk', 'plugins/Skript/scripts/astral_viajes.sk'),
        ('build/minas/Skript/scripts/astral_minas.sk', 'plugins/Skript/scripts/astral_minas.sk'),
        ('build/gameplay/astral_gameplay.sk', 'plugins/Skript/scripts/astral_gameplay.sk'),
        ('build/gameplay/astral_panel.sk', 'plugins/Skript/scripts/astral_panel.sk'),
    ]
    files += [(f'build/mythicmobs/mobs/{key}.yml', f'plugins/MythicMobs/mobs/{key}.yml')
              for key in ('mazmorra', 'bosque', 'tumba', 'cumbre', 'forja')]
    body = '''# Tanda 1: preparada, NO desplegada

El dueno debe revisar primero las vistas previas `build/previews/mazmorras.png`,
`expediciones.png` y `panel-tab.png`. Son aproximaciones; comprobar despues con cliente real.
No subir archivos privados, logs, mapas ni mundos. Santuario queda en espera.

## Archivos a reemplazar (con servidor apagado)

| Local | Destino relativo a la raiz del servidor |
|---|---|
'''
    body += ''.join(f'| `{local}` | `{remote}` |\n' for local, remote in files)
    body += '''
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
de TNT, creepers, wither y calaveras conservando sus explosiones. Quedan pendientes la
proteccion de otras explosiones y bolas de ghast hasta validar configuracion y comportamiento
en el servidor. No se aplico ningun cambio al servidor.

Fuentes oficiales consultadas:
- https://worldguard.enginehub.org/en/latest/regions/flags/
- https://worldguard.enginehub.org/en/latest/config/

El panel general usa `%player_armor%` como equivalente al `[armor]` de BetterHud;
esta fila muestra armadura vanilla. Confirmar con el dueno si quiere en otra tanda
la defensa RPG, que es una magnitud diferente y necesita su propio placeholder.
No se cambiaron balance, oleadas, jefes, Duels ni barra roja de la Momia.
Retirar BetterHud del pack puede ahorrar fuentes, pero requiere separar y validar
el shader combinado con Stellarity; se propone para otra tanda, no se hizo ahora.

Herramienta opcional: `tools/empower_api.py` simula por defecto; `--yes` ejecuta.
Operaciones: `list /carpeta`, `read /archivo`, `write local /archivo`,
`upload local /carpeta`, `command "comando"`, `restart`. No se uso contra el servidor.
'''
    digest = hashlib.sha1((ROOT / 'build/AstralRPG-Textures.zip').read_bytes()).hexdigest()
    body += f'\nSHA-1 del ZIP local regenerado: `{digest}`.\n'
    body += '''
## Verificacion local realizada

- `python -m unittest discover` desde datapack-src: 137 pruebas aprobadas.
- `python -m unittest discover -s tools -p test_tanda1_tools.py`: 5 aprobadas.
- `python datapack-src/verify.py`: JSON, referencias, arte y mazmorras correctos.
- R2 `--dry-run` y Empower simulacion: correctos, sin contactar servicios.
- Revisadas visualmente las previas de expediciones, mazmorras y panel TAB.
- Comparacion con ZIP anterior: datapack cambia solo `mob/roll.mcfunction`;
  resource pack conserva todas las entradas y sus bytes. El orden lo fijan los
  slots de los menus; el SHA-1 del ZIP cambia por su regeneracion.
- Se corrigieron expectativas antiguas de pruebas sobre doble salto,
  varita de curacion vanilla y Saltador/Gancho, sin cambiar su implementacion.
- No hubo prueba en Paper/cliente real ni consola del servidor en esta tanda.
'''
    (out / 'tanda1.md').write_text(body, encoding='utf-8')


if __name__ == '__main__':
    generate()
