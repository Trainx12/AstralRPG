"""Lista de instalacion de la tanda 3c: build/deploy/tanda3c.md. No ejecuta nada en el servidor."""
import hashlib
from pathlib import Path
from mobs.tanda3c import NPC_MODELOS, MAQUINAS, MAZMORRAS, PERSONAJES

ROOT = Path(__file__).resolve().parents[2]
LISTAS = ('build/lobby/comandos.txt', 'build/minas/instalacion.txt', 'build/bosque/instalacion.txt', 'build/minijuegos/despliegue.txt')
MEJORADOS = ('astral_coloso_musgoso', 'astral_bosque_planta', 'astral_momia', 'astral_yeti', 'astral_golem_forja', 'astral_cangrejo',
             'astral_chaman', 'astral_chocobo', 'astral_ave', 'astral_pterodactilo')


def spawns():
    """Lineas 'mm mobs spawn' ya publicadas de cada NPC que recibe modelo, sin repetir."""
    out = {}
    for rel in LISTAS:
        for line in (ROOT / rel).read_text(encoding='utf-8').splitlines():
            parts = line.split()
            if line.startswith('mm mobs spawn ') and len(parts) >= 5 and parts[3] in NPC_MODELOS:
                out.setdefault(parts[3], [])
                if line not in out[parts[3]]:
                    out[parts[3]].append(line)
    return out


def text():
    pack = ROOT / '.local/terceros/AstralRPG-privado/build/AstralRPG-Textures.zip'
    sha = hashlib.sha1(pack.read_bytes()).hexdigest() if pack.exists() else '(armar el pack FINAL)'
    modelos = list(MAQUINAS) + ['astral_npc_' + p for p in PERSONAJES] + list(MEJORADOS)
    L = ['# Tanda 3c: maquinas de Mini juegos, NPC en 3D y mejoras de jefes', '',
         'Generado por `datapack-src/mobs/entrega_tanda3c.py`. Nada de esto se instala solo.', '',
         '## Archivos', '',
         '- Pack FINAL (privado) a R2: `python tools/subir_pack_r2.py .local/terceros/AstralRPG-privado/build/AstralRPG-Textures.zip`',
         f'- `resource-pack-sha1={sha}` en `server.properties` (comprobar antes la descarga publica).',
         '- `plugins/BetterModel/models/`: ' + ', '.join(f'`{m}.bbmodel`' for m in modelos)
         + ' desde `build/models/`, y `astral_vendedor.bbmodel` desde el build privado (ahora con el hueso del nombre).',
         '- `plugins/MythicMobs/mobs/`: `tanda3c.yml`, `arena.yml`, `portales.yml`, `mazmorra.yml`, `bosque.yml`, `tumba.yml`, `cumbre.yml`, `forja.yml`'
         ' desde `build/mythicmobs/mobs/`; `astral.yml` desde el build PRIVADO (conserva los vendedores).',
         '- `plugins/MythicMobs/skills/`: `tanda3c.yml` publico y `astral.yml` del build PRIVADO.',
         '- `plugins/Skript/scripts/astral_minijuegos.sk` (usa `minecraft:kill`).',
         '- Santuario no se toca. La Tienda sigue como aldeano.', '',
         '## Orden', '',
         '1. `list` (sin jugadores), respaldo en `.local/deploy-backups/tanda3c-<fecha>/`, apagar.',
         '2. Subir pack a R2, verificar SHA-1 publico, actualizar `server.properties`, subir archivos y comparar tamanos.',
         '3. Encender, esperar `Done (` y revisar el log (modelos cargados, sin errores de MythicMobs).', '',
         '## NPC', '',
         'Cada NPC conserva su aldeano, nombre y clics; el modelo se pone solo al cargar (`~onLoad`). Si alguno sigue viendose como aldeano,',
         'rehacerlo en su lugar con estas lineas (primero `forceload add` alrededor en `astral_minas` y `astral_bosque`):', '', '```',
         'rg flag -w lobby __global__ mob-spawning allow', 'rg flag -w astral_bosque __global__ mob-spawning allow']
    for mid, lines in spawns().items():
        L.append(f'mm mobs kill {mid}')
        L += lines
    L += ['rg flag -w lobby __global__ mob-spawning deny', 'rg flag -w astral_bosque __global__ mob-spawning deny', '```', '',
          'Guardianes escondidos de mazmorra (' + ', '.join('`astral_npc_' + k + '`' for k in MAZMORRAS) + '): usan la bruja y siguen con el nombre oculto;'
          ' los recoloca el dueno solo si hiciera falta.', '',
          '## Maquinas de Mini juegos', '',
          'Las dos abren el mismo panel (`dm open parkour`). El dueno elige el lugar; el ultimo numero es hacia donde miran (0 sur, 90 oeste, 180 norte, -90 este):',
          '', '```', 'rg flag -w lobby __global__ mob-spawning allow',
          'mm mobs spawn astral_maquina_arcade 1 lobby,<x>,<y>,<z>,<giro>,0', 'mm mobs spawn astral_maquina_capsulas 1 lobby,<x>,<y>,<z>,<giro>,0',
          'mm mobs kill astral_npc_parkour', 'rg flag -w lobby __global__ mob-spawning deny', '```', '',
          '## Probar con un jugador', '',
          '- Nombre visible arriba de cada NPC, maquina y vendedor (hueso `mtag_nombre` de BetterModel).',
          '- Clic en cada NPC abre su menu de siempre y hace el saludo; clic en los bordes de las maquinas tambien abre el panel.',
          '- Pantalla, marquesina y luces de las maquinas a brillo maximo; cupula transparente con las capsulas a la vista.',
          '- Jefes: yeti, golem de la forja, momia, chaman y cangrejo con su tamano y ataques de siempre.', '']
    return '\n'.join(L)


def main():
    dest = ROOT / 'build/deploy/tanda3c.md'
    dest.write_text(text(), encoding='utf-8')
    print(dest)


if __name__ == '__main__':
    main()
