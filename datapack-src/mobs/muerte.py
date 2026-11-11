"""Caida no repetida, reproducida por TrackerExtraAnimation.DEATH de BetterModel.

Solo criaturas: no cambia mascotas, NPC, cofres ni monturas.
"""
MODELS = {'astral_'+k for k in ('mapache','pinguino','espantapajaros','abejorro','arana','cara',
    'momia','yeti','golem_forja','cangrejo','chaman','coloso_musgoso','bosque_planta','creeper_nuclear')}
MODELS.update('astral_esq_'+k for k in ('arquero','escudero','nigromante','guardian'))


def ensure(model):
    if model.name not in MODELS or 'death' in model.anims:return model
    roots=[b for b,d in model.bones.items() if d['parent'] is None and not b.startswith(('b_','p_','mtag_'))]
    model.bone('death_root',(0,0,0))
    for b in roots:model.bones[b]['parent']='death_root'
    # La traslacion deja el costado apoyado sobre el suelo al terminar.
    half=max(c['to'][0] for c in model.cubes)
    channels={'death_root':{'rotation':(0,0,'q.anim_time * 112.5'),
                            'position':(0,f'q.anim_time * {round(half/.8,4)}',0)}}
    for b in model.bones:
        if b.startswith(('arm','brazo','head','cabeza','jaw')):
            channels[b]={'rotation':('q.anim_time * 18',0,'q.anim_time * -12')}
    model.anim('death',.8,channels,loop='once')
    return model


def adapted(data,mid):
    """Derivados privados: envolver raices sin modificar originales ni texturas."""
    import uuid
    if mid not in ('astral_goblin','astral_abejorro') or any(a['name']=='death' for a in data.get('animations',[])):
        return data
    root=str(uuid.uuid5(uuid.NAMESPACE_URL,mid+'/death_root'))
    group=dict(name='death_root',uuid=root,origin=[0,0,0],rotation=[0,0,0])
    data.setdefault('groups',[]).append(group)
    data['outliner']=[dict(uuid=root,children=data['outliner'])]
    frames=[]
    for channel,xyz in [('rotation',(0,0,'q.anim_time * 112.5')),('position',(0,'q.anim_time * 8',0))]:
        frames.append(dict(channel=channel,time=0,interpolation='linear',
            uuid=str(uuid.uuid5(uuid.NAMESPACE_URL,mid+'/death/'+channel)),
            data_points=[dict(zip('xyz',map(str,xyz)))]))
    data.setdefault('animations',[]).append(dict(name='death',loop='once',length=.8,
        uuid=str(uuid.uuid5(uuid.NAMESPACE_URL,mid+'/death')),override=False,
        animators={root:dict(name='death_root',type='bone',keyframes=frames)}))
    return data
