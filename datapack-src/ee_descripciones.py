"""Descripciones en espanol de ExcellentEnchants (las que se ven en armas, armaduras y libros).

Toma las configs del server (plugins/ExcellentEnchants/enchants/*.yml, bajadas a una carpeta local),
cambia SOLO las lineas de `Description:` y deja todo lo demas igual (valores, comentarios).
Conserva los numeros de ExcellentEnchants (%...%), asi siempre coinciden con su config.

  python ee_descripciones.py <carpeta con los .yml del server>  -> build/excellentenchants/enchants/*.yml
Despues: subirlos a plugins/ExcellentEnchants/enchants/ y REINICIAR (EE no las toma con reload).
Con --config <config.yml del server> tambien arma build/excellentenchants/config.yml con su tooltip apagado
(la lista estilo Hypixel la hace AstralMesa).
"""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build' / 'excellentenchants' / 'enchants'

CH = '%enchantment_trigger_chance%%'          # "25%"
POC = '%enchantment_potion_level% (%enchantment_potion_duration% s)'  # "II (5 s)"
C = '❤'

ES = {
    'auto_reel': 'Recoge la caña sola cuando pica un pez.',
    'bane_of_netherspawn': f'Hace %damage%{C} más de daño a mobs del Nether.',
    'blast_mining': f'{CH} de chance de picar con una explosión.',
    'blindness': f'{CH} de chance de dejar ciego al enemigo {POC} al golpear.',
    'bomber': f'{CH} de chance de disparar una TNT que explota en %time% s.',
    'cold_steel': f'{CH} de chance de dar fatiga de minado {POC} a quien te pega.',
    'confusing_arrows': f'{CH} de chance de que la flecha dé náusea {POC}.',
    'confusion': f'{CH} de chance de dar náusea {POC} al golpear.',
    'cure': f'{CH} de chance de curar piglins zombi y aldeanos zombi al golpearlos.',
    'curse_of_breaking': f'Maldición: {CH} de chance de gastar %amount% de durabilidad de más.',
    'curse_of_death': 'Maldición: al matar a un jugador podés morir vos también.',
    'curse_of_drowned': f'Maldición: {CH} de chance de pescar un ahogado.',
    'curse_of_fragility': 'Maldición: no se puede usar en yunque ni piedra de afilar.',
    'curse_of_mediocrity': f'Maldición: {CH} de chance de que lo que sueltan salga sin encantar.',
    'curse_of_misfortune': f'Maldición: {CH} de chance de que bloques y mobs no suelten nada.',
    'cutter': f'{CH} de chance de sacarle una pieza de armadura al enemigo y dañarla un %damage%%.',
    'darkness_arrows': f'{CH} de chance de que la flecha dé oscuridad {POC}.',
    'darkness_cloak': f'{CH} de chance de dar oscuridad {POC} a quien te pega.',
    'decapitator': f'{CH} de chance de que el jugador o mob suelte su cabeza.',
    'double_catch': f'{CH} de chance de pescar el doble.',
    'double_strike': f'{CH} de chance de hacer doble daño.',
    'dragon_heart': 'Te da absorción %enchantment_potion_level% todo el tiempo.',
    'dragonfire_arrows': f'{CH} de chance de que la flecha deje fuego de dragón (radio %radius%, %duration% s).',
    'electrified_arrows': f'{CH} de chance de que la flecha llame un rayo con %damage%{C} de daño extra.',
    'elemental_protection': 'Reduce un %amount%% el daño de pociones y elementos.',
    'ender_bow': 'Dispara perlas de ender en vez de flechas.',
    'exhaust': f'{CH} de chance de dar hambre {POC} al golpear.',
    'explosive_arrows': f'{CH} de chance de disparar una flecha explosiva.',
    'fire_shield': f'{CH} de chance de prender fuego %duration% s a quien te pega.',
    'flame_walker': 'Caminás sobre lava y el magma no te hace daño.',
    'flare': f'{CH} de chance de poner una antorcha donde cae la flecha.',
    'ghast': 'Dispara bolas de fuego en vez de flechas.',
    'glassbreaker': 'Rompe el vidrio al instante.',
    'hardened': f'{CH} de chance de ganar resistencia {POC} al recibir daño.',
    'haste': 'Te da prisa minera %enchantment_potion_level% mientras picás.',
    'hover': f'{CH} de chance de que la flecha dé levitación {POC}.',
    'ice_aspect': f'Congela y da lentitud {POC} al golpear.',
    'ice_shield': f'{CH} de chance de congelar y dar lentitud {POC} a quien te pega.',
    'infernus': 'El tridente prende fuego %time% s al enemigo que toca.',
    'jumping': 'Salto %enchantment_potion_level% todo el tiempo.',
    'kamikadze': f'{CH} de chance de explotar al morir.',
    'lightweight': 'Podés pisar huevos de tortuga, cultivos y hojas goteantes sin romperlos.',
    'lingering': f'{CH} de chance de que las flechas con poción dejen una nube del efecto.',
    'lucky_miner': f'{CH} de chance de ganar un %amount%% más de XP de los minerales.',
    'night_vision': 'Visión nocturna todo el tiempo.',
    'nimble': 'Lo que sueltan los mobs va directo a tu inventario.',
    'paralyze': f'{CH} de chance de dar fatiga de minado {POC} al golpear.',
    'poisoned_arrows': f'{CH} de chance de que la flecha envenene {POC}.',
    'rage': f'{CH} de chance de ganar fuerza {POC} al golpear.',
    'rebound': 'Rebotás al caer, como sobre un bloque de slime.',
    'regrowth': f'Te cura %amount%{C} cada algunos segundos.',
    'replanter': 'Vuelve a plantar los cultivos al cosecharlos o con clic derecho.',
    'restore': f'{CH} de chance de salvar el objeto cuando se rompe (vuelve al %amount%%).',
    'river_master': 'Tirás la caña más lejos.',
    'rocket': f'{CH} de chance de lanzar al enemigo por el aire.',
    'saturation': 'Te llena %amount% de comida cada algunos segundos.',
    'seasoned_angler': 'Ganás un %amount%% más de XP pescando.',
    'silk_chest': 'Los cofres salen enteros con todo lo que tienen adentro.',
    'silk_spawner': f'{CH} de chance de llevarte el generador de mobs.',
    'smelter': f'{CH} de chance de que lo que picás salga ya fundido.',
    'sniper': 'Las flechas vuelan un %amount%% más rápido.',
    'soulbound': 'No se te cae al morir.',
    'speed': 'Velocidad %enchantment_potion_level% todo el tiempo.',
    'stopping_force': f'{CH} de chance de recibir un %amount%% menos de empuje.',
    'survivalist': 'Los pescados salen ya cocinados.',
    'swiper': f'{CH} de chance de robarle %amount% de XP a los jugadores.',
    'telekinesis': 'Lo que picás va directo a tu inventario.',
    'temper': f'Hace un %amount%% más de daño por cada %radius%{C} de vida que te falta.',
    'thrifty': f'{CH} de chance de que los mobs suelten su huevo.',
    'thunder': f'{CH} de chance de llamar un rayo con %damage%{C} de daño extra.',
    'treefeller': 'Tala el árbol entero de un golpe.',
    'tunnel': 'Pica varios bloques a la vez.',
    'vampire': f'{CH} de chance de curarte %amount%{C} al golpear.',
    'vampiric_arrows': f'{CH} de chance de curarte %amount%{C} cuando la flecha pega.',
    'veinminer': 'Pica hasta %amount% bloques de la veta de una.',
    'venom': f'{CH} de chance de envenenar {POC} al golpear.',
    'village_defender': f'Hace %amount%{C} más de daño a los saqueadores.',
    'water_breathing': 'Respirás bajo el agua todo el tiempo.',
    'wisdom': 'Los mobs sueltan x%modifier% de XP.',
    'wither': f'{CH} de chance de dar wither {POC} al golpear.',
    'withered_arrows': f'{CH} de chance de que la flecha dé wither {POC}.',
}

