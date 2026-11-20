"""Mesa de encantamientos propia: plugin AstralMesa (reemplaza a LynExp).

Ofrece todos los encantamientos que acepta el objeto (vanilla, ExcellentEnchants y otros plugins),
con paginas, menos las mejoras del Herrero (namespace astral). Mismo cobro que LynExp:
el nivel N de un encantamiento de nivel maximo M cuesta la XP de ceil(N/M*30) niveles (max 1395 puntos).
Tambien conserva lo demas de LynExp: botella de vidrio en la mesa embotella XP y los items de mobs
en un conducto dan XP.

  python mesa_encantamientos.py --jdk <java25>   -> build/mesa/AstralMesa.jar + config.yml + entrega.md
"""
import argparse
import os
from pathlib import Path
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'build' / 'mesa'
STAMP = (2026, 11, 20, 0, 0, 0)

# Mismos valores que tenia LynExp en el server.
CONDUCTO = {'rotten_flesh': 2, 'bone': 3, 'spider_eye': 4, 'string': 1, 'gunpowder': 5,
            'blaze_rod': 10, 'ender_pearl': 8, 'ghast_tear': 12, 'slime_ball': 6}


# Que hace cada encantamiento (se muestra en el libro de la mesa). Sin numeros: los valores de
# ExcellentEnchants pueden cambiar en su config; "mas nivel = mas fuerte" vale para todos los que suben.
VANILLA = {
    'protection': 'Reduce casi todo el daño que recibís.',
    'fire_protection': 'Reduce el daño de fuego y lava y te apaga más rápido.',
    'feather_falling': 'Reduce el daño por caída.',
    'blast_protection': 'Reduce el daño de explosiones y el empuje que te dan.',
    'projectile_protection': 'Reduce el daño de flechas, tridentes y bolas de fuego.',
    'respiration': 'Aguantás más tiempo la respiración bajo el agua.',
    'aqua_affinity': 'Picás bajo el agua a la velocidad normal.',
    'thorns': 'Le devuelve daño a quien te pega (gasta más la armadura).',
    'depth_strider': 'Caminás más rápido bajo el agua.',
    'frost_walker': 'Congela el agua bajo tus pies para caminar arriba.',
    'binding_curse': 'Maldición: no te podés sacar la armadura (salvo al morir).',
    'soul_speed': 'Corrés más rápido sobre arena y tierra de almas.',
    'swift_sneak': 'Te movés más rápido agachado.',
    'sharpness': 'Más daño a todos los enemigos.',
    'smite': 'Mucho más daño a muertos vivientes (zombis, esqueletos, wither).',
    'bane_of_arthropods': 'Mucho más daño a arañas, abejas y lepismas, y los frena.',
    'knockback': 'Empuja más lejos a quien golpeás.',
    'fire_aspect': 'Prende fuego a quien golpeás.',
    'looting': 'Los mobs sueltan más botín.',
    'sweeping_edge': 'Más daño al golpe de barrido de la espada.',
    'efficiency': 'Picás, talás y cavás más rápido.',
    'silk_touch': 'Los bloques salen enteros (vidrio, minerales sin romper, etc.).',
    'unbreaking': 'El objeto se gasta más lento.',
    'fortune': 'Los minerales y cultivos sueltan más cosas.',
    'power': 'Las flechas hacen más daño.',
    'punch': 'Las flechas empujan más lejos.',
    'flame': 'Las flechas prenden fuego.',
    'infinity': 'Con una sola flecha en el inventario, disparás sin gastar.',
    'luck_of_the_sea': 'Pescás más tesoros y menos basura.',
    'lure': 'Los peces pican más rápido.',
    'loyalty': 'El tridente vuelve a tu mano después de tirarlo.',
    'impaling': 'Más daño del tridente a criaturas del agua.',
    'riptide': 'Con lluvia o en el agua, el tridente te lanza con él.',
    'channeling': 'Con tormenta, el tridente llama un rayo sobre el enemigo.',
    'multishot': 'La ballesta dispara 3 flechas a la vez.',
    'quick_charge': 'La ballesta carga más rápido.',
    'piercing': 'Las flechas de ballesta atraviesan varios enemigos.',
    'density': 'Más daño de la maza según la altura de la caída.',
    'breach': 'La maza ignora parte de la armadura del enemigo.',
    'wind_burst': 'Al golpear con la maza cayendo, salís impulsado hacia arriba.',
    'lunge': 'La lanza te impulsa hacia adelante al atacar.',
    'mending': 'La XP que juntás repara el objeto.',
    'vanishing_curse': 'Maldición: el objeto desaparece al morir.',
}

