"""Tanda 3c: maquinas de Mini juegos y modelos 3D de los NPC. No ejecuta nada en el servidor."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
# Las dos maquinas abren el mismo panel que el aldeano de Mini juegos (astral_npc_parkour).
MAQUINAS = {'astral_maquina_arcade': ('pantalla', 'marquesina', 'neon', 'luces', 'botones'),
            'astral_maquina_capsulas': ('cupula', 'pomo')}
MENU_MINIJUEGOS = 'parkour'

# Que personaje 3D usa cada NPC (decision del dueno, plan seccion 8). Los que no figuran quedan como estan.
NPC_MODELOS = {
    'astral_npc_expediciones': 'mago', 'astral_npc_guia_expediciones': 'mago', 'astral_npc_guia_cavernas': 'mago',
    'astral_npc_guia_reino': 'mago', 'astral_npc_viajero': 'mago',
    'astral_npc_herrero': 'herrero', 'astral_npc_subastas': 'subastas', 'astral_npc_bazar': 'bazar',
    'astral_npc_cronista': 'cronista',
    'astral_npc_minas': 'minero', 'astral_npc_mina_viaje': 'minero', 'astral_npc_bosque_viaje': 'minero',
    'astral_npc_arena': 'caballero', 'astral_npc_portales': 'hechicero',
    'astral_npc_tienda': 'comerciante',
}
# Mazmorras: la entrada escondida usa la bruja y el guia del final el mago (Santuario tambien, 13/11).
MAZMORRAS = ('mina', 'bosque', 'tumba', 'cumbre', 'forja', 'santuario')
LUCES = {'mago': ('cristal',), 'bazar': ('farol',), 'minero': ('lampara', 'farol', 'oro'), 'hechicero': ('gema',),
         'bruja': ('gema',), 'comerciante': ('lentes',)}
PERSONAJES = ('mago', 'herrero', 'subastas', 'bazar', 'cronista', 'minero', 'caballero', 'hechicero', 'bruja', 'comerciante')


def npc_skills(mid, dungeon=None):
    """Lineas de Skills que ponen el modelo 3D sobre el aldeano (que sigue con sus clics de siempre)."""
    if dungeon is not None:
        if dungeon not in MAZMORRAS:
            return []
        model = 'bruja' if mid == 'entrada' else 'mago'
    else:
        model = NPC_MODELOS.get(mid)
    if not model:
        return []
    return [f'skill{{s=AST_NPC_{model}}} @self ~onSpawn', f'skill{{s=AST_NPC_{model}}} @self ~onLoad',
            'state{s=saludo} @self ~onInteract']


def machine(mid):
    return {'Type': 'VILLAGER', 'Display': '&a&lMini juegos', 'Health': 100,
            'Options': dict(NoAI=True, Invincible=True, Silent=True, Despawn=False, Persistent=True, Collidable=False,
                            NoGravity=True, PreventItemPickup=True, PreventOtherDrops=True, PreventRandomEquipment=True,
                            PreventSunburn=True, AlwaysShowName=True, Profession='NITWIT', VillagerType='PLAINS'),
            'Skills': ['cancelevent @self ~onInteract', 'cancelevent @self ~onDamaged',
                       f'skill{{s=AST_MODELO_{mid}}} @self ~onSpawn', f'skill{{s=AST_MODELO_{mid}}} @self ~onLoad',
                       f'command{{c="dm open {MENU_MINIJUEGOS} <trigger.name>"}} @self ~onInteract']}


def definitions():
    mobs, skills = {}, {}
    for mid, lit in MAQUINAS.items():
        mobs[mid] = machine(mid)
        # Pantallas y luces a brillo maximo (15/15), sin depender de la luz del lugar.
        skills['AST_MODELO_' + mid] = {'Skills': [f'model{{m={mid}}} @self'] +
                                       [f'brightness{{pid={part};b=15;s=15}} @self' for part in lit]}
    for model in PERSONAJES:
        skills['AST_NPC_' + model] = {'Skills': [f'model{{m=astral_npc_{model}}} @self'] +
                                      [f'brightness{{pid={part};b=15;s=15}} @self' for part in LUCES.get(model, ())]}
    return mobs, skills


def generate():
    mobs, skills = definitions()
    for sub, data in (('mobs', mobs), ('skills', skills)):
        dest = ROOT / 'build/mythicmobs' / sub / 'tanda3c.yml'
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text('# Generado por mobs/tanda3c.py\n' + yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=10000),
                        encoding='utf8')


if __name__ == '__main__':
    generate()
