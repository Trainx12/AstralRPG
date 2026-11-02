"""Espadas de bloques, construidas por perfiles y superficies de material.

Las cinco siluetas siguen las referencias privadas documentadas en
REFERENCIAS_ARMAS.md. Solo se exportan geometria y texturas originales.
Las coordenadas y giros respetan el formato de modelos vanilla.
"""
import math
from varitas3d import Wand, hx


def weapon(iid, name, colors):
    w = Wand(iid, name, {key: (hx(color), animation) for key,color,animation in colors},
             tilt=-28, tex_dir='item/armas3d')
    w.refined_materials=True
    return w


def plate(w, x, y, width, height, material, depth=0.92, glow=0, angle=0):
    """Relieve separado de ambas caras: no hay superficies coplanares."""
    for side in (-1,1):
        w.cen((x,y,8+side*depth),(width,height,.10),material,
              ('z',angle) if angle else None,glow)


def section(profile,y):
    for (ya,wa),(yb,wb) in zip(profile,profile[1:]):
        if ya<=y<=yb:return wa+(wb-wa)*(y-ya)/(yb-ya)
    return profile[-1][1]


def blade(w,profile,body,shade,edge,ridge,depth=1.35,step=.65,glow=0):
    """Seccion de diamante escalonada: nervio, hombros, biseles y filo fino.

    No se resuelve la hoja como una plancha de espesor constante. El ancho
    del perfil se muestrea por tramos; el brillo queda reservado al filo.
    body puede elegir el material por altura para las hojas de fuego.
    """
    y0,y1=profile[0][0],profile[-1][0]
    count=math.ceil((y1-y0)/step)
    for i in range(count):
        a=y0+(y1-y0)*i/count;b=y0+(y1-y0)*(i+1)/count
        wd=section(profile,(a+b)/2)*getattr(w,'blade_scale',1.2)
        if wd<.18:continue
        sw=body((a+b)/2) if callable(body) else body
        # Centro grueso, flancos de media seccion y filos casi laminados.
        w.box((8-wd*.20,a,8-depth/2),(8+wd*.20,b,8+depth/2),ridge or sw)
        for side in (-1,1):
            for f0,f1,thick,mat in ((.20,.39,depth*.72,sw),(.39,.48,depth*.38,shade),(.48,.51,.18,edge)):
                xa,xb=8+side*wd*f0,8+side*wd*f1
                w.box((min(xa,xb),a,8-thick/2),(max(xa,xb),b,8+thick/2),mat,None,glow if mat==edge else 0)


def ferrule(w,y,material,width=2.3,height=.45):
    w.cen((8,y,8),(width,height,width),material)
    w.cen((8,y,8),(width*.78,height+.08,width*.78),material,('y',45))


def wrapped_grip(w,y0,y1,core,wrap,metal,width=1.65):
    w.cen((8,(y0+y1)/2,8),(width,y1-y0,width),core)
    # Vendas cruzadas inclinadas, con costura visible en las cuatro caras.
    for k in range(math.ceil((y1-y0)/.9)):
        y=y0+.38+k*.9
        if y+.28>y1:continue
        for side in (-1,1):
            w.cen((8,y,8+side*(width/2+.035)),(width+.08,.29,.12),wrap,('z',22.5))
            w.cen((8+side*(width/2+.035),y,8),(.12,.29,width+.08),wrap,('x',-22.5))
    for y in (y0+.15,y1-.15):ferrule(w,y,metal,width+ .45,.45)


def jewel(w,x,y,size,rim,gem,shine,depth=1.2):
    for side in (-1,1):
        z=8+side*depth
        w.cen((x,y,z),(size*1.35,size*1.35,.32),rim,('z',45))
        w.cen((x,y,z+side*.23),(size,size,.24),gem,('z',45),12)
        w.cen((x-.16*size,y+.18*size,z+side*.39),(size*.33,size*.33,.10),shine,('z',45),14)
        for dx,dy in ((-.72,0),(.72,0),(0,-.72),(0,.72)):
            w.cen((x+dx*size,y+dy*size,z+side*.1),(.20,.20,.26),rim)