PH = re.compile(r'%[a-z_]+%')
BLOQUE = re.compile(r'(^  Description:\r?\n)((?:  - .*\r?\n)+)', re.M)


def traducir(texto, clave):
    nl = '\r\n' if '\r\n' in texto else '\n'
    m = BLOQUE.search(texto)
    if not m:
        raise SystemExit(f'{clave}: no encontre Description')
    viejo = m.group(2)
    # Los numeros que usa el ingles tienen que seguir estando (y no inventar otros).
    usados_en = set(PH.findall(viejo)) - {'%enchantment_potion_type%'}
    usados_es = set(PH.findall(ES[clave]))
    if not usados_es <= set(PH.findall(viejo)):
        raise SystemExit(f'{clave}: placeholders que no existen: {usados_es - set(PH.findall(viejo))}')
    if usados_en - usados_es:
        print(f'  aviso {clave}: no muestra {sorted(usados_en - usados_es)}')
    linea = ES[clave].replace("'", "''")
    nuevo = f"  - '<gray>{linea}</gray>'{nl}"
    return texto[:m.start(2)] + nuevo + texto[m.end(2):]


def apagar_tooltip(cfg):
    # La lista de encantamientos estilo Hypixel la arma AstralMesa (con estas mismas descripciones);
    # si EE tambien agrega las suyas, salen dos veces.
    texto = Path(cfg).read_bytes().decode('utf-8')
    nuevo = texto.replace('  EnchantTooltip: true', '  EnchantTooltip: false', 1)
    if nuevo == texto and 'EnchantTooltip: false' not in texto:
        raise SystemExit('config.yml: no encontre Modules.EnchantTooltip')
    (OUT.parent / 'config.yml').write_bytes(nuevo.encode('utf-8'))
    print('  config.yml: Modules.EnchantTooltip = false')


def main(src):
    src = Path(src)
    OUT.mkdir(parents=True, exist_ok=True)
    hechos = 0
    for f in sorted(src.glob('*.yml')):
        clave = f.stem
        if clave not in ES:
            print('  sin traduccion:', clave)
            continue
        texto = f.read_bytes().decode('utf-8')
        (OUT / f.name).write_bytes(traducir(texto, clave).encode('utf-8'))
        hechos += 1
    faltan = sorted(set(ES) - {f.stem for f in src.glob('*.yml')})
    print(f'ee_descripciones: {hechos} archivos -> {OUT}' + (f' (sin archivo: {faltan})' if faltan else ''))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('origen', help='carpeta con los enchants/*.yml bajados del server')
    ap.add_argument('--config', help='plugins/ExcellentEnchants/config.yml bajado del server: apaga su tooltip')
    a = ap.parse_args()
    main(a.origen)
    if a.config:
        apagar_tooltip(a.config)
