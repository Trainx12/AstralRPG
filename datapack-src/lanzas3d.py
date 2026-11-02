"""Cinco lanzas volumetricas basadas en la seleccion de referencias del dueno."""
from espadas3d import weapon, wrapped_grip, blade, ferrule, jewel, plate, rune, chain


def spear(tier,name,colors,shaft,wrap,metal):
    w=weapon(f'lanza_{tier}',name,colors)
    w.tex_dir='item/lanzas3d'
    w.box((7.32,-11,7.32),(8.68,22,8.68),shaft)
    wrapped_grip(w,-8,1.2,shaft,wrap,metal,1.6)
    for y in (-10.5,2.2,10,18.5,20):ferrule(w,y,metal,2.1,.35)
    w.cen((8,-11.7,8),(1.05,1.05,1.05),metal,('z',45))
    return w


def recluta():
    w=spear(1,'Lanza del Recluta',[
        ('wood','72513c','s'),('wrap','ac9474','s'),('iron','30384a','s'),('steel','a4b8c8','s'),
        ('ridge','e6edf0','s'),('dark','55687a','s'),('rivet','c9ba97','s')],'wood','wrap','iron')
    blade(w,[(21,2.5),(23,2.8),(28,1.5),(31.3,.15)],'steel','dark','ridge','steel',1.2,step=.5)
    w.cen((8,21,8),(4.9,.75,1.5),'iron')
    for side in (-1,1):
        w.seg((8+side*2.0,21),45 if side==1 else 225,1.6,.6,'iron',(7.45,8.55))
        for y in (5,13,20.5):plate(w,8+side*.45,y,.22,.22,'rivet',.82)
    plate(w,8,25.5,.22,5.8,'dark',.69)
    for y in (5,13):plate(w,8,y,.20,1.4,'dark',.74,angle=22.5)
    return w


def centinela():
    w=spear(2,'Lanza del Centinela',[
        ('wood','364a37','s'),('wrap','7d9472','s'),('gold','c6a35b','s'),('leaf','4ea783','s'),
        ('dark','245455','s'),('edge','b6edb0','s'),('gem','a8f89d','pulse'),('shine','ecffd0','spark')],'wood','wrap','gold')
    blade(w,[(21,2.9),(24,4.0),(27,2.7),(31.2,.2)],'leaf','dark','edge','leaf',1.4,step=.55)
    for side in (-1,1):
        w.seg((8+side*1.2,20.8),45 if side==1 else 135,2.5,.60,'gold',(7.35,8.65))
        for y in (24,26,28):
            plate(w,8+side*.85,y,.85,.15,'dark',.78,angle=side*22.5)
    jewel(w,8,21.8,.85,'gold','gem','shine',.9)
    for y in (6,12,17):rune(w,8,y,'gold',.79)
    for x,y in ((5,27),(10.7,24)):w.cen((x,y,8),(.40,.40,.40),'shine',('z',45),12)
    return w


def carmesi():
    w=spear(3,'Lanza Carmesi',[
        ('shaft','382233','s'),('wrap','a04b4a','s'),('bone','dfc9a1','s'),('red','bd2541','s'),
        ('dark','60213c','s'),('edge','ff926d','s'),('gem','f64f59','pulse'),('shine','ffd5a0','pulse')],'shaft','wrap','bone')
    blade(w,[(21,2.8),(24,2.6),(29,1.5),(31.1,.2)],'red','dark','edge','red',1.4,step=.5)
    for side in (-1,1):
        p=w.seg((8+side*1.6,20.8),90-side*22.5,4.1,.8,'red',(7.4,8.6))
        w.seg(p,90-side*22.5,2.0,.45,'edge',(7.7,8.3))
        w.seg((8+side*1.4,20),-45 if side==1 else 225,1.6,.7,'bone',(7.1,8.9))
    jewel(w,8,23,1.10,'dark','gem','shine',1.0)
    for y in (5.5,8.1,13.5):ferrule(w,y,'bone',2.25,.55)
    chain(w,9.6,16,4,'bone')
    return w


def vendaval():
    w=spear(4,'Lanza del Vendaval',[
        ('shaft','382d51','s'),('wrap','6d5483','s'),('gold','c7aa76','s'),('purple','8454b4','s'),
        ('deep','492c70','s'),('edge','d4baff','s'),('gem','bd8cff','pulse'),('wind','e3cfff','flow')],'shaft','wrap','gold')
    # Guja de perfil lateral; el borde describe tres curvas angulares.
    w.blade((8,20.3),[(90,3.8,2.0),(67.5,3.0,2.7),(45,2.7,2.4),(67.5,2.0,1.1)],
            'purple',edge='edge',spine='deep',side=-1,z=(7.25,8.75),edge_w=.3)
    w.cen((8,21.2,8),(5.0,.7,2),'gold')
    for side in (-1,1):
        w.seg((8+side*2.1,21.1),-45 if side==1 else 135,1.45,.65,'gold',(7.3,8.7))
        for y in (8,12,16):plate(w,8,y,.26,1.3,'wind',.82,8)
    jewel(w,8,21.5,1,'deep','gem','edge',1.16)
    for x,y in ((10,25),(11.1,27)):
        plate(w,x,y,1.1,.16,'wind',.90,8,22.5)
    return w


def astral():
    w=spear(5,'Lanza Astral',[
        ('shaft','203b54','s'),('wrap','527087','s'),('silver','a1c9d4','s'),('ice','72cee5','s'),
        ('deep','386d9b','s'),('edge','e4ffff','s'),('gem','4ce6e3','pulse'),('shine','d8fffb','spark')],'shaft','wrap','silver')
    blade(w,[(21.5,2.3),(26,2),(31.5,.18)],'ice','deep','edge','ice',1.35,step=.5)
    for side in (-1,1):
        p=w.seg((8,21.4),22.5 if side==1 else 157.5,3.6,1.0,'silver',(7.25,8.75))
        p=w.seg(p,90,3.5,1.25,'ice',(7.35,8.65))
        w.seg(p,90-side*22.5,2.5,.55,'edge',(7.65,8.35))
        w.seg((8+side*1.5,21.4),270-side*45,1.7,.55,'deep',(7.5,8.5))
        for y in (4,8,12,16):
            plate(w,8,y,.3,1.2,'gem',.84,8)
    jewel(w,8,21.7,1.20,'silver','gem','shine',1.10)
    for x,y in ((4.4,25.8),(11.7,28.8)):w.cen((x,y,8),(.42,.42,.42),'shine',('z',45),13)
    return w


SPEARS=[recluta(),centinela(),carmesi(),vendaval(),astral()]


def assets():
    from varitas3d import assets as export
    return export(SPEARS)
