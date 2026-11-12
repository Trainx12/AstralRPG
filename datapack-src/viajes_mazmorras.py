"""Menu y comando de viajes personales, desbloqueados al hablar con cada guardian."""
import json
from pathlib import Path
from mobs.mazmorra import MINA
from mobs.mazmorras_data import catalog
from adventure_ui import title as adventure_title, regions

ROOT=Path(__file__).resolve().parent.parent
ORDER=('bosque','mina','tumba','cumbre','forja','santuario')   # posiciones del arte del menu
# Progreso por dificultad (tier): para la expedicion de una hay que terminar la anterior.
PROGRESO=('bosque','mina','tumba','cumbre','forja','santuario')
ICONS=('OAK_SAPLING','IRON_PICKAXE','CHISELED_SANDSTONE','SNOWBALL','BLAZE_POWDER','NETHER_STAR')
EXPLORATION={
    'bosque':('cavernas',(172.5,102,89.5,0,0)),
    'tumba':('exp_desierto',(180.233,102,134.266,-124.8,0)),
    'mina':('cavernas',(172.5,102,89.5,0,0)),
    'cumbre':('exp_nieve',(16.5,83,10.5,0,0)),
    'forja':('forja',(1536.5,222,1900.5,0,0)),
    'santuario':('exp_santuario',(26.5,103,-31.5,180,0)),
}


def destinations():
    data={d['key']:d for d in [MINA]+catalog()}
    return [data[key] for key in ORDER]


def numero(key):
    return PROGRESO.index(key)+1


def completada(key):
    return f'astral.completada.{key}'


def permission(key):
    return f'astral.descubierto.{key}'


def menu_data():
    items={}
    for index,(d,icon) in enumerate(zip(destinations(),ICONS)):
        key=d['key'];slot=(10,11,12,14,15,16)[index]
        req={'requirements':{'descubierta':{'type':'has permission','permission':permission(key)}}}
        where={'bosque':'Cavernas','tumba':'Desierto','mina':'Cavernas','cumbre':'Hielo','forja':'Reino','santuario':'Santuario'}[key]
        items[key]={
            'material':icon,'slot':slot,'priority':1,'display_name':f'&a&l{numero(key)}. {d["name"]}',
            'lore':['&aDestino descubierto.','&7Clic para viajar al inicio de la mazmorra.'],
            'view_requirement':req,'click_requirement':dict(req,deny_commands=['[message] &cPrimero encuentra y habla con su aldeano.']),
            'click_commands':['[close]',f'[player] mazmorras {key}']}
        items[key+'_bloqueada']={
            'material':'GRAY_DYE','slot':slot,'priority':2,'display_name':f'&8&l{numero(key)}. {d["name"]}',
            'lore':['&cSin descubrir.',f'&7Busca a su aldeano en {where}.','&7Habla con el al menos una vez para desbloquearla.'],
            'click_commands':['[message] &ePrimero debes encontrar y hablar con el aldeano de esta mazmorra.','[sound] ENTITY_VILLAGER_NO']}
    items['info']={'material':'COMPASS','slot':4,'display_name':'&b&lMazmorras descubiertas',
                   'lore':['&7Encuentra a cada guardian para guardar su destino.','&7Tus descubrimientos son personales y permanentes.',
                           '&7Tambien puedes usar &e/mazmorras <destino>&7.']}
    items['cerrar']={'material':'BARRIER','slot':53,'display_name':'&cCerrar','click_commands':['[close]']}
    items['volver']={'material':'ARROW','slot':45,'display_name':'&fVolver al atlas','click_commands':['[openguimenu] principal']}
    items['explorar']={'material':'MAP','slot':49,'display_name':'&aBuscar nuevos destinos','click_commands':['[openguimenu] expediciones']}
    items['ayuda']={'material':'BOOK','slot':51,'display_name':'&dSellos de descubrimiento',
                    'lore':['&7El candado indica un portal sin descubrir.','&7Habla con su guardian para activarlo.']}
    items['saldo']={'material':'GOLD_NUGGET','slot':8,'display_name':'&6Tu saldo','lore':['&e%vault_eco_balance_formatted%$'],'update':True}
    themed_cards(items,'mazmorras')
    return {'menu_title':adventure_title('mazmorras'),'size':54,'update_interval':1,'items':items}


def themed_cards(items,kind):
    """Todas las piezas de una tarjeta conservan la misma accion y requisitos."""
    from copy import deepcopy
    for key,slots in regions(kind):
        for locked in ((False,True) if kind=='mazmorras' else (False,)):
            name=key+('_bloqueada' if locked else '')
            original=items.pop(name)
            for index,slot in enumerate(slots):
                entry=deepcopy(original)
                entry.update(material='PAPER',slot=slot,item_model=f'astral:aventuras/{kind}_{key}'+('_locked' if locked else '')+f'_{index}')
                entry['item_flags']=['HIDE_ATTRIBUTES']
                items[name if index==0 else f'{name}_hit_{index}']=entry


