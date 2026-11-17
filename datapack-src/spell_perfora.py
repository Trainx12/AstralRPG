"""Bastones: seleccion sincronica de cajas reales y hasta tres impactos distintos."""
from escala import HECHIZO_PERFORA


def generate(files):
    def fn(name, lines):
        files['data/astral/function/spell/' + name + '.mcfunction'] = '\n'.join(lines) + '\n'
    # AstralDecor resuelve cajas vanilla/BetterModel una sola vez por disparo.
    # El marcador es sincronico: no hay tareas pendientes ni tags compartidos entre ticks.
    fn('fx_rayo', [])  # Se emite tras conocer la longitud real del trazado.
    trace = ['scoreboard players set #spell.end astral.tmp 0',
             'scoreboard players set #spell.ready astral.tmp 0',
             'summon marker ~ ~ ~ {Tags:["astral.spell.perfora"]}',
             'kill @e[type=marker,tag=astral.spell.perfora,distance=0..]',
             'execute unless score #spell.ready astral.tmp matches 1 run return 0']
    for i, factor in enumerate(HECHIZO_PERFORA, 1):
        trace += [f'execute if score #sk astral.tmp matches 1 store result storage astral:tmp spell.dmg float {factor} run scoreboard players get #base astral.tmp',
                  f'execute if score #sk astral.tmp matches 1000 store result storage astral:tmp spell.dmg float {factor * 1000} run scoreboard players get #base astral.tmp',
                  f'execute as @e[tag=astral.spell.hit{i},distance=0..,limit=1] at @s run function astral:spell/hit with storage astral:tmp spell',
                  f'tag @e[tag=astral.spell.hit{i},distance=0..] remove astral.spell.hit{i}']
    trace += ['execute store result storage astral:tmp spell.len float 0.001 run scoreboard players get #spell.mm astral.tmp',
              'function astral:spell/fx_perfora with storage astral:tmp spell',
              'execute if score #spell.wall astral.tmp matches 1 run function astral:spell/wall_end with storage astral:tmp spell',
              'function astral:spell/ray with storage astral:tmp spell']
    fn('trace', trace)
    fn('wall_end', ['$execute positioned ^ ^ ^$(len) run function astral:spell/pared with storage astral:tmp spell'])
    # Sobrescribe tambien cast en ramas anteriores al arreglo de hitboxes, sin incorporarlo.
    key = 'data/astral/function/spell/cast.mcfunction'
    files[key] = files[key].replace('function astral:spell/ray with storage', 'function astral:spell/trace with storage')
    fn('fx_perfora', ['$execute if entity @a[scores={astral.fx=1..,astral.fx.bastones=1..},distance=..96] run summon marker ~ ~ ~ {Tags:["astral.fx","fx.rayo","fxc.$(fxh)","fxe.$(fxe)","fxlen.$(len)"]}'])
    old = files['data/astral/function/spell/ray.mcfunction'].splitlines()
    fn('ray', old[:4] + [
        'execute if score #steps astral.tmp >= #spell.end astral.tmp run return 0',
        'scoreboard players add #steps astral.tmp 1',
        'execute positioned ^ ^ ^0.5 run function astral:spell/ray with storage astral:tmp spell'])
    hit = files['data/astral/function/spell/hit.mcfunction'].splitlines()
    fn('hit', ['tag @s add astral.spell.hit'] + hit[:-1] + ['tag @s remove astral.spell.hit', 'return 1'])