def chain(w,x,y,length,metal):
    for k in range(length):
        cy=y-k*.82;cx=x+math.sin(k*.55)*.22
        # Eslabones abiertos alternando sus planos, no bloques macizos.
        if k%2==0:
            for dx in (-.30,.30):w.cen((cx+dx,cy,8),(.16,.78,.18),metal)
            for dy in (-.39,.39):w.cen((cx,cy+dy,8),(.70,.16,.18),metal)
        else:
            for dz in (-.30,.30):w.cen((cx,cy,8+dz),(.18,.78,.16),metal)
            for dy in (-.39,.39):w.cen((cx,cy+dy,8),(.18,.16,.70),metal)


def rune(w,x,y,mat,depth=1,glow=0):
    plate(w,x,y,.12,1.1,mat,depth,glow)
    plate(w,x+.24,y+.26,.60,.12,mat,depth+.02,glow,45)
    plate(w,x+.24,y-.26,.60,.12,mat,depth+.02,glow,-45)


def espada_saqueador():
    w=weapon('espada_1','Espada del Saqueador',[
        ('steel','aab9cf','s'),('cold','647088','s'),('edge','eef4ff','s'),('ridge','c4d1e1','s'),
        ('groove','303b54','s'),('guard','586076','s'),('trim','9d92a0','s'),('grip','30272b','s'),
        ('wrap','705951','s'),('ruby','b62c3f','pulse'),('glint','ffc0b6','pulse'),('rivet','d1c2a0','s')])
    wrapped_grip(w,-6.4,2.6,'grip','wrap','guard')
    ferrule(w,-7,'guard',2.55,.7)
    w.cen((8,-7.9,8),(1.6,1.6,1.3),'guard',('z',45))
    jewel(w,8,-7.9,.65,'trim','groove','steel',.92)
    # Guarda de acero curvada hacia el mango, tres niveles y remates claros.
    w.cen((8,3.4,8),(6.4,1.2,2),'guard')
    for side in (-1,1):
        p=w.seg((8+side*2.5,3.5),0 if side==1 else 180,1.7,1.1,'trim',(7.05,8.95))
        p=w.seg(p,-45 if side==1 else 225,2.4,1.15,'guard',(7.1,8.9))
        w.cen((*p,8),(1.15,.75,2.05),'ridge',('z',-45 if side==1 else 45))
    w.blade_scale=1.35
    profile=[(4.1,3.9),(7,3.8),(18.7,3.65),(24.8,3.35),(28,1.5),(29.1,.20)]
    blade(w,profile,'steel','cold','edge','ridge',1.6)
    # Canal hundido, dos nervaduras de acero y punta con sello de diamante.
    plate(w,8,15.2,.62,19.0,'groove',.84)
    for side in (-1,1):plate(w,8+side*.46,15.2,.16,18.6,'steel',.86)
    jewel(w,8,26,.7,'steel','trim','edge',.64)
    for y in (6.5,8.7,10.9):
        for side in (-1,1):
            w.seg((8+side*1.8,y),45 if side==1 else 135,1.25,.65,'guard',(7.5,8.5))
    w.cen((8,4.3,8),(3.7,1.1,1.85),'guard')
    jewel(w,8,4.5,1.05,'trim','ruby','glint',1.07)
    for side in (-1,1):
        for y in (-4.6,-1.6,1.4):plate(w,8+side*.48,y,.20,.20,'rivet',.96)
    return w


