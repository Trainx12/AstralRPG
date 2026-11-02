"""Mascotas con anatomia y detalles en relieve; 16 unidades = un bloque.

Se conservan nombres de huesos y animaciones para BetterModel/MythicMobs.
Ejecutar este modulo exporta las seis mascotas y build/previews/mascotas-3d.png.
"""
from bbmodel import Model, swing


def pair(m, bone, a, b, color, pat=None):
    for s in (-1, 1):
        x0, x1 = sorted((s * a[0], s * b[0]))
        m.cube(bone, (x0, a[1], a[2]), (x1, b[1], b[2]), color, pat=pat)


def eyes(m, y, z, x, color, side):
    # Iris frontal y lateral: la mirada se lee tambien desde el costado.
    pair(m, 'head', (x-.5, y-.45, z-.18), (x+.5, y+.45, z+.2), color)
    pair(m, 'head', (x-.12, y-.35, z-.3), (x+.12, y+.3, z-.18), '#151822')
    pair(m, 'head', (x-.3, y+.1, z-.35), (x-.08, y+.34, z-.3), '#ffffff')
    pair(m, 'head', (side, y-.4, z+.35), (side+.18, y+.4, z+1.15), color)
    pair(m, 'head', (side+.18, y-.28, z+.55), (side+.25, y+.28, z+.78), '#151822')


def canine(fox=False):
    pid = 'zorro' if fox else 'lobo'
    m = Model('astral_pet_' + pid)
    fur, dark, light = ('#addcf2', '#45678c', '#effaff') if fox else ('#7c8795', '#404c5e', '#dce2e4')
    h = 4.5 if fox else 5.5
    m.bone('body', (0, h, 0))
    m.blob('body', (0, h+1, .5), (2.1 if fox else 2.7, 2.1 if fox else 2.6, 4.4), fur, pat='fur', axis=2)
    m.blob('body', (0, h+.8, -2.9), (2.25 if fox else 2.9, 2.6, 2.1), light, pat='fur')
    m.blob('body', (0, h+1.8, -3.7), (1.9, 2.4, 1.8), fur, pat='fur')
    # Escapulas, muslos y pies separados de la cana de cada pata.
    legs = []
    for n, x, z in (('leg_fl',-1.6,-2.8), ('leg_fr',1.6,-2.8), ('leg_bl',-1.6,3.1), ('leg_br',1.6,3.1)):
        m.bone(n, (x,h-.2,z), 'body'); legs.append(n)
        m.blob(n, (x,h-.9,z+.15), (1 if fox else 1.3,1.7,1.4), fur, pat='fur', levels=2)
        m.rcube(n, (x-.65,.7,z-.6), (x+.65,h-1,z+.6), dark, r=.3, pat='fur')
        m.rcube(n, (x-.85,0,z-1.2), (x+.85,1.25,z+.65), dark if fox else light, r=.35, pat='fur')
        for dx in (-.45,0,.45):
            m.cube(n, (x+dx-.1,.15,z-1.38), (x+dx+.1,.48,z-1.12), '#b6d9ef' if fox else '#3c4652')
    m.bone('head', (0,h+2,-4), 'body')
    m.blob('head', (0,h+2.7,-5.7), (2.15 if fox else 2.55,2,2.15), fur, pat='fur')
    # Mejillas abiertas, mandibula inferior, hocico que se afina y nariz humeda.
    pair(m,'head',(1.4,h+1.4,-6.3),(2.9 if fox else 3.2,h+2.5,-4.3),light,'fur')
    pair(m,'head',(2,h+1.2,-5.1),(2.6,h+2,-3.5),fur,'fur')
    m.rcube('head',(-1.3,h+.8,-8.9),(1.3,h+1.5,-6),light,r=.3,pat='fur')
    m.rcube('head',(-1.25,h+1.5,-8.7),(1.25,h+2.6,-6.2),light,r=.4,pat='fur')
    m.rcube('head',(-.7,h+2,-9.25),(.7,h+2.7,-8.6),dark,r=.2)
    m.cube('head',(-.3,h+2.5,-9.29),(.1,h+2.65,-9.25),'#b8c9da')
    eyes(m,h+3,-7.55,1.35,'#7be5ff' if fox else '#efc15d',2.15)
    pair(m,'head',(.8,h+3.55,-7.6),(2,h+3.85,-6.6),dark,'fur')
    for s in (-1,1):
        x = s*1.5
        # Tres escalones estrechan la oreja hasta una punta real.
        for k,w in enumerate((.95,.65,.3)):
            y=h+4+k*(1.1 if fox else .85)
            m.rcube('head',(x-w,y,-6),(x+w,y+1.1,-4.65),fur,r=.15,pat='fur')
        m.cube('head',(x-.45,h+4.25,-6.05),(x+.45,h+5.3,-5.9),'#719bc5' if fox else '#c8aba7')
    # Mechones del collar, sin collar artificial.
    for x in (-1.4,0,1.4):
        m.cube('body',(x-.45,h-1,-4.25),(x+.45,h+.6,-3.4),light,pat='fur')
    tail_angle=-10 if fox else 20
    m.bone('tail',(0,h+1,4),'body',rotation=(tail_angle,0,0))
    for k,(z,rx,ry) in enumerate(((4.8,1,1),(6.3,1.65,1.55),(8.1,2.05 if fox else 1.4,1.8 if fox else 1.3),(9.8,1.6 if fox else .95,1.4),(11.1,.85,.85))):
        m.blob('tail',(0,h+1,z),(rx,ry,1.5),light if k>=3 else fur,pat='fur',axis=2,levels=2)
    m.anim('walk',.6,{**{b:{'rotation':(swing(32,1.667,0 if i in (0,3) else 180),0,0)} for i,b in enumerate(legs)},'tail':{'rotation':(tail_angle,swing(18,1.667),0)}})
    m.anim('idle',2,{'tail':{'rotation':(tail_angle,swing(16,.5),0)},'head':{'rotation':(swing(3,.5),swing(9,.5),0)}})
    return m


