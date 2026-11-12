"""Llegadas del dueno: fuente unica para NPC, viajes, transiciones y auditoria.

Cumbre Y30 comprobada en el mapa local; Y52.7 no tiene piso en esas X/Z.
Las salidas usan Essentials spawn (spawn vigente del lobby), no coordenadas viejas.
"""
from santuario_azeroth import ARRIVAL, ARRIVAL_YAW

ROUTES = {
    'mina': [(10.5,-45,-124.5,0),(19.5,-39,-158.5,0),(43.5,-24,-201.5,0),(40.5,24,-225.5,0)],
    'bosque': [(1468.5,101,1570.5,0),(1603.7,100,1413.4,-177.9)],
    'tumba': [(-148.426,62,-97.473,0),(-203.163,88,203.533,0),(0.368,73,-44.104,0)],
    'cumbre': [(-25.6,33,-23.4,49.9),(-54.9,30,6.5,45.7)],
    'forja': [(23.2,13,-159.4,151.5),(-125.5,13,-125.7,-13.4),(0.8,47,26,-178.2)],
    'santuario': [(*ARRIVAL,ARRIVAL_YAW)],
}


def apply(dungeon):
    routes=ROUTES[dungeon['key']]
    if len(routes)!=len(dungeon['rooms']):
        raise ValueError('Cantidad de rutas distinta de salas: '+dungeon['key'])
    for room,route in zip(dungeon['rooms'],routes):
        room.update(llegada=route[:3],yaw=route[3])
