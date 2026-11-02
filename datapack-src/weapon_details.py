"""Acabados de materiales y herrajes para las familias de armas originales.

Las piezas siguen las caras locales de cada hoja; no se agregan adornos
sueltos al azar. No cambia los anclajes de mano ni la mecanica de los arcos.
"""
import math


def material_texture(w):
    """Atlas compatible de 32 px: metal cepillado, cuero, hueso y cristal.

    Los metales no usan ruido aleatorio que parezca tela. Se conservan los
    ocho cuadros y el tiempo de las animaciones originales.
    """
    from PIL import Image
    import varitas3d as v
    n=v.FRAMES if any(kind!='s' for _,kind in w.palette.values()) else 1
    im=Image.new('RGBA',(v.TEX,v.TEX*n))
    for name,slot in w.slots.items():
        base,kind=w.palette[name]
        for y in range(v.TS):
            for x in range(v.TS):
                if name.startswith(('wood','bark','shaft')):
                    pattern=(.93,.98,1.04,.97,1.0,1.07,.98,.94)[x]
                    if (x+y*2)%17==0:pattern-=.05
                elif name.startswith(('wrap','grip','leather','cloth','tassel')):
                    pattern=.86 if (x+y//2)%6==0 else 1.02
                elif name.startswith(('bone','ivory','tooth')):
                    pattern=(.91,.97,1.04,1.06,1.02,.99,.96,.89)[x]
                elif kind!='s':
                    pattern=1.10 if x+y in (5,6) else .96 if x<3 else 1.02
                else:
                    pattern=(1.12,1.06,1.02,.99,.98,.96,.94,.88)[x]
                    if y==1 and x<5:pattern+=.04
                for frame in range(n):
                    # Animacion del material sin parpadeo aleatorio.
                    im.putpixel((slot%4*v.TS+x,frame*v.TEX+slot//4*v.TS+y),
                                v._frame_color(base,kind,frame,0,x,y,pattern))
    return im,n


def choose(w,*names):
    return next((name for name in names if name in w.palette),next(iter(w.palette)))


def band(w,y,metal,width=2.55):
    w.cen((8,y,8),(width,.28,width),metal)
    for x in (-.7,.7):
        for side in (-1,1):w.cen((8+x,y,8+side*(width/2+.05)),(.19,.19,.13),metal,('z',45))


def rune(w,x,y,z,material,size=.8,glow=0):
    w.cen((x,y,z),(.12,size,.10),material,None,glow)
    for sign in (-1,1):
        w.cen((x+.20,y+sign*.18,z),(.48,.12,.10),material,('z',sign*45),glow)


def surface(w,e,a,b,mat,glow=0):
    """Pieza del relieve en las coordenadas LOCALES de la pieza original."""
    w.box(a,b,mat,e['rot'],glow)


def laminate(w,materials,trim,engraving,minimum_y=16,limit=12):
    """Biseles laterales y grabado longitudinal sobre las hojas existentes."""
    candidates=[]
    for e in list(w.els):
        a,b=e['from'],e['to'];dx,dy,dz=[b[i]-a[i] for i in range(3)]
        if e['sw'] not in materials or a[1]<minimum_y or min(dx,dy)<.55 or dz<.45:continue
        if e['rot'] and e['rot'][0]!='z':continue
        candidates.append(e)
    for e in sorted(candidates,key=lambda e:(e['to'][0]-e['from'][0])*(e['to'][1]-e['from'][1]),reverse=True)[:limit]:
        a,b=e['from'],e['to'];dx,dy=[b[i]-a[i] for i in range(2)]
        long_x=dx>dy
        for side in (-1,1):
            z=a[2]-.09 if side<0 else b[2]+.03
            if long_x:
                surface(w,e,(a[0]+.18,a[1]+dy*.24,z),(b[0]-.18,a[1]+dy*.24+.13,z+.06),trim)
                surface(w,e,(a[0]+.25,a[1]+dy*.51,z-.015),(b[0]-.25,a[1]+dy*.51+.13,z+.075),engraving)
                for x in (a[0]+.35,b[0]-.35):
                    surface(w,e,(x-.07,a[1]+dy*.73,z),(x+.07,a[1]+dy*.73+.18,z+.08),trim)
            else:
                surface(w,e,(a[0]+dx*.22,a[1]+.20,z),(a[0]+dx*.22+.11,b[1]-.20,z+.06),trim)
                # Marca de taller con tres cortes en el centro de cada faceta.
                for t in (.35,.5,.65):
                    surface(w,e,(a[0]+dx*.45,a[1]+dy*t,z),(a[0]+dx*.72,a[1]+dy*t+.10,z+.08),engraving)


def gem_prongs(w,metal):
    """Engarces de cuatro garras para sujetar los cristales grandes."""
    gems=[e for e in list(w.els) if e['rot'] and e['rot'][:2]==('z',45)
          and e['glow'] and 1.5<=e['to'][0]-e['from'][0]<=4.5]
    for e in gems[:3]:
        c=[(a+b)/2 for a,b in zip(e['from'],e['to'])]
        r=(e['to'][0]-e['from'][0])*.60
        for side in (-1,1):
            for dx,dy in ((-r,0),(r,0),(0,-r),(0,r)):
                w.cen((c[0]+dx,c[1]+dy,c[2]+side*.88),(.26,.46,.35),metal,('z',45))


def open_chain(w,x,y,metal,count=5,z=8):
    for k in range(count):
        cy=y-k*.7
        for sign in (-1,1):
            if k%2:
                w.cen((x,cy,z+sign*.25),(.13,.70,.13),metal)
                w.cen((x,cy+sign*.35,z),(.13,.13,.63),metal)
            else:
                w.cen((x+sign*.25,cy,z),(.13,.70,.13),metal)
                w.cen((x,cy+sign*.35,z),(.63,.13,.13),metal)


def refine_wand(w):
    if getattr(w,'refined_materials',False):return w
    metal=choose(w,'silver','gold','silver2','bone2','bark')
    glow=choose(w,'rune','gem2','core2','crystal2','gem')
    dark=choose(w,'wood2','bone2','dark','gold2')
    gem_prongs(w,metal)
    if w.iid=='baston_1':
        # Nudos de madera, nervaduras de las hojas y ataduras de raices.
        for y in (4.7,9.3,14.5):
            for side in (-1,1):
                w.cen((8+side*.65,y,8+side*1.10),(.30,1.35,.25),'bark',('z',side*22.5))
        for y in (1.9,12.7):band(w,y,'cord',2.4)
        for side in (-1,1):
            w.seg((8+side*1.0,17.5),90-side*45,2.0,.30,'bark',(6.75,6.95))
        open_chain(w,10.1,15.1,'cord',4)
        w.cen((10.1,12.3,8),(.55,.9,.55),'bead',('y',45),10)
    elif w.iid=='baston_2':
        for y in (4.5,7.4,11.2,14.4):
            for side in (-1,1):rune(w,8,y,8+side*1.18,'gold',.85)
        for y in (17.3,18.7):band(w,y,'gold2',3.6)
        open_chain(w,10.5,15.5,'gold',5)
        for y in (11,10.4,9.8):w.cen((10.5,y,8),(.46,.5,.46),'tassel')
    elif w.iid=='baston_3':
        for y in (2.5,8.8,14.2):
            for side in (-1,1):rune(w,8,y,8+side*1.28,glow,.90,8)
        for y in (-1.2,5.8,12.2):band(w,y,metal,2.7)
        open_chain(w,10.0,16.0,metal,5)
        w.cen((10,12.4,8),(.65,1.1,.65),glow,('z',45),10)
    elif w.iid=='baston_4':
        # Mango con filigrana y cuello con nervaduras de plata.
        for y in (-2.5,4.3,10.8,15.1):band(w,y,metal,2.6)
        for y in (2,6,10,13.5):
            for side in (-1,1):rune(w,8,y,8+side*1.26,glow,.95,9)
        for side in (-1,1):
            w.seg((8+side*1.1,18),90-side*22.5,2.3,.25,metal,(6.45,6.65))
    else:
        # Rosario astral, rayos grabados y estrellas sobre la vara.
        for y in (-3,2,7,12,16):
            for side in (-1,1):rune(w,8,y,8+side*1.12,metal,.85)
        open_chain(w,10.2,15.5,metal,6)
        w.cen((10.2,11.1,8),(.75,.75,.55),glow,('z',45),11)
        for x in (6.2,9.8):w.cen((x,18.6,8),(.5,.5,2.3),metal,('z',45))
    w.refined_materials=True
    return w


def refine_scythe(w):
    if getattr(w,'refined_materials',False):return w
    metal=choose(w,'metal','fin','steel','nail','bone2','silver','iron')
    dark=choose(w,'steel2','blade','dark','navy','blue2','shadow')
    light=choose(w,'edge','neon2','tq2','gem2','rune','runeg')
    bodies={'steel','steel2','blade','dark','dark2','navy','navy2','prism','prism2','bone','bone2','blue','shadow2'}
    laminate(w,bodies,metal,dark,minimum_y=18,limit=9)
    gem_prongs(w,metal)
    if w.iid=='guadana_2':
        # Calavera: cejas oblicuas, suturas, pomulos y dientes en relieve.
        skulls=[e for e in w.els if e['sw']=='bone' and e['to'][2]-e['from'][2]>3]
        if skulls:
            e=max(skulls,key=lambda e:e['to'][1]);a,b=e['from'],e['to']
            cx=(a[0]+b[0])/2;cy=(a[1]+b[1])/2
            for side in (-1,1):
                z=a[2]-.15 if side<0 else b[2]+.15
                for dx in (-.8,.8):w.cen((cx+dx,cy+.7,z),(1.0,.28,.18),'bone2',('z',-22.5 if dx<0 else 22.5))
                for dx in (-.8,-.4,0,.4,.8):w.cen((cx+dx,a[1]+.20,z),(.27,.6,.25),'bone2')
                rune(w,cx,b[1]-.5,z,'hole',.7)
        open_chain(w,10.5,18.2,'chain',8)
    elif w.iid=='guadana_3':
        for y in (6.2,9,13.2,17):
            for side in (-1,1):rune(w,8,y,8+side*1.13,'neon2',.8,9)
        for y in (-2.8,4.6):band(w,y,'metal',2.7)
    elif w.iid=='guadana_4':
        for y in (9.5,11.5,13.5):
            for side in (-1,1):rune(w,10.7,y,8+side*.65,'rune',.7,9)
        for y in (4.4,17.5):band(w,y,'fin',2.6)
    elif w.iid=='guadana_5':
        open_chain(w,10.4,18.2,'blue2',7)
        for y in (9,11.5,14,16.5):
            for side in (-1,1):rune(w,8,y,8+side*1.10,'tq2',.8,8)
        for y in (8,18):band(w,y,'bone2',2.7)
    elif w.iid=='guadana_umbria':
        for y in (6.5,12.5,18):
            for side in (-1,1):rune(w,8,y,8+side*1.13,'rune',.85,9)
        open_chain(w,10.5,18.5,metal,5)
    else:
        for y in (-1,4.5,11,16.7):band(w,y,'iron',2.4)
        for y in (1,6.5,12):
            for side in (-1,1):w.cen((8,y,8+side*1.22),(.25,.25,.14),'steel',('z',45))
    w.refined_materials=True
    return w


def refine_axe(w):
    if getattr(w,'refined_materials',False):return w
    metal=choose(w,'gold','steel','iron','ice2')
    dark=choose(w,'stone2','iron2','red2','ice3','iron')
    light=choose(w,'rune','lava2','ember','gem','crystal')
    laminate(w,{'stone','stone2','iron','iron2','red','red2','ice','ice3'},metal,dark,limit=14)
    for y in (-3.7,-1,1.7,7.2,11.8):
        band(w,y,metal,2.3)
        for side in (-1,1):rune(w,8,y+.8,8+side*1.15,dark,.65)
    gem_prongs(w,metal)
    # Cabezal de tres escalones con pernos transversales.
    for y,width in ((17.7,3.2),(18.4,3.7),(26.5,3.4)):
        band(w,y,metal,width)
    if w.iid in ('hacha_4','hacha_5'):
        for side in (-1,1):
            for k in range(4):
                x=8+side*(3.1+k*.8);y=23.7-k*.7
                for face in (-1,1):rune(w,x,y,8+face*.93,light,.55,9)
        if w.iid=='hacha_5':open_chain(w,10.5,17.0,'steel',6)
    elif w.iid=='hacha_3':
        for x,y in ((3.2,22.3),(4.7,24),(5.6,20.3)):
            for side in (-1,1):rune(w,x,y,8+side*.92,light,.8,7)
    elif w.iid=='hacha_2':open_chain(w,10.4,17,metal,5)
    else:
        # Correas alrededor de la union con la cabeza de piedra.
        for side in (-1,1):
            for y in (19.4,25.2):w.cen((8,y,8+side*1.65),(2.0,.24,.16),'wrap',('z',22.5))
    w.refined_materials=True
    return w


def refine_bow(w):
    if getattr(w,'refined_materials',False):return w
    base=w.tex_name
    metal=choose(w,'gold','silver','ring','bone2','wood2')
    wrap=choose(w,'wrap','teal2','wood2','violet','deep')
    light=choose(w,'gem','core2','ring','leaf2','lens')
    # Empunadura siempre en (6,8), para los cuatro estados de tensado.
    for y in (6.5,9.5):
        w.cen((6,y,8),(2.65,.3,2.1),metal)
        for side in (-1,1):w.cen((6,y,8+side*1.13),(.25,.25,.15),metal,('z',45))
    for y in (7.1,7.7,8.3,8.9):
        for side in (-1,1):w.cen((6,y,8+side*1.03),(1.75,.22,.12),wrap,('z',22.5))
    bodies={'wood','wood2','gold','silver','silver2','tan','crystal','bone','bone2','deep'}
    laminate(w,bodies,metal,wrap,minimum_y=10,limit=6)
    laminate(w,bodies,metal,wrap,minimum_y=-10,limit=6)
    for sign in (-1,1):
        for side in (-1,1):
            rune(w,6.0,8+sign*3.1,8+side*1.18,light,.8,8 if w.palette[light][1]!='s' else 0)
    if base=='arco_1':
        # Nervaduras de las hojas y nudos de cuerda para el arco de madera.
        for sign in (-1,1):
            for k in range(3):
                w.seg((4.6,8+sign*(4.4+k*.75)),180-sign*22.5,1.0,.16,metal,(7,7.13))
    elif base=='arco_2':
        for y in (3.7,12.3):
            for side in (-1,1):w.cen((5.1,y,8+side*.98),(.45,.45,.12),light,('z',45),8)
    elif base=='arco_3':
        # Tornillos de ajuste, reticula y abrazaderas de la mira.
        for x in (4,6.5,8.7):
            w.cen((x,11.15,7.35),(.24,.45,.18),metal)
        w.cen((7.4,10.4,6.95),(.40,.40,.40),metal,('y',45))
    elif base=='arco_4':
        for sign in (-1,1):
            for k in range(3):
                w.cen((4.8-k*.5,8+sign*(5+k*.65),7.0),(.8,.25,.12),'wind',('z',sign*22.5),8)
    else:
        for sign in (-1,1):
            for k in range(3):
                for side in (-1,1):w.cen((5.5,8+sign*(4.2+k*.8),8+side*.98),(1.1,.28,.25),'bone2',('z',sign*22.5))
    w.refined_materials=True
    return w


def refine_gauntlet(w):
    if getattr(w,'refined_materials',False):return w
    for x in (5.55,7.25,8.95,10.65):
        for y in (2.7,4.0):
            w.cen((x,y,3.65),(1.1,.25,.23),'steel')
        w.cen((x,6.8,3.55),(.32,.32,.18),'core2',('z',45),9)
    for y in (-4.1,-2.7,-1.3):
        for side in (-1,1):
            w.cen((8+side*3.65,y,8),(.25,.85,3.2),'red2')
            for z in (6.7,9.3):w.cen((8+side*3.84,y,z),(.15,.24,.24),'steel')
    for x in (6.5,9.5):rune(w,x,3.6,11.97,'core2',1,10)
    w.refined_materials=True
    return w
