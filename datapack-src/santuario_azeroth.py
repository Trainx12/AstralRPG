"""Configuracion propia del Santuario; nunca incluye bloques del mapa ajeno."""
import json

WORLD = 'santuario_azeroth'
# Paper 26.1: level-name=world (servidor vigente) + namespace + path.
BUKKIT_WORLD = 'world_minecraft_santuario_azeroth'
BOUNDS = (144, -48, 351, 159)
ARRIVAL = (247.5, 57, 14.5)
CENTER = (247.5, 57, 19.5)
# Orden original, cinco oleadas de un Ancestral. Pies sobre vidrio natural.
BOSSES = ((233.5, 57, 1.5), (299.5, 57, 37.5), (267.5, 57, 106.5),
          (197.5, 57, 36.5), (247.5, 57, 19.5))
CHEST = (247.5, 57, 23.5)
GUIDE = (249.5, 57, 23.5)


def commands():
    w = BUKKIT_WORLD
    lines = ['# Santuario Azeroth. Instalar primero datapack y regiones con servidor APAGADO.',
             '# Dimension del datapack: NO mv create ni importar como THE_END.',
             '# Ruta SOLO nueva: world/dimensions/minecraft/santuario_azeroth/region/',
             '# Paper la carga desde el datapack; no crear/importar con Multiverse.',
             '# Conservar santuario_interstellar y sus regiones como respaldo.',
             f'execute in minecraft:{WORLD} run difficulty hard']
    for rule, value in [('spawn_mobs','false'), ('keep_inventory','true'), ('random_tick_speed','0'),
                        ('mob_griefing','false'), ('tnt_explodes','false'), ('advance_weather','false')]:
        lines.append(f'execute in minecraft:{WORLD} run gamerule minecraft:{rule} {value}')
    for flag,value in [('build','deny'),('block-break','deny'),('block-place','deny'),('chest-access','deny'),
                       ('pvp','deny'),('interact','allow'),('use','deny'),('mob-spawning','allow'),
                       ('creeper-explosion','deny'),('other-explosion','deny'),('tnt','deny')]:
        lines.append(f'rg flag -w {w} __global__ {flag} {value}')
    lines += ['lp group default permission set astral.santuario.cd false',
              '# SOLO con la mazmorra vacia; retirar el controlador del mundo viejo:',
              'execute in minecraft:santuario_interstellar run forceload add 46 48',
              'mm mobs kill astral_santuario_control_sala1',
              'execute in minecraft:santuario_interstellar run forceload remove 46 48',
              '# Crear una sola vez el controlador nuevo:',
              f'execute in minecraft:{WORLD} run forceload add 144 -48 351 159',
              f'mm mobs spawn astral_santuario_control_sala1 1 {w},247.5,57,19.5',
              '# Conservar las cargas del recorte: las oleadas recorren sectores separados.',
              f'# Revision OP: execute in minecraft:{WORLD} run minecraft:tp <jugador> 247.5 57 14.5 0 0']
    return '\n'.join(lines)+'\n'


def generate(files):
    # Formato 26.1, comprobado contra dimension_type/the_end.json del JAR 26.1.2.
    # Solo el cielo del End: sin pelea, islas, gateways, portales ni dragon.
    kind = dict(ambient_light=0.35, coordinate_scale=1.0, default_clock='minecraft:the_end',
                has_ceiling=False, has_ender_dragon_fight=False, has_fixed_time=True,
                has_skylight=True, height=384, logical_height=384, min_y=-64,
                infiniburn='#minecraft:infiniburn_overworld',
                monster_spawn_block_light_limit=0, monster_spawn_light_level=0,
                skybox='end', timelines=[], attributes={
                    'minecraft:visual/sky_color': '#000000',
                    'minecraft:visual/fog_color': '#181318',
                    'minecraft:visual/sky_light_color': '#ac60cd',
                    'minecraft:visual/sky_light_factor': 0.0,
                    'minecraft:visual/ambient_light_color': '#3f473f',
                    'minecraft:gameplay/bed_rule': {'can_set_spawn': 'never', 'can_sleep': 'never', 'explodes': False},
                    'minecraft:gameplay/respawn_anchor_works': False})
    dimension = {'type': 'astral:santuario', 'generator': {'type': 'minecraft:flat', 'settings': {
        'biome': 'minecraft:the_void', 'features': False, 'lakes': False,
        'layers': [{'block': 'minecraft:air', 'height': 1}]}}}
    for path, value in [('data/astral/dimension_type/santuario.json', kind),
                        (f'data/minecraft/dimension/{WORLD}.json', dimension)]:
        files[path] = json.dumps(value, indent=2)+'\n'
    files['data/astral/function/santuario/load.mcfunction'] = '\n'.join([
        f'execute in minecraft:{WORLD} run forceload add 144 -48 351 159',
        *[f'execute in minecraft:{WORLD} run gamerule minecraft:{rule} {value}' for rule,value in (
            ('keep_inventory','true'),('spawn_mobs','false'),('random_tick_speed','0'),
            ('mob_griefing','false'),('tnt_explodes','false'),('advance_weather','false'))]])+'\n'
    files.setdefault('data/astral/function/load.mcfunction','')
    files['data/astral/function/load.mcfunction'] += 'function astral:santuario/load\n'
