"""Pack FINAL privado de la revision del 23/11 sobre el pack instalado (modelos-22-11, 2df2bf6a). No despliega.

- Taladros y motosierras: icono plano de antes en el inventario (iconos_19_11) y 3D solo en la mano (herramientas3d).
- Mena de Asura: textura del dueno (pack-source/asura_ore_dueno.png).
- Guia Astral: fondos en su propio rango de caracteres (0xE200), ya no chocan con las ventanas (Cavernas tapaba la pagina 1).
- Portales Astrales: sin las casillas de Mini juegos y Arenas PvP.
- Efectos: interruptores y pestanas recortados 1 px mas abajo/derecha (quedaban corridos).

python datapack-src/deploy_revision_23_11.py -> ASTRAL_PRIVADO/build/entregas/revision-23-11/
"""
import hashlib
import io
import json
import zipfile

from terceros import privado

BASE = 'build/entregas/modelos-22-11/AstralRPG-Textures.zip'
BASE_SHA = '2df2bf6a1b3e99f03f3066a1e9ebd78b24692089'
OUT = 'build/entregas/revision-23-11'


def main(extra=None):
    blob = (privado() / BASE).read_bytes()
    if hashlib.sha1(blob).hexdigest() != BASE_SHA:
        raise ValueError('La base no coincide con el pack instalado (modelos-22-11)')
    z = zipfile.ZipFile(io.BytesIO(blob))
    files = {n: z.read(n) for n in z.namelist()}
    original = dict(files)

    # 1) Herramientas: modelos planos de iconos_19_11 (solo herramientas) + seleccion por contexto.
    import iconos_19_11
    import herramientas3d
    ids = {p.iid for p in herramientas3d.piezas()}
    for n, d in iconos_19_11.assets().items():
        if any(n.endswith(f'/{i}.json') or n.endswith(f'/{i}.png') for i in ids):
            files[n] = d
    files.update(herramientas3d.assets())

    # 2) Mena de Asura
    import tanda4b_world
    files['assets/astral/textures/block/asura_ore.png'] = tanda4b_world.own_textures()['assets/astral/textures/block/asura_ore.png']

    # 3) Guia Astral (mismo armado que deploy_guia_cofre, con los caracteres nuevos)
    import deploy_guia_cofre
    for n, d in deploy_guia_cofre.change(list(files), z).items():
        if d is None:
            files.pop(n, None)
        else:
            files[n] = d

    # 4) Portales: solo cambian los dibujos (mismos caracteres y medidas).
    import travel_ui
    vfiles, vprov = travel_ui.assets()
    font = json.loads(files['assets/minecraft/font/default.json'])
    viejos = {p['file']: p for p in font['providers'] if p.get('file', '').startswith('astral:font/viajes/portales')}
    for p in vprov:
        f = p.get('file', '')
        if f.startswith('astral:font/viajes/portales'):
            v = viejos.get(f)
            if v is None or {k: v[k] for k in p} != p:
                raise ValueError(f'Cambio la medida de {f}: rearmar tambien los caracteres')
            files['assets/astral/textures/' + f.split(':', 1)[1]] = vfiles['assets/astral/textures/' + f.split(':', 1)[1]]

    # 5) Efectos: piezas de las pestanas y los interruptores.
    import ventanas_19_11
    vf, _ = ventanas_19_11.assets()
    for n, d in vf.items():
        if '/ventanas1911/interruptor_' in n or '/ventanas1911/nivel_' in n:
            files[n] = d

    # 6) /trade (AxTrade): fondo nuevo (caracteres 0xF4D0) y botones trade_*.
    import ventanas_19_11 as V19
    vf, vprov = V19.assets()
    nuevos = [p for p in vprov if p.get('file', '').startswith('astral:font/ventanas2011/trade_')]
    font = json.loads(files['assets/minecraft/font/default.json'])
    font['providers'] = [p for p in font['providers'] if not p.get('file', '').startswith('astral:font/ventanas2011/trade_')]
    usados = {c for p in font['providers'] for c in [x for r in p.get('chars', []) for x in r] + list(p.get('advances', {}))}
    for p in nuevos:
        if set(p['chars'][0]) & usados:
            raise ValueError('caracter del /trade ocupado')
    espacio = next(p for p in vprov if p.get('type') == 'space')
    vuelta = {c: v for c, v in espacio['advances'].items() if 0xF4D8 <= ord(c) <= 0xF4DF}
    font['providers'] = nuevos + font['providers'] + [{'type': 'space', 'advances': vuelta}]
    files['assets/minecraft/font/default.json'] = json.dumps(font, ensure_ascii=False).encode()
    for n, d in vf.items():
        if '/ventanas2011/trade_' in n or '/ventanas1911/trade_' in n:
            files[n] = d

    # 7) Items de historia (historia_arte.py): faltaban en el pack (se veian violeta y negro). La gomera queda en 3D.
    import historia_arte
    ids = list(historia_arte.ICONS)
    for n, d in historia_arte.assets().items():
        if any(n.endswith(f'/{i}.json') or n.endswith(f'/{i}.png') for i in ids):
            files[n] = d

    if extra:
        files.update(extra)
    out = privado() / OUT
    out.mkdir(parents=True, exist_ok=True)
    target = out / 'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as w:
        for name, data in sorted(files.items()):
            w.writestr(zipfile.ZipInfo(name, (2026, 11, 23, 0, 0, 0)), data, compress_type=zipfile.ZIP_DEFLATED)
    sha = hashlib.sha1(target.read_bytes()).hexdigest()
    (out / 'pack.sha1').write_text(sha + '\n')
    changed = sorted(n for n, d in files.items() if original.get(n) != d)
    (out / 'procedencia.json').write_text(json.dumps({'base': BASE, 'base_sha1': BASE_SHA, 'final_sha1': sha, 'changed': changed,
                                                      'removed': sorted(set(original) - set(files))}, indent=2), encoding='utf8')
    print('FINAL', target, sha, 'cambiados', len(changed), 'borrados', len(set(original) - set(files)))
    return target, sha


if __name__ == '__main__':
    main()
