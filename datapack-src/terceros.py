"""Catalogo propio y rutas del circuito privado. Nunca exportar arte a build publico."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def privado():
    return Path(os.environ.get('ASTRAL_PRIVADO', ROOT / '.local/terceros/AstralRPG-privado')).resolve()


# id propio, nombre, rareza, color, icono, efectos de nivel 1/10/20.
PETS = [
    ('ghastito', 'Ghastito de Nube', 'rare', '#EEF3F8', 'GHAST_SPAWN_EGG', ('slow_falling', 'regeneration', 'luck')),
    ('bombardero', 'Bombardero Musgoso', 'epic', '#71AE45', 'CREEPER_SPAWN_EGG', ('resistance', 'strength', 'haste')),
    ('canonero', 'Canonero de Bolsillo', 'rare', '#7A8A99', 'FIRE_CHARGE', ('strength', 'haste', 'luck')),
    ('encapuchado', 'Zorro Encapuchado', 'epic', '#ED994C', 'FOX_SPAWN_EGG', ('speed', 'night_vision', 'strength')),
    ('llamita', 'Llamita Viajera', 'common', '#EACF9A', 'LLAMA_SPAWN_EGG', ('jump_boost', 'luck', 'resistance')),
    ('hondero', 'Pequeno Hondero', 'common', '#CFA272', 'SLIME_BALL', ('haste', 'speed', 'luck')),
    ('saqueador', 'Saqueador Elegante', 'rare', '#9EA882', 'PILLAGER_SPAWN_EGG', ('luck', 'strength', 'resistance')),
    ('brujita', 'Brujita Estelar', 'legendary', '#CC86F1', 'WITCH_SPAWN_EGG', ('regeneration', 'fire_resistance', 'luck')),
    ('desierto', 'Cubito del Desierto', 'common', '#E6C076', 'SAND', ('fire_resistance', 'haste', 'resistance')),
    ('jungla', 'Cubito de la Jungla', 'rare', '#65AD57', 'JUNGLE_SAPLING', ('jump_boost', 'speed', 'strength')),
    ('frondoso', 'Cubito Frondoso', 'rare', '#91D677', 'MOSS_BLOCK', ('regeneration', 'haste', 'resistance')),
    ('micelio', 'Cubito de Micelio', 'epic', '#BB8DAF', 'MYCELIUM', ('regeneration', 'luck', 'absorption')),
    ('pradera', 'Cubito de Pradera', 'common', '#9ACD61', 'WHEAT', ('speed', 'luck', 'regeneration')),
    ('sabana', 'Cubito de Sabana', 'common', '#DCAB61', 'ACACIA_SAPLING', ('haste', 'fire_resistance', 'speed')),
    ('nieve', 'Cubito de Nieve', 'rare', '#C4E7F7', 'SNOWBALL', ('speed', 'resistance', 'luck')),
    ('pantano', 'Cubito de Pantano', 'rare', '#78975B', 'LILY_PAD', ('water_breathing', 'regeneration', 'resistance')),
    ('honguito', 'Honguito Errante', 'epic', '#E6AD79', 'RED_MUSHROOM', ('regeneration', 'resistance', 'haste')),
]

EFFECT_NAMES = {'slow_falling': 'Caida lenta', 'regeneration': 'Regeneracion I', 'luck': 'Suerte',
                'resistance': 'Resistencia I', 'strength': 'Fuerza I', 'haste': 'Prisa I',
                'speed': 'Velocidad I', 'night_vision': 'Vision nocturna', 'jump_boost': 'Salto I',
                'fire_resistance': 'Resistencia al fuego', 'absorption': '2 corazones de absorcion',
                'water_breathing': 'Respiracion acuatica'}


def pet_definitions():
    return {pid: dict(n=i, nombre=name, rareza=rarity, color=color, icono=icon,
                     fuente='Gacha de Monturas', efectos=[[(e, 0)] for e in effects],
                     texto=[('' if j == 0 else '+ ') + EFFECT_NAMES[e] for j, e in enumerate(effects)],
                     # Sin el repositorio privado, se usa un modelo propio disponible.
                     modelo='astral_pet_lobo')
            for i, (pid, name, rarity, color, icon, effects) in enumerate(PETS, 7)}


def sources():
    base = privado() / 'x'
    currets = ['baby_ghast', 'bombardier_creeper', 'cannon', 'hoody_fox', 'llama', 'slingshot', 'swag_pillager', 'twinkle_witch']
    biomes = ['desert', 'jungle', 'lush', 'mushroom', 'plains', 'savanna', 'snow', 'swamp']
    result = {}
    for i, (pid, *_) in enumerate(PETS):
        pack, filename = ('cubees_currets', 'cubee-' + currets[i]) if i < 8 else (
            ('cubees_biomas', 'cubee-' + biomes[i - 8]) if i < 16 else ('shroomling', 'shroomling'))
        candidates = sorted((base / pack).rglob(filename + '.bbmodel'))
        if pack == 'cubees_biomas':
            candidates = [p for p in candidates if 'ItemsAdder Compatibility' in p.parts and 'Cubees Rework – Edition' in p.parts]
        if not candidates:
            raise FileNotFoundError('Falta modelo privado de ' + pid)
        result['astral_pet_' + pid] = candidates[0]
    for mid, pack, filename in [('astral_goblin', 'goblin', 'goofy_goblin'),
                                ('astral_abejorro', 'grub', 'armored_grub'),
                                ('astral_vendedor', 'seller', 'seller'),
                                ('espada_heroe_errante', 'espada', 'Zelda fantasy sword redo')]:
        result[mid] = next((base / pack).rglob(filename + '.bbmodel'))
    return result
