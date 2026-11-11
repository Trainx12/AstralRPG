"""Lista de instalacion reproducible de la tanda 4a; no despliega ni usa red."""
from pathlib import Path
from terceros import ROOT, PETS, privado


def main():
    private = '.local/terceros/AstralRPG-privado/build/'
    public = 'build/'
    paths = [
        (public + 'AstralRPG-Items.zip', 'world/datapacks/AstralRPG-Items.zip'),
        (private + 'AstralRPG-Textures.zip', 'Cloudflare R2: AstralRPG-Textures.zip (NO subir el pack publico)'),
        (private + 'mythicmobs/mobs/astral.yml', 'plugins/MythicMobs/mobs/astral.yml'),
        (private + 'mythicmobs/skills/astral.yml', 'plugins/MythicMobs/skills/astral.yml'),
        (public + 'mythicmobs/mobs/mascotas.yml', 'plugins/MythicMobs/mobs/mascotas.yml'),
        (private + 'mythicmobs/skills/mascotas.yml', 'plugins/MythicMobs/skills/mascotas.yml'),
    ]
    paths += [(public + f'lobby/CrazyCrates/crates/{name}.yml', f'plugins/CrazyCrates/crates/{name}.yml')
              for name in ('gacha_monturas', 'gacha_monturas_garantia')]
    menus = ['mascotas', 'mascotas_2', 'mascotas_3', 'misiones'] + ['mascota_' + p[0] for p in PETS]
    paths += [(public + f'menus/DeluxeMenus/gui_menus/{name}.yml', f'plugins/DeluxeMenus/gui_menus/{name}.yml') for name in menus]
    paths += [(private + 'models/' + path.name, 'plugins/BetterModel/models/' + path.name)
              for path in sorted((privado() / 'build/models').glob('*.bbmodel'))]
    sha_path = privado() / 'build/pack.sha1'
    sha = sha_path.read_text().strip() if sha_path.is_file() else 'PENDIENTE: convertir assets con BetterModel y armar pack FINAL'
    lines = ['# Tanda 4a - instalacion pendiente', '',
             'Generado por `python datapack-src/deploy_tanda4a.py`. No acredita despliegue. Servidor activo: Empower; Aternos es copia.', '',
             '## Archivos locales -> destinos', '', '| Archivo local | Destino |', '|---|---|']
    lines += [f'| `{src}` | `{dest}` |' for src, dest in paths]
    lines += ['', 'Con ASTRAL_PRIVADO distinto, sustituir el prefijo privado por esa ruta.', '',
              'Combinar las entradas nuevas de `build/menus/DeluxeMenus/config-gui_menus.yml` en `plugins/DeluxeMenus/config.yml`; conservar las existentes.', '',
              '## Apagado, pack y reinicio', '',
              '1. Crear respaldo de los archivos listados y server.properties. Apagar el servidor.',
              '2. Subir los archivos a los destinos. NO sustituir mundos ni usar Worlds > Upload en world.',
              '3. Desde la raiz local: `python tools/subir_pack_r2.py .local/terceros/AstralRPG-privado/build/AstralRPG-Textures.zip`.',
              f'4. Solo si la descarga publica verifica: fijar `resource-pack-sha1={sha}` en server.properties.',
              '   URL: `https://pub-5e0d1c63a1554ba7b8e33b038e1a06fe.r2.dev/AstralRPG-Textures.zip`.',
              '5. Encender. Este cambio requiere reinicio por datapack y propiedades del pack.',
              '6. Si se actualizan solo configuraciones en una prueba: `bettermodel reload`, `mm reload`, `crates reload`, `dm reload`.', '',
              '## Comandos de consola tras arrancar', '',
              'Agregar solo los objetivos nuevos; no borrar niveles ni permisos existentes:', '', '```text']
    lines += [f'scoreboard objectives add {prefix}{pid} dummy' for pid, *_ in PETS for prefix in ('pxp_', 'plv_', 'pmod_')]
    lines += ['mm mobs kill astral_mascotas_control', 'execute in minecraft:lobby run forceload add 180 190',
              'rg flag -w lobby __global__ mob-spawning allow',
              'mm mobs spawn astral_mascotas_control 1 lobby,180.5,92,190.5', '```', '',
              'Rehacer vendedores en las posiciones del generador. Si el dueno los movio, registrar sus coordenadas reales antes de quitarlos.', '', '```text']
    for mid in ('astral_npc_venta', 'astral_npc_tienda', 'astral_npc_mina_venta', 'astral_npc_bosque_venta'):
        lines.append('mm mobs kill ' + mid)
    for filename in ('build/lobby/comandos.txt', 'build/minas/instalacion.txt', 'build/bosque/instalacion.txt'):
        for line in (ROOT / filename).read_text(encoding='utf-8').splitlines():
            if line.startswith('mm mobs spawn ') and line.split()[3] in ('astral_npc_venta', 'astral_npc_tienda', 'astral_npc_mina_venta', 'astral_npc_bosque_venta'):
                lines.append(line)
    lines += ['```', '', 'Prueba manual de Goblin (no tiene aparicion natural ni esta en mazmorras):', '',
              '`mm mobs spawn astral_goblin 1 <mundo>,<x>,<y>,<z>`', '',
              'Espada sin receta ni habilidad, solo administracion:', '',
              '`loot give <jugador> loot astral:item/espada_heroe_errante`', '',
              'Comprobar `/mascotas` y las tres paginas, invocacion con/sin permiso, bonus en mazmorras (niveles 1/10/20), evolucion 30, seguimiento y guardado.',
              'Abrir los cuatro tipos de vendedor; comprobar nombre, hitbox de jugador y menus previos. Probar espada en mano y GUI con el pack FINAL.',
              'Revisar consola: errores de modelos, animaciones, skills, funciones o texturas. El smoke local sin jugador no prueba interacciones ni bonus.', '',
              'La vista previa con arte esta solamente en el repositorio privado: `build/previews/tanda4a.png`.']
    dest = ROOT / 'build/deploy/tanda4a.md'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
