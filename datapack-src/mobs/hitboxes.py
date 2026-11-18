"""Caja BetterModel comun, sin textura: conserva la escala y la geometria visible."""
import uuid

BOSSES = frozenset(('astral_momia', 'astral_yeti', 'astral_golem_forja',
                    'astral_cangrejo', 'astral_chaman', 'astral_coloso_musgoso',
                    'astral_trainx', 'astral_ave', 'astral_pterodactilo'))


def attach(data):
    from mobs.tamanos import bounds_data
    mid = data['name']
    if mid not in BOSSES:
        return data
    # Idempotente: las cajas anteriores nunca cuentan como geometria.
    old = {e['uuid'] for e in data['elements'] if e.get('name') == 'astral_hitbox'}
    data['elements'] = [e for e in data['elements'] if e['uuid'] not in old]
    groups = data.get('groups', [])
    old.update(g['uuid'] for g in groups if g.get('name') == 'b_astral_hitbox')
    data['groups'] = [g for g in groups if g['uuid'] not in old]
    data['outliner'] = [n for n in data['outliner'] if (n if isinstance(n, str) else n['uuid']) not in old]
    box = bounds_data(data)
    cube = str(uuid.uuid5(uuid.NAMESPACE_URL, mid + '/hitbox/cube'))
    group = str(uuid.uuid5(uuid.NAMESPACE_URL, mid + '/hitbox/group'))
    data['elements'].append(dict(name='astral_hitbox', type='cube', uuid=cube,
        origin=[0, 0, 0], **{'from': [v[0]*16 for v in box], 'to': [v[1]*16 for v in box]},
        faces={s: {'uv': [0, 0, 0, 0], 'texture': None} for s in ('north','south','east','west','up','down')}))
    node = dict(name='b_astral_hitbox', uuid=group, origin=[0,0,0], rotation=[0,0,0], children=[cube])
    data['groups'].append(node)
    data['outliner'].append(node)
    return data
