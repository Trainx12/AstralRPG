"""Genera la entrega y los comandos de actualizacion sin tocar mundos."""
import hashlib
import json
import math
from pathlib import Path
from mobs.tamanos import ROOT, rows, dimensions, scale, VANILLA, preview

LEGACY_CENTERS={
 'mina':[(10.5,-45,-124.5),(19.5,-39,-158.5),(43.5,-24,-201.5),(36.5,24,-248.5)],
 'bosque':[(1440.5,104,1568.5),(1504.5,107,1504.5),(1600.5,97,1440.5)],
 'tumba':[(-148.5,60,-98.5),(-175.5,88,203.5),(.568,72,.512)],
 'cumbre':[(16.5,64,18.5),(24.5,66,-1.5),(6.5,63,32.5)],
 'forja':[(82.5,52,-55.5)]}

def upgrade_commands(d):
    from explosion_protection import commands as explosion_commands
    key=d['key']; w=d['world']
    lines=['# Actualizacion Tanda 2. Mazmorra VACIA. No crear/importar/reemplazar mundos.',
           '# Respaldar archivos del servidor; apagar para instalar el datapack y YAML, luego iniciar.',
           '# El arranque carga MythicMobs; si se ajusto despues: mm reload.',
           '# Cargar y retirar cada controlador anterior.']
    for i,(x,y,z) in enumerate(LEGACY_CENTERS[key],1):
        lines += [f'execute in minecraft:{w} run forceload add {math.floor(x)} {math.floor(z)}',
                  f'mm mobs kill astral_{key}_control_sala{i}',
                  f'execute in minecraft:{w} run forceload remove {math.floor(x)} {math.floor(z)}']
    # Retirar tambien controladores nuevos de una instalacion parcial, sin duplicarlos.
    for r in d['rooms']:
        x,y,z=r['centro']
        lines += [f'execute in minecraft:{w} run forceload add {math.floor(x)} {math.floor(z)}',
                  f'mm mobs kill astral_{key}_control_{r["id"]}',
                  f'execute in minecraft:{w} run function astral:tanda2/{key}/{r["id"]}/cleanup',
                  f'execute in minecraft:{w} run forceload remove {math.floor(x)} {math.floor(z)}']
    lines += ['# Limpiar restos de la version anterior (solo IDs de ESTA mazmorra).']
    legacy={
        'mina':['minero','esqueleto','ahogado','arana','capataz','golem','guardian'],
        'bosque':['espantapajaros','abejorro','cara','chaman'],
        'tumba':['espantapajaros','arana','cara','momia']+[f's{n}_{m}' for n in (1,2) for m in ('arana','momia','esqueleto','cara','espantapajaros','golem')],
        'cumbre':['arana','cara','espantapajaros','yeti'],
        'forja':['espantapajaros','arana','cara','golem_forja']}
    lines += [f'mm mobs kill astral_{key}_{m}' for m in legacy[key]]
    lines += ['# Crear exactamente un controlador en cada punto nuevo.']
    for r in d['rooms']:
        x,y,z=r['centro']
        lines += [f'execute in minecraft:{w} run forceload add {math.floor(x)} {math.floor(z)}',
                  f'mm mobs spawn astral_{key}_control_{r["id"]} 1 {w},{x},{y},{z}',
                  f'execute in minecraft:{w} run forceload remove {math.floor(x)} {math.floor(z)}']
    lines += ['# Conservar NPC, protecciones y permisos existentes. No ejecutar mv create ni pegar mapas.', *explosion_commands(w)]
    return '\n'.join(lines)+'\n'

def collision(world,point,entity,sc):
    from mobs.terreno import get,AIR,solid
    x,y,z=point; width,height=VANILLA[entity]; width*=sc; height*=sc
    found=[]; count=0; solids=0; types={}
    for xx in range(math.floor(x-width/2),math.ceil(x+width/2)):
        for zz in range(math.floor(z-width/2),math.ceil(z+width/2)):
            for yy in range(math.floor(y),math.ceil(y+height)):
                block=get(world,xx,yy,zz)
                if block not in AIR:
                    count+=1
                    solids+=int(solid(block))
                    types[block]=types.get(block,0)+1
                    if len(found)<8: found.append([xx,yy,zz,block])
    return dict(ancho=round(width,3),alto=round(height,3),bloques_no_aire=count,
                bloques_solidos=solids,tipos=types,ejemplos=found)


def movement(world,point,entity,sc):
    """Muestrea trayectos cortos, sin inferir la IA ni cambiar el punto pedido."""
    x,y,z=point
    return {name:[dict(distancia=distance,**collision(world,(x+dx*distance,y,z+dz*distance),entity,sc))
                  for distance in (.25,.5,.75,1)]
            for name,dx,dz in [('este',1,0),('oeste',-1,0),('sur',0,1),('norte',0,-1)]}

