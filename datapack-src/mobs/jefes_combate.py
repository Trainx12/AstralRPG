"""Combate comun de los jefes (pedido del dueno 13/11/2026): persiguen, pegan de cerca y de lejos.

Cada jefe (por modelo) recibe:
- Velocidad VELOCIDAD (un poco mas que la arana vanilla, 0.30) e IA hostil explicita.
- Golpe al piso (AST_JEFE_SLAM_<modelo>): animacion `slam`, anillo de aviso de radio RADIO_SLAM,
  y al impacto bloques que saltan (blockwave: bloques falsos, no cambia el mapa), columnas de
  particulas alrededor, dano y un empujon hacia arriba. Solo si hay un jugador a 6 bloques o menos.
- Ataque de lejos (AST_JEFE_DISPARO_<modelo>): animacion `throw` y un proyectil tematico a los
  jugadores que esten entre 7 y 32 bloques.
- Salto hacia el objetivo si se aleja mas de 11 bloques (AST_JEFE_SALTO), para que no se escape caminando.
Los tiempos coinciden con mobs/animaciones.py (impacto del slam a los 15 ticks).
El dano de las skills lo multiplica astral_gameplay.sk por el tier de la mazmorra, igual que el golpe.
"""
from mobs.animaciones import SLAM_IMPACTO

VELOCIDAD = 0.33
RADIO_SLAM = 5
IMPACTO_TICKS = round(SLAM_IMPACTO * 20)

# modelo: particula, particula del proyectil, item del proyectil, sonido de aviso, dano slam, dano disparo, efecto extra del disparo
TEMAS = {
    'astral_momia': dict(p='cloud', bloque='SAND', item='SAND', trail='cloud', snd='entity.husk.ambient',
                         slam=8, disparo=6, extra='potion{type=SLOWNESS;duration=40;level=1}'),
    'astral_yeti': dict(p='snowflake', bloque='SNOW_BLOCK', item='SNOWBALL', trail='snowflake', snd='entity.ravager.roar',
                        slam=11, disparo=8, extra='potion{type=SLOWNESS;duration=60;level=1}'),
    'astral_golem_forja': dict(p='flame', bloque='MAGMA_BLOCK', item='MAGMA_BLOCK', trail='flame', snd='entity.blaze.shoot',
                               slam=12, disparo=9, extra='ignite{ticks=50}'),
    'astral_cangrejo': dict(p='bubble_pop', bloque='SAND', item='PRISMARINE_CRYSTALS', trail='splash', snd='entity.guardian.attack',
                            slam=7, disparo=5, extra='throw{velocity=6;velocityY=2}'),
    'astral_chaman': dict(p='happy_villager', bloque='MOSS_BLOCK', item='SLIME_BALL', trail='item_slime', snd='entity.evoker.prepare_attack',
                          slam=6, disparo=5, extra='potion{type=POISON;duration=60;level=1}'),
    'astral_coloso_musgoso': dict(p='spore_blossom_air', bloque='MOSSY_COBBLESTONE', item='MOSSY_COBBLESTONE', trail='spore_blossom_air',
                                  snd='entity.iron_golem.attack', slam=12, disparo=9, extra='potion{type=SLOWNESS;duration=40;level=0}'),
    # Mini jefes de las Minas Olvidadas: mobs vanilla sin modelo 3D (sin animaciones de BetterModel).
    'astral_mina_capataz': dict(p='bubble_pop', bloque='PRISMARINE', item='PRISMARINE_SHARD', trail='splash', snd='entity.drowned.shoot',
                                slam=8, disparo=6, extra='potion{type=SLOWNESS;duration=40;level=0}', modelo=False),
    'astral_mina_golem': dict(p='crit', bloque='COBBLESTONE', item='COBBLESTONE', trail='crit', snd='entity.iron_golem.attack',
                              slam=10, disparo=7, extra='potion{type=SLOWNESS;duration=40;level=0}', modelo=False),
}


