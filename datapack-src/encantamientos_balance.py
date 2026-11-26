"""Temple (excellentenchants:temper) rehecho y nerfeado (25/11/2026, pedido del dueno).

El de ExcellentEnchants sumaba 5% por nivel por cada 0,5 de vida perdida, sin tope. Con la vida escalada
(300 en T1 ... 100.000 en T10) a media vida multiplicaba el dano x100 a x20.000. Ahora es proporcional:

    bonus = POR_NIVEL% x nivel x (vida que falta / vida maxima)

Nivel V: +50% casi muerto, +25% a media vida, nada con la vida llena. Solo golpes cuerpo a cuerpo.
El de EE queda en 0 (ee_descripciones.py AJUSTES; entra al reiniciar).

Regla del dueno: el Temple nuevo arranca solo para ByTrainx. `/temple publico` lo abre, `/temple privado` lo cierra.

26/11 (dueno): los niveles II-V del Temple se sentian iguales; queda SOLO el nivel I (EE MaxLevel 1 en
ee_descripciones.py AJUSTES) y los objetos viejos con II-V cuentan como I.

Trueno (excellentenchants:thunder), 26/11: el de EE sumaba 1,5-2,5 de dano FIJO, nada con el dano escalado
(x5 por tier). Ahora el rayo suma un % del golpe, asi crece con el tier del arma:

    chance = RAYO_CHANCE + RAYO_CHANCE_NIVEL x nivel      (I 10% ... V 18%)
    extra  = RAYO_EXTRA + RAYO_EXTRA_NIVEL x nivel del golpe (I +55% ... V +115%)

El de EE queda con chance 0 (AJUSTES). Arranca solo para ByTrainx: `/rayo publico` | `/rayo privado`.

    python encantamientos_balance.py   ->  build/gameplay/astral_temple.sk  (plugins/Skript/scripts/)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POR_NIVEL = 10   # % extra por nivel con la vida en 0
TEMPLE_MAX = 1   # nivel maximo que cuenta (26/11: solo el I)
RAYO_CHANCE, RAYO_CHANCE_NIVEL = 8, 2    # % de chance
RAYO_EXTRA, RAYO_EXTRA_NIVEL = 40, 15    # % del golpe que suma el rayo
PRUEBA = 'ByTrainx'


def script():
    return f'''# Generado por datapack-src/encantamientos_balance.py: no editar a mano.
# Temple: +{POR_NIVEL}% por nivel x (vida que falta / vida maxima). Reemplaza al de ExcellentEnchants (sin tope).

on damage of living entity:
    attacker is a player
    damage cause is entity attack
    attacker's tool is enchanted with excellentenchants:temper
    if name of attacker is not "{PRUEBA}":
        {{astral.temple.publico}} is true
    set {{_max}} to max health of attacker
    {{_max}} > 0
    set {{_falta}} to {{_max}} - health of attacker
    {{_falta}} > 0
    set {{_lvl}} to level of excellentenchants:temper of attacker's tool
    if {{_lvl}} > {TEMPLE_MAX}:
        set {{_lvl}} to {TEMPLE_MAX}
    set {{_bonus}} to {POR_NIVEL} * {{_lvl}} * {{_falta}} / {{_max}}
    set damage to damage * (1 + {{_bonus}} / 100)

# Trueno: rayo con un % del golpe (crece con el tier del arma). El de ExcellentEnchants queda en chance 0.
on damage of living entity:
    attacker is a player
    damage cause is entity attack
    attacker's tool is enchanted with excellentenchants:thunder
    if name of attacker is not "{PRUEBA}":
        {{astral.rayo.publico}} is true
    set {{_lvl}} to level of excellentenchants:thunder of attacker's tool
    set {{_chance}} to {RAYO_CHANCE} + {RAYO_CHANCE_NIVEL} * {{_lvl}}
    if chance of {{_chance}}%:
        set {{_extra}} to {RAYO_EXTRA} + {RAYO_EXTRA_NIVEL} * {{_lvl}}
        set damage to damage * (1 + {{_extra}} / 100)
        strike lightning effect at victim

command /rayo [<text>]:
    permission: op
    trigger:
        if arg-1 is "publico":
            set {{astral.rayo.publico}} to true
            send "&aTrueno nuevo: abierto para todos." to sender
        else if arg-1 is "privado":
            delete {{astral.rayo.publico}}
            send "&eTrueno nuevo: solo {PRUEBA}." to sender
        else:
            send "&7/rayo publico | privado  ({RAYO_CHANCE}%%+{RAYO_CHANCE_NIVEL}%% por nivel de chance, +{RAYO_EXTRA}%%+{RAYO_EXTRA_NIVEL}%% del golpe)" to sender

command /temple [<text>]:
    permission: op
    trigger:
        if arg-1 is "publico":
            set {{astral.temple.publico}} to true
            send "&aTemple nuevo: abierto para todos." to sender
        else if arg-1 is "privado":
            delete {{astral.temple.publico}}
            send "&eTemple nuevo: solo {PRUEBA}." to sender
        else:
            send "&7/temple publico | privado  (+{POR_NIVEL}%% por nivel segun la vida que falta)" to sender
'''


def main():
    out = ROOT.parent / 'build/gameplay/astral_temple.sk'
    out.write_text(script(), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
