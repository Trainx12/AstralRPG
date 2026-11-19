"""Atlas Celestial experimental. No modifica los dialogos de la Guia publicada.

Los cuerpos minecraft:item usan los componentes del generador, nunca una copia de
sus stats. El arte es decorativo: no simula controles ni tapa widgets vanilla.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'datapack-src/pack-source/guia_atlas'
FONT = 'astral:guia_atlas'
ENTRADA = 'astral:guia_esc'  # dialogo del boton Guia Astral de ESC: abre la ventana de cofre
GUIA_CMD = 'guiaastral'      # comando de DeluxeMenus (guia_cofre.py)


def text(value, color='#30241b', **kw):
    return dict(text=value, color=color, italic=False, **kw)


def line(*parts):
    # Raiz vacia: en una lista JSON los hermanos HEREDAN el estilo del primero.
    # Sin esto el texto toma la fuente de iconos y sale en cuadraditos.
    return [''] + list(parts)


# Minecraft guarda los glifos en hojas de 256 px: un dibujo mas ancho no carga
# y sale un cuadradito. Se corta en tiras que se pegan con un espacio de -1.
MAX_GLYPH = 240
JOIN = ''


def strips(width):
    return -(-width // MAX_GLYPH)


def message(value, width=330):
    return dict(type='minecraft:plain_message', contents=value if isinstance(value, (dict, list)) else text(value), width=width)


def glyph(name):
    # La altura de linea del dialogo no crece con el bitmap de la fuente.
    # El arte baja desde la primera linea (ascent normal) para que el dialogo
    # no lo recorte arriba; las lineas vacias reservan su alto.
    from PIL import Image
    n = DECOR.index(name)
    height = 48 if n >= 5 else 32
    parts = strips(Image.open(ART / (name + '.png')).width)
    chars = JOIN.join([chr(0xE900 + n)] + [chr(0xE980 + n * 4 + k) for k in range(1, parts)])
    return message(line(text(chars, 'white', font=FONT), text('\n' * (height // 9))), 360)


DECOR = ['cabecera', 'indice', 'catalogo', 'receta', 'ficha'] + [
    'como', 'consumibles', 'proteccion', 'cocina', 'misiones', 'materiales',
    'talismanes', 'mundos', 'especiales', 'berserker', 'mago', 'arquero']


def action(label, target=None, command=None, icon=None, width=170):
    if target == 'atlas/indice':      # el indice ahora es la ventana de cofre
        target, command = None, GUIA_CMD
    label = line(text(icon, 'white', font=FONT), text(' ' + label)) if icon else text(label)
    result = dict(label=label, width=width)
    if target:
        result['action'] = dict(type='show_dialog', dialog='astral:' + target)
    if command:
        result['action'] = dict(type='run_command', command=command)
    return result


def dialog(title, body, actions=(), back='atlas/indice', columns=2, close=False):
    if not actions:
        # multi_action exige al menos un boton ("List must have contents") y un
        # dialogo invalido impide cargar TODO el registro de dialogos del server.
        return dict(type='minecraft:notice', title=text('Atlas Celestial · ' + title, '#8a4500', bold=True),
                    body=body, pause=False, after_action='none', can_close_with_escape=True,
                    action=action('Volver' if back else 'Cerrar', back))
    return dict(type='minecraft:multi_action', title=text('Atlas Celestial · ' + title, '#8a4500', bold=True),
                body=body, actions=list(actions), columns=columns, pause=False,
                after_action='close' if close else 'none', can_close_with_escape=True,
                exit_action=action('Volver' if back else 'Cerrar', back))


def body_item(stack, description, size=24):
    return dict(type='minecraft:item', item=stack, width=size, height=size,
                show_tooltip=True, show_decorations=True,
                description=dict(contents=text(description), width=280))


def bestiary():
    """Definiciones efectivas, incluidas variantes elite/ancestral de Mythic."""
    from mobs.mythic import MOBS, ELITES, ANCESTRALES, ancestral_def, mob_block
    import yaml
    rows = []
    definitions = [(mid, mid, d, None) for mid, d in MOBS.items()]
    definitions += [(mid + '_elite', mid, MOBS[mid], e) for mid, e in ELITES.items()]
    definitions += [(mid + '_ancestral', mid, ancestral_def(mid), e) for mid, e in ANCESTRALES.items()]
    for mid, model, source, elite in definitions:
        effective = yaml.safe_load(mob_block(mid, source, model=model, elite=elite))[mid]
        spawn = source.get('spawn', {})
        rows.append(dict(id=mid, model=model, name=re.sub(r'&[0-9a-fk-or]', '', effective.get('Display', source['name'])),
                         kind=source['kind'], hp=effective.get('Health', source.get('hp', 0)),
                         damage=effective.get('Damage', source.get('damage', 0)),
                         drops=effective.get('Drops', []), astral=source.get('astral', []),
                         spawn=spawn, fly=source.get('fly', False), jump=source.get('jump'),
                         tier='Variante ' + ('ancestral' if mid.endswith('_ancestral') else 'elite') if elite else 'Base',
                         skills=effective.get('Skills', [])))
    from items import MOB_DROPS
    vanilla = {}
    for _, (mobs, drops) in MOB_DROPS.items():
        for mob in mobs:
            vanilla.setdefault(mob, []).extend(drops)
    for mob, drops in vanilla.items():
        rows.append(dict(id='vanilla_' + mob.split(':')[-1], model=None, name=mob.split(':')[-1].replace('_', ' ').title(),
                         kind='hostil', hp=None, damage=None, drops=[], astral=[(i, p) for i, p, _ in drops],
                         conditions=[f'{i}: solo en {c}' for i, _, c in drops if c],
                         spawn={}, fly=False, jump=None, tier='Vanilla / elite del datapack', skills=[]))
    return rows


def generate(files, items, recipes, stack, ing_pred, ing_name):
    def put(path, obj):
        files['data/astral/' + path] = json.dumps(obj, ensure_ascii=False, indent=1) if not isinstance(obj, str) else obj

    def page(path, *args, **kwargs):
        put('dialog/atlas/' + path + '.json', dialog(*args, **kwargs))

    # Numeracion estable, compartida por los dos packs. Los iconos se derivan
    # del mismo PNG que usa el item; el cuerpo sigue usando su modelo completo.
    # Las gemas (gemas.py, 7d) no van al Atlas: si entraran correrian los glifos de todos los demas.
    ids = sorted(i for i in items if items[i].get('kind') != 'gema')
    icons = {iid: chr(0xEA00 + n) for n, iid in enumerate(ids)}
    put('atlas/iconos.json', icons)
    original = json.loads(files['data/astral/dialog/guia.json'])
    index = []
    section_icons = ['lingote_astral', 'esencia_elite', 'frasco_xp_gigante', 'cuero_tratado',
                     'manzana_esmeralda', 'gema_luminica', 'cristal_arcano', 'espada_1', 'baston_1', 'arco_1',
                     'lanza_1', 'esencia_elite', 'gancho', 'taladro_1', 'motosierra_1']
    # El indice se lee de la Guia: nuevas entradas futuras no desaparecen.
    for n, button in enumerate(original['actions']):
        button = json.loads(json.dumps(button))
        label = button['label']
        button['label'] = line(text(icons.get(section_icons[n % len(section_icons)], icons[ids[0]]), 'white', font=FONT),
                               text(' '), label)
        button['width'] = 170
        a = button.get('action', {})
        target = a.get('dialog', '')
        if target == 'astral:guia/berserker':
            a['dialog'] = 'astral:atlas/berserker'
        elif target.startswith('astral:guia/'):
            # Copia local del dialogo informativo, con regreso al prototipo.
            name = target.split('/')[-1]
            source = json.loads(files['data/astral/dialog/' + target.split(':')[1] + '.json'])
            if name in DECOR:
                source['body'].insert(0, glyph(name))
            for field in ('exit_action', 'action'):
                if field in source:
                    source[field] = action('Volver a la Guia', command=GUIA_CMD, width=200)
            put('dialog/atlas/seccion/' + name + '.json', source)
            a['dialog'] = 'astral:atlas/seccion/' + name
        index.append(button)
    index += [action('Bestiario', 'atlas/bestiario/1'), action('Donde se consiguen', 'guia/drops')]
    page('indice', 'Indice', [glyph('indice'), message('Elegi una seccion.')], index, back=None)
    # Boton "Guia Astral" del menu de pausa (ESC) y acciones rapidas: abre el Atlas.
    indice = json.loads(files['data/astral/dialog/atlas/indice.json'])
    indice['external_title'] = text('Guía Astral', '#8a4500')
    put('dialog/atlas/indice.json', indice)
    # ESC no puede abrir un cofre directo: un dialogo chico con un boton que lo abre.
    put('dialog/guia_esc.json', dict(
        type='minecraft:notice', title=text('Guía Astral', '#8a4500', bold=True),
        external_title=text('Guía Astral', '#8a4500'),
        body=[glyph('cabecera'), message('Clases, equipo, recetas, criaturas y mundos.')],
        pause=False, after_action='close', can_close_with_escape=True,
        action=dict(label=text('Abrir la Guía Astral', '#1a1a1a'), width=200,
                    action=dict(type='run_command', command=GUIA_CMD))))
    for tag in ('pause_screen_additions', 'quick_actions'):
        files[f'data/minecraft/tags/dialog/{tag}.json'] = json.dumps({'values': [ENTRADA]})

    from tanda_xp import XP, SUERTE_SEGUNDOS
    from gacha_balance import FACTOR_SUERTE
    body = [glyph('consumibles')]
    for iid, amount in XP.items():
        body.append(body_item(stack(iid), f"{items[iid]['name']} · {amount:,} puntos de XP vanilla.\nClic: uno. Shift + clic: stack de la mano. Maximo 16."))
    body += [body_item(stack('manzana_esmeralda'),
                       f"Manzana de la Suerte · +{SUERTE_SEGUNDOS // 60} minutos acumulables por manzana.\nRaro, Epico y Legendario ×{FACTOR_SUERTE}; no garantiza premios.")]
    page('seccion/consumibles', 'Experiencia y suerte', body)

    berserker = []
    from escala import TIER_MAX
    for tier in range(1, TIER_MAX + 1):
        iid = next(i for i in ids if i.startswith(f'berserker_{tier}_'))
        berserker.append(action('Armadura ' + str(tier), f'atlas/catalogo/armadura_{tier}/1', icon=icons[iid]))
    for prefix, label in [('espada_', 'Espadas'), ('hacha_', 'Hachas'), ('cuchillo_', 'Cuchillos')]:
        iid = next(i for i in ids if i.startswith(prefix))
        berserker.append(action(label, 'atlas/catalogo/' + prefix[:-1] + '/1', icon=icons[iid]))
    page('berserker', 'Berserker I–X', [glyph('berserker')], berserker)

    groups = {f'armadura_{t}': [r for r, (o, _, _) in recipes.items() if o.startswith(f'berserker_{t}_')]
              for t in range(1, TIER_MAX + 1)}
    groups.update({p[:-1]: [r for r, (o, _, _) in recipes.items() if re.fullmatch(p + r'\d+', o)]
                   for p in ('espada_', 'hacha_', 'cuchillo_')})
    for group, rids in groups.items():
        total = (len(rids) + 5) // 6
        for start in range(0, len(rids), 6):
            number = start // 6 + 1
            path = f'catalogo/{group}/{number}'
            body, buttons = [glyph('catalogo')], []
            for rid in rids[start:start + 6]:
                out, count, ingredients = recipes[rid]
                body.append(body_item(stack(out, count), items[out]['name']))
                buttons.append(action(items[out]['name'], f'atlas/receta/{rid}', icon=icons[out]))
                # Cantidades exactas; no fingir disponibilidad en un dialogo estatico.
                detail = [glyph('receta'), body_item(stack(out, count), items[out]['name'], 48), message('Necesitas:')]
                for kind, iid, amount in ingredients:
                    ingredient = stack(iid) if kind == 'c' else dict(id='minecraft:potion' if iid == 'water_bottle' else iid, count=1)
                    if iid == 'water_bottle':
                        ingredient['components'] = {'minecraft:potion_contents': {'potion': 'minecraft:water'}}
                    detail.append(body_item(ingredient, f'{amount} × {ing_name(kind, iid)}'))
                detail.append(message('Cantidades requeridas. La Forja comprueba inventario y Mesa de Herreria a 3 bloques al pulsar Forjar; avisa si faltan materiales.'))
                page(f'receta/{rid}', items[out]['name'], detail,
                     [action('Forjar', command=f'/trigger astral.forja set {rid}', width=200)],
                     back='atlas/' + path, columns=1, close=True)
            if number > 1:
                buttons.append(action('← Anterior', f'atlas/catalogo/{group}/{number - 1}'))
            if number < total:
                buttons.append(action('Siguiente →', f'atlas/catalogo/{group}/{number + 1}'))
            page(path, f'{group.replace("_", " ")} · {number}/{total}', body, buttons, back='atlas/berserker')

    rows = bestiary()
    put('atlas/bestiario.json', rows)
    labels = {'hostil': ('Agresivo', '#b01c1c'), 'pasivo': ('Pacifico', '#1d7a2e'),
              'montura': ('Montura', '#00727a'), 'jefe': ('Jefe', '#8a4500')}
    for start in range(0, len(rows), 6):
        number = start // 6 + 1
        buttons = []
        for row in rows[start:start + 6]:
            mid = row['id']
            buttons.append(action(row['name'], 'atlas/criatura/' + mid))
            label, color = labels[row['kind']]
            spawn = row['spawn']
            where = (spawn.get('world', 'world') + ': ' + ', '.join(spawn.get('biomes', []))) if spawn else ('Apariciones vanilla en sus biomas; drops Astral del datapack.' if row['model'] is None else 'Solo invocacion/evento; sin aparicion natural configurada.')
            if spawn.get('night'):
                where += ' · De noche'
            if spawn.get('cave'):
                where += ' · Cuevas'
            portrait = message(line(text(chr(0xF000 + rows.index(row)), 'white', font=FONT), text('\n' * 7))) if row['model'] else message('Criatura vanilla · aspecto del cliente.')
            body = [glyph('ficha'), portrait,
                    message(text(label, color, bold=True)), message(where),
                    message(f"{row['tier']} · Vida base {row['hp']} · Daño base {row['damage']} (antes del escalado)." if row['hp'] is not None else 'Vida y daño dependen de la especie vanilla y del tier.'),
                    message('Drops vanilla: ' + '; '.join(str(d) for d in row['drops']))]
            from escala import VIDA_MOB, DANO_MOB, VIDA_REF, TIER_MAX
            if row['model'] is None or any('mob/roll' in s for s in row['skills']):
                body.append(message('Tier I–X · Multiplicadores sobre la base: ' + '; '.join(
                    f'{t}: vida ×{VIDA_MOB[t]:g}, daño ×{DANO_MOB[t]:g}' for t in range(1, TIER_MAX + 1))))
            elif row['kind'] == 'jefe':
                body.append(message('Jefe de mundo I–X · Vida: ' + '; '.join(
                    f'{t}: {25 * VIDA_REF[t]:,}' for t in range(1, TIER_MAX + 1)) + '. Daño de skills segun su definicion.'))
            body += [message(c) for c in row.get('conditions', [])]
            for drop in row['astral']:
                iid, chance, *amount = drop
                description = f'{amount[0] if amount else 1} × {items.get(iid, {}).get("name", iid)} · {chance:.0%}'
                body.append(body_item(stack(iid), description) if iid in items else message(description))
            if row['kind'] == 'montura':
                if row['fly']:
                    controls = 'Montura voladora BetterModel; consultar los controles de vuelo del servidor.'
                elif row['model'] == 'astral_lagarto':
                    controls = 'Domada: ponele silla. WASD bajo agua; mira para subir/bajar; espacio sube. Respiracion acuatica durante la monta sumergida.'
                else:
                    controls = f"Domada: ponele silla, WASD para moverte y espacio para saltar. Fuerza de salto configurada: {row['jump']}."
                body.append(message(controls))
            page('criatura/' + mid, row['name'], body, back=f'atlas/bestiario/{number}')
        if number > 1:
            buttons.append(action('← Anterior', f'atlas/bestiario/{number - 1}'))
        if start + 6 < len(rows):
            buttons.append(action('Siguiente →', f'atlas/bestiario/{number + 1}'))
        page(f'bestiario/{number}', f'Bestiario · {number}/{(len(rows) + 5) // 6}', [glyph('catalogo')], buttons)

    put('function/atlas/load.mcfunction', 'scoreboard objectives add astral.guia2 trigger\n')
    put('function/atlas/open.mcfunction', 'scoreboard players reset @s astral.guia2\ndialog show @s astral:atlas/indice\n')
    put('function/atlas/tick.mcfunction', 'execute as @a[scores={astral.guia2=1..}] run function astral:atlas/open\nscoreboard players enable @a astral.guia2\n')
    for tag, value in [('load', 'astral:atlas/load'), ('tick', 'astral:atlas/tick')]:
        path = f'data/minecraft/tags/function/{tag}.json'
        obj = json.loads(files[path])
        if value not in obj['values']:
            obj['values'].append(value)
        files[path] = json.dumps(obj)


def assets():
    """Solo arte propio normalizado y reemplazable, sin originales privados."""
    import io
    from PIL import Image
    files, providers = {}, [dict(type='space', advances={JOIN: -1})]
    for n, name in enumerate(DECOR):
        path = ART / (name + '.png')
        if not path.exists():
            raise FileNotFoundError('Falta reserva Atlas: ' + str(path))
        im = Image.open(path).convert('RGBA')
        parts = strips(im.width)
        for k in range(parts):
            suffix = f'_{k}' if parts > 1 else ''
            buf = io.BytesIO()
            im.crop((im.width * k // parts, 0, im.width * (k + 1) // parts, im.height)).save(buf, 'PNG')
            files[f'assets/astral/textures/gui/atlas/{name}{suffix}.png'] = buf.getvalue()
            providers.append(dict(type='bitmap', file=f'astral:gui/atlas/{name}{suffix}.png',
                                  height=48 if n >= 5 else 32, ascent=7,
                                  chars=[chr(0xE900 + n) if k == 0 else chr(0xE980 + n * 4 + k)]))
    files['assets/astral/font/guia_atlas.json'] = json.dumps(dict(providers=providers)).encode()
    return files