def triggers(model):
    """Lineas de Skills (sin el '- ') para el bloque del jefe."""
    if model not in TEMAS:
        return []
    return [f'skill{{s=AST_JEFE_SLAM_{model}}} @self ~onTimer:30 ?playerwithin{{d=6}}',
            f'skill{{s=AST_JEFE_DISPARO_{model}}} @PlayersInRing{{min=7;max=32}} ~onTimer:40',
            'skill{s=AST_JEFE_SALTO} @target ~onTimer:40']


def metaskills():
    """YAML de MythicMobs (skills) comun a todos los jefes."""
    out = ['# Generado por mobs/jefes_combate.py: golpe al piso, disparo y salto de los jefes.',
           'AST_JEFE_SALTO:', '  Cooldown: 7', '  TargetConditions:', '  - distance{d=>11} true', '  Skills:',
           '  - sound{s=entity.ravager.step;v=1.2;p=0.6} @self',
           '  - leap{velocity=130;noise=0}', '']
    for model, t in TEMAS.items():
        p = t['p']
        anim = (lambda st: [f'  - state{{s={st}}} @self']) if t.get('modelo', True) else (lambda st: [])
        out += [f'AST_JEFE_SLAM_{model}:', '  Cooldown: 9', '  Skills:',
                *anim('slam'),
                f'  - sound{{s={t["snd"]};v=1.6;p=0.7}} @self',
                # Aviso: anillo en el piso del radio del golpe, dos veces antes del impacto.
                f'  - particlering{{p={p};radius={RADIO_SLAM};points=48;amount=1;y=0.2}} @self',
                '  - delay 7',
                f'  - particlering{{p={p};radius={RADIO_SLAM};points=48;amount=1;y=0.2}} @self',
                f'  - delay {IMPACTO_TICKS - 7}',
                '  - sound{s=entity.generic.explode;v=1.3;p=0.6} @self',
                '  - sound{s=block.anvil.land;v=0.8;p=0.5} @self',
                # Bloques que saltan alrededor (falsos: el mapa no cambia).
                f'  - blockwave{{m={t["bloque"]};r={RADIO_SLAM};d=14;v=0.35;hv=0;n=0.15;hsb=false}} @selflocation',
                f'  - particles{{p={p};amount=30;hS=0.25;vS=1.6;y=1.6;speed=0.03}} @Ring{{radius=4;points=8}}',
                f'  - particles{{p={p};amount=16;hS=0.25;vS=1;y=1;speed=0.03}} @Ring{{radius=2;points=5}}',
                '  - particles{p=explosion;amount=4;hS=1.5;vS=0.2} @self',
                f'  - damage{{a={t["slam"]}}} @PlayersInRadius{{r={RADIO_SLAM}}}',
                f'  - throw{{velocity=2;velocityY=4}} @PlayersInRadius{{r={RADIO_SLAM}}}',
                '']
        out += [f'AST_JEFE_DISPARO_{model}:', '  Cooldown: 5', '  Skills:',
                *anim('throw'),
                f'  - sound{{s={t["snd"]};v=1.2;p=1.2}} @self',
                '  - delay 8',
                f'  - projectile{{onTick=AST_JEFE_DISPARO_TICK_{model};onHit=AST_JEFE_DISPARO_HIT_{model};v=16;i=1;hR=1;vR=1;mr=40;'
                f'bulletType=ITEM;material={t["item"]};hnp=true}}',
                '',
                f'AST_JEFE_DISPARO_TICK_{model}:', '  Skills:',
                f'  - particles{{p={t["trail"]};amount=3;hS=0.1;vS=0.1;speed=0}} @origin',
                '',
                f'AST_JEFE_DISPARO_HIT_{model}:', '  Skills:',
                f'  - damage{{a={t["disparo"]}}}',
                f'  - {t["extra"]}',
                f'  - particles{{p={p};amount=20;hS=0.6;vS=0.6;speed=0.05}} @origin',
                '']
    return '\n'.join(out) + '\n'
