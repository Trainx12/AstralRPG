"""Esqueletos de 315ab9d a 16 px y Creeper Nuclear de 1008f75 a 32 px."""
import math
import random
from PIL import ImageDraw
from bbmodel import Model, hexc
from creatures_tanda3a import vine, swing

VARIANTS = ('arquero', 'escudero', 'nigromante', 'espadachin', 'guardian')


class DungeonModel(Model):
    def _paint(self, size, pos):
        im = super()._paint(size, pos)
        draw = ImageDraw.Draw(im)
        for (i, face), (x, y, w, h) in pos.items():
            mat = self.cubes[i]['pat']
            rng = random.Random(f'{self.name}/{i}/{face}')
            if mat == 'ice':
                # Vetas conectadas irregulares, luces y huecos de alpha reales.
                for yy in range(h):
                    for xx in range(w):
                        v = rng.random()
                        c = im.getpixel((x+xx, y+yy))
                        if v < .20: c = (47,141,255,125)
                        elif v < .42: c = (95,182,255,140)
                        elif v < .51: c = (168,227,255,153)
                        elif v < .55: c = (240,251,255,255)
                        else: c = (95,182,255,115 if (xx+yy+i)%5 else 145)
                        im.putpixel((x+xx,y+yy),c)
                for _ in range(max(1,w*h//30)):
                    xx,yy=rng.randrange(w),rng.randrange(h)
                    draw.line((x+xx,y+yy,x+min(w-1,xx+2),y+min(h-1,yy+3)),fill='#eaf6ff')
            elif mat in ('bone','rust','cloth','wood','wrap'):
                if self.cubes[i].get('decals',{}).get(face):
                    continue  # Preservar ojos/nariz y dientes, el motor ya agrega ruido.
                base=hexc(self.cubes[i]['color'])
                dark=tuple(int(v*.62) for v in base)+(255,)
                light=tuple(min(255,int(v*1.18)) for v in base)+(255,)
                for _ in range(max(1,w*h//19)):
                    xx,yy=rng.randrange(w),rng.randrange(h)
                    for j in range(rng.randint(1,4)):
                        if yy+j<h:
                            draw.point((x+xx,y+yy+j),fill=dark)
                            if xx+1<w: draw.point((x+xx+1,y+yy+j),fill=light)
                        xx=max(0,min(w-1,xx+rng.choice((-1,0,1))))
                if mat=='rust':
                    for _ in range(max(1,w*h//12)):
                        draw.point((x+rng.randrange(w),y+rng.randrange(h)),fill=rng.choice(('#74543c','#9b7750','#a4b3a0')))
        return im


def skeleton(kind):
    m=DungeonModel('astral_esq_'+kind)
    bone= '#8bbcc1' if kind=='arquero' else '#aab99a' if kind=='guardian' else '#d8d2b4'
    joint='#68a78d' if kind=='arquero' else '#859e76' if kind=='guardian' else '#b9b28f'
    cloth='#333e40' if kind=='arquero' else '#4d441f'
    metal='#6d8582'; dark='#171d18'; leather='#43351f'
    def box(b,a,c,col=bone,pat='bone',**kw): m.cube(b,a,c,col,pat=pat,**kw)
    m.bone('body',(0,18,0))
    box('body',(-.8,12,-.8),(.8,24,.8))
    for y,w in ((16,3),(19,3.7),(22,4)):
        box('body',(-w,y,-1.7),(w,y+1.2,1.6))
        box('body',(-w,y+1,-1.7),(-w+.9,y+2,1.6),'#7f8a7c')
        box('body',(w-.9,y+1,-1.7),(w,y+2,1.6),'#b9b28f')
    box('body',(-3.5,12,-1.6),(3.5,14,1.6))
    box('body',(-4,13,-2),(4,14.5,2),leather,'wrap')
    for b,x in (('leg_l',-2.3),('leg_r',2.3)):
        m.bone(b,(x,13,0),'body',rotation=(8 if x<0 else -10,0,10 if x<0 else -10))
        box(b,(x-.85,1,-.85),(x+.85,13,.85))
        box(b,(x-1.1,6,-1.1),(x+1.1,7.8,1.1),joint)
        for y in (1,4,9,11): box(b,(x-1.15,y,-1.2),(x+1.15,y+1.2,1.2),cloth,'wrap')
        box(b,(x-1.3,0,-1.9),(x+1.3,1.8,1.4),leather,'cloth')
    for b,x in (('arm_l',-5),('arm_r',5)):
        # Frente del modelo = -Z: con el brazo hacia -Y, X POSITIVO
        # levanta la mano hacia delante. El signo anterior la llevaba a +Z.
        poses={'arquero':((78,-65,0),(78,0,0)),
               'escudero':((30,0,-22),(12,0,18)),
               'nigromante':((0,0,-112),(0,0,12)),
               'espadachin':((-15,0,-24),(-30,0,92)),
               'guardian':((-22,-12,-25),(0,-10,172))}
        m.bone(b,(x,23,0),'body',rotation=poses[kind][0 if x<0 else 1])
        box(b,(x-.85,11,-.85),(x+.85,23,.85))
        box(b,(x-1,16,-1),(x+1,18,1),joint)
        for y in (12,15,20): box(b,(x-1.25,y,-1.2),(x+1.25,y+1.3,1.2),cloth,'wrap')
        box(b,(x-1.1,10,-1.3),(x+1.1,12,1.2))
    m.bone('head',(0,24,0),'body')
    box('head',(-4,24,-4),(4,32,4),decals={'north':[(1,2,2,2,dark),(5,2,2,2,dark),(3,4,2,1.5,dark),(1,6,6,1,dark)]})
    # Dientes separados y mandibula, no una banda blanca sobre la cara.
    for x in (-2.7,-1.3,.1,1.5): box('head',(x,24,-4.35),(x+.9,25.5,-4.02),bone)
    box('head',(-3.2,23.5,-3.7),(3.2,24.2,2),'#b9b28f')
    # Arcos supraorbitales, sienes y pomulos sobresalen del craneo.
    for x in (-3.8,.6):
        box('head',(x,29.5,-4.6),(x+3.2,30.4,-3.8),joint)
    for x in (-4,2.6):
        box('head',(x,25.6,-4.6),(x+1.4,27.3,-3.5),bone)
    box('head',(-2.7,23.1,-4.1),(2.7,24,-2.3),joint)
    # Vertebras, esternon y pelvis abierta, con costillas en capas.
    for y in range(14,24,2):
        box('body',(-1.1,y,.4),(1.1,y+.8,1.4),joint)
    box('body',(-.5,17,-2),(.5,23,-1.3),bone)
    for x in (-3.9,2):
        box('body',(x,11,-1.9),(x+1.9,13.2,1.8),joint)
    # Hilos cosidos y flecos independientes sobre las vendas.
    for b,x in (('leg_l',-2.3),('leg_r',2.3),('arm_l',-5),('arm_r',5)):
        y=9 if b.startswith('leg') else 15
        for j in range(3):
            box(b,(x-.9+j*.65,y,-1.35),(x-.65+j*.65,y+.45,-1.18),'#a89b70','wrap')
        box(b,(x+.8,y-1.8,-1.25),(x+1.3,y+.2,-.95),cloth,'cloth')
    if kind in ('escudero','guardian'):
        box('head',(-4.5,30,-4.4),(4.5,32.6,4.4),metal,'rust')
        for x in (-4.5,3.6): box('head',(x,26,-3.8),(x+.9,31,4.4),metal,'rust')
        box('head',(-4.5,29.5,-4.6),(4.5,30.5,-4.2),'#a4b3a0','rust')
    if kind in ('escudero','espadachin','guardian'):
        for x,b in ((-5,'arm_l'),(5,'arm_r')):
            if kind=='espadachin' and x>0: continue
            box(b,(x-2,21,-2.4),(x+2,24.7,2.4),metal,'rust')
            for dx in (-1.3,1.3): box(b,(x+dx-.25,22,-2.7),(x+dx+.25,22.5,-2.4),'#c8d1b6')
        if kind=='escudero':
            # Anneaux de cota: pequenas piezas alternadas, con huecos de hueso.
            for row in range(5):
                for col in range(7):
                    x=-3.8+col*1.1+(row%2)*.3; y=17+row*1.2
                    box('body',(x,y,-2.4),(x+.72,y+.8,-1.8),metal if (row+col)%2 else '#a2afa0','rust')
            box('body',(-4,18,-2.6),(4,18.7,-2.3),'#a4b3a0','rust')
        else:
            box('body',(-3.8,17,-2.1),(3.8,22.5,1.8),leather,'cloth')
            vine(m,'body',[(-4,23,-2.5),(0,19,-2.7),(4,15,-2.5)],1.2,'#9e8b59')
        # Escudos con tablones, borde y remaches, en brazo izquierdo.
        if kind!='espadachin':
            green=kind=='guardian'; wood='#586739' if green else '#c8c28a'
            edge='#73c5cc' if green else '#888969'
            box('arm_l',(-12,9,-3.3),(-3,21,-1.5),edge,'rust')
            for j in range(4): box('arm_l',(-10.8+j*1.7,10.2,-3.6),(-9.25+j*1.7,19.8,-3.3),wood,'wood')
            if green:
                box('arm_l',(-8.3,12,-4),(-7.3,18,-3.5),'#87a866','wrap')
                box('arm_l',(-10,14.5,-4),(-5.6,15.5,-3.5),'#87a866','wrap')
            for x in (-11.5,-3.9):
                for y in (10,19.8): box('arm_l',(x,y,-3.85),(x+.6,y+.6,-3.6),'#d6d7ac')
        # Espadas: recta larga o cimitarra escalonada, filo y guarda.
        if kind!='escudero':
            sword_start=len(m.cubes)
            offset=0
            box('arm_r',(4.5,10,-1.7),(5.5+offset,12,-.7),leather,'wrap')
            box('arm_r',(4.5+offset,10,-1.7),(5.5+offset,15,-.7),leather,'wrap')
            box('arm_r',(2.8+offset,14,-1.7),(7.2+offset,15,-.7),'#9e8b59','rust')
            for j in range(8):
                x=4.5+offset-(j*j*.12 if kind=='espadachin' else 0)
                width=(3.4-j*.15) if kind=='espadachin' else 1.7
                box('arm_r',(x,15+j*2,-1.6),(x+width,17+j*2,-.8),'#c6c8a5')
                box('arm_r',(x+width-.2,15+j*2,-1.7),(x+width+.3,17+j*2,-.7),'#edf0ce')
            # El equipo tiene su propio pivote: la hoja no gira hacia el pecho.
            m.bone('weapon',(5,12,-1),'arm_r',rotation=(0,0,-72 if kind=='espadachin' else -14))
            for c in m.cubes[sword_start:]:
                c['bone']='weapon'
                if kind=='guardian':
                    c['from'][1]+=5; c['to'][1]+=5
    if kind=='arquero':
        for x,b in ((-5,'arm_l'),(5,'arm_r')):
            box(b,(x-1.6,21,-1.7),(x+1.6,24.2,2),'#718e8b','cloth')
            for j in range(5):
                box(b,(x-2+j*.8,20.4-j%2*.8,-2),(x-1.4+j*.8,23.5,2),'#94a8a1','fur')
        for j in range(5): box('body',(-4+j*1.5,10-j%2,-2.3),(-2.7+j*1.5,15,2.3),'#344d4b','cloth')
        vine(m,'body',[(-4,23,-2.4),(0,18,-2.5),(4,14,-2.4)],1.1,'#99b2a2')
        for b,x,y,z in (('head',-3,31,-3),('head',2,30,1),('arm_l',-5,18,-1.5),('arm_r',5,22,-1.5)):
            for j in range(3):
                box(b,(x+j*.7,y,z),(x+.4+j*.7,y+2.8-j*.7,z+.6),'#a8e3ff',rotation=(0,0,18-j*15))
        bow=[(6,3,-4),(9,7,-4),(11,14,-4),(11,21,-4),(9,28,-4),(6,32,-4)]
        bow_start=len(m.cubes)
        # La empunadura comparte la mano derecha; contrarrotacion para que
        # el arco siga vertical y giro Y para que la flecha apunte a -Z.
        m.bone('bow_grip',(5,11,0),'arm_r',rotation=(-78,0,0))
        m.bone('bow',(5,11,0),'bow_grip',rotation=(0,90,0))
        vine(m,'bow',bow,1.3,'#3d4222')
        vine(m,'bow',[bow[0],(4,17,-4),bow[-1]],.22,'#d6d7ac')
        vine(m,'bow',[(-3,17,-4.1),(12,17,-4.1)],.35,'#b9b28f')
        box('bow',(11.5,16.5,-4.7),(13,17.5,-3.6),'#b8e0d7')
        for y in (4,29): box('bow',(5.7,y,-4.4),(6.7,y+1.2,-3.5),'#9aa57c','wrap')
        for cube in m.cubes[bow_start:]:
            for field in ('from','to','origin'):
                if cube.get(field) is not None:
                    cube[field]=[v+delta for v,delta in zip(cube[field],(-6,-6,4))]
        box('body',(-4.4,15,2),(-1,25,4.6),leather,'wood')
        for x in (-4,-2.8,-1.7):
            box('body',(x,23,3),(x+.3,29,3.3),'#b9b28f')
            box('body',(x-.3,27.5,2.8),(x+.6,29,3.5),'#d4e8dc','feather')
    if kind=='nigromante':
        # Capucha abierta: techo, laterales, espalda y cavidad frontal.
        box('head',(-5,31,-4.8),(5,33,4.8),cloth,'cloth')
        box('head',(-4,30.3,-4.65),(4,31,-4.1),'#292718','cloth')
        for x in (-5,4): box('head',(x,23,-4.8),(x+1,32,4.8),cloth,'cloth')
        box('head',(-5,23,4),(5,32,5),cloth,'cloth')
        # Viseras de tela hunden el rostro; ojos luminosos en la sombra.
        box('head',(-4.1,25,-4.35),(4.1,30.5,-4.05),'#1b2119','cloth')
        for x in (-2.8,1.3): box('head',(x,27.8,-4.55),(x+1.5,28.5,-4.3),'#e7f5ad')
        for x in (-4.7,3.8): box('head',(x,23.8,-5.5),(x+.9,32,-4.5),'#39361b','cloth')
        box('body',(-4.3,10,-2.5),(4.3,24,2.5),cloth,'cloth')
        for j in range(7):
            x=-5+j*1.4
            box('body',(x,2+j%3*1.4,-2.8),(x+1.25,13,2.8),cloth,'cloth')
            for k in range(2):
                box('body',(x+k*.6,1+j%3*1.4-k*.4,-2.9),(x+k*.6+.35,5+j%3,-2.45),'#39331c','cloth')
        vine(m,'body',[(-4.4,13.5,-2.9),(0,13,-3.1),(4.4,13.5,-2.9)],.55,'#9a8954')
        vine(m,'body',[(1,13,-3.2),(1.6,10,-3.3),(.8,7,-3.3)],.4,'#9a8954')
        for x,b in ((-5,'arm_l'),(5,'arm_r')): box(b,(x-1.6,15,-1.6),(x+1.6,24,1.6),cloth,'cloth')
        vine(m,'arm_r',[(9,0,-2),(9,25,-2),(10,32,-2),(9,35,-2),(6,36,-2),(5,34,-2)],1.2,'#765c2c')
        for b,x,y,z in (('arm_r',8,33.5,-2),('body',0,19,-2.8)):
            box(b,(x-1,y-1,z-.7),(x+1,y+1,z+.7),'#c8392e')
            box(b,(x-.5,y-.4,z-.85),(x+.2,y+.6,z-.7),'#ffad77')
        m.bone('orb',(-5,9,-2),'arm_l')
        m.blob('orb',(-5,8,-1),(3.8,4.3,3.3),'#ffe964')
        m.blob('orb',(-5,8,-3.7),(2.4,2.8,1),'#fffbd0')
        box('orb',(-6,7,-4.8),(-4,9,-4.5),'#ffffff')
        for j in range(8):
            a=j*math.pi/4; dx,dy=math.cos(a),math.sin(a)
            vine(m,'orb',[(-5+dx*5,8+dy*5,-1),(-5+dx*(7+j%2),8+dy*(7+j%2),-1)],.45,'#ffe75b')
        vine(m,'arm_r',[(6,36,-2),(4,35,-2),(4,32,-2),(6,31,-2),(7,32,-2)],.8,'#917336')
    if kind=='espadachin':
        for y in (24.5,25.4): box('head',(-4.15,y,-4.7),(4.15,y+.65,4.1),'#a2a284','wrap')
        for x in (-3,1.8):
            box('body',(x,11,-3.2),(x+1.8,14,-2),'#67502a','cloth')
            box('body',(x+.6,12.5,-3.5),(x+1.1,13.3,-3.2),'#c2a365','rust')
    if kind=='guardian':
        box('head',(-.6,31.8,-4.5),(.6,34,3.8),'#819e7b','rust')
        for b,a,c in [('head',(-4.7,30,-4.7),(-1,32.8,-4.4)),('body',(1,18,-2.5),(3.6,22,-2.1)),('leg_l',(-3.5,7,-1.5),(-1.5,10,-1.2))]:
            box(b,a,c,'#65723b','wrap')
        for b,x,y,z in (('head',2,30,-4.5),('arm_l',-5.5,23,-2.5),('arm_r',4,22,-2.5),('leg_r',2,5,-1.5)):
            for j in range(4):
                box(b,(x+j*.55,y-j%2*.7,z),(x+.8+j*.55,y+.7,z+.4),'#56733c' if j%2 else '#839454','wrap')
        # Escudo cuadrado, ensanchar sin adelgazar el marco turquesa.
        for c in m.cubes:
            if c['bone']=='arm_l' and c['from'][2] < -3:
                for k in ('from','to'):
                    c[k][0]=-7.5+(c[k][0]+7.5)*1.3
    if kind in ('guardian','espadachin'):
        # Codo flexionado y mano sobre la empunadura, sin segundo hueso alzado.
        m.cubes=[c for c in m.cubes if c['bone']!='arm_r']
        m.bones['arm_r']['rotation']=[0,0,0]
        hand=(6.3,17.8,-1.1) if kind=='guardian' else (4.6,11.8,-1.1)
        elbow=(7,19,0) if kind=='guardian' else (7,17,0)
        vine(m,'arm_r',[(5,23,0),elbow,hand],1.5,bone)
        for x,y,z in (elbow,hand):
            box('arm_r',(x-.9,y-.7,z-1),(x+.9,y+.7,z+1),joint)
        if kind=='guardian':
            box('arm_r',(3,21,-2.4),(7,24.7,2.4),metal,'rust')
            for x in (3.5,6): box('arm_r',(x,22,-2.7),(x+.5,22.5,-2.4),'#c8d1b6')
        for y in (14,16):
            if kind=='espadachin': box('arm_r',(4.9,y,-1.3),(6.8,y+.7,1),cloth,'wrap')
    m.anim('idle',3,{'body':{'position':(0,swing(.18,1/3),0)},'head':{'rotation':(0,swing(3,1/3),0)}})
    m.anim('walk',1,{b:{'rotation':(swing(a),0,0)} for b,a in [('leg_l',24),('leg_r',-24),('arm_l',-14),('arm_r',14)]})
    if kind=='arquero':
        attack={'arm_r':{'rotation':(swing(4,1/1.3),0,0)},
                'arm_l':{'rotation':(swing(-12,1/1.3),swing(-8,1/1.3),0)}}
    elif kind=='nigromante':
        attack={'arm_r':{'rotation':(swing(-25,1/1.3),0,0)},
                'orb':{'scale':('1+math.sin(q.anim_time*276.923)*0.35',)*3},
                'head':{'rotation':(swing(-8,1/1.3),0,0)}}
    else:
        attack={'arm_r':{'rotation':(swing(70,1/1.3),0,swing(-12,1/1.3))},
                'arm_l':{'rotation':(swing(20 if kind=='escudero' else 35,1/1.3),0,0)}}
        if kind in ('guardian','espadachin'):
            attack['weapon']={'rotation':(swing(-45,1/1.3),0,swing(-22,1/1.3))}
    m.anim('attack',.65,attack,loop='once')
    return m


class NuclearModel(Model):
    def _face_size(self, c, face):
        w,h=super()._face_size(c,face)
        return w*2,h*2

    def _paint(self, size, pos):
        # Los calcos se expresan en unidades de modelo; duplicar tambien su UV.
        originals=[c['decals'] for c in self.cubes]
        for c in self.cubes:
            c['decals']={f:[(x*2,y*2,w*2,h*2,col) for x,y,w,h,col in ds] for f,ds in c['decals'].items()}
        try:
            im = super()._paint(size, pos)
        finally:
            for c,decals in zip(self.cubes,originals): c['decals']=decals
        draw = ImageDraw.Draw(im)
        for (i, face), (x, y, w, h) in pos.items():
            mat = self.cubes[i]['pat']
            rng = random.Random(f'{self.name}/{i}/{face}')
            if mat in ('camo','hazard'):
                palette=['#2f4a1c','#4c6b25','#6f8a2f','#5a3d1a','#c9a227']
                patches={}
                for yy in range(h):
                    for xx in range(w):
                        key=(xx//3,yy//3)
                        if key not in patches: patches[key]=rng.choices(palette,[44,25,15,10,6])[0]
                        col=hexc(patches[key]); k=rng.uniform(.78,1.05)
                        if mat=='hazard' and face not in ('up','down') and h//3<=yy<2*h//3:
                            col=hexc('#ffd21f' if (xx+abs(yy-h//2))%10<5 else '#11160c'); k=1
                        im.putpixel((x+xx,y+yy),tuple(min(255,int(v*k)) for v in col)+(255,))
                if mat=='camo' and self.cubes[i]['bone']=='body' and face=='south':
                    # Disco negro y tres sectores amarillos separados por 60 grados.
                    cx,cy=x+w/2,y+h/2
                    r=min(w,h)/2-.3
                    for yy in range(h):
                        for xx in range(w):
                            dx,dy=x+xx+.5-cx,y+yy+.5-cy
                            d=math.hypot(dx,dy)
                            if d<=r:
                                angle=(math.degrees(math.atan2(dy,dx))+90)%120
                                col='#ffd21f' if d<r*.18 or (r*.35<d<r*.88 and angle<60) else '#11160c'
                                draw.point((x+xx,y+yy),fill=col)
            elif mat in ('bone','rust','cloth','wood','wrap'):
                if self.cubes[i].get('decals',{}).get(face):
                    # Fisuras en la frente y sien: no atraviesan los ojos.
                    for pts in (((2,0),(3,2),(2,4)),((w-3,1),(w-4,3),(w-3,5))):
                        draw.line([(x+xx,y+yy) for xx,yy in pts],fill='#7f8a7c')
                    continue  # Preservar ojos/nariz y dientes, el motor ya agrega ruido.
                base=hexc(self.cubes[i]['color'])
                dark=tuple(int(v*.62) for v in base)+(255,)
                light=tuple(min(255,int(v*1.18)) for v in base)+(255,)
                for _ in range(max(1,w*h//19)):
                    xx,yy=rng.randrange(w),rng.randrange(h)
                    for j in range(rng.randint(1,4)):
                        if yy+j<h:
                            draw.point((x+xx,y+yy+j),fill=dark)
                            if xx+1<w: draw.point((x+xx+1,y+yy+j),fill=light)
                        xx=max(0,min(w-1,xx+rng.choice((-1,0,1))))
                if mat=='rust':
                    for _ in range(max(1,w*h//12)):
                        draw.point((x+rng.randrange(w),y+rng.randrange(h)),fill=rng.choice(('#74543c','#9b7750','#a4b3a0')))
        return im


def creeper():
    m=NuclearModel('astral_creeper_nuclear'); m.bone('body',(0,12,0))
    m.cube('body',(-3,6,-2),(3,18,2),'#4c6b25',pat='camo')
    m.bone('head',(0,18,0),'body')
    m.cube('head',(-4,18,-4),(4,26,4),'#4c6b25',pat='camo')
    # Cavidades oscuras y luz separadas: solo la cara se ilumina a 15/15.
    m.bone('face',(0,22,-4),'head')
    for x,y,w,h in ((-3,22,2,2),(1,22,2,2),(-1,20,2,2),(-2,19,4,2),(-2,18,1,2),(1,18,1,2)):
        m.cube('head',(x-.15,y-.15,-4.08),(x+w+.15,y+h+.15,-4.01),'#7a1010')
        m.cube('face',(x,y,-4.16),(x+w,y+h,-4.09),'#ffd21f',decals={'north':[(0,0,w,.3,'#ffe866')]})
    # Cuatro patas, formando dos bloques de pies al verlos de frente.
    for i,(x,z) in enumerate(((-2,-3),(2,-3),(-2,3),(2,3))):
        b='leg'+str(i); m.bone(b,(x,6,z),'body')
        m.cube(b,(x-2,0,z-2),(x+2,6,z+2),'#4c6b25',pat='hazard')
    m.anim('idle',2,{'head':{'rotation':(0,swing(2,.5),0)}})
    m.anim('walk',1,{f'leg{i}':{'rotation':(swing(18 if i in (0,3) else -18),0,0)} for i in range(4)})
    m.anim('swell',1.5,{'body':{'scale':('1+q.anim_time*0.12','1+q.anim_time*0.06','1+q.anim_time*0.12')}},loop='once')
    return m


def arquero(): return skeleton('arquero')
def escudero(): return skeleton('escudero')
def nigromante(): return skeleton('nigromante')
def espadachin(): return skeleton('espadachin')
def guardian(): return skeleton('guardian')
ALL=[arquero,escudero,nigromante,espadachin,guardian,creeper]
