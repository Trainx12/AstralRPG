"""Escultura propia a 16 texeles/bloque, sin importar arte de las referencias."""
import math
import random
from PIL import ImageDraw
from bbmodel import Model, hexc, swing as _swing


def swing(amp, speed=1, phase=0):
    return _swing(amp, round(speed, 4), phase)


class FloraModel(Model):
    """Grietas y nervaduras distintas por cara, sobre el sombreado del motor."""
    def _paint(self, size, pos):
        im = super()._paint(size, pos)
        draw = ImageDraw.Draw(im)
        for (i, face), (x, y, w, h) in pos.items():
            cube = self.cubes[i]; mat = cube.get('pat')
            rng = random.Random(f'{self.name}/{i}/{face}')
            if mat not in ('rock', 'moss', 'bark', 'leaf', 'bud'): continue
            base = hexc(cube['color'])
            def color(k): return tuple(min(255, int(c*k)) for c in base)+(255,)
            for _ in range(max(1, w*h//(100 if mat=='leaf' else 35))):
                xx, yy = rng.randrange(w), rng.randrange(h)
                for step in range(rng.randint(2, max(3, h//2))):
                    if 0 <= xx < w and 0 <= yy < h:
                        draw.point((x+xx,y+yy), fill=color(.56 if mat=='rock' else .72))
                        if xx+1 < w: draw.point((x+xx+1,y+yy),fill=color(1.12))
                    xx += rng.choice((-1,0,0,1)); yy += 1
            if mat=='moss':
                for _ in range(w*h//8):
                    xx,yy=rng.randrange(w),rng.randrange(h)
                    draw.point((x+xx,y+yy),fill=rng.choice(('#8ea33a','#4f6620','#6f8a28')))
            if mat in ('leaf','bark') and w>3:
                for yy in range(h):
                    draw.point((x+min(w-1,w//2+yy//4%2),y+yy),fill=color(.63))
            if mat=='bud' and w>=6 and h>=6:
                for yy in range(h):
                    for xx in range(w):
                        if yy in (1,h-2) or (xx+i)%7==0:
                            old=im.getpixel((x+xx,y+yy))
                            draw.point((x+xx,y+yy),fill=(min(255,old[0]+18),old[1]+5,min(255,old[2]+3),255))
                left,top,right,bottom=x+1,y+1,x+w-2,y+h-2
                draw.line([(left,bottom),(left,top),(right,top),(right,bottom),
                           (left+2,bottom),(left+2,top+2),(right-2,top+2)],fill=color(.55),width=1)
        return im


def flower(m,b,x,y,z,seed,pink=False):
    rng=random.Random(seed)
    petal=rng.choice(('#c03d7e','#d9578b','#e76895') if pink else ('#f2c230','#e8902a','#d9ad26'))
    r=rng.uniform(.45,.8)
    for dx,dy in rng.sample([(-1,0),(1,0),(0,-1),(0,1)],rng.randint(3,4)):
        m.cube(b,(x+dx*r-r*.6,y+dy*r-r*.6,z-.3),(x+dx*r+r*.6,y+dy*r+r*.6,z),petal)
    m.cube(b,(x-.25,y-.25,z-.5),(x+.25,y+.25,z-.3),'#f6d66a')


def vine(m,b,pts,width=.65,color='#4a2e1c'):
    for a,c in zip(pts,pts[1:]):
        dx,dy,dz=[c[k]-a[k] for k in range(3)]
        length=math.sqrt(dx*dx+dy*dy+dz*dz)
        mid=tuple((a[k]+c[k])/2 for k in range(3))
        m.cube(b,(mid[0]-width/2,mid[1]-length/2,mid[2]-width/2),
               (mid[0]+width/2,mid[1]+length/2,mid[2]+width/2),color,
               rotation=(0,-math.degrees(math.atan2(dz,dx)), -math.degrees(math.atan2(math.hypot(dx,dz),dy))),
               origin=mid,pat='bark')


def coloso():
    m=FloraModel('astral_coloso_musgoso')
    stone,light,dark='#a9acb0','#d2d4d6','#6b6f74'
    m.bone('body',(0,18,0))
    def rock(b,a,c,col=stone): m.cube(b,a,c,col,pat='rock')
    rock('body',(-12,12,-6),(12,28,7))
    rock('body',(-13,10,-7),(13,14,7),dark)
    rock('body',(-13,12,-7.4),(13,14,-6.8),light)
    for x,y,z,w,h in [(-10,18,-6.3,1,5),(-10,18,-6.3,5,1),(-6,18,-6.3,1,3),
                       (-2,17,-6.3,1,7),(-2,17,-6.3,5,1),(2,17,-6.3,1,4),
                       (6,20,-6.3,1,5),(6,20,-6.3,4,1)]:
        rock('body',(x,y,z),(x+w,y+h,z+.4),dark)
    for b,x in [('leg_l',-7),('leg_r',7)]:
        m.bone(b,(x,11,0),'body')
        rock(b,(x-4.8,1,-5),(x+4.8,11,5))
        rock(b,(x-5.3,0,-7),(x+5.3,2,5),light)
        rock(b,(x-4,2,-7.2),(x+3.5,3,-6.8),dark)
    m.bone('head',(0,27,-2),'body',rotation=(0,-6,0))
    rock('head',(-9,25,-9),(9,35,3))
    rock('head',(-10,33,-10),(10,35.5,3))
    rock('head',(-10,33,-10.2),(10,33.6,-9.8),'#69707e')
    rock('head',(-8,29,-9.4),(8,32,-9),dark)
    rock('head',(3,29,-9.8),(6.2,31.8,-9.4),'#3fd9c2')
    rock('head',(3.5,30,-10),(4.3,31.7,-9.8),'#9ff5ea')
    rock('head',(-3,26,-12),(2.8,31,-9),light)
    rock('head',(-6,25,-9.6),(6,26,-9.2),dark)
    # Mejillas labradas y hundidas: el rostro no queda como una cara plana.
    for x in (-8,5):
        rock('head',(x,25,-10.1),(x+3,29,-9.6),'#687078')
        rock('head',(x,25,-10.5),(x+3,25.8,-10.1),light)
    rock('head',(-8,26,-10.5),(-7.2,29,-10.1),light)
    rock('head',(7.2,26,-10.5),(8,29,-10.1),light)
    # Dos marcos abiertos y una placa con gema vertical larga.
    for x,y,z,w,h in [(-10,34,0,7,10),(-6,34,4,6,8)]:
        for a,c in [((x,y,z),(x+1.5,y+h,z+2)),((x+w-1.5,y,z),(x+w,y+h,z+2)),
                    ((x,y+h-1.5,z),(x+w,y+h,z+2))]: rock('head',a,c)
    rock('head',(-3,34,-8),(4,44,-4))
    rock('head',(-1.8,35,-8.5),(2.5,42.8,-8),dark)
    rock('head',(-.8,35.5,-8.8),(1.5,42,-8.5),'#3fd9c2')
    rock('head',(-.6,36,-9),(.1,41.6,-8.8),'#9ff5ea')
    m.bone('arm_r',(14,27,1),'body')
    rock('arm_r',(11,24,-4),(19,31,6))
    rock('arm_r',(16,28,-3),(23,35,6))
    rock('arm_r',(18,33,-3),(25,43,5))
    rock('arm_r',(14,40,-5),(25,46,6))
    pts=[]
    for j in range(23):
        t=j*math.pi/3
        pts.append((21.3+4.2*math.cos(t),29+j*.7,1+5*math.sin(t)))
    vine(m,'arm_r',pts,1.8)
    vine(m,'arm_r',[(15,27,-4.3),(18,30,-4.5),(19,35,-4.4),
                       (23,38,-4.4),(22,43,-5.7)],1.5,'#6b4428')
    vine(m,'arm_r',[(14.5,44,-5.8),(18,43,-5.9),(20,44,-5.9),
                       (20,46,-5.8)],1.8,'#5b4238')
    for x,y,z,w,h in [(17,31,-4,3,3),(22,36,-4,3,4),(16,42,-5.6,4,2)]:
        m.cube('arm_r',(x,y,z),(x+w,y+h,z+.7),'#6f8a28',pat='moss')
    m.bone('arm_l',(-15,27,1),'body',rotation=(0,0,-10))
    rock('arm_l',(-20,18,-4),(-12,29,5))
    rock('arm_l',(-22,8,-6),(-11,20,6))
    for y in (9,13,18):
        rock('arm_l',(-22.6,y,-6.5),(-10.4,y+1.5,6.5),dark)
        rock('arm_l',(-22.8,y+1.2,-6.7),(-10.2,y+1.8,6.7),light)
    rng=random.Random('cortina-coloso')
    for b,x0,x1,top,z in [('body',-13,14,29,-6.8),('body',-13,14,14,-7.8),
                          ('body',-12,13,28,7),('arm_l',-21,-11,24,-6.9),
                          ('leg_l',-11,-3,10,-5.8),('leg_r',3,12,10,-5.8)]:
        x=x0
        while x<x1:
            w=rng.uniform(2.2,4.2); low=top-rng.uniform(2.5,6)
            m.cube(b,(x,low,z),(min(x1,x+w),top+rng.uniform(0,.8),z+.8),rng.choice(('#6f8a28','#8ea33a','#4f6620')),pat='moss')
            # Largos y anchos diferentes, con un segundo escalon en el borde.
            if rng.random()<.7:
                m.cube(b,(x+.3,low-rng.uniform(.5,1.7),z-.1),
                       (min(x1,x+w-.3),low+.6,z+.9),'#6f8a28',pat='moss')
            if rng.random()<.35:
                vine(m,b,[(x+.6,top,z-.2),(x+.5,low+2,z-.3),(x+1.2,low-.7,z-.4)],.55)
            x+=w-.15
    for x in (-14,8): m.cube('body',(x,28,-4),(x+6,30.5,7),'#6f8a28',pat='moss')
    # El faldon forma masas asimetricas; los flecos salen de estas placas.
    for x,y,w,h in [(3,8,9,7),(6,5,5,5),(-12,10,5,4),(-12,23,5,6),(8,24,6,5)]:
        # Cuentagotas: musgo (342,485), raiz (413,81) de jefe-mina-referencia.
        m.cube('body',(x,y,-8.2),(x+w,y+h,-7.5),'#51561c',pat='moss')
        vine(m,'body',[(x+1,y+h,-8.5),(x+2,y+2,-8.6),(x+4,y,-8.5)],.8,'#5b4238')
    for i,(b,x,y,z) in enumerate([('arm_l',-20,17,-7),('arm_l',-12,12,-7),
                                   ('body',-10,28,-7.5),('body',8,12,-8.4),('body',10,27,-7.5)]):
        flower(m,b,x,y,z,i)
    m.anim('idle',3,{'body':{'position':(0,swing(.22,1/3),0)},'arm_r':{'rotation':(swing(2,1/3),0,swing(1,1/3))}})
    m.anim('walk',1.6,{b:{'rotation':(swing(a,1/1.6),0,0)} for b,a in [('leg_l',12),('leg_r',-12),('arm_l',8),('arm_r',-5)]})
    m.anim('attack',.9,{'arm_r':{'rotation':(swing(-85,1/1.8),0,swing(-12,1/1.8))},'body':{'rotation':(swing(10,1/1.8),0,0)}},loop='once')
    return m


def planta():
    m=FloraModel('astral_bosque_planta'); m.bone('root',(0,0,0))
    m.cube('root',(-4.5,0,-4.5),(4.5,6,4.5),'#394b20',pat='bark')
    vine(m,'root',[(-5,1,-5),(0,.6,-6),(5,1,-5),(6,1,0),(5,.6,5),(0,1,6),(-5,1,5),(-6,1,0),(-5,1,-5)],.8,'#b04073')
    for i,(x,z) in enumerate([(-5,-4),(4,-5),(5,3),(-4,5)]): flower(m,'root',x,2,z,i+30,True)
    m.bone('stem',(0,4,0),'root',rotation=(0,0,15))
    # Cuentagotas planta: tallo (194,429), oliva (327,282), rojo (291,345).
    m.cube('stem',(-3,4,-2.5),(3,24,3),'#978725',pat='bark')
    for x in (-2.6,0,2): m.cube('stem',(x,5,-2.8),(x+.65,23,-2.5),'#657423',pat='bark')
    for y in (10,17):
        m.cube('stem',(2.5,y,-1),(5,y+1.6,1),'#cb4384',rotation=(0,0,25),pat='bud')
    m.bone('head',(0,25,0),'stem',rotation=(0,-12,-16))
    m.cube('head',(0,25,-7),(17,30,4),'#4c501e',pat='leaf')
    m.cube('head',(-.7,29.5,-7.5),(17.7,31,4.5),'#747b2d',pat='leaf')
    for x in (1,5,9,13):
        m.cube('head',(x,25,-7.3),(x+1.8,28.3,-7),'#4a4e21',pat='leaf')
    m.cube('head',(.7,24.5,-6.6),(16.3,25,3),'#a92530',pat='leaf')
    m.cube('head',(1,19,2.5),(16,25,4),'#af1f1f',pat='leaf')
    m.bone('jaw',(8,23,3),'head',rotation=(-38,0,-9))
    m.cube('jaw',(0,20,-9),(17,22,3),'#4e6121',pat='leaf')
    m.cube('jaw',(1,22,-8.3),(16,22.6,2.7),'#d82d2b',pat='leaf')
    m.cube('jaw',(6,22.6,-8.8),(10.5,23.1,-1),'#f34c59',pat='leaf')
    for i,x in enumerate((1,4.5,8,11.5,15)):
        m.cube('head',(x,21-i%2,-7.3),(x+1.1,25,-6.2),'#a5b638',pat='leaf')
        m.cube('jaw',(x+.3,22.4,-7.7),(x+1.3,24,-6.6),'#ced471',pat='leaf')
    for i,(x,y,z,r,rot) in enumerate([(-6,26,-1,5.4,(5,-12,-8)),(1,32,6,5,(0,16,-20))]):
        b=f'bud{i}'; m.bone(b,(x,y,z),'head',rotation=rot)
        m.cube(b,(x-r,y-r,z-r),(x+r,y+r,z+r),'#b43773',pat='bud')
        m.cube(b,(x-r-.3,y+r-.6,z-r-.3),(x+r+.3,y+r+.4,z+r+.3),'#da588b',pat='bud')
    for i,(x,y,z,w,h,angle) in enumerate([(-9,32,7,7,15,38),(13,30,8,8,10,-43),(-8,18,-1,9,10,-45)]):
        b=f'leaf{i}'; m.bone(b,(x,y,z),'head' if i<2 else 'stem',rotation=(0,-10,angle))
        m.cube(b,(x-w/2,y-h/2,z),(x+w/2,y+h/2,z+.7),'#377b7d',pat='leaf')
        # Extremos separados: evita caras coplanares que parpadean en el cliente.
        for ya,yb in ((y-h/2-1.5,y-h/2),(y+h/2,y+h/2+1.5)):
            m.cube(b,(x-w/2+1,ya,z),(x+w/2-1,yb,z+.7),'#45aba0',pat='leaf')
        m.cube(b,(x-.6,y-h/2,z-.25),(x+.6,y+h/2,z),'#246e70',pat='leaf')
    m.anim('idle',3,{'stem':{'rotation':(0,0,swing(3,1/3))},'head':{'rotation':(swing(2,1/3),0,0)}})
    m.anim('attack',.6,{'head':{'position':(0,0,swing(-4,1/1.2))},'jaw':{'rotation':(swing(32,1/1.2),0,0)}},loop='once')
    m.anim('spit',.8,{'head':{'rotation':(swing(-22,1/1.6),0,0)},'jaw':{'rotation':(swing(-18,1/1.6),0,0)}},loop='once')
    # Alto maximo 2,45 bloques incluyendo las hojas inclinadas.
    for cube in m.cubes:
        for key in ('from','to','origin'):
            if cube.get(key): cube[key]=[v*.976 for v in cube[key]]
    for bone in m.bones.values(): bone['origin']=[v*.976 for v in bone['origin']]
    return m
