"""Modelos de armadura de MCreator (clases Java compiladas) -> geo de GeckoLib para armaduras_t6_10.py.

Lee la salida de `javap -c` del metodo createBodyLayer (CubeListBuilder/PartPose) con una pila simple.
El codigo es propio; los modelos que se lean son de terceros y sus salidas van solo al circuito privado.
JDK: variable ASTRAL_JDK (carpeta bin con javap) o javap en el PATH.
"""
import math, re, subprocess, sys, json

import os, shutil
JAVAP = os.path.join(os.environ['ASTRAL_JDK'], 'javap') if os.environ.get('ASTRAL_JDK') else (shutil.which('javap') or 'javap')
PIVOT = {'head': (0, 0, 0), 'body': (0, 0, 0), 'rightarm': (-5, 2, 0), 'leftarm': (5, 2, 0),
         'rightleg': (-1.9, 12, 0), 'leftleg': (1.9, 12, 0), 'rightboot': (-1.9, 12, 0), 'leftboot': (1.9, 12, 0)}


class Part:
    def __init__(self, name, parent=None):
        self.name, self.parent, self.cubes, self.pose = name, parent, [], (0, 0, 0, 0, 0, 0)


class Builder:
    def __init__(self):
        self.uv, self.mirror, self.cubes = (0, 0), False, []


def parse(cls_path):
    out = subprocess.run([JAVAP, '-c', '-p', '-constants', cls_path], capture_output=True, text=True).stdout
    i = out.find('createBodyLayer()')
    code = out[i:out.find('\n\n', i)]
    st, loc, parts, tex = [], {}, [], (64, 64)
    for line in code.splitlines():
        m = re.match(r'\s*\d+: (\w+)\s*(.*)', line)
        if not m:
            continue
        op, rest = m.groups()
        if op in ('iconst_m1',):
            st.append(-1)
        elif op.startswith('iconst_'):
            st.append(int(op[-1]))
        elif op.startswith('fconst_'):
            st.append(float(op[-1]))
        elif op in ('bipush', 'sipush'):
            st.append(int(rest.split()[0]))
        elif op in ('ldc', 'ldc_w'):
            c = rest.split('//', 1)[1].strip()
            if c.startswith('float'):
                st.append(float(c.split()[1].rstrip('f')))
            elif c.startswith('int'):
                st.append(int(c.split()[1]))
            elif c.startswith('String'):
                st.append(c.split(' ', 1)[1])
            else:
                st.append(c)
        elif op == 'new':
            st.append('NEW')
        elif op == 'dup':
            st.append(st[-1])
        elif op.startswith('astore'):
            loc[rest or op.split('_')[1]] = st.pop()
        elif op.startswith('aload'):
            st.append(loc[rest or op.split('_')[1]])
        elif op == 'pop':
            st.pop()
        elif op in ('invokespecial', 'invokevirtual', 'invokestatic'):
            sig = rest.split('//', 1)[1]
            if 'MeshDefinition."<init>"' in sig:
                st.pop(); st.pop(); st.append('MESH')
            elif 'CubeDeformation."<init>":(F)' in sig:
                f = st.pop(); st.pop(); st.pop(); st.append(('DEF', f))
            elif 'CubeDeformation."<init>":(FFF)' in sig:
                c = st.pop(); b = st.pop(); a = st.pop(); st.pop(); st.pop(); st.append(('DEF', (a + b + c) / 3))
            elif 'MeshDefinition.m_171576_' in sig:
                st.pop(); r = Part('root'); parts.append(r); st.append(r)
            elif 'CubeListBuilder.m_171558_' in sig:
                st.append(Builder())
            elif 'CubeListBuilder.m_171514_' in sig:  # texOffs
                v = st.pop(); u = st.pop(); b = st[-1]; b.uv = (u, v)
            elif 'CubeListBuilder.m_171480_' in sig:  # mirror()
                st[-1].mirror = True
            elif 'CubeListBuilder.m_171555_' in sig:  # mirror(bool)
                v = st.pop(); st[-1].mirror = bool(v)
            elif 'CubeListBuilder.m_171488_' in sig:  # addBox(6F, def)
                d = st.pop(); vals = [st.pop() for _ in range(6)][::-1]; b = st[-1]
                b.cubes.append(dict(box=vals, inf=d[1], uv=b.uv, mirror=b.mirror))
            elif 'CubeListBuilder.m_171481_' in sig:  # addBox(6F) sin deformacion
                vals = [st.pop() for _ in range(6)][::-1]; b = st[-1]
                b.cubes.append(dict(box=vals, inf=0, uv=b.uv, mirror=b.mirror))
            elif 'CubeListBuilder.m_171506_' in sig:  # addBox(6F, bool mirror)
                mr = st.pop(); vals = [st.pop() for _ in range(6)][::-1]; b = st[-1]
                b.cubes.append(dict(box=vals, inf=0, uv=b.uv, mirror=bool(mr)))
            elif 'PartPose.m_171419_' in sig:
                z = st.pop(); y = st.pop(); x = st.pop(); st.append(('POSE', (x, y, z, 0, 0, 0)))
            elif 'PartPose.m_171423_' in sig:
                v = [st.pop() for _ in range(6)][::-1]; st.append(('POSE', tuple(v)))
            elif 'PartDefinition.m_171599_' in sig:
                pose = st.pop()[1]; b = st.pop(); name = st.pop(); par = st.pop()
                p = Part(name, par); p.cubes = b.cubes; p.pose = pose; parts.append(p); st.append(p)
            elif 'LayerDefinition.m_171565_' in sig:
                h = st.pop(); w = st.pop(); st.pop(); tex = (w, h); st.append('LAYER')
            else:
                raise RuntimeError('no entiendo ' + sig)
        elif op in ('areturn', 'return'):
            break
    return parts, tex


