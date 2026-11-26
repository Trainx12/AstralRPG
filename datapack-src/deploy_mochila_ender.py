"""FINAL privado por delta de Ender y AstralDecor 1.24.8 sobre monturas 1.24.7."""
import argparse
import hashlib
import io
import os
from pathlib import Path
import subprocess
import shutil
import tempfile
import zipfile

from terceros import privado

ROOT = Path(__file__).resolve().parents[1]
DECOR_BASE_SHA1 = '0ea575f26a8740a946574ecd58c265b88f0de177'
PUBLIC_BASE_COMMIT = '2e292e9b739275106be39825c08bbfa86d8e2b25'


def public_outputs():
    """Aislar esta tarea: la regeneracion completa puede incluir trabajo concurrente ajeno."""
    from tanda_xp import assets
    out=ROOT/'build/mochilas-ender';out.mkdir(parents=True,exist_ok=True)
    own={n:b for n,b in assets().items() if Path(n).stem=='mochila_ender'}
    assert len(own)==3
    for filename,delta in [('AstralRPG-Textures.zip',own),('AstralRPG-Items.zip',None)]:
        base=subprocess.check_output(['git','show',f'{PUBLIC_BASE_COMMIT}:build/{filename}'],cwd=ROOT)
        with zipfile.ZipFile(io.BytesIO(base)) as old:
            names=set(old.namelist())
            if delta is None:
                with zipfile.ZipFile(ROOT/'build'/filename) as generated:
                    def allowed(n):
                        return ('taladro' in n or n.startswith('data/astral/function/upgrade/slot/')
                                or n.startswith('data/astral/function/mejora/') or n=='data/astral/function/load.mcfunction')
                    delta={n:generated.read(n) for n in generated.namelist() if allowed(n)
                           and (n not in names or old.read(n)!=generated.read(n))}
            target=out/filename
            with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as new:
                for n in old.namelist():
                    if n not in delta:new.writestr(old.getinfo(n),old.read(n))
                for n,b in sorted(delta.items()):
                    info=zipfile.ZipInfo(n,(2026,11,26,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                    new.writestr(info,b)
        with zipfile.ZipFile(io.BytesIO(base)) as old, zipfile.ZipFile(target) as new:
            assert all(old.read(n)==new.read(n) for n in names if n not in delta)
        print('Entrega aislada:',target,'delta:',len(delta),'SHA-1:',hashlib.sha1(target.read_bytes()).hexdigest())
    config=out/'ExpendableBackpacks/config.yml';config.parent.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'datapack-src/plugin-presets/ExpendableBackpacks--config.yml',config)


def delivery():
    out=ROOT/'build/mochilas-ender'
    private=privado()/'build/entregas/mochila-ender-26-11'
    rows=[(out/'AstralRPG-Items.zip','/world/datapacks/AstralRPG-Items.zip'),
          (out/'AstralDecor.jar','/plugins/update/AstralDecor.jar'),
          (out/'ExpendableBackpacks/config.yml','/plugins/ExpendableBackpacks/config.yml'),
          (private/'AstralRPG-Textures.zip','R2 (pendiente de Claude), luego resource-pack-sha1 de server.properties')]
    menus=ROOT/'build/menus/DeluxeMenus'
    rows += [(menus/'gui_menus'/n,'/plugins/DeluxeMenus/gui_menus/'+n) for n in
             ('g_mochilas.yml','g_mochila_netherite.yml','g_mochila_ender.yml')]
    rows += [(menus/'config-guia.yml','Combinar SOLO g_mochila_ender en /plugins/DeluxeMenus/config.yml: gui_menus')]
    table='\n'.join(f'| `{p.relative_to(ROOT).as_posix()}` | `{dest}` | `{hashlib.sha1(p.read_bytes()).hexdigest()}` |' for p,dest in rows)
    text=f'''# Taladros y Mochila de Ender — 26/11/2026

Preparado localmente. **SIN DESPLEGAR. No se subio a R2 ni al servidor.**

**CONFIG DE MOCHILAS Y ASTRALDECOR 1.24.8 VAN JUNTOS EN EL MISMO REINICIO.**
Si se activa inception sin este JAR, el plugin permite meter mochilas en cualquier mochila.
Usar la ventana diaria de las **05:00**: instalar la config con el servidor apagado en esa ventana,
con el JAR 1.24.8 ya listo en update, y arrancar. No activar `reiniciopendiente` ni reiniciar antes.

| Archivo local | Destino | SHA-1 |
|---|---|---|
{table}

La configuracion publica es una plantilla: conservar otras preferencias del servidor y cambiar
`allow-backpack-inception: true`. Registrar `g_mochila_ender: {{file: g_mochila_ender.yml}}` bajo `gui_menus`.
El inicio carga todo. Si se modifican SOLO menus despues, `dm reload`; no usar recarga general de plugins.
Nunca sustituir mundos ni usar Worlds > Upload.

AstralDecor 1.24.8 **REEMPLAZA a la 1.24.7 en /plugins/update**, e incluye sus monturas.
Base local SHA-1 `{DECOR_BASE_SHA1}`. Se reemplazan solo `AstralDecor*.class` y la version de plugin.yml;
se verifican bytes identicos del resto (incluidas AstralMounts*.class), ausencia de Gomera y version exacta.
Antes de reemplazar el JAR pendiente remoto, comparar con la entrega de monturas y descargar/revisar si difiere.
Se compila con Java 25; el fuente de compilacion temporal sustituye la inicializacion de Gomera por AstralSpell.
No se modifica AstralMesa: su precio de subasta todavia no suma la mejora del taladro.

El datapack y pack PUBLICO aislados estan en `build/mochilas-ender/`, base fija `{PUBLIC_BASE_COMMIT}`.
El primero aplica solo 433 entradas de mejoras/migracion de taladros; el segundo solo tres archivos
provisorios propios. Los ZIP generales en build contienen otras regeneraciones: **NO usarlos para esta entrega**.
El pack publico aislado SHA-1 `{hashlib.sha1((out/'AstralRPG-Textures.zip').read_bytes()).hexdigest()}`
es de reserva, **NO reemplaza el FINAL privado** en el servidor.

FINAL privado: base preferida del Bazar 26/11 `0312be092e42a975d016e114281e5ee4ceab196c`;
delta de solo `assets/astral/models/item/mochila_ender.json`, `assets/astral/items/mochila_ender.json`
y `assets/astral/textures/item/mochilas/mochila_ender.png`. Los otros archivos se comparan byte por byte.
Si no existe la base pendiente del Bazar, el generador usa la base en vivo del 25/11 con prefijo
`0fc13619`; tambien acepta `--base <FINAL.zip>` explicito. Revisar que corresponda a la version a instalar.
El SHA-1 resultante cambia segun la base. Imprime ambos hashes. No se sube a R2 automaticamente.
Vista privada revisada: `{private.relative_to(ROOT).as_posix()}/previews/mochilas-3d.png` (7 columnas).

Oculto por defecto: `#pub astral.mejtal = 0` y `#pub astral.mochender = 0`.
Solo ByTrainx mejora taladros y guarda mochilas normales en Ender. En normales se bloquea cualquier mochila;
Ender dentro de Ender se bloquea siempre, tambien clones y otras UUID. No altera UUID ni contenido.
Los interruptores se conservan en reinicios/recargas. Solo cuando el dueno lo pruebe y autorice:

```
scoreboard players set #pub astral.mejtal 1
scoreboard players set #pub astral.mochender 1
```

Para abrir el texto de la Guia: cambiar `ENDER_PUBLICO = True` en guia_cofre.py, regenerar y subir las
tres paginas afectadas; `dm reload`. Con False conserva el aviso general de bloqueo.
Para cerrar de nuevo, poner ambos scores en 0 (no borra mochilas ya guardadas y permite sacarlas).

Reproducir desde datapack-src con Python + Pillow/numpy/PyYAML y Java 25 del plan:

```
python build.py
python guia_cofre.py
python build_pack.py pack-source
python deploy_mochila_ender.py --public-only
python deploy_mochila_ender.py --java <java25>
python -m unittest test_ficha test_forge_story test_guia_cofre test_taladros_ender -q
python ../tools/probar_taladros_ender_paper.py --java <java25> --base ../.local/testsrv
python deploy_mochila_ender.py --delivery-only
```

Verificaciones: 16 pruebas Python focalizadas; comprobaciones de delta, version y aislamiento del JAR;
Guia con receta real, navegacion y slots sin solapamientos; vista 3D privada revisada.
El ensayo Paper termino con **373 comprobaciones correctas, cero fallos**, en dos arranques
(371 + 2), incluyendo atributo nativo 1,600000024 con +10 y persistencia real del plugin.
Usa eventos Bukkit reales. El JAR local ExpendableBackpacks-1.2.0.jar declara 1.0.0 en plugin.yml;
es el mismo binario de la prueba, no se redistribuye en esta entrega.
El movimiento aprobado por evento se aplica en el ensayo: no simula paquetes completos de un cliente.
Reconexion mediante eventos; reconexion de cliente y revision visual en sala del dueno siguen pendientes.
Logs privados en `.local/ender-probe/`; no publicar.

`verify.py` valida JSON y referencias del datapack y se detiene en un fallo previo:
`motosierra_basica` usa `minecraft:select`, pero el verificador espera un modelo simple (`KeyError: model`).
Se comprobo la misma definicion en HEAD. `test_gameplay` tiene dos fallos previos corroborados en HEAD:
requisito de armadura antiguo (Defensa en lugar de Combate) y click_requirement de Cazador de Bugs.
No se modifican esas funciones ni se afirma que la suite general este completamente verde.

Pendientes remotos de Claude: subir archivos correspondientes y FINAL a R2, verificar descarga y SHA-1,
actualizar propiedades, esperar el reinicio autorizado, comprobar consola/version y prueba real del dueno.
Probar taladros I-IX, conservar +N al forjar, normal dentro de Ender con contenido, salir/entrar y reiniciar,
normal vs Ender, shift/1-9/F/arrastre, otro jugador con privado/publico y clon Ender siempre bloqueado.
No anunciar nada mientras siga oculto.

Discord para cuando el dueno lo abra (guardar, NO publicar ahora):
> El Herrero ahora mejora taladros hasta +10 para picar mas rapido.
> La Mochila de Ender tiene un nuevo aspecto y su receta esta en la Guia Astral.
> Solo la Mochila de Ender puede guardar mochilas normales; otra de Ender no entra.
'''
    (ROOT/'build/deploy/taladros-mochila-ender-26-11.md').write_text(text,'utf8')


def decor(java, server):
    base = ROOT/'build/monturas/AstralDecor.jar'
    assert hashlib.sha1(base.read_bytes()).hexdigest() == DECOR_BASE_SHA1, 'Base monturas distinta: revisar'
    work = Path(tempfile.mkdtemp(prefix='ender-', dir=ROOT/'.local'))
    source = (ROOT/'datapack-src/runtime/AstralDecor.java').read_text('utf8')
    assert source.count('new AstralGomera(this, new AstralSpell(this));') == 1
    source = source.replace('new AstralGomera(this, new AstralSpell(this));', 'new AstralSpell(this);')
    assert 'Gomera' not in source
    (work/'AstralDecor.java').write_text(source, 'utf8')
    deps = [base, *server.joinpath('libraries').rglob('*.jar'), server/'plugins/mythicmobs.jar', server/'plugins/bettermodel.jar']
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8',
                    '-classpath', os.pathsep.join(map(str, deps)), '-d', str(work), str(work/'AstralDecor.java')], check=True)
    target = ROOT/'build/mochilas-ender/AstralDecor.jar'
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(base) as old, zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as new:
        assert b'version: 1.24.7' in old.read('plugin.yml')
        for name in old.namelist():
            if name.startswith('astral/AstralDecor') and name.endswith('.class'):continue
            data = old.read(name)
            if name == 'plugin.yml':data = data.replace(b'version: 1.24.7', b'version: 1.24.8')
            new.writestr(old.getinfo(name), data)
        for p in sorted((work/'astral').glob('AstralDecor*.class')):
            assert b'AstralGomera' not in p.read_bytes()
            info = zipfile.ZipInfo('astral/'+p.name, (2026,11,26,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            new.writestr(info, p.read_bytes())
    with zipfile.ZipFile(base) as old, zipfile.ZipFile(target) as new:
        changed = {n for n in set(old.namelist()) | set(new.namelist())
                   if n not in old.namelist() or n not in new.namelist() or old.read(n)!=new.read(n)}
        assert all(n=='plugin.yml' or n.startswith('astral/AstralDecor') and n.endswith('.class') for n in changed), changed
        assert not any('Gomera' in n or n=='gomera.json' for n in new.namelist())
    print('AstralDecor 1.24.8:', target, hashlib.sha1(target.read_bytes()).hexdigest())


def pack(base=None):
    from mochilas3d import archivos, vistas
    default = privado()/'build/entregas/bazar-ventanas-26-11/AstralRPG-Textures.zip'
    base = Path(base) if base else default if default.exists() else privado()/'build/entregas/bazar-ventanas-25-11/AstralRPG-Textures.zip'
    sha = hashlib.sha1(base.read_bytes()).hexdigest()
    if base == default:assert sha.startswith('0312be09'), sha
    elif base == privado()/'build/entregas/bazar-ventanas-25-11/AstralRPG-Textures.zip':assert sha.startswith('0fc13619'), sha
    files, vista, ps, pos = archivos()
    delta = {n:b for n,b in files.items() if Path(n).stem=='mochila_ender'}
    assert len(delta)==3
    out = privado()/'build/entregas/mochila-ender-26-11'
    out.mkdir(parents=True, exist_ok=True)
    target = out/'AstralRPG-Textures.zip'
    with zipfile.ZipFile(base) as old, zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as new:
        for n in old.namelist():
            if n not in delta:new.writestr(old.getinfo(n),old.read(n))
        for n,b in delta.items():
            info=zipfile.ZipInfo(n,(2026,11,26,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            new.writestr(info,b)
    with zipfile.ZipFile(base) as old, zipfile.ZipFile(target) as new:
        assert set(new.namelist())-set(old.namelist()) <= set(delta)
        assert all(new.read(n)==old.read(n) for n in old.namelist() if n not in delta)
    vistas(vista,ps,pos,out/'previews')
    result=hashlib.sha1(target.read_bytes()).hexdigest()
    (out/'pack.sha1').write_text(result+'\n')
    print('Base:',base,'SHA-1:',sha)
    print('FINAL:',target,'SHA-1:',result)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', type=Path)
    p.add_argument('--java', type=Path)
    p.add_argument('--server', type=Path, default=ROOT/'.local/testsrv')
    p.add_argument('--public-only',action='store_true',help='Solo ZIP publicos aislados sobre la base fijada')
    p.add_argument('--delivery-only',action='store_true')
    a=p.parse_args()
    if a.delivery_only:
        delivery()
        raise SystemExit(0)
    if a.public_only:
        public_outputs()
        raise SystemExit(0)
    if a.java:decor(a.java.resolve(),a.server.resolve())
    pack(a.base)
