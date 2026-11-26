"""24/11 (dueno): skill minima para equipo sin clase (Carnivora, Agua) y ropa de oficio.
Mismo nivel que el arma del tier (items.ARMOR_LEVEL_SIN_CLASE); picos y palas como el taladro del tier."""
from items import SKILLS, ARMOR_LEVEL_SIN_CLASE
from tools import DRILLS, CHAINSAWS


def nivel(iid, tier):
    """(skill, nivel) del item, o None si queda sin requisito."""
    if iid.endswith(('_pico', '_pala')):
        return 'mining', DRILLS[tier - 1]['lvl']
    if iid.startswith('minero_'):
        return 'mining', DRILLS[tier - 1]['lvl']
    if iid.startswith('talador_'):
        return 'foraging', CHAINSAWS[tier - 1]['lvl']
    return 'fighting', ARMOR_LEVEL_SIN_CLASE[tier]


def pdc(kind, iid, tier):
    skill, lvl = nivel(iid, tier)
    return {f'auraskills:{kind}_requirements': {f'auraskills:{skill}': int(lvl)}}


def linea(txt, iid, tier):
    skill, lvl = nivel(iid, tier)
    return txt(f'Requiere: {SKILLS[skill]} {lvl}', 'red')
