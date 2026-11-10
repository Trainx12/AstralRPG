"""Geometria y texturas originales: piedra labrada y flora del Bosque."""
from bbmodel import Model, swing as _swing


def swing(amp, speed=1, phase=0):
    # BetterModel rechaza literales Molang con demasiados decimales.
    return _swing(amp, round(speed, 4), phase)


def flor(m, bone, x, y, z, color):
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        m.cube(bone, (x+dx-.5, y+dy-.5, z-.4), (x+dx+.5, y+dy+.5, z), color)
    m.cube(bone, (x-.4, y-.4, z-.6), (x+.4, y+.4, z-.3), '#F4CE51')


def coloso():
    m = Model('astral_coloso_musgoso')
    m.bone('body', (0, 20, 0))
    stone, edge, dark = '#B5BAB6', '#D2D4C6', '#5E686C'

    def slab(b, a, c):
        m.cube(b, a, c, stone, pat='brick')
        # Marco labrado y recuadro hundido, con juntas propias.
        x,y,z = a; X,Y,Z = c
        m.cube(b, (x+.8,y+.8,z-.25), (X-.8,Y-.8,z), dark, pat='stone')
        m.cube(b, (x+1.6,y+1.6,z-.5), (X-1.6,Y-1.6,z-.25), stone, pat='brick')
        m.cube(b, (x,y,z-.65), (X,y+.8,z), edge)
        m.cube(b, (x,Y-.8,z-.65), (X,Y,z), edge)

    slab('body', (-10,16,-6), (10,31,6))
    slab('body', (-11,12,-6.5), (11,17,6.5))
    for name, x in (('leg_l',-6),('leg_r',6)):
        m.bone(name,(x,13,0),'body')
        slab(name,(x-4,1,-5),(x+4,13,5))
        m.cube(name,(x-4.7,0,-6),(x+4.7,2,5.5),edge,pat='stone')
    m.bone('head',(0,30,0),'body')
    slab('head',(-7,30,-6),(7,39,5))
    # Una sola cuenca iluminada y gema vertical en la frente.
    m.cube('head',(-5.7,34,-6.7),(5.7,36,-6.1),dark)
    m.cube('head',(2,34,-7),(4.7,36,-6.6),'#3FD9C2')
    m.cube('head',(2.5,35,-7.2),(3.3,35.8,-7),'#ACFFF0')
    slab('head',(-2.7,37,-7),(2.7,46,-2))
    m.cube('head',(-1.2,39,-7.6),(1.2,44.5,-7),'#3FD9C2')
    m.cube('head',(-.9,40,-7.8),(-.3,44,-7.6),'#A3F7D8')
    # Corona asimetrica, puntas altas, hueco entre los dos brazos de piedra.
    for x,h in ((-7,46),(5,48)):
        slab('head',(x,38,-1),(x+2,h,3))
    m.cube('head',(-7,45,-1),(0,47,3),stone,pat='brick')
    m.cube('head',(5,46,-1),(10,48,3),stone,pat='brick')
    for name,x,raised in (('arm_l',-15,True),('arm_r',15,False)):
        m.bone(name,(x,29,0),'body')
        lo,hi=(27,42) if raised else (14,29)
        slab(name,(x-4,lo,-4.5),(x+4,hi,4.5))
        slab(name,(x-4.5,lo-5,-5),(x+4.5,lo,5))
        for yy in (lo,lo+5,hi-1):
            m.cube(name,(x-4.4,yy,-5),(x+4.4,yy+1,5),edge)
        # Raiz enroscada: tramos que recorren frente, lateral y dorso.
        for j in range(7):
            yy=lo+j*2
            side=(-1 if j%2 else 1)
            m.cube(name,(x-4,yy,-5.7),(x+2,yy+1.4,-4.8),'#705139',pat='wood')
            xx=x+side*3.6
            m.cube(name,(xx,yy, -4.8),(xx+1,yy+3,4.7),'#705139',pat='wood')
        m.cube(name,(x-4.8,hi-3,-5.5),(x+4.8,hi+1,4),'#657627',pat='stone')
        flor(m,name,x+1,lo+2,-5.8,'#EFCB36')
    # Musgo de volumen irregular y lianas independientes sobre pecho/cintura.
    for i,(x,y,w,h) in enumerate(((-10,28,7,4),(4,28,7,4),(-9,23,4,6),(5,18,5,5),
                                  (-10,12,7,6),(3,10,7,8),(-8,6,3,5),(7,4,3,5))):
        bone='body' if y>=10 else ('leg_l' if x<0 else 'leg_r')
        m.cube(bone,(x,y,-7.4),(x+w,y+h,-6.4),['#68792B','#7B8A32','#536326'][i%3],pat='stone')
        for j in range(2):
            xx=x+1+j*2
            m.cube(bone,(xx,y-3-j,-7.8),(xx+.9,y+2,-7.1),'#82702F',pat='wood')
            m.cube(bone,(xx+.4,y-1-j,-8),(xx+1.8,y+.2-j,-7.6),'#6B8235')
    for x,y,z in ((-7,28,-8),(7,21,-8),(5,14,-8),(-9,11,-8)):
        flor(m,'body',x,y,z,'#F0CC38')
    # Raices marrones de la corona, hombros y espalda.
    for x,y,z in ((-5,39,3),(6,41,3),(-10,28,5),(8,25,6),(-8,16,6),(8,14,6)):
        b='head' if y>35 else 'body'
        m.cube(b,(x,y-8,z),(x+1.2,y+2,z+1.2),'#70513B',pat='wood')
        m.cube(b,(x-1,y-4,z-.3),(x+2,y-2,z+1.5),'#748039',pat='stone')
    m.anim('idle',3,{'body':{'position':(0,swing(.25,1/3),0)}})
    m.anim('walk',1.4,{b:{'rotation':(swing(a,1/1.4),0,0)} for b,a in
                      (('leg_l',18),('leg_r',-18),('arm_l',-10),('arm_r',10))})
    m.anim('attack',.8,{'arm_l':{'rotation':(swing(-65,.625),0,0)},
                          'arm_r':{'rotation':(swing(-75,.625),0,0)},
                          'body':{'rotation':(swing(12,.625),0,0)}},loop='once')
    return m


