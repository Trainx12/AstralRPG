"""Tanda 16/11: mercader y golems. Solo codigo/configuracion propios."""
import json
from copy import deepcopy
import yaml
from terceros import ROOT
from tanda_xp import XP, NOMBRES, PRECIOS

GOLEM_DUNGEONS = {'bosque': 'bosque', 'mina': 'cristal', 'cumbre': 'hielo'}
# Tiradas independientes por muerte: pequeno / grande / gigante / barril.
GOLEM_XP = {t: (min(.80,.20+.06*t), min(.55,.05+.045*t), min(.30,.01+.022*t), min(.08,.001+.004*t)) for t in range(1,11)}
MERCHANT = [(iid, round(PRECIOS[iid]*.85), 4 if iid!='barril_xp' else 1) for iid in PRECIOS]
from economia import plata as _x
MERCHANT += [(i, _x(p), s) for i, p, s in [('cristal_arcano', 1800, 6), ('cristal_refinado', 6500, 3), ('esencia_elite', 2500, 4),
                                          ('llave_cosmeticos', 425, 3)]]
# 26/11: sin cosmeticos de espalda (retirados); el gacha tampoco los sortea.
MERCHANT_SPECIAL = {
    'llave_cosmeticos': dict(name='Llave virtual de Gacha de Cosmeticos', model='cosmeticos/nav_gacha',
        command='crates give virtual gacha_cosmeticos 1 %player% -s', plugin='CrazyCrates'),
}


def definitions():
    mobs={};skills={}
    for kind in GOLEM_DUNGEONS.values():
        mid='astral_golem_'+kind
        mobs[mid]={'Type':'ZOMBIE','Display':'&aGolem de '+kind,'Health':20,'Damage':3,
            'Options':dict(Silent=True,Glowing=True,MovementSpeed=.25,PreventSunburn=True,PreventOtherDrops=True,
                PreventRandomEquipment=True,PreventItemPickup=True,Despawn=False,FollowRange=64),
            'AIGoalSelectors':['clear','meleeattack','randomstroll'],'AITargetSelectors':['clear','players'],
            'Skills':[f'model{{m={mid}}} @self ~onSpawn',f'model{{m={mid}}} @self ~onLoad',
                'state{s=attack} @self ~onAttack','skill{s=AST_MUERTE} @self ~onDeath',
                'glowbone{g=true;c=FFFFFF} @self ~onTimer:20',
                'sound{s=entity.iron_golem.hurt;v=0.6} @self ~onDamaged',
                'sound{s=entity.iron_golem.death;v=0.6} @self ~onDeath',
                'command{c="execute as <caster.uuid> at @s run function astral:golems/xp"} @self ~onDeath']}
    for kind in GOLEM_DUNGEONS.values():
        mob=deepcopy(mobs['astral_golem_'+kind])
        mob['Skills']=[s for s in mob['Skills'] if not s.startswith('glowbone')]
        mob['Skills'][:0]=['addtag{tag=inf.mob} @self ~onSpawn','addtag{tag=inf.nuevo} @self ~onSpawn','addtag{tag=astral.seen} @self ~onSpawn']
        mobs['astral_golem_'+kind+'_infinita']=mob
    from mobs.mazmorra import MINA
    from mobs.mazmorras_data import catalog
    for d in [MINA]+catalog():
        key=d['key']
        if key not in GOLEM_DUNGEONS:continue
        kind=GOLEM_DUNGEONS[key]
        for r in d['rooms']:
            if r.get('boss_room'):continue
            room=r['id'];mid=f'astral_golem_{kind}_{key}_{room}'
            mob=deepcopy(mobs['astral_golem_'+kind])
            mob['Skills'].insert(0,f'skill{{s=AST_GOLEM_INICIO_{key}_{room}}} @self ~onSpawn')
            mobs[mid]=mob
            skills[f'AST_GOLEM_INICIO_{key}_{room}']={'Skills':[
                f'addtag{{tag=ad.{key}.{room}}} @self',f'addtag{{tag=ad.{key}.{room}.wave}} @self',
                'addtag{tag=ad.vanilla} @self',
                'command{c="execute as <caster.uuid> at @s run function astral:mob/roll"} @self']}
            skills[f'AST_GOLEM_CONVIERTE_{key}_{room}']={'TargetConditions':[f'hastag{{tag=ad.golem.{key}.{room}}} true'],
                'Skills':[f'removetag{{tag=ad.golem.{key}.{room};sync=true}}',
                    f'summon{{type={mid};amount=1;radius=0;onSurface=false;sync=true}}','remove{sync=true}']}
    # Sin selector players ni hurtbytarget: el runtime asigna exclusivamente al agresor.
    mobs['astral_goblin_vendedor']={'Type':'ZOMBIE','Display':'&2Goblin Mercader','Health':10000000,'Damage':3,
        'Options':dict(Silent=True,MovementSpeed=.32,PreventSunburn=True,PreventOtherDrops=True,PreventRandomEquipment=True,
            PreventItemPickup=True,Despawn=False,AlwaysShowName=True),
        'AIGoalSelectors':['clear','meleeattack','lookatplayers','randomstroll'],'AITargetSelectors':['clear'],
        'Skills':['addtag{tag=astral.mercader} @self ~onSpawn','addtag{tag=astral.seen} @self ~onSpawn',
            'model{m=astral_goblin} @self ~onSpawn','model{m=astral_goblin} @self ~onLoad',
            'remove @self ~onTimer:6000']}
    return mobs,skills


def datapack(files):
    def fn(p,lines):files['data/astral/function/'+p+'.mcfunction']='\n'.join(lines)+'\n'
    fn('golems/xp',[f'execute if entity @s[tag=astral.mt{t}] run function astral:golems/xp/t{t}' for t in range(1,11)])
    for t,chances in GOLEM_XP.items():
        fn(f'golems/xp/t{t}',[f'execute if predicate astral:golems/t{t}/{iid} run loot spawn ~ ~0.5 ~ loot astral:item/{iid}' for iid in XP])
        for iid,chance in zip(XP,chances):
            files[f'data/astral/predicate/golems/t{t}/{iid}.json']=json.dumps(dict(condition='minecraft:random_chance',chance=chance))


def generate():
    mobs,skills=definitions()
    for sub,data in [('mobs',mobs),('skills',skills)]:
        p=ROOT/'build/mythicmobs'/sub/'correcciones-goblin.yml';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False,width=10000),'utf8')
    items={}
    for i,(iid,price,stock) in enumerate(MERCHANT):
        special=MERCHANT_SPECIAL.get(iid,{})
        items[iid]={'material':'PAPER','item_model':'astral:'+special.get('model',iid),'slot':10+i,'display_name':'&a'+special.get('name',NOMBRES.get(iid,iid.replace('_',' ').title())),
            'lore':[f'&e{price:,}$',f'&7Limite por visita: {stock}', '&7La compra valida cercania y stock.'],
            'click_commands':[f'[console] astralmercader %player_name% {iid}','[close]']}
    items['close']={'material':'PAPER','item_model':'astral:cosmeticos/nav_close','slot':26,'display_name':'&cCerrar','click_commands':['[close]']}
    p=ROOT/'build/menus/DeluxeMenus/gui_menus/goblin_mercader.yml'
    p.write_text(yaml.safe_dump({'menu_title':'&2Goblin Mercader','size':27,'items':items},allow_unicode=True,sort_keys=False),'utf8')


if __name__=='__main__':generate()