def espada_carnicero():
    w=weapon('espada_2','Espada del Carnicero',[
        ('iron','30313f','s'),('iron2','191d2b','s'),('ridge','505064','s'),('ivory','e8d7a8','s'),
        ('bone','ab9778','s'),('silver','a3afbd','s'),('grip','4e172b','s'),('wrap','8d3844','s'),
        ('ruby','9f2638','pulse'),('glint','e9c17f','s'),('chain','898597','s'),('groove','111520','s')])
    wrapped_grip(w,-5.3,2.5,'grip','wrap','iron')
    w.cen((8,-6,8),(2.4,.85,2.35),'ivory')
    w.cen((8,-7,8),(1.5,1.5,1.6),'bone',('z',45))
    # Pomo con abertura: estructura de colgante y cadena con eslabones reales.
    for x in (7.15,8.85):w.box((x-.18,-9.2,7.8),(x+.18,-6.6,8.2),'ivory')
    w.box((7,-9.4,7.8),(9,-9.0,8.2),'bone')
    chain(w,10.9,2.2,11,'chain')
    jewel(w,10.75,-7.0,.7,'bone','grip','silver',.15)
    # Cuchilla con hombro escalonado y filo de hueso lateral asimetrico.
    for k in range(34):
        y=4.2+k*.65
        left=4.9 if y<22 else 4.9+(y-22)*.85
        right=10.8 if y<23.4 else 10.8-(y-23.4)*.14
        if left>=right:continue
        # El agujero superior se conserva abierto tambien en el cuerpo.
        if y>=25.0:
            w.box((left,y,7.38),(8.75,y+.65,8.62),'iron')
            w.box((10,y,7.38),(right,y+.65,8.62),'iron')
        else:
            w.box((left,y,7.38),(right,y+.65,8.62),'iron')
        w.box((left-.35,y,7.66),(left,y+.65,8.34),'ivory')
        w.box((right-.42,y,7.20),(right,y+.65,8.80),'iron2')
    w.cen((8,4,8),(6.7,1.05,2.2),'iron2')
    for side in (-1,1):
        w.seg((8+side*2.8,3.7),-45 if side==1 else 225,1.65,1.1,'bone',(7,9))
        w.cen((8+side*4.0,2.5,8),(1.2,1.5,2.2),'silver',('z',45 if side==1 else -45))
    # Blindaje en el centro, hendidura longitudinal y collar superior.
    plate(w,8.6,15,.55,19,'groove',.68)
    for y in (6.6,10.2,14,17.8,21.5):
        plate(w,9.8,y,.28,.28,'silver',.89)
        for x,dy in ((6.2,-.4),(6.8,.1)):
            plate(w,x,y+dy,.43,.14,'ridge',.69,angle=22.5)
    for y in (7.5,12.8,18.0):
        plate(w,5.48,y,.33,1.1,'bone',.70)
    # Agujero real entre las tres piezas del remate (no mancha pintada).
    w.box((8.2,25.3,7.3),(8.75,27.1,8.7),'iron2')
    w.box((10,25.3,7.3),(10.55,27.1,8.7),'iron2')
    w.box((8.2,27.1,7.3),(10.55,27.65,8.7),'ridge')
    jewel(w,8,3.8,1.2,'ridge','ruby','glint',1.25)
    return w


def espada_ensangrentada():
    w=weapon('espada_3','Espada Ensangrentada',[
        ('red','ad1933','s'),('ruby','e83b48','s'),('shadow','531631','s'),('edge','ffd2ba','s'),
        ('hot','ff816b','flow'),('guard','302631','s'),('trim','685257','s'),('ivory','cab58e','s'),
        ('grip','211b28','s'),('wrap','68404b','s'),('gem','e72e49','pulse'),('shine','ffcebc','pulse')])
    wrapped_grip(w,-6.7,2.5,'grip','wrap','trim',1.7)
    # Alma clara visible en el mango como en el espadon carmesi de referencia.
    plate(w,8,-2.0,.35,7.0,'ivory',.99)
    w.cen((8,-7.5,8),(3.1,.8,2.0),'guard')
    for side in (-1,1):
        p=w.seg((8+side*1.25,-7.3),45 if side==1 else 135,1.7,.85,'red',(7.1,8.9))
        w.cen((*p,8),(.9,.65,1.5),'ruby')
    profile=[(4.1,4.9),(8,5.3),(17,5.5),(23,4.8),(27,2.5),(29.5,.25)]
    blade(w,profile,'red','shadow','edge','ruby',1.55)
    # Dos canales separados: arriba se abren, dejando una punta bifurcada.
    for side in (-1,1):
        plate(w,8+side*.94,16.1,.28,20.0,'shadow',.81)
        plate(w,8+side*1.35,14.7,.15,16.7,'hot',.60,9)
        w.seg((8+side*1.6,24),90-side*22.5,4.0,.7,'red',(7.5,8.5))
    # Facetas diagonales cortas, con sombras en vez de brillo en toda la hoja.
    for y in (8,12.3,16.6,20.9):
        for side in (-1,1):
            plate(w,8+side*1.45,y,.90,1.15,'ruby',.60,angle=-22.5)
    # Guarda de marco abierto, con cuernos rojos y gema encastrada.
    for side in (-1,1):
        w.box((8+side*2.3-.45,2.2,6.9),(8+side*2.3+.45,5.2,9.1),'guard')
        p=w.seg((8+side*2.3,3.5),-45 if side==1 else 225,2.3,1.15,'trim',(7.25,8.75))
        p=w.seg(p,45 if side==1 else 135,1.7,1.0,'red',(7.3,8.7))
        w.cen((*p,8),(.9,1.1,1.5),'ruby')
    for y in (2.25,5.2):w.cen((8,y,8),(5.4,.7,2.3),'trim')
    jewel(w,8,3.7,1.35,'guard','gem','shine',1.35)
    for y in (7,11):
        w.seg((5.6,y),135,1.15,.6,'shadow',(7.45,8.55))
    return w