def planta():
    m=Model('astral_bosque_planta')
    m.bone('root',(0,0,0))
    m.cube('root',(-4,0,-4),(4,5,4),'#425022',pat='wood')
    for x,z,rot in ((-5,0,0),(4,1,0),(0,-5,90),(1,4,90)):
        m.cube('root',(x-2,0,z-1),(x+2,2,z+1),'#5E6430',rotation=(0,rot,0),pat='wood')
        flor(m,'root',x,2,z-1.4,'#CD4A8A')
    m.bone('stem',(0,4,0),'root')
    for x,y,z in ((0,3,0),(-1,8,0),(-2,13,0)):
        m.cube('stem',(x-2,y,z-2),(x+2,y+6,z+2),'#8D952F',pat='wood')
        m.cube('stem',(x-2.3,y+1,z-2.3),(x-1.3,y+5,z-2),'#59651E')
    m.bone('head',(-2,18,0),'stem')
    # Paladar abierto: volumen verde arriba, cavidad roja y lengua adelantada abajo.
    m.cube('head',(-7,18,-6),(5,21,3),'#4B601E',pat='scale')
    m.cube('head',(-6.5,17.6,-6),(4.5,18,1),'#731E28')
    m.cube('head',(-7.5,20.5,-6.5),(5.5,22,3.5),'#67762A',pat='scale')
    m.bone('jaw',(-2,16,2),'head',rotation=(-28,0,0))
    m.cube('jaw',(-7,13,-7),(5,15,3),'#4A5B1F',pat='scale')
    m.cube('jaw',(-6,15,-6),(4,15.6,2),'#BA303C')
    m.cube('jaw',(-3,15.6,-7),(.5,16.2,-1),'#F14A59')
    # Dientes intercalados arriba y abajo, sin tapar la apertura.
    for x in (-6,-3,0,3):
        m.cube('head',(x,15.4,-6),(x+1.2,18,-4.8),'#ABB849')
        m.cube('jaw',(x+.5,15,-6),(x+1.6,17,-5),'#B8BE52')
    for x in (-6.7,3.7):
        for z in (-2,1): m.cube('head',(x,16,z),(x+1.1,18.2,z+1),'#9BA936')
    # Dos capullos laterales y uno alto, cada uno con espiral original en relieve.
    for i,(x,y,z,sz) in enumerate(((-8,18,2,3.3),(1,24,3,3.5),(4,16,4,2.5))):
        b=f'bud{i}'; m.bone(b,(x,y-3,z),'stem')
        m.cube(b,(x-1,y-5,z-1),(x+1,y,z+1),'#62752D')
        m.cube(b,(x-sz,y-3,z-2),(x+sz,y+3,z+2),'#A32B71',pat='cloth')
        m.cube(b,(x-sz-.3,y+2.5,z-2.4),(x+sz+.3,y+3.3,z+2.3),'#DA528E')
        # Espiral cuadrada: contorno abierto hacia el centro, no textura copiada.
        for a,c in (((x-2.5,y-2,z-2.5),(x-1.5,y+2,z-2)),
                    ((x-2.5,y+1,z-2.5),(x+2,y+2,z-2)),
                    ((x+1,y-1.5,z-2.5),(x+2,y+2,z-2)),
                    ((x-.5,y-1.5,z-2.5),(x+2,y-.5,z-2)),
                    ((x-.5,y-1.5,z-2.5),(x+.5,y+.5,z-2))):
            m.cube(b,a,c,'#662151')
    # Hojas turquesa grandes, escalonadas y con nervadura clara.
    for i,(x,y,z,angle) in enumerate(((-7,24,4,-35),(6,24,5,35),(-6,12,-1,-50),(5,13,2,50))):
        b='stem'; org=(x,y,z)
        m.cube(b,(x-2,y-4,z),(x+2,y+4,z+1),'#339B96',rotation=(0,0,angle),origin=org,pat='scale')
        m.cube(b,(x-1,y-5,z),(x+1,y+5,z+1),'#56B8AC',rotation=(0,0,angle),origin=org)
        m.cube(b,(x-.3,y-4,z-.3),(x+.3,y+4,z),'#257D7D',rotation=(0,0,angle),origin=org)
    m.anim('idle',3,{'stem':{'rotation':(0,0,swing(4,1/3))},
                     'head':{'rotation':(swing(3,1/3),0,0)}})
    m.anim('attack',.6,{'head':{'position':(0,0,swing(-3,1/.6)),
                                     'rotation':(swing(18,1/.6),0,0)},
                         'jaw':{'rotation':(swing(30,1/1.2),0,0)}},loop='once')
    m.anim('spit',.8,{'head':{'rotation':(swing(-20,1/.8),0,0)},
                      'stem':{'rotation':(swing(-8,1/.8),0,0)}},loop='once')
    return m
