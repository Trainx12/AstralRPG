"""Entrega de balance: FINAL por delta sobre tanda XP; sin publicar arte privado."""
from pathlib import Path
import hashlib
import json
import io
import subprocess
import zipfile
from terceros import ROOT, privado
from balance_equipo import *
from escala import fmt
from ficha import num

BASE='a2bfd7260c3c099e6be3a916dd4154e8c7c3d1c4'
BASE_FINAL='build/entregas/tanda-xp-cuchillo/AstralRPG-Textures.zip'

def preview(model, icon, solid, target):
    """Proyecciones ortograficas de la geometria exportada, con su textura real."""
    from PIL import Image,ImageDraw
    sheet=Image.new('RGB',(800,350),'#252b36');d=ImageDraw.Draw(sheet)
    d.text((30,15),'Icono / frente / costado (geometria del modelo)',fill='white')
    sheet.paste(icon.resize((240,240),Image.Resampling.NEAREST),(15,65),icon.resize((240,240),Image.Resampling.NEAREST))
    textures={'#icon':icon,'#solid':solid}
    # Rasterizacion de caras con z-buffer (una muestra por voxel de textura).
    for side,origin in ((False,280),(True,550)):
        canvas=Image.new('RGBA',(230,260));depth={}
        for element in model['elements']:
            a,b=element['from'],element['to'];face=element['faces']['west' if side else 'north'];tex=textures[face['texture']]
            uv=face['uv'];color=tex.getpixel((min(tex.width-1,int((uv[0]+uv[2])/32*tex.width)),min(tex.height-1,int((uv[1]+uv[3])/32*tex.height))))
            if color[3]==0:continue
            x0,x1=(a[2],b[2]) if side else (a[0],b[0]);dep=a[0] if side else a[2]
            for x in range(max(0,round(x0*12+10)),min(230,round(x1*12+10))):
                for y in range(max(0,round((16-b[1])*12+30)),min(260,round((16-a[1])*12+30))):
                    if (x,y) not in depth or dep<depth[x,y]:canvas.putpixel((x,y),color);depth[x,y]=dep
        sheet.paste(canvas,(origin,40),canvas)
    target.parent.mkdir(parents=True,exist_ok=True);sheet.save(target)

def final():
    import agua_texturas
    from PIL import Image
    out=privado()/'build/entregas/balance-especiales-agua';out.mkdir(parents=True,exist_ok=True)
    base=privado()/BASE_FINAL
    if not base.exists():raise FileNotFoundError('Falta el FINAL posterior a tiers 6-10 y tanda XP; no usar el publico.')
    generated=agua_texturas.generate()
    # Solo dos entradas: modelo de casco y color cerrado. Todo lo demas se conserva byte por byte.
    changed=('assets/astral/models/item/agua_casco_3d.json','assets/astral/textures/item/agua_casco_solido.png')
    with zipfile.ZipFile(base) as z:files={n:z.read(n) for n in z.namelist()}
    # Conservar tambien el trabajo de menu publicado despues de XP (a2bfd72), aun sin FINAL propio.
    overlay=ROOT/'build/disenos-menu/recursos-menu.zip'
    with zipfile.ZipFile(overlay) as z:
        menu={n:z.read(n) for n in z.namelist()}
    assert all(n.startswith('assets/') for n in menu)
    files.update(menu)
    for name in changed:files[name]=(generated/name).read_bytes()
    target=out/'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):z.writestr(zipfile.ZipInfo(name,(2026,11,16,0,0,0)),data,compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(base) as old,zipfile.ZipFile(target) as new:
        assert set(old.namelist())<=set(new.namelist())
        assert all(old.read(n)==new.read(n) for n in old.namelist() if n not in changed and n not in menu)
        assert json.loads(new.read('assets/astral/items/agua_helmet.json'))['model']['cases'][0]['when']=='head'
    from pack_audit import audit
    audit(target)
    digest=hashlib.sha1(target.read_bytes()).hexdigest()
    (out/'pack.sha1').write_text(digest+'\n')
    (out/'delta.json').write_text(json.dumps(dict(base=str(BASE_FINAL),base_sha1=hashlib.sha1(base.read_bytes()).hexdigest(),changed=changed,menu_overlay=list(menu),menu_commit=BASE),indent=2))
    icon=Image.open(io.BytesIO(files['assets/astral/textures/item/agua_helmet.png'])).convert('RGBA')
    solid=Image.open(generated/'assets/astral/textures/item/agua_casco_solido.png').convert('RGBA')
    preview(json.loads(files[changed[0]]),icon,solid,ROOT/'build/Servicios-preview/casco_agua.png')
    return target,digest