def espada_coloso():
    w=weapon('espada_4','Espada del Coloso',[
        ('teal','249f9d','s'),('blue','3761a4','s'),('deep','203e69','s'),('edge','8aeee0','s'),
        ('mint','44d5b0','pulse'),('navy','172838','s'),('trim','456c80','s'),('silver','84a8b8','s'),
        ('groove','162e47','s'),('gem','31d7ca','pulse'),('shine','b5fff0','spark'),('wrap','314455','s')])
    wrapped_grip(w,-7,2.6,'navy','wrap','trim',1.8)
    # Gancho de pomo, perfil abierto de tres tramos como la referencia.
    p=(8,-7.1)
    for angle,ln,wd in ((270,1.9,1.6),(225,2.4,1.4),(180,2.0,1.1),(135,1.8,.65)):
        p=w.seg(p,angle,ln,wd,'navy',(7.25,8.75))
    # Hoja de cristal con remate oblicuo y facetas diagonales de turquesa y azul.
    profile=[(4.5,5.4),(11,5.5),(22.2,5.0),(27,4.5),(29.5,3.3),(30.5,1.2)]
    blade(w,profile,'teal','deep','edge','blue',1.75,step=.55)
    for side in (-1,1):
        plate(w,8+side*.48,17,.25,23.8,'groove',.94)
    # Incrustaciones diagonales escalonadas: cada cara tiene su propia faceta.
    for k in range(6):
        y0=6+k*3.7
        for j in range(8):
            x=5.9+j*.60;y=y0+j*.25
            if abs(x-8)>section(profile,y)*.43:continue
            depth=.94 if abs(x-8)<1.05 else .68
            plate(w,x,y,.58,.85,'mint' if (j+k)%3 else 'deep',depth,3)
    w.cen((8,3.7,8),(5.8,1.6,2.65),'navy')
    # Aletas en abanico con nervaduras y borde plateado.
    for side in (-1,1):
        for k in range(3):
            angle=22.5+k*22.5 if side==1 else 157.5-k*22.5
            start=(8+side*2.2,3.5-k*.5)
            p=w.seg(start,angle,3.5-k*.45,1.05,'trim',(7.0,9.0))
            w.seg(start,angle,3.2-k*.45,.24,'silver',(6.91,7.0))
            w.seg(start,angle,3.2-k*.45,.24,'silver',(9.0,9.09))
            w.cen((*p,8),(.6,.6,1.7),'silver',('z',45))
    jewel(w,8,3.8,1.4,'trim','gem','shine',1.5)
    for y in (-5.9,-3.1,-.3):ferrule(w,y,'silver',2.1,.28)
    # Pocas esquirlas bien ubicadas conservan la silueta del espadon.
    for x,y,sz in ((4.3,25,.50),(11.6,18,.45),(7,31.1,.45)):
        w.cen((x,y,8),(sz,sz,sz),'shine',('z',45),13)
    return w


