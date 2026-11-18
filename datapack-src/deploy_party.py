"""Entrega Party: regenerar salidas y sumar solo el icono/marco al ultimo FINAL."""
import hashlib
import json
from pathlib import Path
import zipfile
import argparse
from PIL import Image, ImageDraw, ImageFont
from terceros import ROOT, privado
from final_base import select_base

NAME = 'party-17-11'


def patch(source, target, assets):
    with zipfile.ZipFile(source) as z:
        original = {n:z.read(n) for n in z.namelist()}
        if len(original) != len(z.namelist()): raise ValueError('ZIP con entradas duplicadas')
    merged = original | assets
    temp = target.with_suffix('.party.tmp.zip')
    with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as z:
        for n,b in merged.items(): z.writestr(zipfile.ZipInfo(n,(2026,11,17,0,0,0)),b,compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(temp) as z:
        assert z.testzip() is None
        assert all(z.read(n)==b for n,b in original.items() if n not in assets)
    import shutil
    shutil.copyfile(temp,target);temp.unlink()
    from pack_audit import audit
    return {'preserved':len(original.keys()-assets.keys()),'references':audit(target),'sha1':hashlib.sha1(target.read_bytes()).hexdigest()}


def previews(folder):
    from menu_ui import preview
    preview(folder,'party_menu_astral.png')
    font_path=Path('C:/Windows/Fonts/arial.ttf')
    font=ImageFont.truetype(str(font_path),19) if font_path.exists() else ImageFont.load_default(size=19)
    small=ImageFont.truetype(str(font_path),15) if font_path.exists() else ImageFont.load_default(size=15)
    im=Image.new('RGB',(1050,570),'#151020');d=ImageDraw.Draw(im)
    d.text((25,15),'PARTY ASTRAL · vista representativa del inventario y TAB',fill='#e0bf7e',font=font)
    for row in range(6):
        for col in range(9):
            x,y=25+col*57,65+row*57
            d.rounded_rectangle((x,y,x+53,y+53),4,fill='#2d2438',outline='#8c754a')
    for col,n in enumerate(('Ana [L]','Beto','Ceci')):
        x,y=25+(col+1)*57,122
        d.rectangle((x+15,y+7,x+36,y+28),fill=('#ad85cc','#83b1bc','#c4a56d')[col]);d.text((x+4,y+31),n,fill='#f3dfbf',font=small)
    for x,label in ((196,'Invitar'),(310,'Salir')):d.text((x,246),label,fill='#cfadef',font=small)
    d.text((30,425),'Sin party: Crear/Invitar + invitacion con Aceptar/Rechazar.',fill='#ccc0d6',font=small)
    d.text((30,453),'Lider: clic en cabeza para echar; Salir disuelve el grupo.',fill='#ccc0d6',font=small)
    d.text((30,481),'Espectador: Shift o /party mirar abre las camaras y Mirar libre.',fill='#ccc0d6',font=small)
    lines=['ASTRAL RPG','Mazmorra · Oleada 2/3','Party · Ana (lider)','Ana 100% · Beto 40%','Ceci revive en 12s','','TAB (tambien entre mundos)','Ana 200/200 · Beto 80/200','Ceci revive en 12s','','Camara de Beto','Revivis en 12 · Shift: camaras']
    for i,line in enumerate(lines):d.text((595,70+i*31),line,fill='#ff7777' if 'revive' in line else '#d6b4ff',font=font)
    im.save(folder/'party_interfaz_panel.png')


def generate():
    import mazmorras_copias,infinita,menus,lobby,menu_ui
    mazmorras_copias.generate()
    (ROOT/'build/infinita/astral_infinita.sk').write_text(infinita.script(),encoding='utf8')
    (ROOT/'build/menus/DeluxeMenus/gui_menus/principal.yml').write_text(menus.principal_menu(),encoding='utf8')
    (ROOT/'build/lobby/TAB/secciones-config.yml').write_text(lobby.TAB_SECTIONS,encoding='utf8')
    assets,_=menu_ui.assets()
    keep={n:b for n,b in assets.items() if '/icon_party.' in n or '/principal_' in n and n.endswith('.png')}
    assert len(keep)==5, list(keep)
    out=privado()/'build/entregas'/NAME;out.mkdir(parents=True,exist_ok=True)
    base=select_base(output=out)
    report={'base':base.relative_to(ROOT).as_posix(),'base_sha1':hashlib.sha1(base.read_bytes()).hexdigest(),'assets':sorted(keep)}
    report['final']=patch(base,out/'AstralRPG-Textures.zip',keep)
    report['public']=patch(ROOT/'build/AstralRPG-Textures.zip',ROOT/'build/AstralRPG-Textures.zip',keep)
    (out/'delta.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    (out/'pack.sha1').write_text(report['final']['sha1']+'\n',encoding='utf8')
    folder=ROOT/'build/previews';folder.mkdir(exist_ok=True);previews(folder)
    print(json.dumps(report,indent=2))


def delivery(log, task_copies=None):
    import re
    import shutil
    proof=log.read_text('utf8',errors='replace')
    results=re.findall(r'PARTY RESULT checks=(\d+) failures=(\d+)',proof)
    if not results or results[-1][1]!='0' or 'generated an exception' in proof or 'PARTY FAIL' in proof:
        raise ValueError('Falta un ensayo Paper aprobado y sin excepciones')
    out=privado()/'build/entregas'/NAME
    report=json.loads((out/'delta.json').read_text('utf8'))
    rows=[]
    paths={
        'runtime/AstralParty.jar':'plugins/AstralParty.jar',
        'mazmorras/astral_mazmorras_copias.sk':'plugins/Skript/scripts/astral_mazmorras_copias.sk',
        'infinita/astral_infinita.sk':'plugins/Skript/scripts/astral_infinita.sk',
        'menus/DeluxeMenus/gui_menus/principal.yml':'plugins/DeluxeMenus/gui_menus/principal.yml',
        'lobby/TAB/secciones-config.yml':'plugins/TAB/config.yml (combinar secciones)',
    }
    for name,dest in paths.items():
        src=task_copies if task_copies and name.startswith('mazmorras/') else ROOT/'build'/name
        local=out/'tarea'/name;local.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,local)
        rows.append((local.relative_to(ROOT).as_posix(),dest,hashlib.sha256(local.read_bytes()).hexdigest()))
    accumulated=out/'acumulado/mazmorras/astral_mazmorras_copias.sk'
    accumulated.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'build/mazmorras/astral_mazmorras_copias.sk',accumulated)
    rows.append(((out/'AstralRPG-Textures.zip').relative_to(ROOT).as_posix(),'R2: AstralRPG-Textures.zip',hashlib.sha256((out/'AstralRPG-Textures.zip').read_bytes()).hexdigest()))
    lines=[
        '# Party, panel y reaparicion - 17/11/2026','',
        'Preparado localmente; R2 y servidor NO modificados. La documentacion identifica Empower como principal '
        'y Aternos como copia. Claude debe verificar el panel y los archivos vigentes antes de instalar. '
        'Contexto del pedido: instalado hasta 0f0d23a, AstralDecor 1.18.0; esta entrega no reemplaza AstralDecor.','',
        '## Implementado','',
        '- AstralParty 1.0.0: party solo en memoria, maximo seis; comandos existentes, crear y disolver. '
        'El lider que sale/desconecta disuelve, igual que antes. Invitaciones de 60 segundos, sin addons Skript.',
        '- /party abre inventario: cabezas, invitaciones aceptar/rechazar, candidatos paginados (mismo mundo primero), '
        'invitar, salir/disolver, clic del lider en una cabeza para echar. Menu Astral: Party en slot 33 con icono propio.',
        '- Expansion interna de PlaceholderAPI (no descargar eCloud): %astral_party_en%, lider, cantidad, miembros, linea, '
        'titulo, fila1..fila3 y tab1..tab3. Todos conservan el prefijo astral_party_. '
        'El puente de consola mantiene {-party.lider::*} y {-party.miembros::*}; mazentrar e Infinita conservan party_miembros().',
        '- Todos los tableros TAB tienen Party: lider y tres parejas compactas, nombres de cinco caracteres y porcentaje '
        'de vida, rojo <=30%, muerto con segundos. Maximo 15 lineas. El footer muestra los seis nombres completos y '
        'vida actual/maxima, incluso entre mundos. Se usa la alternativa de footer del plan; no se cambia el orden global de jugadores.',
        '- En copias e Infinita, dano letal con party se cancela y pasa a espectador sin drops. '
        'La muerte real (/kill) tambien conserva objetos/XP y fuerza respawn dentro. '
        '30 segundos en oleadas/Infinita, 15 en sala de jefe; constantes en party.py. '
        'Camara inicial del companero vivo mas cercano; Shift o /party mirar abre cabezas para elegir y Mirar libre. '
        'Action bar inferior y titulo con cuenta regresiva. Mirar libre queda a <=16 bloques de un companero vivo; '
        'se bloquea el cambio de mundo, cofres e interacciones.',
        '- Reaparece junto al companero observado (o uno vivo), modo anterior, vida completa e inmunidad real de 40 ticks. '
        'Sin vivos: todos espectador tres segundos, titulo La mazmorra los conquisto / Todos cayeron, sonido y lobby. '
        'Al desconectarse muerto se restaura modo/lobby; una marca persistente permite recuperar tras reinicio inesperado.',
        '- Los espectadores no suman vivos ni escala de oleadas. Permanecen fisicamente en su copia durante la espera '
        'para conservar la reserva y evitar reasignarla/resetearla; despues de la derrota la liberacion sigue el flujo existente. '
        'Quien espera al ganar revive y puede reclamar su cofre normal (cooldown individual existente); no se castiga su botin. '
        'Sin party se mantiene el flujo previo. No se agrego transferencia de liderazgo (opcional en el plan).','',
        '## Archivos exactos congelados','',
        '| Local | Destino | SHA-256 |','|---|---|---|',
        *[f'| `{src}` | `{dest}` | `{sha}` |' for src,dest,sha in rows],'',
        'Los archivos bajo tarea contienen exclusivamente esta implementacion. El script publicado de copias '
        'se obtuvo aplicando la migracion a HEAD, sin el cambio previo fresh del usuario. '
        f'La copia acumulada local `{accumulated.relative_to(ROOT).as_posix()}` conserva ese trabajo previo; '
        f'SHA-256 `{hashlib.sha256(accumulated.read_bytes()).hexdigest()}`. '
        'Si Claude instala tambien la tanda anterior de Chaman/hitboxes, usar esta acumulada para copias en lugar '
        'de la de tarea. Comparar con el script instalado para no retroceder correcciones. '
        'Los otros cambios previos (datapack, MythicMobs, modelos y AstralDecor) permanecen fuera del commit de Party.','',
        '## FINAL y puesta en marcha','',
        f'FINAL basado en `{report["base"]}`, SHA-1 `{report["base_sha1"]}`. '
        f'Nuevo SHA-1 FINAL: `{report["final"]["sha1"]}`. '
        'Solo cinco rutas propias: icono Party (PNG/modelo/item) y las dos partes del marco del menu. '
        'Todo el resto del FINAL se conserva byte por byte. El ZIP publico es de codigo/arte propio y NO se instala en R2.','',
        '1. Apagar el servidor: se agrega un plugin y cambia resource-pack-sha1. Conservar Java 25 y todos los mundos.',
        '2. Subir los cinco archivos congelados de la tabla a sus destinos. TAB es un fragmento: combinar '
        'header-footer, scoreboard y las otras claves generadas con config.yml, conservando las entradas ajenas. '
        'Mantener Skript 2.17.1 y PlaceholderAPI 2.12.3 (versiones ensayadas). '
        'El menu principal ya esta registrado; no se registra un menu DeluxeMenus nuevo.',
        f'3. Publicar el FINAL: `python tools/subir_pack_r2.py "{(out/"AstralRPG-Textures.zip").relative_to(ROOT).as_posix()}"`. '
        'Comprobar SHA-1 de la descarga publica; no se publico desde esta tarea.',
        f'4. En server.properties conservar resource-pack y poner `resource-pack-sha1={report["final"]["sha1"]}`. '
        'Iniciar de nuevo y revisar consola. El arranque carga scripts, expansion, TAB y menus.',
        '5. Si se ajustan configs tras iniciar: `skript:skript reload astral_mazmorras_copias`, '
        '`skript:skript reload astral_infinita`, `astralpartyinternal sync`, `dm reload`, `tab reload`. '
        'No usar /reload ni PlugMan para el JAR; su cambio siempre requiere reinicio. '
        'No hacen falta mm reload, bettermodel reload ni cambiar el datapack por esta tarea.',
        '6. Probar con dos clientes: /menu -> Party, invitar/aceptar, vida baja, TAB entre mundos; '
        'entrar juntos, caer en oleadas/jefe, cambiar camara con Shift, esperar 30/15 s, victoria con uno caido, '
        'derrota conjunta tres segundos, desconectar caido y volver. Revisar ausencia de errores/excepciones en consola.',
        'Nunca sustituir mundos ni usar Worlds > Upload en la fila world.','',
        '## Verificacion','',
        f'Paper 26.1.2 / Java 25: {results[-1][0]} comprobaciones aprobadas, Skript sin errores y sin excepciones del plugin. '
        'Incluye expansion real PAPI, sync real con Skript/mazentrar, dano real, muerte real, inventario, '
        '30/15 s, derrota, camaras, confinamiento, desconexion/recuperacion y bloqueo de extraccion del menu. '
        'El reloj se adelanta en el ensayo para comprobar los bordes sin esperar todos los tiempos reales.',
        'Ademas: seis tests de generacion, YAML, limite de lineas, metadata y delta del FINAL; auditoria de referencias '
        'de ambos packs y verificacion de bytes conservados. Las vistas party_menu_astral.png y '
        'party_interfaz_panel.png son renders locales/representativos, no capturas de un cliente.',
        'Falta prueba visual con clientes y conjunto completo de plugins remoto (TAB, WorldGuard y MythicMobs). '
        'El ensayo NMS local no acredita ese despliegue ni la apariencia/teclas en cliente.','',
        'Reproducir: `python datapack-src/party.py --java <Java25/bin/java.exe> --server .local/testsrv '
        '--papi <PlaceholderAPI.jar>`; `python datapack-src/deploy_party.py`; '
        '`python -m unittest discover -s datapack-src -p test_party.py`; '
        '`python tools/probar_party_paper.py --java <Java25/bin/java.exe> --base .local/testsrv '
        '--papi <PlaceholderAPI.jar>`.','',
    ]
    (ROOT/'build/deploy/party-17-11.md').write_text('\n'.join(lines),encoding='utf8')
    pending=ROOT/'build/deploy/pendiente-17-11.md';text=pending.read_text('utf8')
    heading='## Party, vida de companeros y reaparicion - 17/11/2026'
    block=(f'\n{heading}\n\n[Archivos exactos y hashes](party-17-11.md): AstralParty 1.0.0, dos scripts, principal.yml, '
        f'secciones TAB y FINAL privado SHA-1 `{report["final"]["sha1"]}` sobre `{report["base_sha1"]}`. '
        'Apagar/reiniciar; R2 y servidor pendientes de Claude. Conservar el script acumulado de copias si se instala '
        'tambien Chaman/hitboxes. No cambiar datapack, AstralDecor, MythicMobs ni mundos por Party.\n')
    pattern=r'\n'+re.escape(heading)+r'\n.*?(?=\n## |\Z)'
    text=re.sub(pattern,lambda m:block,text,flags=re.S) if heading in text else text+block
    pending.write_text(text,encoding='utf8')
    print('Entrega congelada: build/deploy/party-17-11.md')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--delivery-only',action='store_true');p.add_argument('--paper-log',type=Path);p.add_argument('--task-copies',type=Path)
    a=p.parse_args()
    if not a.delivery_only:generate()
    if a.paper_log:delivery(a.paper_log,a.task_copies)