def mascota_lobo(): return canine()
def mascota_zorro(): return canine(True)


def mascota_golem():
    m=Model('astral_pet_golem')
    m.bone('body',(0,5,0))
    m.blob('body',(0,7.5,0),(3.8,3.6,2.65),'#79878a',pat='stone')
    m.rcube('body',(-3.3,8,-3),(3.3,10,-2),'#a6b0aa',r=.4,pat='stone')
    # Nucleo hundido en su marco y cristal de varios volumenes.
    m.rcube('body',(-1.8,5.5,-2.95),(1.8,8.7,-2.3),'#364855',r=.4,pat='stone')
    m.blob('body',(0,7.2,-3.05),(1.2,1.35,.6),'#59b8df',levels=2)
    m.cube('body',(-.35,6.7,-3.7),(.35,7.9,-3.5),'#c4faff')
    m.bone('head',(0,10,0),'body')
    m.rcube('head',(-2.55,10,-2.1),(2.55,14,2.2),'#9ca8a6',r=.7,pat='stone')
    pair(m,'head',(.4,11.6,-2.3),(1.8,12.25,-2.05),'#7de4ff')
    pair(m,'head',(.2,12.35,-2.5),(2.3,13,-1.8),'#5b6b70','stone')
    m.rcube('head',(-1.6,10,-2.4),(1.6,10.7,-1.6),'#647479',r=.2,pat='stone')
    for n,s in (('arm_l',1),('arm_r',-1)):
        x=4.1*s;m.bone(n,(x,9,0),'body')
        m.blob(n,(x,9,0),(2,1.9,2.15),'#9aa39d',pat='stone',levels=2)
        m.rcube(n,(x-1.1,4,-1.25),(x+1.1,8.7,1.3),'#63747a',r=.4,pat='stone')
        m.rcube(n,(x-1.5,2.5,-1.7),(x+1.5,5.4,1.4),'#89958f',r=.5,pat='stone')
        for dx in (-.85,0,.85):
            m.cube(n,(x+dx-.27,2.7,-1.95),(x+dx+.27,3.6,-1.6),'#52636a',pat='stone')
        m.cube(n,(x-.18,6,-1.35),(x+.18,7.9,-1.25),'#6ddcf2')
    for n,x in (('leg_l',-1.8),('leg_r',1.8)):
        m.bone(n,(x,4,0),'body')
        m.rcube(n,(x-1.3,.5,-1.4),(x+1.3,4.6,1.4),'#65767a',r=.4,pat='stone')
        m.rcube(n,(x-1.5,0,-2),(x+1.5,1.4,1.4),'#929f98',r=.4,pat='stone')
        m.cube(n,(x-.8,2,-1.6),(x+.8,3.5,-1.3),'#a7b1aa',pat='stone')
    for bone,a,b in [('head',(-2,13.8,-1),(0,14.35,1)),('head',(.4,13.8,.3),(1.8,14.25,1.7)),('arm_l',(3,10,-1),(5.2,10.8,.8)),('body',(-3,5,1.6),(-1.8,7,2.55))]:
        m.rcube(bone,a,b,'#597c49',r=.15,pat='fur')
    # Grietas en relieve oscuro y pequeñas vetas azules.
    for x,y in ((-2.6,7),(2.5,5.8),(-1.9,13)):
        bone='head' if y>11 else 'body';z=-2.15 if bone=='head' else -2.65
        m.cube(bone,(x,y,z-.15),(x+.18,y+.9,z),'#3d5158')
        m.cube(bone,(x,y+.7,z-.15),(x+.65,y+.88,z),'#3d5158')
    m.anim('walk',.8,{n:{'rotation':(swing(22,1.25,180 if n in ('leg_r','arm_l') else 0),0,0)} for n in ('leg_l','leg_r','arm_l','arm_r')})
    m.anim('idle',3,{'head':{'rotation':(0,swing(10,.333),0)},'body':{'position':(0,swing(.2,.333),0)}})
    return m