def script():
    lines=['# Generado por viajes_mazmorras.py. No acepta un jugador destino ni comandos del usuario.',
           'command /mazmorras [<text>]:','    executable by: players','    description: Viaja a una mazmorra descubierta.',
           '    trigger:','        if arg-1 is not set:',
           '            execute console command "dm open mazmorras %name of player%"','            stop',
           '        set {_destino} to arg-1','        if {_destino} is "minas":','            set {_destino} to "mina"']
    for d in destinations():
        key=d['key'];x,y,z=d['rooms'][0]['llegada']
        lines += [f'        if {{_destino}} is "{key}":',
                  f'            if player does not have permission "{permission(key)}":',
                  '                send "&cPrimero debes encontrar y hablar con el aldeano de esta mazmorra." to player',
                  '                stop']
        if not d.get('enabled',False):
            lines += ['            send "&eEsta mazmorra esta en preparacion." to player','            stop']
        else:
            # Copia libre, party y "ocupada": mazmorras_copias.py.
            lines += [f'            execute console command "mazentrar %name of player% {key}"','            stop']
    lines += ['        send "&eDestinos: bosque, mina, tumba, cumbre, forja y santuario." to player']
    return '\n'.join(lines)+'\n'


def exploration_menu():
    items={}
    names={d['key']:d['name'] for d in destinations()}
    for index,(d,icon) in enumerate(zip(destinations(),ICONS)):
        key=d['key']
        items[key]={'material':icon,'slot':(10,11,12,14,15,16)[index],
                    'display_name':f'&b&l{numero(key)}. {d["name"]}',
                    'lore':['&7Viaja al mapa de exploracion.','&7Busca al aldeano que guarda la entrada.',
                            *([f'&cRequiere terminar: &f{names[PROGRESO[numero(key)-2]]}'] if numero(key)>1 else []),
                            '&eClic para comenzar la busqueda.'],
                    'click_commands':['[close]',f'[player] expediciones {key}']}
    items['info']={'material':'COMPASS','slot':4,'display_name':'&b&lElige tu expedicion',
                   'lore':['&7Van en orden: termina una mazmorra','&7para abrir la expedicion siguiente.','&7Habla con su guardian para desbloquear el viaje rapido.']}
    items['lobby']={'material':'NETHER_STAR','slot':49,'display_name':'&a&lVolver al lobby',
                    'click_commands':['[close]','[player] spawn']}
    items['descubiertas']={'material':'ENDER_PEARL','slot':51,'display_name':'&d&lViaje rapido: mazmorras descubiertas',
                          'click_commands':['[openguimenu] mazmorras']}
    items['cerrar']={'material':'BARRIER','slot':53,'display_name':'&cCerrar','click_commands':['[close]']}
    items['volver']={'material':'ARROW','slot':45,'display_name':'&fVolver al atlas','click_commands':['[openguimenu] principal']}
    items['saldo']={'material':'GOLD_NUGGET','slot':8,'display_name':'&6Tu saldo','lore':['&e%vault_eco_balance_formatted%$'],'update':True}
    themed_cards(items,'expediciones')
    return {'menu_title':adventure_title('expediciones'),'size':54,'update_interval':1,'items':items}


def exploration_script():
    lines=['# Rutas de exploracion publicas. El viaje directo a la mazmorra se controla por separado.',
           'command /expediciones [<text>]:','    aliases: expedicion','    executable by: players',
           '    trigger:','        if arg-1 is not set:',
           '            execute console command "dm open expediciones %name of player%"','            stop']
    names={d['key']:d['name'] for d in destinations()}
    for key,(world,spawn) in EXPLORATION.items():
        coords=' '.join(map(str,spawn))
        lines += [f'        if arg-1 is "{key}":']
        if numero(key)>1:
            prev=PROGRESO[numero(key)-2]
            lines += ['            if player is not op:',
                      f'                if player does not have permission "{completada(prev)}":',
                      f'                    send "&cPrimero termina la mazmorra &f{names[prev]}&c." to player',
                      '                    stop']
        lines += [
                  f'            execute console command "execute in minecraft:{world} run minecraft:tp %name of player% {coords}"',
                  '            stop']
    lines += ['        send "&eUsa /expediciones para elegir un destino." to player']
    return '\n'.join(lines)+'\n'


