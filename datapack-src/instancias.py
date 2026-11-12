"""Copias de las mazmorras (pedido del dueno 12/11/2026): 6 por mazmorra, hasta ~20 jugadores.

Cada copia es un mundo propio (clon del original). La copia 1 es el mundo de siempre.
Entrada, parties y el limite de 8 minutos despues del jefe: mazmorras_copias.py (Skript).
"""
COPIES = 6
# Mundos de Multiverse (se clonan con `mv clone`).
MV_WORLDS = {'mina': 'mina', 'bosque': 'bosque', 'tumba': 'tumba', 'cumbre': 'cumbre_hielo', 'forja': 'forja_volcano'}
# El Santuario es una dimension del datapack: sus copias son dimensiones nuevas del datapack.
SANCTUARY = 'santuario_azeroth'
DUNGEON_WORLDS = {**MV_WORLDS, 'santuario': SANCTUARY}


def copias(world):
    """Nombres de dimension (minecraft:<nombre>) de todas las copias de un mundo de mazmorra."""
    base = world.removeprefix('world_minecraft_')
    names = [base] + [f'{base}_{n}' for n in range(2, COPIES + 1)]
    return ['world_minecraft_' + n for n in names] if world.startswith('world_minecraft_') else names


def bukkit(dimension):
    """Nombre del mundo para Bukkit/Skript: las dimensiones del datapack llevan prefijo."""
    return 'world_minecraft_' + dimension if dimension.startswith(SANCTUARY) else dimension


def expand(names):
    """Agrega las copias de los mundos de mazmorra a una lista, conservando el resto y el orden."""
    out = []
    for name in names:
        base = name.removeprefix('world_minecraft_')
        out += copias(name) if base in DUNGEON_WORLDS.values() else [name]
    return tuple(dict.fromkeys(out))


def expand_map(mapping):
    """Igual que expand, para diccionarios {mundo: valor}."""
    out = {}
    for name, value in mapping.items():
        base = name.removeprefix('world_minecraft_')
        for copy in (copias(name) if base in DUNGEON_WORLDS.values() else [name]):
            out.setdefault(copy, value)
    return out