def generate():
    from mobs.mazmorra import MINA
    from mobs.mazmorras_data import catalog
    from escala import VIDA_JEFE, fmt
    ds=[MINA]+[d for d in catalog() if d['key']!='santuario']
    folder=ROOT/'build/deploy'; folder.mkdir(parents=True,exist_ok=True)
    preview()
    models=rows(); size_rows=['| Mob | s | Alto modelo (bloques) | scale | Alto caja vanilla |',
                            '|---|---:|---:|---:|---:|']
    for mid,model,s,entity in models:
        sc=scale(model,s,entity)
        size_rows.append(f'| {mid} | {s:g} | {dimensions(model,s)[1]:.3f} | {sc:g} | {VANILLA[entity][1]*sc:.3f} |')
    doc=ROOT/'docs/ESCALA_TIERS.md'; text=doc.read_text(encoding='utf-8'); marker='\n## Tanda 2: cajas medidas y vida de jefes\n'
    text=text.split(marker)[0]+marker+'\nVida: Bosque 12.500; Minas 72.000; Tumba 460.000; Cumbre 2.475.000; Forja 13.125.000. '+\
         'Se genera desde `EZ_JEFE × VIDA_REF` en `escala.py`.\n\n'+\
         'Oleadas: 87% tier de la mazmorra, 3% uno mas y 10% uno menos (limites 1–5). '+\
         'Mundo abierto conserva 86/4/10. Jefes del mundo y Ancestrales fuera del Santuario: '+\
         '25 EZ del tier calculado por `mob/tier_mundo` al aparecer; sin arma o sin jugador cercano, T1. '+\
         'No se vuelven a curar al cargar chunks. Santuario conserva sus atributos previos.\n\n'+\
         'Medicion de todas las esquinas de los cubos existentes, con rotaciones, en pose de reposo. '+\
         'Se prioriza el alto: una sola escala no puede igualar proporciones distintas entre modelo y entidad. '+\
         'El ancho puede diferir. Las animaciones tampoco tienen una caja dinamica. '+\
         'Mascotas, monturas, NPC y estatuas quedan excluidos.\n\n'+'\n'.join(size_rows)+'\n\n'+\
         'Yeti de Cumbre: modelo de 8 x 14 x 4,4 bloques (`s=4`, dos veces el Ancestral). '+\
         'Caja RAVAGER de 12,409 x 14 con `scale=6,363636`, por debajo del tope 16; coincide el alto, no el ancho. '+\
         'Golem de Forja: modelo 12,9 x 24,25 x 12,9; '+\
         '`scale=8,981481`, priorizando el alto. Vista previa: `build/previews/tamanos-jefes.png`.\n'
    doc.write_text(text,encoding='utf-8')
    pack=ROOT/'build/AstralRPG-Textures.zip'; sha=hashlib.sha1(pack.read_bytes()).hexdigest()
    report=['# Tanda 2: instalacion pendiente','',
            'NO desplegado. El dueno debe ver `build/previews/tamanos-jefes.png` antes de subir.',
            'Servidor actual: Empower (Aternos es copia). No se uso navegador, API ni red para desplegar.',
            'No subir mundos, regiones, mapas, `.local`, logs ni carpetas enteras.', '',
            '## Correccion Tanda 2b', '',
            'Si Tanda 2 ya esta instalada: reemplazar solo `build/mythicmobs/skills/astral.yml` → '+
            '`plugins/MythicMobs/skills/astral.yml`, con Cumbre vacia; ejecutar `mm reload`. '+
            'No requiere apagar ni reiniciar para esta correccion. El siguiente Yeti usa el tamano nuevo; '+
            'un Yeti existente requiere recargar su chunk para aplicar onLoad (comprobar modelo y atributo), '+
            'o completar la partida antes de actualizar. No matar al jefe durante una partida.',
            'Verificar `attribute <UUID> minecraft:scale get` (6.363636), '+
            '`attribute <UUID> minecraft:max_health get` (2475000), ataques, movimiento corto y consola. '+
            'Si Tanda 2 aun no esta instalada, seguir la lista completa y el reinicio indicados abajo.', '',
            '## Archivos locales → destino', '',
            '| Local | Destino |','|---|---|',
            '| build/AstralRPG-Items.zip | world/datapacks/AstralRPG-Items.zip |',
            '| build/lobby/TAB/secciones-config.yml | plugins/TAB/config.yml: agregar type: AND a conditions.daily_count_0..7, conservando el resto |',
            '| build/mythicmobs/mobs/astral.yml | plugins/MythicMobs/mobs/astral.yml |',
            '| build/mythicmobs/skills/astral.yml | plugins/MythicMobs/skills/astral.yml |']
    for name in ('mazmorra','bosque','tumba','cumbre','forja'):
        for sub in ('mobs','skills'): report += [f'| build/mythicmobs/{sub}/{name}.yml | plugins/MythicMobs/{sub}/{name}.yml |']
    report += ['', 'Resource pack y modelos sin cambios; NO subirlos en esta tanda.',
               f'SHA-1 del pack conservado: `{sha}`. URL fija R2 documentada en SERVIDOR.md.', '',
               '## Orden', '',
               '1. Mostrar la vista previa al dueno. Comprobar colisiones y movimiento del Yeti en Paper antes de habilitar Cumbre al publico.',
               '2. Mazmorras vacias: respaldar los archivos que se reemplazan y spigot.yml. Apagar el servidor.',
               '3. Comprobar `settings.attribute.maxHealth.max`: minimo 13125000; conservar o poner 1000000000. '+
               'La copia local fichas-paper tiene 1000000000, pero asw-native conserva 1024; el valor del servidor actual NO esta verificado. '+
               'No subir esas configs locales enteras. Editar solo ese valor si hace falta.',
               '4. Reemplazar los 13 archivos completos listados y editar las 8 condiciones de TAB. No tocar Santuario ni el mundo forja de expedicion.',
               '5. Iniciar: el arranque carga datapack y YAML. Revisar consola por errores de funciones, atributos y MythicMobs. '+
               'Si los YAML/TAB se editaron despues: `mm reload`, `tab reload`. No hace falta `bettermodel reload` ni R2.',
               '6. Ejecutar los bloques siguientes con las mazmorras vacias (limpian controladores viejos, restos y crean los nuevos). '+
               'Los objetivos ad.* se crean al cargar el datapack. Las cargas temporales se retiran al terminar.',
               '7. Probar oleadas con 1, 2 y 5 jugadores: cola, 4 de llegada, limite 6/9, abandono/reset, jefe muerto, ayudantes, cofre y regreso. '+
               'Comprobar magma sin division, piglins/hoglins sin zombificacion, Chaman sin vex, inmunidad al fuego y proyectiles del Yeti. '+
               'Revisar consola y vida real con `attribute <UUID> minecraft:max_health get`. No afirmar despliegue hasta verificarlo.', '',
               '## Resumen por mazmorra', '', '| Mazmorra | Oleadas por sala previa | Puntos | Jefe / vida | s / scale |', '|---|---|---|---|---|']
    audit={}
    for d in ds:
        key=d['key']; model,s,entity={'bosque':('astral_chaman',2,'EVOKER'),'mina':('astral_golem_forja',2,'IRON_GOLEM'),
                                    'tumba':('astral_momia',2,'HUSK'),'cumbre':('astral_yeti',4,'RAVAGER'),'forja':('astral_golem_forja',8,'IRON_GOLEM')}[key]
        report += [f'| {key} | '+', '.join(str(len(r['oleadas'])) for r in d['rooms'][:-1])+' | '+
                   ', '.join(f'{r["id"]}: {len(r["spawn_points"])}' for r in d['rooms'])+f' | {d["rooms"][-1]["centro"]} / {fmt(VIDA_JEFE[key])} | {s} / {scale(model,s,entity)} |']
        audit[key]={r['id']:{k:r[k] for k in ('centro','llegada','spawn_points','spawn_bounds','golem_points') if k in r} for r in d['rooms']}
    report += ['', 'Puntos exactos y selecciones: `build/deploy/tanda2-puntos.json`. Leidos de los mapas locales del servidor, sin modificarlos.', '', '## Limites de tamano comprobados', '']
    for key,entity,model,s in [('cumbre','RAVAGER','astral_yeti',4),('forja','IRON_GOLEM','astral_golem_forja',8)]:
        d=next(d for d in ds if d['key']==key); measure=collision(d['world'],d['rooms'][-1]['centro'],entity,scale(model,s,entity))
        audit[key]['caja_jefe']=measure
        if key=='cumbre':
            audit[key]['movimiento_jefe']=movement(d['world'],d['rooms'][-1]['centro'],entity,scale(model,s,entity))
        report += [f'- {key}: caja vanilla {measure["ancho"]} × {measure["alto"]} bloques; '+
                   f'{measure["bloques_no_aire"]} bloques no aire intersectan su volumen en el punto pedido. '+
                   'Ejemplos y medidas en el JSON. Esta lectura estatica detecta interferencias; falta validar colisiones/IA en Paper.']
        if key=='cumbre':
            report += [f'  Solidos de bloque completo (criterio conservador de terreno.py): {measure["bloques_solidos"]}. '+
                       'Los no aire incluyen bloques parciales, cuyo estado de colision debe comprobar Paper.']
            for direction,samples in audit[key]['movimiento_jefe'].items():
                report += [f'  - {direction}: '+', '.join(f'{p["distancia"]:g} b: {p["bloques_no_aire"]} no aire / {p["bloques_solidos"]} solidos' for p in samples)+'.']
    report += ['', 'Yeti: modelo y caja de 14 bloques de alto; conserva punto, vida, ataques y movimiento casi quieto. '+
               'El ancho vanilla difiere del modelo. El Golem conserva persecucion y step_height alto.', '',
               '## Comandos de actualizacion (sin /)', '']
    for d in ds: report += [f'### {d["key"]}', '', '```text',upgrade_commands(d).rstrip(),'```','']
    (folder/'tanda2.md').write_text('\n'.join(report).rstrip()+'\n',encoding='utf-8')
    (folder/'tanda2-puntos.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

if __name__=='__main__': generate()