def generate():
    from menu_ui import decorate
    menu=ROOT/'build/menus/DeluxeMenus/gui_menus/mazmorras.yml'
    skript=ROOT/'build/mapas_exploracion/astral_viajes.sk'
    menu.parent.mkdir(parents=True,exist_ok=True);skript.parent.mkdir(parents=True,exist_ok=True)
    # JSON es YAML valido y preserva exactamente los requisitos anidados.
    menu.write_text(json.dumps(decorate(menu_data()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    menu.with_name('expediciones.yml').write_text(json.dumps(decorate(exploration_menu()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    skript.write_text(script()+'\n'+exploration_script(),encoding='utf-8')
    guides=[]
    for world,x,y,z,floor in [('exp_desierto',179.5,102,135.5,'sandstone'),
                              ('exp_santuario',25.5,103,-31.5,'sandstone')]:
        import math
        bx,bz=math.floor(x),math.floor(z)
        near=f'@e[type=minecraft:villager,x={x},y={y},z={z},distance=..0.6,limit=1]'
        guides += [f'execute in minecraft:{world} run forceload add {bx} {bz}',
                   f'rg flag -w {world} __global__ mob-spawning allow',
                   f'execute in minecraft:{world} if block {bx} {y-1} {bz} minecraft:{floor} '
                   f'if block {bx} {y} {bz} minecraft:air if block {bx} {y+1} {bz} minecraft:air '
                   f'unless entity {near} run mm mobs spawn astral_npc_guia_expediciones 1 {world},{x},{y},{z}',
                   f'execute in minecraft:{world} run data get entity {near} Pos',
                   f'execute in minecraft:{world} run forceload remove {bx} {bz}']
    skript.with_name('guias-expediciones.txt').write_text('\n'.join(guides)+'\n',encoding='utf-8')
    # Ajuste solicitado en captura F3 del dueno; solo el guia y su NPC de prueba.
    old_guide='@e[type=minecraft:villager,x=184.5,y=95,z=145.5,distance=..0.6,limit=1]'
    test_guardian='@e[type=minecraft:villager,x=185.27445222064034,y=95,z=144.0311717429187,distance=..0.15,limit=1]'
    desert_adjustment=[
        'execute in minecraft:exp_desierto run forceload add 176 128 191 159',
        'execute in minecraft:exp_desierto if block 179 101 135 minecraft:sandstone '
        'if block 179 102 135 minecraft:air if block 179 103 135 minecraft:air '
        f'run minecraft:tp {old_guide} 179.5 102 135.5 -124.8 0',
        'mv setspawn exp_desierto:180.233,102,134.266,-124.8,0',
        f'execute in minecraft:exp_desierto run minecraft:data merge entity {test_guardian} {{Health:0.0f}}',
        f'execute in minecraft:exp_desierto run minecraft:kill {test_guardian}',
        'skript reload astral_viajes',
        'execute in minecraft:exp_desierto run minecraft:data get entity '
        '@e[type=minecraft:villager,x=179.5,y=102,z=135.5,distance=..0.6,limit=1] Pos',
        f'execute in minecraft:exp_desierto if entity {test_guardian} run minecraft:data get entity {test_guardian} Pos',
        'execute in minecraft:exp_desierto run forceload remove 176 128 191 159',
    ]
    skript.with_name('ajuste-desierto.txt').write_text('\n'.join(desert_adjustment)+'\n',encoding='utf-8')
    audit_loads=[];audit_checks=[];audit_cleanup=[]
    arrivals=[('cavernas',172.5,102,91.5),('exp_desierto',179.5,102,135.5),
              ('exp_santuario',25.5,103,-31.5)]
    for world,x,y,z in arrivals:
        report_path=ROOT/'.local/mapas/astral-nuevos/preparados'/f'{world}-informe.json'
        if not report_path.exists():continue # Los mapas privados no son necesarios para generar los menus.
        report=json.loads(report_path.read_text(encoding='utf-8'))
        selector=f'@e[type=minecraft:villager,x={x},y={y},z={z},distance=..0.6,limit=1]'
        conditions=[]
        for bx,by,bz,floor in report['aparicion']['piso_3x3']:
            conditions.append(f'if block {bx} {by} {bz} {floor}')
            conditions += [f'if block {bx} {by+h} {bz} minecraft:air' for h in (1,2,3)]
        audit_loads.append(f'execute in minecraft:{world} run forceload add {int(x)} {int(z)}')
        audit_checks += [f'execute in minecraft:{world} '+ ' '.join(conditions)+f' run minecraft:data get entity {selector} Pos']
        audit_cleanup.append(f'execute in minecraft:{world} run forceload remove {int(x)} {int(z)}')
    for filename,lines in [('preparar-revision.txt',audit_loads),('comprobar-llegadas.txt',audit_checks),
                           ('liberar-revision.txt',audit_cleanup)]:
        skript.with_name(filename).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    skript.with_name('revisar-llegadas.txt').write_text('\n'.join(audit_loads+audit_checks+audit_cleanup)+'\n',encoding='utf-8')


if __name__=='__main__':generate()
