"""Configuracion propia del Santuario; nunca incluye bloques del mapa ajeno."""
import json

WORLD = 'santuario_azeroth'
# Paper 26.1: level-name=world (servidor vigente) + namespace + path.
BUKKIT_WORLD = 'world_minecraft_santuario_azeroth'
# 12/11/2026: el mapa viejo quedo bugeado; ahora la dimension guarda spiritarena.schem
# pegada entera (tools/pegar_santuario_spirit.py) con este punto como destino de WorldEdit.
# La estructura ocupa de (191, 61, 187) a (321, 191, 321): todo en la region r.0.0.
PASTE_ORIGIN = (256, 64, 256)
BOUNDS = (191, 187, 321, 321)  # forceload x1 z1 x2 z2

# ===================== COORDENADAS DEL SANTUARIO (UNICO LUGAR) =====================
# PROVISORIO hasta que el dueno diga donde van la entrada, los jefes y el cofre:
# todo arriba del centro de la estructura, parado sobre vidrio violeta (y=179).
# Para cambiarlas: editar este bloque, `python build.py` y `python mobs/mazmorra.py`.
ARRIVAL = (256.5, 180, 254.5)   # tp de entrada y rescate
CENTER = (256.5, 180, 254.5)    # controlador de las oleadas
RADIUS = 150                    # jugadores dentro de este radio cuentan como "en el Santuario"
# Cinco oleadas de un Ancestral: Cangrejo, Chaman, Momia, Yeti, Golem de Forja.
BOSSES = ((256.5, 180, 254.5),) * 5
FLOOR_Y = 180                   # piso donde aparecen los jefes
CHEST = (258.5, 180, 256.5)     # cofre del premio final
GUIDE = (256.5, 180, 256.5)     # NPC guia
# ====================================================================================


def commands():
    w = BUKKIT_WORLD
    lines = ['# Santuario Azeroth. Instalar primero datapack y regiones con servidor APAGADO.',
             '# Dimension del datapack (cielo del End): NO mv create ni importar como THE_END.',
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
              '# SOLO con la mazmorra vacia. Retirar controladores viejos y crear UNO nuevo:',
              'mm mobs kill astral_santuario_control_sala1',
              f'execute in minecraft:{WORLD} run forceload remove all',
              f'execute in minecraft:{WORLD} run forceload add {BOUNDS[0]} {BOUNDS[1]} {BOUNDS[2]} {BOUNDS[3]}',
              f'mm mobs spawn astral_santuario_control_sala1 1 {w},{CENTER[0]},{CENTER[1]},{CENTER[2]}',
              f'# Revision OP: execute in minecraft:{WORLD} run minecraft:tp <jugador> {ARRIVAL[0]} {ARRIVAL[1]} {ARRIVAL[2]} 0 0']
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
        f'execute in minecraft:{WORLD} run forceload add {BOUNDS[0]} {BOUNDS[1]} {BOUNDS[2]} {BOUNDS[3]}',
        *[f'execute in minecraft:{WORLD} run gamerule minecraft:{rule} {value}' for rule,value in (
            ('keep_inventory','true'),('spawn_mobs','false'),('random_tick_speed','0'),
            ('mob_griefing','false'),('tnt_explodes','false'),('advance_weather','false'))]])+'\n'
    files.setdefault('data/astral/function/load.mcfunction','')
    files['data/astral/function/load.mcfunction'] += 'function astral:santuario/load\n'