ROOT_BONE = {'head': 'bipedHead', 'body': 'bipedBody', 'rightarm': 'bipedRightArm', 'leftarm': 'bipedLeftArm',
             'rightleg': 'bipedRightLeg', 'leftleg': 'bipedLeftLeg', 'rightboot': 'bipedRightLeg', 'leftboot': 'bipedLeftLeg'}


def to_geo(class_paths):
    """Une varias piezas (casco, pechera, pantalon, botas) en un geo con huesos biped.

    Lo que cuelga de RightBoot/LeftBoot lleva 'boot' en el nombre (las botas se separan del pantalon por eso).
    """
    bones, tex, roots = [], None, {}
    for n, cp in enumerate(class_paths):
        parts, tex = parse(cp)
        absp, names = {}, {}
        for p in parts:
            if p.name == 'root':
                continue
            key = p.name.lower().replace('_', '')
            if p.parent.name == 'root':
                x, y, z = PIVOT.get(key, p.pose[:3])
                base = (0, 0, 0)
            else:
                x, y, z = p.pose[:3]
                base = absp[id(p.parent)]
            P = (base[0] + x, base[1] + y, base[2] + z)
            absp[id(p)] = P
            cubes = []
            for c in p.cubes:
                bx, by, bz, w, h, d = c['box']
                cubes.append({'origin': [P[0] + bx, 24 - (P[1] + by + h), P[2] + bz], 'size': [w, h, d],
                              'uv': list(c['uv']), 'inflate': c['inf'], 'mirror': c['mirror']})
            rx, ry, rz = (math.degrees(a) for a in p.pose[3:])
            if p.parent.name == 'root':
                rb = ROOT_BONE.get(key)
                if rb and rb not in roots:
                    roots[rb] = {'name': rb, 'pivot': [P[0], 24 - P[1], P[2]], 'cubes': []}
                parent = rb
                boot = 'boot' in key
            else:
                parent = names[id(p.parent)]
                boot = 'boot' in parent.lower()
            bn = f"{'boot_' if boot else ''}p{n}_{p.name}_{len(bones)}"
            names[id(p)] = bn
            bo = {'name': bn, 'pivot': [P[0], 24 - P[1], P[2]], 'rotation': [-rx, -ry, rz], 'cubes': cubes}
            if parent:
                bo['parent'] = parent
            bones.append(bo)
    return {'description': {'texture_width': tex[0], 'texture_height': tex[1]}, 'bones': list(roots.values()) + bones}


if __name__ == '__main__':
    print(json.dumps(to_geo(sys.argv[1:]))[:800])
