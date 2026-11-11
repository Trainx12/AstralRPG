"""Variantes y conversion de reservas de la cola; no ejecuta mm desde funciones."""
from copy import deepcopy
from pathlib import Path
import yaml
from mobs.tamanos import skills as size_skills

ROOT=Path(__file__).resolve().parents[2]
WEIGHTS={'arquero':30,'escudero':20,'nigromante':15,'espadachin':20,'guardian':15}
NUCLEAR_CHANCE=30
NUCLEAR_DAMAGE=2
NUCLEAR_POWER=2
NORMAL_POWER=3


def definitions():
    mobs={}; skills={}
    for kind in WEIGHTS:
        mid='astral_esq_'+kind
        ranged=kind in ('arquero','nigromante')
        goals=['clear']
        if ranged: goals+=['fleeplayers{d=4;s=1.2;ss=1.2}']
        goals+=['bowattack' if kind=='arquero' else 'lookatplayers' if kind=='nigromante' else 'meleeattack','randomstroll']
        sk=[f'skill{{s=AST_ESQ_MODELO_{kind}}} @self ~onSpawn',f'skill{{s=AST_ESQ_MODELO_{kind}}} @self ~onLoad']
        if kind=='nigromante': sk+=['skill{s=AST_ESQ_HECHIZO} @target ~onTimer:80']
        else: sk+=['state{s=attack} @self ~onShoot' if ranged else 'state{s=attack} @self ~onAttack']
        mobs[mid]={'Type':'SKELETON','Display':'&7'+{'arquero':'Arquero de escarcha','escudero':'Escudero','nigromante':'Nigromante','espadachin':'Espadachin','guardian':'Guardian musgoso'}[kind],
            'Health':26 if kind=='guardian' else 20,'Damage':3,
            'Equipment':['BOW HAND'] if kind=='arquero' else ['IRON_SWORD HAND'] if not ranged else [],
            'Options':dict(Glowing=True,MovementSpeed=.19 if kind=='escudero' else .32 if kind=='espadachin' else .25,
                           PreventSunburn=True,PreventOtherDrops=True,PreventRandomEquipment=True,PreventItemPickup=True,
                           Silent=True,Despawn=False),
            'AIGoalSelectors':goals,'AITargetSelectors':['clear','players'],'Skills':sk}
        skills['AST_ESQ_MODELO_'+kind]={'Skills':[f'model{{m={mid}}} @self',f'addtag{{tag=ad.esq.{kind}}} @self',
            *size_skills(mid,1,'SKELETON',protect_sanctuary=False)]}
        if kind=='nigromante':
            skills['AST_ESQ_MODELO_'+kind]['Skills'].append('brightness{pid=orb;b=15;s=15} @self')
    skills.update({
        'AST_ESQ_HECHIZO':{'Conditions':['targetwithin{d=16} true','targetwithin{d=4} false'],
            'Skills':['state{s=attack} @self','projectile{onTick=AST_ESQ_LUZ;onHit=AST_ESQ_IMPACTO;v=9;i=1;hR=0.5;vR=0.5;mr=16} @target']},
        'AST_ESQ_LUZ':{'Skills':['particles{p=flame;amount=3;hS=0.1;vS=0.1} @origin']},
        'AST_ESQ_IMPACTO':{'Skills':['damage{a=5;pkb=false} @PlayersNearOrigin{r=1}']},
    })
    # Copias explicitas por sala: no se infiere pertenencia buscando al controlador cercano.
    from mobs.mazmorra import MINA
    from mobs.mazmorras_data import catalog
    for d in [MINA]+[d for d in catalog() if d['key'] not in ('santuario','forja')]:
        key=d['key']
        for r in d['rooms']:
            room=r['id']; root=f'AST_ESQ_{key}_{room}'
            # Las oleadas son wave; los dos ayudantes del jefe de Minas son companion.
            suffix='companion' if r.get('boss_room') else 'wave'
            choices=[]
            for kind,weight in WEIGHTS.items():
                mid=f'astral_esq_{kind}_{key}_{room}'
                mob=deepcopy(mobs['astral_esq_'+kind])
                mob['Skills'].insert(0,f'skill{{s={root}_INICIO}} @self ~onSpawn')
                mob['Skills'].append('glowbone{g=true;c=FFFFFF} @self ~onTimer:20')
                mobs[mid]=mob
                choice=root+'_'+kind
                skills[choice]={'Skills':[f'summon{{type={mid};amount=1;radius=0;onSurface=false;sync=true}}']}
                choices.append(f'{choice} {weight}')
            skills[root+'_INICIO']={'Skills':[f'addtag{{tag=ad.{key}.{room}}} @self',f'addtag{{tag=ad.{key}.{room}.{suffix}}} @self',
                'addtag{tag=ad.vanilla} @self','command{c="execute as <caster.uuid> at @s run function astral:mob/roll"} @self']}
            skills[f'AST_ESQ_CONVIERTE_{key}_{room}']={'TargetConditions':[f'hastag{{tag=ad.esq.{key}.{room}}} true'],
                'Skills':[f'removetag{{tag=ad.esq.{key}.{room};sync=true}}','randomskill{s='+','.join(choices)+';sync=true}','remove{sync=true}']}
    mid='astral_creeper_nuclear'
    mobs[mid]={'Type':'CREEPER','Display':'&e&lCreeper Nuclear','Health':20,
        'Options':dict(Glowing=False,ExplosionRadius=NORMAL_POWER*NUCLEAR_POWER,PreventOtherDrops=True,Despawn=True),
        'Skills':['addtag{tag=astral.nuclear} @self ~onSpawn',
            'command{c="execute as <caster.uuid> at @s run function astral:mob/roll"} @self ~onSpawn',
            'skill{s=AST_NUCLEAR_MODELO} @self ~onSpawn','skill{s=AST_NUCLEAR_MODELO} @self ~onLoad',
            'particles{p=dust;color=#6f8a2f;size=0.65;amount=3;hS=0.45;vS=0.7;speed=0} @self ~onTimer:12',
            'particles{p=dust;color=#ffd21f;size=0.5;amount=1;hS=0.3;vS=0.5;speed=0} @self ~onTimer:30',
            'skill{s=AST_NUCLEAR_HINCHAR} @self ~onPrime']}
    skills['AST_NUCLEAR_MODELO']={'Skills':['model{m=astral_creeper_nuclear} @self','brightness{pid=face;b=15;s=15} @self']}
    skills['AST_NUCLEAR_HINCHAR']={'Skills':['state{s=swell} @self','brightness{b=15;s=15} @self','particles{p=dust;color=#ffd21f;size=0.7;amount=12;hS=0.4;vS=0.6} @self']}
    return mobs,skills