ESPECIALES = {
    'auto_reel': 'Recoge la caña sola cuando pica un pez.',
    'bane_of_netherspawn': 'Más daño a mobs del Nether.',
    'blast_mining': 'Chance de picar con una explosión que rompe bloques alrededor.',
    'blindness': 'Chance de dejar ciego al enemigo al golpearlo.',
    'bomber': 'Chance de que el arco dispare una TNT encendida.',
    'cold_steel': 'Chance de darle fatiga de minado a quien te pega.',
    'confusing_arrows': 'Chance de que la flecha maree (náusea) al enemigo.',
    'confusion': 'Chance de marear (náusea) al enemigo al golpearlo.',
    'cure': 'Chance de curar a piglins zombi y aldeanos zombi al golpearlos.',
    'curse_of_breaking': 'Maldición: chance de gastar durabilidad de más.',
    'curse_of_death': 'Maldición: al matar a un jugador podés morir vos también.',
    'curse_of_drowned': 'Maldición: chance de pescar un ahogado.',
    'curse_of_fragility': 'Maldición: no se puede usar en yunque ni piedra de afilar.',
    'curse_of_mediocrity': 'Maldición: chance de que lo que sueltan salga sin encantar.',
    'curse_of_misfortune': 'Maldición: chance de que bloques y mobs no suelten nada.',
    'cutter': 'Chance de sacarle una pieza de armadura al enemigo y dañarla.',
    'darkness_arrows': 'Chance de que la flecha deje en oscuridad al enemigo.',
    'darkness_cloak': 'Chance de dejar en oscuridad a quien te pega.',
    'decapitator': 'Chance de que el jugador o mob suelte su cabeza.',
    'double_catch': 'Chance de pescar el doble.',
    'double_strike': 'Chance de hacer doble daño.',
    'dragon_heart': 'Te da corazones extra (absorción) todo el tiempo.',
    'dragonfire_arrows': 'Chance de que la flecha deje fuego de dragón donde cae.',
    'electrified_arrows': 'Chance de que la flecha llame un rayo con daño extra.',
    'elemental_protection': 'Reduce el daño de pociones y elementos (fuego, hielo, etc.).',
    'ender_bow': 'El arco dispara perlas de ender en vez de flechas.',
    'exhaust': 'Chance de darle hambre al enemigo al golpearlo.',
    'explosive_arrows': 'Chance de disparar una flecha explosiva.',
    'fire_shield': 'Chance de prender fuego a quien te pega.',
    'flame_walker': 'Caminás sobre lava y el magma no te hace daño.',
    'flare': 'Chance de poner una antorcha donde cae la flecha.',
    'ghast': 'El arco dispara bolas de fuego en vez de flechas.',
    'glassbreaker': 'Rompe el vidrio al instante.',
    'hardened': 'Chance de ganar resistencia al recibir daño.',
    'haste': 'Te da prisa minera mientras picás.',
    'hover': 'Chance de que la flecha haga levitar al enemigo.',
    'ice_aspect': 'Congela y frena al enemigo al golpearlo.',
    'ice_shield': 'Chance de congelar y frenar a quien te pega.',
    'infernus': 'El tridente prende fuego al enemigo que toca.',
    'jumping': 'Saltás más alto todo el tiempo.',
    'kamikadze': 'Chance de explotar al morir.',
    'lightweight': 'Podés pisar huevos de tortuga y cultivos sin romperlos.',
    'lingering': 'Chance de que las flechas con poción dejen una nube del efecto.',
    'lucky_miner': 'Chance de ganar más XP de los minerales.',
    'night_vision': 'Visión nocturna todo el tiempo.',
    'nimble': 'Lo que sueltan los mobs va directo a tu inventario.',
    'paralyze': 'Chance de darle fatiga de minado al enemigo al golpearlo.',
    'poisoned_arrows': 'Chance de que la flecha envenene.',
    'rage': 'Chance de ganar fuerza al golpear.',
    'rebound': 'Rebotás al caer, como sobre un bloque de slime.',
    'regrowth': 'Te cura un poco de vida cada algunos segundos.',
    'replanter': 'Vuelve a plantar los cultivos al cosecharlos.',
    'restore': 'Chance de salvar el objeto cuando está por romperse.',
    'river_master': 'Tirás la caña más lejos.',
    'rocket': 'Chance de lanzar al enemigo por el aire.',
    'saturation': 'Te llena la comida cada algunos segundos.',
    'seasoned_angler': 'Ganás más XP pescando.',
    'silk_chest': 'Los cofres salen enteros con todo lo que tienen adentro.',
    'silk_spawner': 'Chance de llevarte el generador de mobs al picarlo.',
    'smelter': 'Chance de que lo que picás salga ya fundido.',
    'sniper': 'Las flechas vuelan más rápido.',
    'soulbound': 'No se te cae al morir.',
    'speed': 'Velocidad todo el tiempo.',
    'stopping_force': 'Chance de recibir menos empuje.',
    'survivalist': 'Los pescados salen ya cocinados.',
    'swiper': 'Chance de robarle XP a los jugadores al golpearlos.',
    'telekinesis': 'Lo que picás va directo a tu inventario.',
    'temper': 'Más daño cuanta menos vida te queda.',
    'thrifty': 'Chance de que los mobs suelten su huevo de aparición.',
    'thunder': 'Chance de llamar un rayo con daño extra al golpear.',
    'treefeller': 'Tala el árbol entero de un golpe.',
    'tunnel': 'Pica varios bloques a la vez (3x3).',
    'vampire': 'Chance de curarte al golpear.',
    'vampiric_arrows': 'Chance de curarte cuando la flecha pega.',
    'veinminer': 'Pica toda la veta de mineral de una.',
    'venom': 'Chance de envenenar al enemigo al golpearlo.',
    'village_defender': 'Más daño a los saqueadores (illagers).',
    'water_breathing': 'Respirás bajo el agua todo el tiempo.',
    'wisdom': 'Los mobs sueltan más XP.',
    'wither': 'Chance de darle efecto wither al enemigo al golpearlo.',
    'withered_arrows': 'Chance de que la flecha dé efecto wither.',
}


