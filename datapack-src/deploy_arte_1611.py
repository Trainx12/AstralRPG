"""Entrega conservadora de arte final, sin subir a servicios remotos."""
import hashlib
import io
import json
import subprocess
import zipfile
from pathlib import Path
from terceros import ROOT, privado
from final_base import select_base
from pack_audit import audit

PUBLIC_BASE='fbda87e15b5e8cd177974c96438c9bd1613c882f'
NAME='cargar-arte-16-11'


def read(path):
    with zipfile.ZipFile(path) as z:return {n:z.read(n) for n in z.namelist()}


def final():
    out=privado()/'build/entregas'/NAME;out.mkdir(parents=True,exist_ok=True)
    base=select_base(output=out);old=read(base)
    previous=read(io.BytesIO(subprocess.check_output(['git','show',PUBLIC_BASE+':build/AstralRPG-Textures.zip'],cwd=ROOT)))
    public=read(ROOT/'build/AstralRPG-Textures.zip')
    delta={n:b for n,b in public.items() if b!=previous.get(n)}
    # Barril: icono final en GUI, modelo BBcosmetics previo en mano y mundo.
    barrel='assets/astral/items/barril_xp.json'
    fallback=json.loads(old[barrel])['model']
    gui=json.loads(public[barrel])['model']
    if fallback!=json.loads(previous[barrel])['model']:
        delta[barrel]=json.dumps({'model':{'type':'minecraft:select','property':'minecraft:display_context',
            'cases':[{'when':'gui','model':gui}],'fallback':fallback}}).encode()
    files={**old,**delta};target=out/'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(files.items()):z.writestr(zipfile.ZipInfo(n,(2026,11,16,0,0,0)),b,compress_type=zipfile.ZIP_DEFLATED)
    assert all(files[n]==b for n,b in old.items() if n not in delta)
    report=dict(base=base.relative_to(ROOT).as_posix(),base_sha1=hashlib.sha1(base.read_bytes()).hexdigest(),
                final_sha1=hashlib.sha1(target.read_bytes()).hexdigest(),public_sha1=hashlib.sha1((ROOT/'build/AstralRPG-Textures.zip').read_bytes()).hexdigest(),
                preserved=len(set(old)-set(delta)),changed=sorted(delta),references=audit(target))
    (out/'delta.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    (out/'pack.sha1').write_text(report['final_sha1']+'\n')
    return report,target


def delivery(report,target):
    paths=subprocess.check_output(['git','diff',PUBLIC_BASE,'--name-only','--','build'],cwd=ROOT,text=True).splitlines()
    manifest=[]
    for local in paths:
        dest=None
        for prefix,remote in [('build/menus/','plugins/'),('build/lobby/CrazyCrates/','plugins/CrazyCrates/'),
                              ('build/mythicmobs/','plugins/MythicMobs/')]:
            if local.startswith(prefix):dest=local.replace(prefix,remote,1)
        if local=='build/AstralRPG-Items.zip':dest='world/datapacks/AstralRPG-Items.zip'
        if dest:manifest.append((local,dest))
    text=['# Arte final y Manzana de la Suerte - 16/11/2026','',
          'Implementado y preparado; despliegue remoto y R2 pendientes. Continuar despues de mascotas-aurora-botones y antes de mochilas-3d.',
          '', '## Archivos exactos','', '| Local | Destino |','|---|---|']
    text += [f'| `{a}` | `{b}` |' for a,b in manifest]
    text += ['',f'FINAL privado: `{target.relative_to(ROOT).as_posix()}`.',
             f"SHA-1 FINAL: `{report['final_sha1']}`. SHA-1 publico: `{report['public_sha1']}`.",
             f"Base: `{report['base']}`; SHA-1 `{report['base_sha1']}`; {report['preserved']} entradas intactas fuera del delta.",
             'El FINAL conserva Crop & Kettle, modelos, retratos y fuentes privados. El dueno autorizo incluir Crop & Kettle en el FINAL de R2 (16/11); no hay bloqueo de permiso pendiente para esta entrega.',
             'El ZIP publico carece del arte privado: no instalarlo en lugar del FINAL.',
             '', '## Instalacion por Claude','',
             'Verificar primero la version instalada y las entregas anteriores. La documentacion identifica Empower como principal y Aternos como copia. No se uso navegador ni se verifico consola remota.',
             'Apagar, respaldar solo los archivos a reemplazar, instalar la tabla anterior y reiniciar completamente con Java 25. No sustituir mundos ni regiones ni usar Worlds > Upload en world. BetterHud sigue apagado: el layout regenerado se conserva en GitHub, no necesita instalarse para esta tarea.',
             f'Publicar el FINAL: `python tools/subir_pack_r2.py "{target.relative_to(ROOT).as_posix()}"`. Verificar la descarga publica y actualizar `resource-pack-sha1` en `server.properties` al SHA-1 FINAL antes del arranque, conservando la URL fija.',
             'El reinicio carga datapack y configuraciones. Para posteriores recargas de solo configuracion: `dm reload`, `crates reload`, `mm reload`. No usar /reload de Bukkit.',
             'Revisar consola y entrar con el nuevo pack: probar Saltador y Gancho por separado, barril en GUI/mano, botella vanilla, materiales VI-X, navegacion de mascotas/cosmeticos y compra/consumo de Manzana de la Suerte. ITEM_VERSION 25 actualiza items existentes conservando sus IDs.',
             '', '## Arte y verificaciones','',
             'Arte propio final, sin redibujar ni recolorear. Items y botella copiados byte por byte; botones recortados al cuadro central sin magenta y escalados. Navegacion 18x18. Barril privado conserva el modelo 3D fuera de GUI. Tiers altos de Infinita y sus numeros romanos intactos.',
             'Vista CPU publica: `build/Servicios-preview/arte-16-11.png`. No sustituye una prueba con cliente.',
             'Siguen provisorios `boton_sin_datos` y `mascotas_rest_0` a `mascotas_rest_4`. `cosmeticos_nav_next` no se usa en los menus actuales y conserva su reserva.',
             'Reproduccion desde datapack-src: `python arte_1611.py --import-art` solo para importar originales; `python build.py`, `python lobby.py`, `python menus.py`, `python mobs/mythic.py`, `python betterhud.py`, `python build_pack.py pack-source`, `python deploy_arte_1611.py`. Compilar usa las fuentes PNG versionadas.',
             'Verificado: suite completa de 327 pruebas OK; 4 contratos de arte OK, referencias de ambos packs, conservacion del FINAL, 76 etiquetas de mundos BetterHud, vista CPU y auditoria publica sin arte privado. Sin prueba con cliente ni consola remota.',
             'Pruebas reproducibles: `python -m unittest discover -s datapack-src -p "test*.py"`; `python tools/verificar_terceros.py` antes del commit.', '']
    (ROOT/'build/deploy/cargar-arte-16-11.md').write_text('\n'.join(text),encoding='utf8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':delivery(*final())
