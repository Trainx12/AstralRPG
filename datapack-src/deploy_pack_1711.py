"""Un solo FINAL privado sobre el pack desplegado 6421c6d3; sin red."""
import hashlib
import json
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw

import armas_mod as A
import armas_planas3d as P
import cascos_planos as C
import varitas3d as V
import services_ui as UI
from terceros import ROOT, privado
from pack_audit import audit

BASE_SHA = '6421c6d38ec1303051a44b3f42b52a2b3f3dcb42'
BASE = privado() / 'build/entregas/modelos-3d-efectos/AstralRPG-Textures.zip'
OUT = privado() / 'build/entregas/pack-17-11'


def build():
    if hashlib.sha1(BASE.read_bytes()).hexdigest() != BASE_SHA:
        raise ValueError('La base debe ser exactamente el FINAL desplegado 6421c6d3')
    with zipfile.ZipFile(BASE) as z:
        files = {n: z.read(n) for n in z.namelist()}
    before = dict(files)
    files.update(V.assets([V.curacion()]))
    # Incluir los arcos propios T1-T5, con display actualizado, sin pisar otros assets.
    with zipfile.ZipFile(ROOT / 'build/AstralRPG-Textures.zip') as z:
        for n in z.namelist():
            if n.startswith('assets/astral/models/item/arco_'):
                files[n] = z.read(n)
    ranged = A.Salida()
    for iid, spec in A.ARMAS.items():
        if spec[0] == 'arco':
            A.hacer_arco(ranged, iid, spec[1])
        elif spec[0] == 'ballesta':
            A.hacer_ballesta(ranged, iid, spec[1])
    # Solo agua_arco, sin regenerar cuchillos ni otras armas previas.
    water = A.Salida()
    P.agua(water, BASE)
    for n, blob in water.files.items():
        if 'agua_arco' in n:
            ranged.files[n] = blob
    files.update(ranged.files)
    # Delta propio de Reparar, sin reemplazar fuentes ni otras ventanas privadas.
    ui, _ = UI.assets()
    files.update({n: b for n, b in ui.items() if '/repair_' in n or
                  n.startswith('assets/astral/textures/font/servicios/herrero_')})
    OUT.mkdir(parents=True, exist_ok=True)
    icons = C.normalize(files, OUT / 'previews/cascos_iconos.png')
    target = OUT / 'AstralRPG-Textures.zip'
    tmp = target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for n, blob in sorted(files.items()):
            z.writestr(zipfile.ZipInfo(n, (2026, 11, 17, 0, 0, 0)), blob, compress_type=zipfile.ZIP_DEFLATED)
    refs = audit(tmp)
    tmp.replace(target)
    sha = hashlib.sha1(target.read_bytes()).hexdigest()
    delta = {'base_sha1': BASE_SHA, 'final_sha1': sha,
             'changed': sorted(n for n in files if files[n] != before.get(n)),
             'removed': sorted(set(before) - set(files)), 'iconos': icons, 'references': refs}
    assert not delta['removed']
    (OUT / 'delta.json').write_bytes(C.js(delta))
    (OUT / 'pack.sha1').write_text(sha + '\n')
    wand_preview()
    UI.repair_preview()
    manifest(target, sha, len(delta['changed']), len(icons))
    print(target, sha, 'cambios', len(delta['changed']), 'iconos', len(icons))
    return target


def wand_preview():
    w = V.curacion()
    path = ROOT / 'build/previews/varita_curacion_3d.gif'
    V.preview(str(path), [w], W=250)
    sheet = Image.new('RGBA', (750, 364), '#221834')
    frame = V.texture(w)[0].crop((0, 0, V.TEX, V.TEX))
    for i, (label, angle) in enumerate((('Frente', 0), ('Perfil', 90), ('Volumen', 25))):
        view = V._rot_of([0, angle, 0])
        im = V.render(w, frame, view, 10, (250, 330), 8.5)
        sheet.alpha_composite(im, (i*250, 0))
        ImageDraw.Draw(sheet).text((i*250+85, 342), label, fill='white')
    sheet.convert('RGB').save(path.with_suffix('.png'))


