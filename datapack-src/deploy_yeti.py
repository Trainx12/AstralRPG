"""Entrega conjunta sobre Tienda. No publica ni despliega; conserva derivados privados previos."""
from pathlib import Path
import hashlib
import re
import shutil
import yaml
from terceros import ROOT,privado
from mobs.mazmorra import MINA
from mobs.tanda2 import configure
from mobs.mazmorras_data import catalog
from mobs.tamanos import rows,dimensions,scale,VANILLA,SPECIAL

PRIVATE='.local/terceros/AstralRPG-privado/build/entregas/yeti-bastones-guia'


def preview():
    from PIL import Image,ImageDraw
    from mobs.build_models import preview3d
    from mobs.creatures import yeti
    m=yeti();tex=m.export()[1]
    base=preview3d(m,tex,yaw=0,pitch=0,scale=1,background=(0,0,0,0))
    canvas=Image.new('RGB',(1200,570),'#18232b');draw=ImageDraw.Draw(canvas)
    unit=30;ground=500
    for center,s,title in ((250,2,'Ancestral: 7 b'),(740,SPECIAL['astral_yeti_cumbre'][1],'Cumbre: 10 b = Ancestral +3')):
        dims=dimensions('astral_yeti',s)
        im=base.crop(base.getbbox()).resize((round(dims[0]*unit),round(dims[1]*unit)),Image.Resampling.NEAREST)
        canvas.paste(im,(center-im.width//2,ground-im.height),im)
        sc=scale('astral_yeti',s,'RAVAGER');w,h=VANILLA['RAVAGER']
        draw.rectangle((center-w*sc*unit/2,ground-h*sc*unit,center+w*sc*unit/2,ground),outline='#ffbf6b',width=2)
        draw.text((center-110,520),title,fill='white')
    draw.rectangle((1100,ground-1.8*unit,1118,ground),fill='#b6ddf5');draw.text((1050,520),'Jugador 1.8 b',fill='white')
    draw.line((0,ground,1200,ground),fill='#a8acb5')
    draw.text((12,12),'Vista CPU a 30 px/bloque. Naranja: caja vanilla conservadora (ancho y alto).',fill='white')
    canvas.save(ROOT/'build/previews/yeti-tamano.png')


def main():
    source=privado()/'build/entregas/tienda-modelo'
    dest=privado()/'build/entregas/yeti-bastones-guia';dest.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source/'AstralRPG-Textures.zip',dest/'AstralRPG-Textures.zip')
    sha=hashlib.sha1((dest/'AstralRPG-Textures.zip').read_bytes()).hexdigest()
    # Conservar modelos privados y skills ajenas. Solo reemplazar atributos de caja
    # y la escala visual del Yeti de Cumbre en las skills comunes.
    for kind in ('mobs','skills'):
        data=yaml.safe_load((source/f'mythicmobs/{kind}/astral.yml').read_text(encoding='utf8'))
        public=yaml.safe_load((ROOT/f'build/mythicmobs/{kind}/astral.yml').read_text(encoding='utf8'))
        if kind=='skills':
            for key,value in public.items():
                if not key.startswith('AST_MODEL_') or key not in data:continue
                commands=[v for v in value.get('Skills',[]) if 'minecraft:scale base set' in v or 'minecraft:step_height base set' in v]
                if not commands:continue
                existing=data[key]['Skills']
                existing[:]=[v for v in existing if 'minecraft:scale base set' not in v and 'minecraft:step_height base set' not in v]+commands
            data['AST_MODEL_astral_yeti_cumbre']=public['AST_MODEL_astral_yeti_cumbre']
        p=dest/f'mythicmobs/{kind}/astral.yml';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False,width=10000),encoding='utf8')
    files=[('build/runtime/AstralDecor.jar','plugins/AstralDecor.jar'),
           ('build/AstralRPG-Items.zip','world/datapacks/AstralRPG-Items.zip'),
           ('build/models/astral_npc_comerciante.bbmodel','plugins/BetterModel/models/astral_npc_comerciante.bbmodel')]
    files += [(f'{PRIVATE}/mythicmobs/{k}/astral.yml',f'plugins/MythicMobs/{k}/astral.yml') for k in ('mobs','skills')]
    files += [(f'build/mythicmobs/skills/{n}.yml',f'plugins/MythicMobs/skills/{n}.yml') for n in ('tanda3a','tanda3b','tanda3c','mazmorra','bosque','tumba','cumbre','forja')]
    lines=['# Yeti, bastones, guias y peluches: entrega conjunta con Tienda','',
           'Generado por `datapack-src/deploy_yeti.py`. Incluye tienda-modelo de 2714f24. NO desplegado. Servidor activo documentado: Empower; Aternos es la copia antigua.', '',
           '## Archivos exactos', '', '| Local | Destino |','|---|---|']
    lines += [f'| `{a}` | `{b}` |' for a,b in files]
    lines += ['',f'Pack FINAL conjunto: `{PRIVATE}/AstralRPG-Textures.zip` (mismo contenido que Tienda, SHA-1 `{sha}`). No usar el ZIP publico.',
              f'Comando para Claude: `python tools/subir_pack_r2.py {PRIVATE}/AstralRPG-Textures.zip`. Verificar descarga publica antes de fijar `resource-pack-sha1={sha}`.', '',
              '## Instalacion: un solo reinicio', '',
              '1. Sala vacia, respaldar archivos de la tabla y server.properties. Apagar el servidor.',
              '2. Reemplazar solo los archivos de la tabla. Conservar configs y mundos. Si AstralDecor/config.yml ya existe, integrar npc-models, npc-skills y hidden-npcs del config.yml incluido en el JAR (los mismos de Tienda).',
              '3. Publicar el FINAL en R2 y verificar su SHA-1; actualizar server.properties. No subir plugins de prueba, logs ni mapas.',
              '4. Encender y esperar Done, catalogo BetterModel y MythicMobs listos. Revisar consola de AstralDecor, datapack y ambos plugins. El JAR requiere reinicio; no usar /reload.',
              '5. No cambian controladores ni sus posiciones: no recrearlos. Dejar vacias las salas para que su RESET quite cofres/guias anteriores; la siguiente victoria genera los nuevos. Si la sala ya estaba finalizada, vaciarla y comprobar RESET antes de entrar.',
              '6. El arranque carga todo. Solo para ajustes posteriores: `mm reload` (YAML), `bettermodel reload` (modelos); datapack con servidor apagado y reinicio. No ejecutar listados completos de lobby ni comandos de pegado de mapas.',
              'Nunca sustituir mundos ni usar Worlds > Upload en world. No instalar configuraciones completas del Paper local.', '',
              '## Guias', '', '| Mazmorra | Cofre x y z | Guia x y z |','|---|---|---|']
    for d in [configure(MINA)]+[d for d in catalog() if d['key']!='santuario']:
        fin=d['rooms'][-1]['final_npcs'];lines.append(f'| {d["key"]} ({d["world"]}) | {fin["cofre"]} | {fin["guia"]} |')
    lines += ['', 'Cinco pisos naturales comprobados en las regiones locales: distancia 2 b, tres bloques libres. Sin bloques de apoyo. Mago de Tanda3c, nombre visible, mismo menu Expediciones, mira al jugador cercano. LIMPIA elimina copias y RESET retira cofre/guia. Santuario permanece en espera.', '',
              '## Modelos y caja de combate', '',
              'Yeti Ancestral: 7 b; Cumbre: 10 b (Ancestral +3), s=20/7. El arte y las animaciones se conservan.',
              'Se evaluaron las subcajas b_/ob_ de BetterModel: https://github.com/toxicity188/BetterModel/wiki/Configuring-custom-hitbox . Se elige ampliar la entidad base para compartir la caja entre melee, flechas y selector vanilla del baston sin entidades intermediarias ni cambiar assets.',
              'Caja vanilla cuadrada conservadora: cubre todos los vertices de reposo para cualquier yaw. El radio incluye profundidad y brazos; al escalar uniformemente puede sobrar altura. No es una caja por hueso ni una malla exacta de las animaciones.', '',
              'Volumen de aparicion revisado en las cinco regiones locales: Mina, Bosque, Cumbre y Forja sin bloques dentro de la caja; Tumba contiene solo un bloque minecraft:light en 0 79 0 (sin colision). No se modifico el terreno.', '',
              'Se reemplazo la condicion execute unless dimension por astral:in_sanctuary: la anterior no aplicaba atributos si faltaba alguno de los dos mundos en el registro. El predicado conserva la exclusion de Santuario sin exigir cargarlo.', '',
              '| Mob | Modelo ancho/alto/profundidad b | scale | Caja ancho/alto b |','|---|---|---|---|']
    for mid,model,s,entity in rows():
        sc=scale(model,s,entity);dims=dimensions(model,s);w,h=VANILLA[entity]
        lines.append(f'| {mid} | {dims[0]:.3f} / {dims[1]:.3f} / {dims[2]:.3f} | {sc} | {w*sc:.3f} / {h*sc:.3f} |')
    lines += ['', 'Bastones: spell/ray intersecta la AABB completa con dx/dy/dz en pasos de .5 b; tolerancia .5 b. Mantiene filtro de NPC NoAI, bloqueo por paredes, alcance y un solo impacto.', '',
              '## Peluches y pendientes visuales', '',
              'Los seis usan NONE, escala maxima .8 b, base alineada a la superficie y caja Interaction por altura. El frente apunta al colocador. Los antiguos se migran una sola vez al habilitar el plugin o cargar el chunk; conservan UUID, item guardado y cantidad. No hace falta recogerlos ni ejecutar un comando.',
              'Lobby bloqueado para todos, incluso OP/bypass: Aca no se pueden poner peluches. No otorgar worldguard.region.bypass.lobby para esta tarea. Recoger sigue respetando WorldGuard.',
              'Vista CPU propia: build/previews/yeti-tamano.png. No equivale a una captura de Minecraft. Capturas de cliente de los seis peluches de frente/costado y prueba visual remota siguen pendientes; no hay cliente grafico usado en esta entrega.',
              f'Vista CPU privada de los seis peluches, frente/costado: `{PRIVATE}/previews/peluches-derechos-CPU.png`. Pez tropical: rotacion X=-90 adicional porque el original esta acostado. No publicar esta vista en GitHub.',
              'Las pruebas Paper con jugador simulado verifican estado, selectores y ray tracing; no sustituyen swings de cliente, vuelos reales de flecha ni consola remota. Resultados locales comprobados al final.', '']
    suite=ROOT/'.local/yeti-tests.txt'
    probes=[ROOT/'.local/decor-probe'/n for n in ('primero.log','reinicio.log')]
    if suite.exists():
        blob=suite.read_bytes();report=blob.decode('utf-16' if blob.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf8',errors='replace')
        count=re.search(r'Ran (\d+) tests',report)
        if count and '\nOK' in report:
            lines += ['## Verificaciones locales', '',f'- Suite Python: {count[1]} pruebas aprobadas. Incluye piso natural de guias, cajas a 72 orientaciones por mob y vertices transformados de los seis peluches.']
    if all(p.exists() for p in probes):
        runtime='\n'.join(p.read_text(encoding='utf8',errors='replace') for p in probes)
        if runtime.count('DECOR RESULT failures=0')==2 and 'DECOR FAIL' not in runtime:
            lines += [f'- Paper 26.1.2 / BetterModel 3.6.0 / MythicMobs 5.13.0 / WorldGuard: {runtime.count("DECOR PASS")} comprobaciones aprobadas, incluido reinicio.',
                      '- Bastones: pies/centro/cabeza visibles, a 1.5 y 18 b del borde de la caja; zombi, esqueleto 3D, Cumbre, pez, aranita, Momia, Golem, Coloso y Ancestral. Ray tracing Paper horizontal sobre esas alturas; no son disparos reales de flecha.',
                      '- Peluches: seis transformaciones, frente al colocador, alturas por modelo, lobby OP bloqueado sin consumir y seis antiguos migrados tras reiniciar sin perderlos.',
                      '- Logs solo en .local. Falta revision con cliente y despliegue remoto.', '']
    (ROOT/'build/deploy/yeti-bastones-guia.md').write_text('\n'.join(lines),encoding='utf8')
    preview()
    print('Entrega conjunta preparada; SHA-1 FINAL',sha)


if __name__=='__main__':main()
