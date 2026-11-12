"""Panel lateral (TAB) segun el mundo (pedido del dueno 12/11/2026).

TAB usa el primer tablero cuyo display-condition se cumple. Se agregan antes de los existentes:
- Mazmorra Infinita: tier, tiempo a la proxima subida y bajas (scores que pone astral_infinita.sk).
- Parkour y mini juegos: tiempo en el mapa (score pk.seg/pk.min de astral_panel_mundos.sk) y muertes.
- Arenas PvP: bajas y muertes contra jugadores, como desafiar.
- Survival (mundo, Nether, End): coordenadas, bioma, nivel, muertes y monstruos.
El lobby sigue con misiones diarias e historia (tablero "astral"); mazmorras y minas, con los suyos.
"""
from pathlib import Path

from sidebar import TITLE, DIVIDER, PURPLE, TEXT, MUTED, section, ref, score, condition

ROOT = Path(__file__).resolve().parents[1]
SURVIVAL = ('world', 'world_nether', 'world_the_end')


def _or(name, worlds):
    return (f'  {name}:\n    type: OR\n    conditions:\n' + ''.join(f'      - "%world%={w}"\n' for w in worlds)
            + '    true: "true"\n    false: "false"\n')


def _board(name, cond, rows):
    assert len(rows) <= 15, name
    return (f'    {name}:\n      title: "{TITLE}"\n      display-condition: "%condition:{cond}%=true"\n      lines:\n'
            + ''.join(f'        - "{row}"\n' for row in rows))


def _two(value):
    """mm:ss con cero adelante en los segundos."""
    return f'{score(value)}'


def boards_and_conditions():
    from infinita import WORLDS as INF, TIERS
    from minijuegos import parkour_worlds, arena_worlds
    player = [ref('sidebar_world'), DIVIDER,
              f"{section('♟ Jugador')} {TEXT}%player%",
              f"{PURPLE}◷ {MUTED}Tiempo jugado {TEXT}{ref('playtime')}",
              f"{section('✦ Stats')} {PURPLE}❤ {TEXT}%player_health_rounded%/%player_max_health_rounded%",
              f"{PURPLE}⛃ {MUTED}Oro {TEXT}%vault_eco_balance_formatted%  {PURPLE}⚡ {MUTED}Poder {TEXT}%auraskills_power%",
              f"{PURPLE}☠ {MUTED}Monstruos {TEXT}%statistic_mob_kills%", DIVIDER]
    footer = []  # fecha e IP solo en el TAB
    boards = [
        _board('infinita', 'pm_infinita', player + [
            f"{section('☠ Mazmorra Infinita')}",
            f"{PURPLE}✦ {MUTED}Dificultad {TEXT}{ref('pm_inf_tier')}",
            f"{PURPLE}◷ {MUTED}Sube en {TEXT}{score('inf.min')}:{ref('pm_inf_seg')}",
            f"{PURPLE}⚔ {MUTED}Bajas {TEXT}{score('inf.kills')}",
            f"{PURPLE}♟ {MUTED}/party para jugar en grupo",
            *footer]),
        _board('parkour', 'pm_parkour', player + [
            f"{section('⛰ Mini juegos')}",
            f"{PURPLE}◷ {MUTED}Tiempo aqui {TEXT}{score('pk.min')}:{ref('pm_pk_seg')}",
            f"{PURPLE}☠ {MUTED}Caidas totales {TEXT}%statistic_deaths%",
            f"{PURPLE}» {MUTED}/spawn para salir",
            *footer]),
        _board('arenas', 'pm_arenas', player + [
            f"{section('⚔ Arenas PvP')}",
            f"{PURPLE}⚔ {MUTED}Jugadores vencidos {TEXT}%statistic_player_kills%",
            f"{PURPLE}☠ {MUTED}Muertes {TEXT}%statistic_deaths%",
            f"{PURPLE}» {MUTED}Duelo: /desafiar",
            *footer]),
        _board('survival', 'pm_survival', player + [
            f"{section('⚒ Survival')}",
            f"{PURPLE}✦ {MUTED}Nivel {TEXT}%player_level%  {PURPLE}☠ {MUTED}Muertes {TEXT}%statistic_deaths%",
            f"{PURPLE}» {MUTED}/menu · /sethome · /spawn",
            *footer]),
    ]
    tier_names = {t: n for t, n, _ in TIERS}
    conds = [_or('pm_infinita', INF), _or('pm_parkour', parkour_worlds()), _or('pm_arenas', arena_worlds()),
             _or('pm_survival', SURVIVAL)]
    # Nombre del tier (inf.tier 1..6) y extra de 5+ (inf.plus).
    out = f"<#FF6B6B>{tier_names[6]} (+%objective_score_{{inf.plus}}%)"
    for t in range(6, 0, -1):
        if t == 6:
            conds.append(condition('pm_inf_tier6', f"{score('inf.plus')}>=1", out, tier_names[6]))
            nxt = ref('pm_inf_tier6')
        else:
            conds.append(condition(f'pm_inf_tier{t}', f"{score('inf.tier')}<={t}", tier_names[t], nxt))
            nxt = ref(f'pm_inf_tier{t}')
    conds.append(f'  pm_inf_tier:\n    conditions:\n      - "{score("inf.tier")}>=1"\n    true: "{nxt}"\n    false: "-"\n')
    for key, obj in (('pm_inf_seg', 'inf.seg'), ('pm_pk_seg', 'pk.seg')):
        conds.append(condition(key, f"{score(obj)}>=10", score(obj), '0' + score(obj)))
    return ''.join(boards), ''.join(conds)


def apply(tab_sections):
    boards, conds = boards_and_conditions()
    return tab_sections.replace("  scoreboards:\n", "  scoreboards:\n" + boards, 1).replace(
        "\nconditions:\n", "\nconditions:\n" + conds, 1)


def script():
    """Tiempo en el mapa de mini juegos (pk.min / pk.seg) para el panel."""
    from minijuegos import parkour_worlds
    worlds = ' or '.join(f'"{w}"' for w in parkour_worlds())
    return f'''# Generado por panel_mundos.py: contador del panel lateral en mini juegos.
on load:
    execute console command "scoreboard objectives add pk.min dummy"
    execute console command "scoreboard objectives add pk.seg dummy"

every 1 second:
    loop all players:
        if name of world of loop-player is {worlds}:
            add 1 to {{-pk.t::%uuid of loop-player%}}
            set {{_t}} to {{-pk.t::%uuid of loop-player%}}
            execute console command "scoreboard players set %name of loop-player% pk.min %floor({{_t}} / 60)%"
            execute console command "scoreboard players set %name of loop-player% pk.seg %mod({{_t}}, 60)%"

on world change:
    delete {{-pk.t::%uuid of player%}}
'''


def generate():
    out = ROOT/'build/panel'
    out.mkdir(parents=True, exist_ok=True)
    (out/'astral_panel_mundos.sk').write_text(script(), encoding='utf8')


if __name__ == '__main__':
    generate()