def bird(fire=False):
    m=Model('astral_pet_fenix' if fire else 'astral_pet_cuervo')
    h=11 if fire else 10
    col,dark,light=('#ed6a24','#a92d25','#ffd05b') if fire else ('#272d49','#151c30','#536281')
    m.bone('body',(0,h,0))
    m.blob('body',(0,h+1,0),(2.5,2.8,3.7),col,pat='feather',axis=2)
    m.blob('body',(0,h+.5,-1.5),(2,2.35,2.4),light if fire else '#35405c',pat='feather')
    m.blob('body',(0,h+3,-2.7),(1.55,2,1.6),col,pat='feather')
    m.bone('head',(0,h+3,-2.5),'body')
    m.blob('head',(0,h+4.6,-3.9),(1.95,1.9,1.9),col,pat='feather')
    # Pico largo de cuervo / pico curvado de rapaz para el fenix.
    beak='#eeb343' if fire else '#495466'
    m.rcube('head',(-.85,h+3.6,-7.1),(.85,h+4.65,-5.2),beak,r=.25)
    m.cube('head',(-.5,h+3.25,-7.65),(.5,h+4.15,-6.6),beak)
    m.cube('head',(-.6,h+3.55,-7.2),(.6,h+3.7,-5.4),dark)
    eyes(m,h+4.9,-5.45,1.15,'#fff0ab' if fire else '#b993ff',1.7)
    pair(m,'head',(.6,h+5.45,-5.5),(1.8,h+5.75,-4.65),dark,'feather')
    # Garganta con plumas y cresta dirigida hacia atras.
    for k in range(3):
        pair(m,'head',(.4+k*.4,h+2.5-k*.2,-4.5),(.9+k*.4,h+3.5,-3.2),light if fire else col,'feather')
        if fire:
            m.cube('head',(-.38,h+6,-4.8+k*1.15),(.38,h+8-k*.35,-4+k*1.15),light,rotation=(-20,0,0),pat='feather')
    for n,s in (('wing_l',1),('wing_r',-1)):
        m.bone(n,(s*2,h+2,0),'body')
        m.blob(n,(s*3.3,h+2,0),(2,1.1,2.65),col,pat='feather',axis=0,levels=2)
        for k in range(6):
            # Cada remera tiene cana, punta afinada y un perfil distinto.
            x=3.8+k*.95;z=-1.8+k*.65;length=4.2-k*.3
            a,b=sorted((s*x,s*(x+1.1)))
            m.rcube(n,(a,h+1.5-k*.1,z),(b,h+2.2-k*.1,z+length),dark if k%2 else col,r=.2,pat='feather')
            m.cube(n,(a+.15,h+2.21-k*.1,z+.3),(b-.15,h+2.35-k*.1,z+length-.6),light,pat='feather')
            m.cube(n,(a+.2,h+1.5-k*.1,z+length-.2),(b-.2,h+2-k*.1,z+length+.65),light if fire else dark,pat='feather')
        for k in range(3):
            a,b=sorted((s*(2.2+k*1.5),s*(3.9+k*1.5)))
            m.rcube(n,(a,h+2.2,-1.7+k*.3),(b,h+2.8,.7+k*.4),col,r=.2,pat='feather')
    m.bone('tail',(0,h,3),'body')
    for k,x in enumerate((-1.4,-.7,0,.7,1.4)):
        end=9+(3-abs(k-2)*1.4 if fire else -abs(k-2)*.6)
        m.rcube('tail',(x-.4,h-.3,2.7),(x+.4,h+.5,end),col,r=.15,pat='feather')
        m.cube('tail',(x-.26,h+.51,4),(x+.26,h+.7,end-.7),light,pat='feather')
        if fire:
            m.rcube('tail',(x-.65,h-.2,end-1),(x+.65,h+.55,end+.7),'#ffac36',r=.2,pat='feather')
            m.cube('tail',(x-.25,h+.1,end+.4),(x+.25,h+.5,end+1.8),'#ffe6a0')
    for x in (-1,1):
        m.cube('body',(x-.24,h-2.2,-.3),(x+.24,h-.5,.25),beak)
        for dx in (-.4,0,.4):
            m.cube('body',(x+dx-.12,h-2.5,-1.25),(x+dx+.12,h-2.15,.2),beak)
    flap={'wing_l':{'rotation':(0,0,swing(28,2))},'wing_r':{'rotation':(0,0,swing(-28,2))},'body':{'position':(0,swing(.55,2),0)}}
    m.anim('walk',.5,flap)
    m.anim('idle',2,{**flap,'head':{'rotation':(0,swing(12,.5),0)},'tail':{'rotation':(swing(5,.5),0,0)}})
    return m


