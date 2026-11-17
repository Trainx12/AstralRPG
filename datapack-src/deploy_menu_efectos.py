"""Regenera el icono elegido de Efectos y aplica solo su PNG al ultimo FINAL. Sin red."""
import hashlib
import io
import json
import shutil
from pathlib import Path
import zipfile

from PIL import Image
from final_base import select_base
from menu_ui import icon, preview
from pack_audit import audit
from services_ui import png
from terceros import ROOT, privado

NAME = 'menu-efectos-17-11'
TEXTURE = 'assets/astral/textures/item/menu/icon_configuraciones.png'
MODEL = 'assets/astral/models/menu/icon_configuraciones.json'
ITEM = 'assets/astral/items/menu/icon_configuraciones.json'


def patch(source, target, texture):
    """Conserva el conjunto completo de entradas y sus bytes fuera de un solo PNG."""
    with zipfile.ZipFile(source) as z:
        if len(z.namelist()) != len(set(z.namelist())):
            raise ValueError('Entradas duplicadas en la base')
        original = {n: z.read(n) for n in z.namelist()}
        entries = z.infolist()
        comment = z.comment
    if TEXTURE not in original:
        raise ValueError('Falta la textura de Efectos en la base')
    model = json.loads(original[MODEL])
    item = json.loads(original[ITEM])
    assert model['textures']['layer0'] == 'astral:item/menu/icon_configuraciones'
    assert model['display']['gui']['scale'] == [1.125, 1.125, 1]
    assert item['model']['model'] == 'astral:menu/icon_configuraciones'
    # Preparar en otra ruta permite actualizar tambien el ZIP publico de forma segura.
    temporary = target.with_suffix('.tmp.zip')
    with zipfile.ZipFile(temporary, 'w') as z:
        z.comment = comment
        for entry in entries:
            z.writestr(entry, texture if entry.filename == TEXTURE else original[entry.filename])
    with zipfile.ZipFile(temporary) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(original)
        changed = sorted(n for n, blob in original.items() if z.read(n) != blob)
        assert changed in ([TEXTURE], [])
        assert z.read(TEXTURE) == texture
    references = audit(temporary)
    # En Windows el ZIP versionado puede permitir escritura pero no reemplazo por rename.
    shutil.copyfile(temporary, target)
    temporary.unlink()
    return dict(changed=changed, preserved=len(original) - len(changed), references=references)


def generate():
    out = privado() / 'build/entregas' / NAME
    out.mkdir(parents=True, exist_ok=True)
    base = select_base(output=out)
    base_sha1 = hashlib.sha1(base.read_bytes()).hexdigest()
    image = icon('configuraciones')
    assert image.size == (18, 18)
    texture = png(image)
    assert Image.open(io.BytesIO(texture)).getpixel((0, 0)) == (201, 161, 79, 255)
    target = out / 'AstralRPG-Textures.zip'
    report = patch(base, target, texture)
    report.update(base=base.relative_to(ROOT).as_posix(), base_sha1=base_sha1,
                  final_sha1=hashlib.sha1(target.read_bytes()).hexdigest())
    public = ROOT / 'build/AstralRPG-Textures.zip'
    report['public'] = patch(public, public, texture)
    previews = ROOT / 'build/previews'
    preview(previews, name='menu_astral_efectos.png')
    for scale in (1, 8):
        (previews / f'menu_astral_efectos_icono_{scale}x.png').write_bytes(
            png(image.resize((18 * scale, 18 * scale), Image.Resampling.NEAREST)))
    (out / 'delta.json').write_text(json.dumps(report, indent=2) + '\n', 'utf8')
    (out / 'pack.sha1').write_text(report['final_sha1'] + '\n', 'utf8')
    pending = ROOT / 'build/deploy/pendiente-17-11.md'
    start, end = '<!-- MENU-EFECTOS-START -->', '<!-- MENU-EFECTOS-END -->'
    section = f'''{start}
## Icono Efectos del Menu Astral (ultimo FINAL)

Arte propio elegido: fuegos artificiales violeta/cian/dorado de Gemini, opcion 3.
Fuente publica `datapack-src/pack-source/ref/gemini/menu_configuraciones.png`, copia
exacta del recorte elegido (394x385). Usa el mismo procesamiento de los iconos de
las hojas 12/28: RGBA, 72x72 BOX, 18x18 LANCZOS y marco dorado; contraste x1,20 y
saturacion x1,15 para mejorar su lectura a 1x. Sin redibujar ni
cambiar fondo, modelo, ID, escala, slot 31, accion o configuracion del menu.

Generador: `python datapack-src/deploy_menu_efectos.py`.
Base mas nueva: `{report['base']}`; SHA-1 `{base_sha1}`.
FINAL vigente: `{target.relative_to(ROOT).as_posix()}`.
SHA-1 FINAL: `{report['final_sha1']}`.
Sustituye el FINAL de Bastones/golemcitos; conserva todos los otros pendientes.
Unico cambio interno: `{TEXTURE}`; {report['preserved']} entradas conservadas byte
por byte, sin altas ni bajas. Tambien regenerado ese PNG en el ZIP publico de
texturas; instalar exclusivamente el FINAL privado, nunca el ZIP publico.

Vistas publicas: `build/previews/menu_astral_efectos.png` (menu completo, 3x),
`build/previews/menu_astral_efectos_icono_1x.png` (18x18) y
`build/previews/menu_astral_efectos_icono_8x.png` (144x144).
ZIP comprobados sin corrupcion; referencias de texturas auditadas en ambos packs.
Falta comprobar la lectura a 1x con cliente Minecraft y consola remota.

### Archivos, destino y reinicio (pendiente de Claude)

- Unico archivo a publicar en R2: `{target.relative_to(ROOT).as_posix()}`,
  destino `AstralRPG-Textures.zip` en la URL fija existente. SHA-1 indicado arriba.
- Cuando corresponda desplegar: `python tools/subir_pack_r2.py "{target.relative_to(ROOT).as_posix()}"`;
  verificar el SHA-1 de la descarga publica antes de actualizar el servidor.
- Apagar y cambiar solo `resource-pack-sha1={report['final_sha1']}` en
  `server.properties`, conservando `resource-pack` y las otras propiedades. Iniciar
  de nuevo. Reinicio requerido para cargar la propiedad; no hacen falta `dm reload`,
  `mm reload`, `bettermodel reload` ni subir menus, datapack o JAR por este icono.
- Cliente: aceptar el pack nuevo, abrir `/menu`, comprobar Efectos en slot 31 y
  su acceso al selector Bajo/Medio/Alto; revisar consola sin errores del pack.
  Mantener las instrucciones acumuladas para las otras tareas.

Preparado localmente; R2 y servidor NO modificados. No hay despliegue verificado.
No sustituir mundos ni usar Worlds > Upload en la fila world.
{end}'''
    previous = pending.read_text('utf8')
    if start in previous:
        before, rest = previous.split(start, 1)
        _, after = rest.split(end, 1)
        previous = before + section + after
    else:
        previous = previous.rstrip() + '\n\n' + section + '\n'
    pending.write_text(previous, 'utf8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    generate()
