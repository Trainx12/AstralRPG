"""Modelos originales inspirados en las referencias privadas; sin imagenes ajenas."""
from espadas3d import weapon, blade, wrapped_grip, ferrule, jewel, rune
from varitas3d import assets as export_assets, check, preview


def sword(iid, name, body, edge, gem, broad=False):
    w=weapon(iid,name,[('body',body,'s'),('dark','202235','s'),('edge',edge,'flow'),
                       ('metal','97a8c0','s'),('gem',gem,'pulse'),('light','edffff','spark'),('grip','382a48','s')])
    wrapped_grip(w,1,7,'dark','grip','metal')
    jewel(w,8,.3,.65,'metal','gem','light')
    w.cen((8,8,8),(7.5,.85,1.8),'dark')
    for side in (-1,1):
        w.cen((8+side*3.5,8.5,8),(1,2,1.5),'metal',('z',-side*22.5))
        w.gem((8+side*4,10,8),.65,'gem',14)
    jewel(w,8,8.5,1.05,'metal','gem','light')
    if broad:
        profile=[(9,3.6),(12,4.2),(21,3),(26,1.5),(28,.1)]
    else:
        profile=[(9,2.5),(12,3.2),(21,2.3),(26,.8),(28,.1)]
    blade(w,profile,'body','dark','edge','metal',glow=12)
    for y in (12,15,18,21):rune(w,7.7,y,'gem',depth=1.1,glow=13)
    if broad:
        for side in (-1,1):
            w.gem((8+side*3,19,8),.65,'gem',14,tall=1.6)
            w.gem((8+side*2.2,24,8),.5,'edge',14)
    return w


def quake():
    w=weapon('hacha_terremoto','Hacha del Sismo',[
        ('stone','423e46','s'),('edge','a4a2a9','s'),('metal','a77b48','s'),
        ('rune','ffd283','pulse'),('wood','4c2c28','s'),('wrap','846446','s'),('light','fff3ce','spark')])
    w.shaft(0,24,'wood',1.8)
    wrapped_grip(w,1,12,'wood','wrap','metal',1.9)
    for y in (13,16,20,24):ferrule(w,y,'metal',2.6)
    for side in (-1,1):
        for y,span in ((17,4),(19,6),(21,6.8),(23,5.6),(25,3.6)):
            w.cen((8+side*(1.1+span/2),y,8),(span,2.1,2),'stone')
            w.cen((8+side*(1.1+span),y,8),(.45,2.1,1.2),'edge')
            for z in (6.93,9.07):
                w.cen((8+side*(1.7+span/2),y,z),(span*.65,.18,.13),'rune',None,13)
        w.gem((8+side*4.3,21,8),1,'rune',13)
    jewel(w,8,20,1.1,'metal','rune','light',depth=1.4)
    return w


def wand():
    w=weapon('varita_estallido','Varita del Estallido',[
        ('dark','302b41','s'),('metal','bd7347','s'),('wrap','6b3939','s'),
        ('red','fa6a5b','pulse'),('light','ffdb8b','spark'),('flow','ffac61','flow')])
    wrapped_grip(w,1,11,'dark','wrap','metal',1.35)
    w.shaft(10,18,'dark',1.5)
    for y in (12,16,18):ferrule(w,y,'metal',2.2)
    # Jaula abierta y nucleo flotante: la varita roja de doce elementos.
    for side in (-1,1):
        w.seg((8+side*1.4,17),45 if side==1 else 135,4,.65,'metal',z=(7.2,8.8))
        w.seg((8+side*4.2,20),90,3,.65,'dark',z=(7.2,8.8))
        w.gem((8+side*3.2,24,8),.6,'flow',14)
    w.gem((8,22,8),2.1,'red',14,tall=1.65)
    w.gem((8,26.2,8),.7,'light',15)
    return w


MODELS=[sword('espada_tormenta','Filo de la Tormenta','36516b','b7f3ff','59cfff'),
        sword('espada_sombras','Danza del Ender','423258','bc81ff','cf6aff',True),
        sword('espada_destello','Filo del Destello','217b7e','c4fff4','50ffd6'),quake(),wand()]


def assets():
    return export_assets(MODELS)


if __name__=='__main__':
    from pathlib import Path
    problems=check(MODELS)
    assert not problems, problems
    preview(str(Path(__file__).resolve().parent.parent/'build/previews/armas_especiales.gif'),MODELS,W=190)