def delivery():
    target,digest=final()
    old_blob=subprocess.check_output(['git','show',BASE+':build/AstralRPG-Items.zip'],cwd=ROOT)
    def item(z,iid):return json.loads(z.read('data/astral/loot_table/item/'+iid+'.json'))['pools'][0]['entries'][0]['functions'][0]['components']
    def damage(c):return next((m['amount']+1 for m in c.get('minecraft:attribute_modifiers',[]) if m['type']=='minecraft:attack_damage' and m['operation']=='add_value'),None)
    lines=['# Balance de especiales y agua — 16/11/2026','',
           'Implementacion local posterior a la tanda XP/cuchillo. Sin acceso remoto ni subida a R2. '
           'Empower es el principal segun docs/SERVIDOR.md; Aternos queda como copia. Confirmar panel/version instalada.',
           '', '## Daño real sin mejoras','', '| Item | Tier | Antes → ahora |','|---|---:|---:|']
    with zipfile.ZipFile(io.BytesIO(old_blob)) as old,zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as new:
        for iid in (*SPECIAL_TIERS,'asura_espada',*(f'lanza_{t}' for t in range(1,11))):
            before,after=item(old,iid),item(new,iid)
            previous=damage(before)
            if iid.startswith('lanza_'):
                # Lanza vanilla medida en Paper: ataque 3/4/5 + Empalar, luego Poder Astral.
                t=int(iid.split('_')[1]);from escala import FACTOR_ARMA
                previous=([3,3,4,4,5,5,5,5,5,5][t-1]+[1,2,3,4,6,7,8,9,10,12][t-1])*round(FACTOR_ARMA[t],3)
            tier=SPECIAL_TIERS.get(iid,4 if iid=='asura_espada' else int(iid.split('_')[1])) if iid not in SPECIAL_TIERS else SPECIAL_TIERS[iid]
            lines.append(f'| `{iid}` | {tier} | {num(previous)} → {num(damage(after))} |')
        ids=[]
        for name in new.namelist():
            if not name.startswith('data/astral/loot_table/item/') or not name.endswith('.json'):continue
            iid=Path(name).stem;c=item(new,iid)
            if 'Tier:' in str(c.get('minecraft:lore',[])):ids.append(iid)
    lines+=['','Lanzas: 90% de la espada de su tier, ataque 1,1 y alcance/estocada vanilla. '
            'La columna anterior estima el golpe directo normal sin carga ni efectos; el daño de embestida depende de velocidad. '
            'Empalar/Poder Astral se retiran del equipo nuevo para evitar multiplicarlo dos veces. '
            'Los encantamientos se conservan al migrar; Empalar/Poder Astral antiguos dejan de multiplicar al detectar spear_balance:1.',
            '', '## Habilidades y fichas','',
            'Sismo causa x2 el atributo de ataque actual y el factor real de mejora +N del Herrero; radio 5, maná 100, recarga 6 s. '
            'Danza usa el daño T4; Estallido el daño del bastón T4 (18.750). '
            'Varita de Curación conserva su balance. Se interpretó “el bastón” como Varita del Estallido; no hay confirmación del dueño de otra identidad.',
            'Asura: daño base +10% respecto de Espada del Coloso T4; cada cuarto golpe directo al mismo enemigo en una ventana de 5 s '
            'causa +50% y cura 5% de vida máxima. Cambiar de objetivo corta la secuencia. '
            'Carnívora: +5% de defensa por pieza respecto de T3 neutro (redondeo por pieza); 4/4 cura 3% de vida máxima al matar un mob.',
            'Talismanes: Vida, Furia, Viento y Roca I/II/III dan 5/10/20%. No existen niveles T6–T10. '
            'Roca aplica además su porcentaje a la Defensa Astral calculada por el datapack.',
            f'Espada de las Mareas: proyectil de {AGUA_PROYECTIL}, maná {AGUA_MANA}, recarga {AGUA_CD/20:g} s. '
            'Hacha: +25% en golpes directos bajo el agua. Arco: conserva flechas vanilla y compensa el rozamiento acuático al del aire. '
            'Pico: atributo +0,8 sobre base 0,2 = 1,0, sin penalidad acuática. Set: aire ilimitado, eficiencia acuática 1, '
            'nado horizontal sostenido x1,5 calibrado con travelInWater de Paper; no se cambia Gracia del Delfín. '
            'Visión sin partículas ni icono solo con 4/4 sumergido; se retira al salir o desequipar; respeta efectos ajenos.',
            'Casco: cuerpo cerrado azul oscuro y aletas desde los píxeles del icono; no usa la cabeza/orejas del mod. '
            'Vista local frente/costado: `build/Servicios-preview/casco_agua.png` (derivado privado, EXCLUIDO del commit). '
            'El resto del set se conserva. Se incluyen tambien los recursos propios del menu Efectos/Bosque ya publicados en a2bfd72; las demas entradas previas se verifican byte por byte.',
            '', '## Durabilidad','',
            'Causa: desgaste vanilla max(1, daño/4) por pieza; el daño escalado lo hace enorme. '
            'AstralDecor limita cada evento de desgaste positivo a 1. Se elimina el desgaste probabilístico anterior. '
            'Armaduras: al menos 2.401 puntos por pieza; se conservan los máximos mayores T1–T10. '
            'Oficios/Agua/Carnívora reciben el mismo mínimo. Armas y utilidades con durabilidad: mínimo 7.201 (salvo indestructibles previas). '
            'Presupuesto conservador: 200 golpes recibidos por mazmorra ×12=2.400; armas 600 usos ×12=7.200. '
            'Es una estimación para todas las copias/Bosque–Santuario/Infinita, no un conteo de partidas humanas ni garantía para Infinita sin límite.',
            'ITEM_VERSION 23 usa la migración por slot existente al entrar/equipar/inventario: '
            'actualiza max_damage, atributos y ficha, conservando desgaste, encantamientos, mejoras +N y demás componentes.',
            '', '## Archivos y despliegue','',
            '| Local | Destino remoto |','|---|---|',
            '| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |',
            '| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` |',
            '| `build/oceano/AstralOceano.jar` | `plugins/AstralOceano.jar` |',
            '| `build/gameplay/astral_armas_especiales.sk` | `plugins/Skript/scripts/special_weapons.sk` (reemplazar, sin duplicado) |',
            '| `build/mazmorras/astral_mazmorras_copias.sk` (si falta tanda previa) | `plugins/Skript/scripts/astral_mazmorras_copias.sk` |',
            '| `build/infinita/astral_infinita.sk` (si falta tanda previa) | `plugins/Skript/scripts/astral_infinita.sk` |',
            '| `build/rankings/astral_rankings.sk` (si falta tanda previa) | `plugins/Skript/scripts/astral_rankings.sk` |',
            '',f'FINAL privado nuevo: `{target.relative_to(ROOT).as_posix()}`; SHA-1 **`{digest}`**. '
            f'Base preservada `{BASE_FINAL}` (posterior al pack tiers 6–10), mas `build/disenos-menu/recursos-menu.zip` de a2bfd72. No instalar el ZIP público.',
            'Apagar antes de reemplazar JAR y datapack. No subir config.yml de AstralOceano: contiene la fecha de regeneración y ajustes existentes. '
            'Los números de combate van dentro del JAR. Subir el FINAL a R2 con '
            f'`python tools/subir_pack_r2.py "{target.relative_to(ROOT).as_posix()}"`; verificar descarga pública y recién entonces '
            'actualizar `resource-pack-sha1` en server.properties. Conservar URL fija. Iniciar Java 25; reinicio completo obligatorio. '
            'No sustituir mundos ni usar Worlds > Upload en world.',
            'Si solo cambia un Skript: `skript:skript reload special_weapons`, `skript:skript reload astral_mazmorras_copias`, '
            '`skript:skript reload astral_infinita`, `skript:skript reload astral_rankings`. El reinicio ya los carga. '
            'MythicMobs no cambia en esta tarea; si se instala la tanda previa: `mm reload` y revisar consola.',
            'Carteles: defaults y comando por mundo ya corregidos en la tanda previa; actualizaciones de Infinita/Trainx siguen activas. '
            'Borrar solo los dos del lobby desde consola:',
            '```text',
            'execute in minecraft:lobby run minecraft:kill @e[type=minecraft:text_display,tag=astral_rank_infinita,x=180.5,y=101.5,z=182.5,distance=..3]',
            'execute in minecraft:lobby run minecraft:kill @e[type=minecraft:text_display,tag=astral_rank_trainx,x=186.5,y=101.5,z=182.5,distance=..3]',
            '```','Limpieza: copias e Infinita conservan lo ya implementado; Fosa ahora elimina items/flechas/tridentes cuando queda vacía. '
            'No borra displays ni cofres de recompensa mientras hay jugadores.',
            '', '## Verificaciones y pendientes','',
            'Suite completa: 300 pruebas, mas contrato final de movilidad. Ensayo Paper: nado horizontal medido 1,49999999x / 1,50000050x; '
            '200 golpes reales T5 con set T5 consumen 200 de durabilidad; visión propia/ajena y proyectil 3.186 verificados. '
            'Skript y MythicMobs cargan; revisar el resultado final del ensayo y auditoría en el resumen de entrega. '
            'El ensayo de limpieza ejecuta los comandos por dimensión; no simula una partida completa con party. '
            'La prueba de daño usa un jugador NMS sin cliente y un mob T5. No se verificó instalación remota. Falta validación visual con cliente real del casco, proyectil, '
            'nado con obstáculos/corrientes y sensaciones de combate. Revisar consola al instalar: sin errores de funciones, loot, modificadores ni Skript.',
            '',f'## Equipo con ficha ({len(ids)})','',', '.join(f'`{iid}`' for iid in sorted(ids)), '']
    text='\n'.join(lines)
    (ROOT/'build/deploy/balance-especiales-agua.md').write_text(text,encoding='utf8')
    (ROOT/'build/deploy/agua-lore-durabilidad.md').write_text('# Agua, lore y durabilidad\n\nEntrega incorporada en [balance-especiales-agua.md](balance-especiales-agua.md).\n',encoding='utf8')
    print(target,digest)

if __name__=='__main__':delivery()
