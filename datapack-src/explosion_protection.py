"""Proteccion que no anula el dano de combate (WorldGuard 7)."""

# Los otros cinco flags pedidos tambien pueden cancelar dano a entidades o TNT.
# Ver build/deploy/tanda1.md: se omiten hasta validar la configuracion del servidor.
SAFE_FLAGS = ('enderdragon-block-damage',)
WORLDS = ('mina', 'bosque', 'tumba', 'cumbre', 'cumbre_hielo', 'forja',
          'forja_volcano', 'cavernas', 'exp_desierto', 'exp_hielo', 'exp_nieve', 'exp_santuario')


def commands(world):
    return [f'rg flag -w {world} __global__ {flag} deny' for flag in SAFE_FLAGS]


BLOCK_CONFIG = '''# Fusionar en config.yml del mundo, conservando sus otras claves.
ignition:
  block-tnt: false
  block-tnt-block-damage: true
mobs:
  block-fireball-explosions: false
  block-fireball-block-damage: true
  block-creeper-explosions: false
  block-creeper-block-damage: true
  block-wither-explosions: false
  block-wither-block-damage: true
  block-wither-skull-explosions: false
  block-wither-skull-block-damage: true
'''