def mascota_cuervo(): return bird()
def mascota_fenix(): return bird(True)


def mascota_dragon():
    m=Model('astral_pet_dragon');h=9
    m.bone('body',(0,h,0))
    m.blob('body',(0,h+1,0),(2.9,2.9,4.3),'#c63d36',pat='scale',axis=2)
    m.blob('body',(0,h+.1,-.5),(2.15,2.25,3.4),'#e6ad55',pat='scale',axis=2)
    for z in (-2,-.5,1,2.5):
        m.rcube('body',(-1.6,h-1.8,z-.4),(1.6,h-1.35,z+.5),'#f8cf78',r=.15,pat='scale')
        m.cube('body',(-.4,h+3.1,z),(.4,h+4.5,z+.8),'#efba65',pat='scale')
    m.blob('body',(0,h+3,-3),(1.9,2.4,1.8),'#cf4a3f',pat='scale')
    m.bone('head',(0,h+3,-3.5),'body')
    m.blob('head',(0,h+4.2,-5.4),(2.5,2.1,2.4),'#e45b49',pat='scale')
    m.rcube('head',(-1.6,h+2.1,-9.2),(1.6,h+3.4,-6),'#d95141',r=.4,pat='scale')
    m.rcube('head',(-1.35,h+1.8,-9),(1.35,h+2.2,-6),'#edbd73',r=.2,pat='scale')
    pair(m,'head',(.7,h+3.35,-8.8),(1.15,h+3.55,-8.2),'#572a2d')
    eyes(m,h+4.6,-7.35,1.4,'#ffe379',2.25)
    pair(m,'head',(.8,h+5.15,-7.5),(2.2,h+5.6,-6.3),'#a83234','scale')
    for s in (-1,1):
        for k in range(3):
            x=s*(1.7+k*.3)
            m.rcube('head',(x-.45+k*.09,h+5.5+k*.85,-5+k*.5),(x+.45-k*.09,h+6.6+k*.85,-3.9+k*.5),'#f1d6a0',r=.12)
        for z in (-6,-4.7):
            a,b=sorted((s*2,s*3.3))
            m.cube('head',(a,h+2.9,z),(b,h+3.8,z+.6),'#ba3936',pat='scale')
    pair(m,'head',(.8,h+1.9,-8.1),(1.1,h+2.55,-7.7),'#fff1cd')
    for n,s in (('wing_l',1),('wing_r',-1)):
        m.bone(n,(s*2.4,h+2,0),'body')
        # Membrana en abanico: segmentos escalonados entre dedos, con grosor.
        for k in range(6):
            x=2.3+k*1.15;a,b=sorted((s*x,s*(x+1.3)))
            m.cube(n,(a,h+2+k*.23,-1+k*.22),(b,h+2.5+k*.23,4.6-k*.45),'#a52c39' if k%2 else '#ba3a43',pat='membrane')
            m.rcube(n,(a,h+2.45+k*.23,-1+k*.22),(b,h+2.95+k*.23,-.45+k*.22),'#e8ae65',r=.15,pat='scale')
        for k in (0,2,4):
            a,b=sorted((s*(3+k*1.1),s*(3.3+k*1.1)))
            m.cube(n,(a,h+2.7+k*.23,-.5+k*.22),(b,h+3+k*.23,4.3-k*.45),'#e8ae65')
        a,b=sorted((s*8.7,s*9.2))
        m.cube(n,(a,h+3.2,-.1),(b,h+4.4,.5),'#fff1cd')
    m.bone('tail',(0,h,4),'body')
    for k in range(6):
        r=1.3-k*.18;z=4.5+k*1.45
        m.blob('tail',(.15*k,h-k*.12,z),(r,r,1.1),'#c63d36',pat='scale',axis=2,levels=2)
        m.cube('tail',(.15*k-.2,h+r-k*.12,z-.3),(.15*k+.2,h+r+.7-k*.12,z+.3),'#edba65')
    m.rcube('tail',(-.1,h-.9,11.9),(1.6,h+.1,13.7),'#f2c878',r=.3,pat='scale')
    for x in (-1.8,1.8):
        for z in (-1.8,2.4):
            m.blob('body',(x,h-1.7,z),(.9,1.4,1.1),'#b43634',pat='scale',levels=2)
            m.rcube('body',(x-.8,h-3,z-1),(x+.8,h-2,z+.8),'#d95742',r=.25,pat='scale')
            for dx in (-.5,0,.5):
                m.cube('body',(x+dx-.13,h-3,z-1.45),(x+dx+.13,h-2.65,z-.9),'#fff1cd')
    flap={'wing_l':{'rotation':(0,0,swing(26,2.5))},'wing_r':{'rotation':(0,0,swing(-26,2.5))},'body':{'position':(0,swing(.6,1.25),0)},'tail':{'rotation':(0,swing(13,1.25),0)}}
    m.anim('walk',.8,flap)
    m.anim('idle',1.6,{**flap,'head':{'rotation':(swing(4,.625),swing(10,.625),0)}})
    return m


