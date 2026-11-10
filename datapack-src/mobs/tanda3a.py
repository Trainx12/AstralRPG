"""Planta de oleadas y estatuas; no coloca ninguna entidad en el Santuario."""
from pathlib import Path
import re
import yaml
from mobs.tamanos import skills as size_skills

ROOT=Path(__file__).resolve().parents[2]
PLANT_POINTS=((1448.5,102,1564.5),(1478.5,102,1561.5),(1457.5,97,1579.5))
PLANT_COUNTS={2:2,3:3}
STATUES=('cangrejo','chaman','momia','yeti','golem_forja')


def statues():
    from mobs.mythic import MOBS
    data={}
    for name in STATUES:
        model='astral_'+name; boss=MOBS[model]
        title=re.sub(r'&[0-9a-fk-or]', '', boss['name'], flags=re.I)
        data['astral_estatua_'+name]={
            'Type':boss['type'], 'Display':f'&6&l{title} &7- Guardian derrotado', 'Health':100,
            'Options':dict(NoAI=True,Invincible=True,Silent=True,Despawn=False,Persistent=True,
                           Collidable=False,NoGravity=True,PreventItemPickup=True,PreventOtherDrops=True,
                           PreventSunburn=True,PreventRandomEquipment=True,AlwaysShowName=True),
            'Skills':[f'model{{m={model};s=2.0}} @self ~onSpawn',
                      f'model{{m={model};s=2.0}} @self ~onLoad',
                      'cancelevent @self ~onDamaged','cancelevent @self ~onInteract']}
    return data


def plant():
    return {'astral_bosque_planta':{
        'Type':'HUSK','Display':'&dPlanta carnivora','Health':40,'Damage':6,
        'Options':dict(NoAI=True,NoGravity=True,MovementSpeed=0,KnockbackResistance=1,Collidable=False,
                       Glowing=True,Silent=True,Despawn=False,PreventOtherDrops=True,
                       PreventSunburn=True,PreventRandomEquipment=True,PreventItemPickup=True),
        'Skills':['skill{s=AST_PLANTA_INICIO} @self ~onSpawn',
                  'skill{s=AST_PLANTA_MODELO} @self ~onLoad',
                  'skill{s=AST_PLANTA_MORDIDA} @self ~onTimer:30 ?playerwithin{d=3}',
                  'skill{s=AST_PLANTA_ESCUPIR} @self ~onTimer:80 ?playerwithin{d=12}']}}


def plant_skills():
    init=['addtag{tag=ad.bosque.sala1} @self','addtag{tag=ad.bosque.sala1.wave} @self',
          'addtag{tag=ad.vanilla} @self',
          'command{c="execute as <caster.uuid> at @s run function astral:mob/roll"} @self',
          'skill{s=AST_PLANTA_MODELO} @self']
    # No reroll al cargar un chunk: conserva tier, vida y pertenencia a la sala.
    data={'AST_PLANTA_INICIO':{'Skills':init},
          'AST_PLANTA_MODELO':{'Skills':['model{m=astral_bosque_planta} @self',
              *size_skills('astral_bosque_planta',1,'HUSK',protect_sanctuary=False)]},
          'AST_PLANTA_MORDIDA':{'Skills':['state{s=attack} @self',
              'damage{a=6;pkb=false} @PlayersInRadius{r=3}']},
          'AST_PLANTA_ESCUPIR':{'Skills':['state{s=spit} @self',
              'projectile{onTick=AST_PLANTA_VENENO_TRAZA;onHit=AST_PLANTA_VENENO;v=7;i=1;hR=0.5;vR=0.5;mr=12;g=0.02} @PlayersInRadius{r=12}']},
          'AST_PLANTA_VENENO_TRAZA':{'Skills':['particles{p=slime;amount=3;hS=0.1;vS=0.1} @origin']},
          'AST_PLANTA_VENENO':{'Skills':['damage{a=6;pkb=false} @PlayersNearOrigin{r=1}',
              'potion{type=POISON;duration=60;level=0} @PlayersNearOrigin{r=1}']}}
    for wave,count in PLANT_COUNTS.items():
        data[f'AST_PLANTAS_OLA{wave}']={'Skills':[
            f'summon{{type=astral_bosque_planta;amount=1;radius=0}} @Location{{x={x};y={y};z={z}}}'
            for x,y,z in PLANT_POINTS[:count]]}
    return data


def generate():
    for sub,data in (('mobs',plant()|statues()),('skills',plant_skills())):
        dest=ROOT/'build/mythicmobs'/sub/'tanda3a.yml'
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text('# Generado por mobs/tanda3a.py (mythic.py)\n'+yaml.safe_dump(
            data,allow_unicode=True,sort_keys=False,width=10000),encoding='utf-8')
