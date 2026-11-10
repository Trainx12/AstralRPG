"""Guardia de comandos vanilla para funciones, incluidas macros y execute/return run.

Valida raices, no sustituye al parser Brigadier de Paper.
"""
import re

ROOTS = set('''advancement attribute ban ban-ip banlist bossbar clear clone damage data
datapack debug defaultgamemode deop dialog difficulty effect enchant execute experience
fill fillbiome forceload function gamemode gamerule give help item jfr kick kill list
locate loot me msg op pardon pardon-ip particle perf place playsound publish random
recipe reload return ride rotate save-all save-off save-on say schedule scoreboard seed
setblock setidletimeout setworldspawn spawnpoint spectate spreadplayers stop stopsound
summon tag team teammsg teleport tell tellraw test tick time title tm tp transfer trigger
version w weather whitelist worldborder xp fetch profile waypoint stopwatch swing'''.split())


def validate(text, source='<function>'):
    for number, line in enumerate(text.splitlines(), 1):
        command = line.strip().removeprefix('$')
        if not command or command.startswith('#'):
            continue
        while command:
            root = command.split()[0].removeprefix('minecraft:')
            if root not in ROOTS:
                raise AssertionError(f'{source}:{number}: comando no vanilla: {root}')
            if root not in ('execute', 'return') or ' run ' not in command:
                break
            command = command.split(' run ', 1)[1]