MASCOTAS=[mascota_lobo,mascota_cuervo,mascota_golem,mascota_zorro,mascota_dragon,mascota_fenix]


def main():
    from pathlib import Path
    from PIL import Image, ImageDraw, ImageFont
    from bbmodel import save
    from build_models import preview3d
    root=Path(__file__).resolve().parents[2]/'build'
    (root/'models').mkdir(parents=True,exist_ok=True)
    (root/'previews').mkdir(parents=True,exist_ok=True)
    sheet=Image.new('RGB',(1440,760),'#111c2c')
    d=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=20)
    for i,fn in enumerate(MASCOTAS):
        m=fn();texture=save(m,str(root/'models'/f'{m.name}.bbmodel'))
        x=(i%3)*480;y=(i//3)*380
        d.rounded_rectangle((x+8,y+8,x+472,y+372),12,fill='#1c2b3b',outline='#516277')
        d.text((x+24,y+22),m.name.removeprefix('astral_pet_').upper(),font=font,fill='#f2d69c')
        for j,yaw in enumerate((35,215)):
            im=preview3d(m,texture,yaw=yaw,pitch=18,scale=10,background=(0,0,0,0))
            ratio=min(218/im.width,290/im.height)
            im=im.resize((round(im.width*ratio),round(im.height*ratio)),Image.Resampling.NEAREST)
            sheet.paste(im,(x+18+j*226+(218-im.width)//2,y+65+(290-im.height)//2),im)
        print(f'{m.name}: {len(m.cubes)} piezas')
    sheet.save(root/'previews/mascotas-3d.png')


if __name__=='__main__':main()