def espada_dios_guerra():
    w=weapon('espada_5','Espada del Dios de la Guerra',[
        ('red','d92748','s'),('magenta','ac245b','s'),('orange','ff642d','s'),('amber','ff9c41','flicker'),
        ('gold','ffcf6d','pulse'),('edge','ffe6a0','s'),('dark','292a50','s'),('violet','4e477d','s'),
        ('trim','7976a0','s'),('grip','29263a','s'),('wrap','645365','s'),('star','ff463d','pulse'),
        ('shine','ffd39c','pulse'),('rune','9e405b','s')])
    wrapped_grip(w,-9.0,2.2,'grip','wrap','violet',2.0)
    # Pomo ancho con alas angulares, anclado al mango y remachado.
    w.cen((8,-9.6,8),(4,.9,2.1),'dark')
    for side in (-1,1):
        p=w.seg((8+side*1.4,-9.5),45 if side==1 else 135,1.7,1.25,'violet',(6.9,9.1))
        w.cen((*p,8),(.8,1.2,1.9),'trim')
    plate(w,8,-9.5,.75,.75,'star',1.18,12,45)
    # La hoja crece y vuelve a cerrarse: gran masa roja/naranja y punta dentada.
    profile=[(4.5,5.7),(7,6.8),(11,6.2),(16,6.7),(20,6.2),(24,5.3),(27.0,3.9),(29.8,1.5),(31,.18)]
    def heat(y):return 'red' if y<11 else 'orange' if y<19 else 'amber' if y<26 else 'gold'
    blade(w,profile,heat,'magenta','edge',None,1.9,step=.6)
    # Frente mosaico de calor: diagonales y rios de fuego, nunca franjas rectas.
    for i in range(37):
        y=5+i*.66
        width=section(profile,y)
        for j in range(7):
            x=8+(j-3)*.72
            if abs(x-8)>width*.43:continue
            level=y+(j-3)*1.05+math.sin(i*.7)*.8
            mat='magenta' if level<9 else 'red' if level<13 else 'orange' if level<20 else 'amber' if level<26 else 'gold'
            depth=1.03 if abs(x-8)<width*.20 else .76
            plate(w,x,y,.70,.64,mat,depth,4 if mat in ('amber','gold') else 0)
    # Vena irregular amarilla bajo el nervio, de grosor cambiante.
    for i in range(20):
        y=8+i*.92;x=8+.42*math.sin(i*.55)
        plate(w,x,y,.25+(i%3)*.10,.94,'gold',1.13,9)
    # Cuernos / alas de tres segmentos, con perfiles oscuros legibles.
    w.cen((8,3.5,8),(6.3,2.5,3.0),'dark')
    for side in (-1,1):
        p=(8+side*2.4,4.0)
        for angle,ln,wd,mat in ((45,2.9,1.7,'violet'),(90,2.6,1.5,'dark'),(135,1.7,1.0,'violet')):
            p=w.seg(p,angle if side==1 else 180-angle,ln,wd,mat,(6.85,9.15))
        w.cen((*p,8),(1.4,.45,2.0),'trim')
        p=w.seg((8+side*2.4,3.3),-22.5 if side==1 else 202.5,2.6,1.3,'dark',(7,9))
        w.seg(p,90,1.4,.80,'violet',(7,9))
        w.seg((8+side*2.3,2.5),-67.5 if side==1 else 247.5,2.3,.9,'violet',(7.1,8.9))
    # Estrella de cuatro puntas encastrada en un rombo en ambas caras.
    jewel(w,8,3.6,1.6,'violet','star','shine',1.72)
    for side in (-1,1):
        z=8+side*2.17
        w.cen((8,3.6,z),(3.4,.55,.14),'star',None,13)
        w.cen((8,3.6,z),(.55,3.4,.14),'star',None,13)
        w.cen((8,3.6,z+side*.09),(.55,.55,.16),'shine',('z',45),15)
    for y,side in ((8,-1),(14,1),(21,-1),(25,1)):
        wd=section(profile,y)
        w.seg((8+side*(wd*.5),y),67.5 if side==1 else 112.5,1.6,.55,heat(y),(7.7,8.3),7)
    for x,y in ((3.5,13.5),(12.2,23.5)):
        w.cen((x,y,8),(.4,.6,.4),'gold',('z',45),13)
    return w


def swords():
    return [espada_saqueador(),espada_carnicero(),espada_ensangrentada(),espada_coloso(),espada_dios_guerra()]
