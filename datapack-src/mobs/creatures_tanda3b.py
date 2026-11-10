"""Esqueletos e hielo originales: geometria y pixel art propios, 16 unidades/bloque."""
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
                        if v < .12: c = (58,134,217,180)
                        elif v < .26: c = (127,200,255,155)
                        elif v < .32: c = (234,246,255,235)
                        else: c = c[:3]+(110 if (xx+yy+i)%5 else 160,)
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
        m.bone(b,(x,13,0),'body',rotation=(0,0,5 if x<0 else -5))
        box(b,(x-.85,1,-.85),(x+.85,13,.85))
        box(b,(x-1.1,6,-1.1),(x+1.1,7.8,1.1),joint)
        for y in (1,4,9,11): box(b,(x-1.15,y,-1.2),(x+1.15,y+1.2,1.2),cloth,'wrap')
        box(b,(x-1.3,0,-1.9),(x+1.3,1.8,1.4),leather,'cloth')
    for b,x in (('arm_l',-5),('arm_r',5)):
        m.bone(b,(x,23,0),'body',rotation=(-16 if kind=='arquero' else 0,0,-100 if kind=='nigromante' and x<0 else -9 if x<0 else 9))
        box(b,(x-.85,11,-.85),(x+.85,23,.85))
        box(b,(x-1,16,-1),(x+1,18,1),joint)
        for y in (12,15,20): box(b,(x-1.25,y,-1.2),(x+1.25,y+1.3,1.2),cloth,'wrap')
        box(b,(x-1.1,10,-1.3),(x+1.1,12,1.2))
    m.bone('head',(0,24,0),'body')
    box('head',(-4,24,-4),(4,32,4),decals={'north':[(1,2,2,2,dark),(5,2,2,2,dark),(3,4,2,1.5,dark),(1,6,6,1,dark)]})
    # Dientes separados y mandibula, no una banda blanca sobre la cara.
    for x in (-2.7,-1.3,.1,1.5): box('head',(x,24,-4.35),(x+.9,25.5,-4.02),bone)
    box('head',(-3.2,23.5,-3.7),(3.2,24.2,2),'#b9b28f')
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
            box('body',(-4.3,18,-2.3),(4.3,23,2.2),metal,'rust')
            box('body',(-4,18,-2.6),(4,18.7,-2.3),'#a4b3a0','rust')
        else:
            box('body',(-3.8,17,-2.1),(3.8,22.5,1.8),leather,'cloth')
            vine(m,'body',[(-4,23,-2.5),(0,19,-2.7),(4,15,-2.5)],1.2,'#9e8b59')
        # Escudos con tablones, borde y remaches, en brazo izquierdo.
        if kind!='espadachin':
            green=kind=='guardian'; wood='#586739' if green else '#c8c28a'
            edge='#85b6ad' if green else '#888969'
            box('arm_l',(-12,9,-3.3),(-3,21,-1.5),edge,'rust')
            for j in range(4): box('arm_l',(-11.3+j*2,9.7,-3.6),(-9.45+j*2,20.3,-3.3),wood,'wood')
            for x in (-11.5,-3.9):
                for y in (10,19.8): box('arm_l',(x,y,-3.85),(x+.6,y+.6,-3.6),'#d6d7ac')
        # Espadas: recta larga o cimitarra escalonada, filo y guarda.
        if kind!='escudero':
            offset=3 if kind=='guardian' else 0
            box('arm_r',(4.5,10,-1.7),(5.5+offset,12,-.7),leather,'wrap')
            box('arm_r',(4.5+offset,10,-1.7),(5.5+offset,15,-.7),leather,'wrap')
            box('arm_r',(2.8+offset,14,-1.7),(7.2+offset,15,-.7),'#9e8b59','rust')
            for j in range(6):
                x=4.5+offset+(j*j*.11 if kind=='espadachin' else 0)
                width=2.7 if kind=='espadachin' else 1.7
                box('arm_r',(x,15+j*2,-1.6),(x+width,17+j*2,-.8),'#c6c8a5')
                box('arm_r',(x+width-.2,15+j*2,-1.7),(x+width+.3,17+j*2,-.7),'#edf0ce')
    if kind=='arquero':
        for x,b in ((-5,'arm_l'),(5,'arm_r')):
            box(b,(x-1.6,21,-1.7),(x+1.6,24.2,2),'#718e8b','cloth')
        for j in range(5): box('body',(-4+j*1.5,10-j%2,-2.3),(-2.7+j*1.5,15,2.3),'#344d4b','cloth')
        vine(m,'body',[(-4,23,-2.4),(0,18,-2.5),(4,14,-2.4)],1.1,'#99b2a2')
        bow=[(7,8,-4),(9,11,-4),(10,16,-4),(9,22,-4),(7,27,-4)]
        vine(m,'arm_r',bow,1.3,'#3d4222')
        vine(m,'arm_r',[bow[0],(6.7,17,-4),bow[-1]],.22,'#d6d7ac')
        vine(m,'arm_r',[(0,17,-4.1),(12,17,-4.1)],.35,'#b9b28f')
        box('arm_r',(11.5,16.5,-4.7),(13,17.5,-3.6),'#b8e0d7')
        box('body',(-4.4,15,2),(-1,25,4.6),leather,'wood')
        for x in (-4,-2.8,-1.7): box('body',(x,23,3),(x+.3,29,3.3),'#b9b28f')
    if kind=='nigromante':
        # Capucha abierta: techo, laterales, espalda y cavidad frontal.
        box('head',(-5,31,-4.8),(5,33,4.8),cloth,'cloth')
        box('head',(-4,30.3,-4.65),(4,31,-4.1),'#292718','cloth')
        for x in (-5,4): box('head',(x,23,-4.8),(x+1,32,4.8),cloth,'cloth')
        box('head',(-5,23,4),(5,32,5),cloth,'cloth')
        box('body',(-4.3,10,-2.5),(4.3,24,2.5),cloth,'cloth')
        for j in range(7):
            x=-5+j*1.4
            box('body',(x,2+j%3*1.4,-2.8),(x+1.25,13,2.8),cloth,'cloth')
        for x,b in ((-5,'arm_l'),(5,'arm_r')): box(b,(x-1.6,15,-1.6),(x+1.6,24,1.6),cloth,'cloth')
        vine(m,'arm_r',[(9,0,-2),(9,25,-2),(10,32,-2),(9,35,-2),(6,36,-2),(5,34,-2)],1.2,'#765c2c')
        for b,x,y,z in (('arm_r',8,33.5,-2),('body',0,19,-2.8)):
            box(b,(x-1,y-1,z-.7),(x+1,y+1,z+.7),'#c8392e')
            box(b,(x-.5,y-.4,z-.85),(x+.2,y+.6,z-.7),'#ffad77')
        m.bone('orb',(-5,9,-2),'arm_l')
        box('orb',(-7,7,-3),(-3,11,1),'#fff19a')
        box('orb',(-6,8,-3.5),(-4,10,-3),'#ffffff')
        for j,(dx,dy) in enumerate(((-3,0),(3,0),(0,3),(0,-3))):
            box('orb',(-5+dx-.3,9+dy-.3,-1),(-5+dx+.3,9+dy+.3,0),'#ffe15a')
    if kind=='guardian':
        for b,a,c in [('head',(-4.7,30,-4.7),(-1,32.8,-4.4)),('body',(1,18,-2.5),(3.6,22,-2.1)),('leg_l',(-3.5,7,-1.5),(-1.5,10,-1.2))]:
            box(b,a,c,'#65723b','wrap')
    m.anim('idle',3,{'body':{'position':(0,swing(.18,1/3),0)},'head':{'rotation':(0,swing(3,1/3),0)}})
    m.anim('walk',1,{b:{'rotation':(swing(a),0,0)} for b,a in [('leg_l',24),('leg_r',-24),('arm_l',-14),('arm_r',14)]})
    if kind=='arquero':
        attack={'arm_r':{'rotation':(swing(-55,1/1.3),0,0)},
                'arm_l':{'rotation':(swing(-70,1/1.3),swing(18,1/1.3),0),
                         'position':(swing(-2,1/1.3),0,swing(-2,1/1.3))}}
    elif kind=='nigromante':
        attack={'arm_r':{'rotation':(swing(-25,1/1.3),0,0)},
                'orb':{'scale':('1+math.sin(q.anim_time*276.923)*0.35',)*3},
                'head':{'rotation':(swing(-8,1/1.3),0,0)}}
    else:
        attack={'arm_r':{'rotation':(swing(-70,1/1.3),0,swing(-12,1/1.3))},
                'arm_l':{'rotation':(swing(-20 if kind=='escudero' else -35,1/1.3),0,0)}}
    m.anim('attack',.65,attack,loop='once')
    return m


def creeper():
    m=DungeonModel('astral_creeper_fantasma'); m.bone('body',(0,12,0))
    m.cube('body',(-3,6,-2),(3,18,2),'#7fc8ff',pat='ice')
    m.bone('head',(0,18,0),'body')
    m.cube('head',(-4,18,-4),(4,26,4),'#7fc8ff',pat='ice')
    for i,(x,z) in enumerate(((-2,-3),(2,-3),(-2,3),(2,3))):
        b='leg'+str(i); m.bone(b,(x,6,z),'body')
        m.cube(b,(x-2,0,z-2),(x+2,6,z+2),'#7fc8ff',pat='ice')
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