BASTONES = [
    'minecraft:looting',                 # botin del mob muerto con el hechizo
    'excellentenchants:wisdom',          # mas XP de los mobs
    'excellentenchants:nimble',          # botin directo al inventario
    'excellentenchants:decapitator',     # cabezas
    'excellentenchants:thrifty',         # huevos de mobs
    'excellentenchants:soulbound',       # no se cae al morir
    'excellentenchants:restore',         # se salva al romperse
    'excellentenchants:curse_of_breaking', 'excellentenchants:curse_of_misfortune', 'excellentenchants:curse_of_mediocrity',
]


def descripciones():
    d = {f'minecraft:{k}': v for k, v in VANILLA.items()}
    d.update({f'excellentenchants:{k}': v for k, v in ESPECIALES.items()})
    return d


def config():
    return {
        'niveles-maximo': 30,
        'particulas': True,
        # astral = mejoras del Herrero (Mejora +N): nunca en la mesa.
        'excluir-namespaces': ['astral'],
        'excluir': [],
        'botella': {'costo-xp': 5},
        'conducto': CONDUCTO,
        # Bastones de mago (carrot_on_a_stick): el juego solo les deja Irrompibilidad y Reparacion.
        # El hechizo es dano magico del jugador, asi que sirven los que actuan al matar o son pasivos.
        'bastones': BASTONES,
        # Texto del libro en la mesa. Si falta uno, el libro sale sin descripcion.
        'descripciones': descripciones(),
    }


PLUGIN_YML = """name: AstralMesa
version: 1.2.0
main: astral.AstralMesa
api-version: '26.1.2'
description: Mesa de encantamientos con todos los encantamientos (vanilla y de plugins) salvo las mejoras del Herrero
softdepend: [ExcellentEnchants]
commands:
  astralmesa:
    description: Recarga la config de la mesa
    usage: /astralmesa reload
    permission: astral.mesa.admin
permissions:
  astral.mesa.admin:
    default: op
"""


def build_plugin(jdk, server):
    import yaml
    jdk, server = Path(jdk), Path(server)
    classes = ROOT / '.local' / 'mesa-classes'
    classes.mkdir(parents=True, exist_ok=True)
    deps = [*server.joinpath('libraries').rglob('*.jar'), *server.joinpath('versions').rglob('*.jar')]
    javac = [str(jdk / ('java.exe' if os.name == 'nt' else 'java')), '-m', 'jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*javac, '-encoding', 'UTF-8', '-source', '25', '-target', '25', '-nowarn', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(classes), str(HERE / 'runtime' / 'AstralMesa.java')], check=True)
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / 'AstralMesa.jar'
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((classes / 'astral').glob('AstralMesa*.class')):
            z.writestr(zipfile.ZipInfo('astral/' + p.name, STAMP), p.read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml', STAMP), PLUGIN_YML)
        z.writestr(zipfile.ZipInfo('config.yml', STAMP), yaml.safe_dump(config(), sort_keys=False, allow_unicode=True))
    return dest


ENTREGA = """# Mesa de encantamientos: AstralMesa (reemplaza a LynExp)

Problema: LynExp arma un libro por nivel y la ventana tiene 48 lugares. Con ExcellentEnchants
los libros pasan de 48 y los vanilla quedaban afuera.

AstralMesa muestra todo (vanilla primero, despues ExcellentEnchants, maldiciones al final) con paginas,
sin las mejoras del Herrero (`astral:`). Saca los niveles que el objeto ya tiene y los que chocan con
lo que ya tiene. El objeto queda en la mesa para encantar varias veces; al cerrar vuelve al inventario.

## Subir
1. Files: `plugins/` -> borrar (o renombrar a `.jar.off`) `LynExp-1.0.0-mc26.1-26.1.2.jar`.
2. Subir `build/mesa/AstralMesa.jar` a `plugins/`.
3. Reiniciar el server (crea `plugins/AstralMesa/config.yml`).
4. Probar: clic derecho en una mesa de encantamientos con una espada en el inventario.

Config: `plugins/AstralMesa/config.yml`, recargar con `astralmesa reload`.
"""


def generate():
    import yaml
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'config.yml').write_text(yaml.safe_dump(config(), sort_keys=False, allow_unicode=True), encoding='utf-8')
    (OUT / 'entrega.md').write_text(ENTREGA, encoding='utf-8')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--jdk')
    ap.add_argument('--server', default=str(ROOT / '.local' / 'testsrv'))
    a = ap.parse_args()
    generate()
    if a.jdk:
        print('plugin ->', build_plugin(a.jdk, a.server))
    print('mesa ->', OUT)