def script():
    # Lista positiva: nunca toca lobby, mazmorras, minas, bosque astral ni juegos.
    # Solo NATURAL: los spawns CUSTOM de Mythic no vuelven a tirar la chance.
    return f'''# Generado por mobs/tanda3b.py. Solo el mundo survival world.
on spawn of creeper:
    spawn reason is natural
    name of world of event-entity is "world"
    chance of {NUCLEAR_CHANCE}%:
        set {{_loc}} to location of event-entity
        cancel event
        execute console command "mm mobs spawn astral_creeper_nuclear 1 world,%x-coordinate of {{_loc}}%,%y-coordinate of {{_loc}}%,%z-coordinate of {{_loc}}%"

# LOW antes de la escala de tier y defensa HIGH de astral_gameplay.
on damage with priority low:
    if attacker is set:
        if scoreboard tags of attacker contains "astral.nuclear":
            damage cause is entity explosion
            set damage to damage * {NUCLEAR_DAMAGE}
        if scoreboard tags of attacker contains "ad.esq.arquero":
            damage cause is projectile
            apply slowness 1 to victim for 2 seconds
    if scoreboard tags of victim contains "ad.esq.escudero":
        attacker is set
        set {{_v}} to vector from location of victim to location of attacker
        set {{_f}} to vector from yaw (yaw of victim) and pitch 0
        set {{_angle}} to angle between {{_f}} and {{_v}}
        if {{_angle}} <= 55:
            set damage to damage * 0.45
'''


def generate():
    mobs,skills=definitions()
    for sub,data in (('mobs',mobs),('skills',skills)):
        dest=ROOT/'build/mythicmobs'/sub/'tanda3b.yml'
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text('# Generado por mobs/tanda3b.py\n'+yaml.safe_dump(data,allow_unicode=True,sort_keys=False,width=10000),encoding='utf8')
    (ROOT/'build/gameplay/astral_tanda3b.sk').write_text(script(),encoding='utf8')