def manifest(target, sha, changed, icons):
    rel = target.relative_to(ROOT).as_posix()
    text = f'''# Pack del 17/11: curacion, arcos, ballestas, cascos y Reparar

Preparado localmente; SIN subir a R2 ni desplegar. Base instalada verificada: `{BASE_SHA}`.
Un unico FINAL privado: `{rel}`. SHA-1: `{sha}`.
{changed} entradas cambiadas/agregadas, ninguna eliminada; {icons} modelos con icono plano nuevo.
Arte propio de la varita en el pack publico; mods y vistas derivadas SOLO en privado.
Este FINAL reemplaza al de bcd2b3e (`e78c4e80...`, no desplegado); no instalar aquel.

## Instalacion conjunta con pendiente-17-11

1. Mantener todos los archivos y pasos de [pendiente-17-11](pendiente-17-11.md).
2. Con acceso autorizado a R2, desde la raiz: `python tools/subir_pack_r2.py {rel}`.
   Descargar la URL publica despues de subir y verificar SHA-1 `{sha}`.
   URL fija: https://pub-5e0d1c63a1554ba7b8e33b038e1a06fe.r2.dev/AstralRPG-Textures.zip
   No usar `build/AstralRPG-Textures.zip`: es el pack publico sin arte privado.
3. Respaldar archivos afectados y APAGAR. Instalar `build/AstralRPG-Items.zip`
   en `world/datapacks/AstralRPG-Items.zip`. Conservar todos los demas datapacks y mundos.
   Instalar `build/services/astral_servicios.sk` en `plugins/Skript/scripts/astral_servicios.sk`.
   Reparar usa las casillas 48-50 (todas clicables), bajo MEJORAR, sin tocar Equipo/Materiales.
4. En `server.properties`, conservar resource-pack con la URL fija y poner
   `resource-pack-sha1={sha}` SOLO despues de verificar la descarga.
5. INICIAR (reinicio completo obligatorio; no hace falta mm reload ni bettermodel reload).
   Para los menus previos: `dm reload`; si se reinstala su Skript: `skript:skript reload special_weapons`.
   Para Herrero: `skript:skript reload astral_servicios` (cero errores); el reinicio ya lo carga.
6. Revisar consola, `datapack list enabled`, descarga del pack con cliente y texturas sin errores.
   Probar arcos T1-T10, Mareas y ballestas 3/4/5 en ambas manos, todos sus estados,
   sin tapar mira ni recortar bordes. Verificar cascos en cabeza/mano/GUI/suelo/marco.

Empower es el principal documentado; Aternos queda como copia. Claude debe confirmar
el destino con navegador y usar solo las funciones permitidas por el panel. Nunca
Worlds > Upload en world ni sustitucion de mundos. Esta tarea no usa APIs remotas.

## Items existentes y vistas

Las varitas ya creadas tienen item_model minecraft:stick y NO cambian solo con el pack.
El datapack agrega `astral:upgrade/varita_curacion_modelo` al chequeo automatico de inventario:
aplica solo item_model y glint, preservando nombre, lore, encantamientos, datos y cantidad.
Los cofres se actualizan al sacar la varita al inventario. Sin subir version global de items.
Como OP se puede ejecutar `execute as <jugador> run function astral:upgrade/varita_curacion_modelo`.
Los cascos y armas con item_model astral existente reciben el aspecto nuevo al aceptar el pack.

Vista propia: `build/previews/varita_curacion_3d.png` (tambien GIF).
Vista propia del Herrero: `build/previews/herrero_reparar.png`, tres estados.
Reparar repite el sistema de MEJORAR: fondo propio y tres tiles con item_model,
gris sin equipo, verde con equipo/material/saldo, rojo si faltan recursos.
Nombre/lore conservan tier y costos; todas las casillas 48-50 responden al clic.
No cambia el costo ni el modificador `astral:reparar`. Volver permanece en 45.
Vistas privadas: `.local/terceros/AstralRPG-privado/build/entregas/pack-17-11/previews/`:
`ballestas_primera_persona.png`, `arcos_primera_persona.png`, `cascos_iconos.png`.
Resumenes nuevos: `ballestas_revision.png`, `arcos_revision.png` (vanilla/base instalada/despues).
Medidas privadas: `primera_persona_medidas.json`, 84 combinaciones de modelo/estado/mano.
Area 76,22%-109,09% de vanilla, centro a <=15 px (ancho 400); todas tocan el borde inferior.
Se normalizan los margenes transparentes del icono conservando su proporcion y orientacion
vanilla; rotacion/reflejo de mano izquierda y UV de fotogramas animados corregidos en el render.
Son renders CPU de los estados de reposo/tensado, sin animacion del brazo ni balanceo;
queda pendiente la validacion visual con cliente real y consola remota.

Verificaciones locales: 48 pruebas aprobadas (ventanas, bazar, oficios, loops,
modelos/efectos y 8 de esta tanda). La auditoria del FINAL y pack publico verifica
modelos/texturas; las regresiones comprueban todos los estados, cabeza intacta, fallbacks
planos, migracion puntual y preservacion de guante, mochilas, BetterModel, fuentes y shaders.
Paper 26.1.2 local / Java 25 / Skript 2.17.1 / Vault 1.7.3 / Essentials 2.22:
carga de 24 estructuras y recarga de `astral_servicios` sin errores. El ensayo usa
un umbral de aviso de watchdog de 60 s solo en su carpeta aislada; no instalar esa config.
No se simulo una compra ni clic con cliente: validar cobro, material y devolucion en remoto.

## Reproducir

```text
python datapack-src/special_weapons.py
python datapack-src/build.py
cd datapack-src
python build_pack.py pack-source
cd ..
python datapack-src/deploy_pack_1711.py
python datapack-src/preview_pack_1711.py --client .local/pack-1711-client.jar
python datapack-src/deploy_destello_guia.py
python -m unittest discover -s datapack-src -p test_pack_1711.py
python tools/probar_herrero_1711.py --java <JDK25/bin/java.exe> --base .local/interfaces-v2-test
python tools/verificar_terceros.py
```
'''
    (ROOT / 'build/deploy/varita-curacion-3d.md').write_text(text, encoding='utf8')


if __name__ == '__main__':
    build()
