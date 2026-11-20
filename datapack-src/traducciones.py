"""Plugins en espanol (AstralRPG es un servidor en espanol).

Dos tipos de cambios:
  1. Archivos de mensajes traducidos enteros: viven en datapack-src/traducciones/<Plugin>/...
     y se copian a build/traducciones/plugins/<Plugin>/... (se suben tal cual al servidor).
  2. Parches sobre archivos del servidor (configs con otros ajustes adentro): se bajan del
     servidor a una carpeta (por defecto .local/traduccion/orig, con la misma ruta que tienen
     dentro de plugins/) y se escriben parchados en .local/traduccion/subir. Esa salida queda
     fuera del repo porque algunas configs pueden tener claves.

Uso (desde datapack-src/):
  python traducciones.py                      # solo copia los mensajes a build/
  python traducciones.py --parchar [carpeta]  # ademas parcha las configs bajadas

Despues de subir: ver build/traducciones/comandos.txt (recargas y avisos de WorldGuard).
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent / 'traducciones'
OUT = ROOT / 'build' / 'traducciones'
ORIG = ROOT / '.local' / 'traduccion' / 'orig'
SUBIR = ROOT / '.local' / 'traduccion' / 'subir'

# Plugins que ya traen espanol: solo hay que elegir el idioma.
# Ruta dentro de plugins/ -> lista de (texto exacto, reemplazo). Cada texto tiene que aparecer.
PARCHES: dict[str, list[tuple[str, str]]] = {
    'AuthMe/config.yml': [
        ('messagesLanguage: en', 'messagesLanguage: es'),
        ('perPlayerLocale: true', 'perPlayerLocale: false'),
    ],
    'Essentials/config.yml': [('#locale: en', 'locale: es')],
    'Bolt/config.yml': [('language: en', 'language: es')],
    'nonchat/config.yml': [('language: en', 'language: es')],
    'AuraSkills/config.yml': [('default_language: en', 'default_language: es')],
    'SkinsRestorer/config.yml': [
        ('    locale: en\n', '    locale: es\n'),
        ('perIssuerLocale: true', 'perIssuerLocale: false'),
    ],
    'ClearLag/config.yml': [
        # {time} del aviso sale "10 minutos" en vez de "600" (usa time-units de messages.yml)
        ('countdown-use-formatted-time: false', 'countdown-use-formatted-time: true'),
        ("warning: '&eYou will be AFK in &c{time}&e...'", "warning: '&eQuedas AFK en &c{time}&e...'"),
        ("afk: '&cYou are now AFK'", "afk: '&cEstas AFK'"),
        ("active: '&aWelcome back!'", "active: '&a¡Volviste!'"),
    ],
    'AxGraves/config.yml': [
        ("prefix: '<gradient:#FF00FF:#DD00FF><b>AxGraves</b></gradient> &7» '",
         "prefix: '<gradient:#FF00FF:#DD00FF><b>Tumbas</b></gradient> &7» '"),
        ('  world: Overworld\n', '  world: Mundo normal\n'),
        ('  world_nether: The Nether\n', '  world_nether: Nether\n'),
        ('  world_the_end: The End\n', '  world_the_end: El End\n'),
    ],
    'CrazyCrates/config.yml': [
        ('name: "<bold><gradient:#e91e63:blue>Crazy Crates</gradient></bold>"',
         'name: "<bold><gradient:#e91e63:blue>Cajas</gradient></bold>"'),
        ('"<gray>Return to the menu."', '"<gray>Volver al menu."'),
        ('"<bold><gold>Next »</bold>"', '"<bold><gold>Siguiente »</bold>"'),
        ('"<bold><gold>« Back</bold>"', '"<bold><gold>« Anterior</bold>"'),
        ('"<bold><gray>Page:</bold> <blue>{page}"', '"<bold><gray>Pagina:</bold> <blue>{page}"'),
    ],
    'CrazyAuctions/config.yml': [
        ("Prefix: '<gray>[<dark_red>Crazy <aqua>Auctions<gray>]: '", "Prefix: '<gray>[<gold>Subastas<gray>]: '"),
        ("'&8Purchase Item: Are You Sure?'", "'&8Comprar: ¿Seguro?'"),
        ("'&8You Are Bidding On This Item.'", "'&8Estas ofertando por este objeto'"),
        ("Categories: '&8Categories'", "Categories: '&8Categorias'"),
        ('"You have some expired items from you auction! Collect them by using /ah collect"',
         '"¡Tenes objetos vencidos en las subastas! Recuperalos con /ah collect"'),
        ("'&aClick here to purchase.'", "'&aClic para comprar.'"),
        ("'&9Price: &e$%price%'", "'&9Precio: &e$%price%'"),
        ("'&9Seller: &e%seller%'", "'&9Vendedor: &e%seller%'"),
        ("'&aClick here to cancel.'", "'&aClic para cancelar.'"),
        ("'&9Expire: &e%time%'", "'&9Vence en: &e%time%'"),
        ("'&aClick here to return to you.'", "'&aClic para recuperarlo.'"),
        ("'&9Full Expire: &e%time%'", "'&9Se borra en: &e%time%'"),
        ("'&aClick here to bid.'", "'&aClic para ofertar.'"),
        ("'&9Current Bid: &e$%topbid%'", "'&9Oferta actual: &e$%topbid%'"),
        ("'&9Top Bidder: &e%topbidder%'", "'&9Mejor oferta de: &e%topbidder%'"),
        ("'&9Time Left: &e%time%'", "'&9Tiempo restante: &e%time%'"),
        ("'&6&lArmor'", "'&6&lArmaduras'"), ("'&6&lWeapons'", "'&6&lArmas'"),
        ("'&6&lTools'", "'&6&lHerramientas'"), ("'&6&lFood'", "'&6&lComida'"),
        ("'&6&lPotions'", "'&6&lPociones'"), ("'&6&lBlocks'", "'&6&lBloques'"),
        ("'&6&lOthers'", "'&6&lOtros'"), ("'&6&lNone'", "'&6&lTodo'"),
        ("'&7This category contains all'", "'&7Esta categoria tiene todas'"),
        ("'&7armor that is currently being sold.'", "'&7las armaduras a la venta.'"),
        ("'&7weapons that are currently being sold.'", "'&7las armas a la venta.'"),
        ("'&7tools that are currently being sold.'", "'&7las herramientas a la venta.'"),
        ("'&7food that is currently being sold.'", "'&7la comida a la venta.'"),
        ("'&7potions that are currently being sold.'", "'&7las pociones a la venta.'"),
        ("'&7blocks that are currently being sold.'", "'&7los bloques a la venta.'"),
        ("'&7This category contains all the'", "'&7Esta categoria tiene todos'"),
        ("'&7other items currently being sold.'", "'&7los demas objetos a la venta.'"),
        ("'&7items currently being sold.'", "'&7los objetos a la venta.'"),
        ("'&6Items You are Selling'", "'&6Lo que estas vendiendo'"),
        ("'&aClick here to view all the items you'", "'&aClic para ver todo lo que'"),
        ("'&aare currently selling on the auction.'", "'&aestas vendiendo en las subastas.'"),
        ("'&6Collect Expired / Canceled Items'", "'&6Recuperar vencidos / cancelados'"),
        ("'&aClick here to view and collect all of the'", "'&aClic para ver y recuperar los'"),
        ("'&aitems you have canceled or has expired.'", "'&aobjetos cancelados o vencidos.'"),
        ("'&6Previous Page'", "'&6Pagina anterior'"),
        ("'&6Refresh Page'", "'&6Actualizar'"),
        ("'&6Next Page'", "'&6Pagina siguiente'"),
        ("Name: '&6Categories'", "Name: '&6Categorias'"),
        ("'&bCurrent Category: &6%category%'", "'&bCategoria actual: &6%category%'"),
        ("'&aWant to see items in specific categories?'", "'&a¿Queres ver una categoria?'"),
        ("'&aClick here to see all categories of items.'", "'&aClic para ver todas las categorias.'"),
        ("'&6Currently looking at items being sold.'", "'&6Estas viendo objetos a la venta.'"),
        ("'&7&l(&6&l!&7&l) &7Click here to see items'", "'&7&l(&6&l!&7&l) &7Clic para ver objetos'"),
        ("'&7that you can bid on.'", "'&7por los que podes ofertar.'"),
        ("'&6Currently looking at items that can be bid on.'", "'&6Estas viendo objetos para ofertar.'"),
        ("'&7that you can buy at a price.'", "'&7que podes comprar a precio fijo.'"),
        ("'&6What Is This Page?'", "'&6¿Que es esta pagina?'"),
        ("'&aThis is the crazy auctions, here you can'", "'&aEstas son las subastas: aca podes'"),
        ("'&aput items for sale, and buy items'", "'&avender objetos y comprar los'"),
        ("'&athat others have put for sale.'", "'&aque venden otros jugadores.'"),
        ("'&aThe auction is also a great place to make'", "'&aTambien es un buen lugar para ganar'"),
        ("'&amoney by selling items that others'", "'&aplata vendiendo cosas que otros'"),
        ("'&amay be interested in buying.'", "'&aquieran comprar.'"),
        ("'&aput items for sale, and bid on items'", "'&avender objetos y ofertar por los'"),
        ("'&aThe bidding auction is also a great place to'", "'&aLas ofertas tambien son un buen lugar'"),
        ("'&amake money by bidding off items that others'", "'&apara ganar plata con objetos que otros'"),
        ("'&amay be interested in bidding on.'", "'&aquieran ofertar.'"),
        ("'&aThese are your current listings, all of'", "'&aEstas son tus ventas: todo lo que'"),
        ("'&athe items you currently have listed on'", "'&atenes publicado en las subastas'"),
        ("'&acrazy auctions are displayed here.'", "'&aaparece aca.'"),
        ("'&aYou can cancel and view your listings'", "'&aPodes cancelarlas y ver cuando'"),
        ("'&aexpire time here.'", "'&avencen.'"),
        ("'&aThis page houses all of your cancelled and'", "'&aAca estan todos tus objetos cancelados'"),
        ("'&aexpired items, when a listings is cancelled'", "'&ao vencidos. Cuando una venta se cancela'"),
        ("'&aor expires you will be able to return that'", "'&ao vence, podes recuperar el objeto'"),
        ("'&aitem back to you from this menu.'", "'&adesde este menu.'"),
        ("'&aJust click on the item and if you have enough'", "'&aHace clic en el objeto y, si tenes lugar'"),
        ("'&ainventory space you will receive that item.'", "'&aen el inventario, lo recibis.'"),
        ("'&aThis page shows all the items that'", "'&aEsta pagina muestra todo lo que'"),
        ("'&aa player has currently on the bidding'", "'&aun jugador tiene en ofertas'"),
        ("'&aand selling market. You can quickly see'", "'&ay a la venta. Asi ves rapido'"),
        ("'&awhat a specific player is selling.'", "'&alo que vende un jugador.'"),
        ("'&aThis page shows all the categories'", "'&aEsta pagina muestra todas las categorias'"),
        ("'&athat you can choose from. When you click'", "'&aque podes elegir. Al hacer clic en'"),
        ("'&aa category it will open the gui with only'", "'&auna, se abre el menu solo con'"),
        ("'&aitems that belong to that category.'", "'&alos objetos de esa categoria.'"),
        ("Name: '&6Back'", "Name: '&6Volver'"),
        ("'&6Return All'", "'&6Recuperar todo'"),
        ("'&aClick here to return all cancelled'", "'&aClic para recuperar todos los objetos'"),
        ("'&aand expired items to your inventory.'", "'&acancelados y vencidos.'"),
        ("Name: '&aConfirm'", "Name: '&aConfirmar'"),
        ("Name: '&cCancel'", "Name: '&cCancelar'"),
        ("'&cYou Can''t Purchase Your Own Item.'", "'&cNo podes comprar tu propio objeto.'"),
        ("'&cYou Can''t Afford This Item.'", "'&cNo te alcanza la plata.'"),
        ("'&cYou are already the top bidder.'", "'&cYa tenes la mejor oferta.'"),
        ("Name: '&7Bidding'", "Name: '&7Oferta'"),
        ("'&7<--&aAdd &cRemove&7-->'", "'&7<--&aSumar &cRestar&7-->'"),
        ("'&9Your Current Bid: &e$%Bid%'", "'&9Tu oferta: &e$%Bid%'"),
        ("'&9Current Top Bid: &e$%topbid%'", "'&9Mejor oferta: &e$%topbid%'"),
        ("'&bBid Now'", "'&bOfertar ya'"),
        ("'&7Click here to Bid Now.'", "'&7Clic para ofertar.'"),
    ],
}

# Claves que faltan en el espanol que trae el plugin (si falta, se veria en ingles).
AGREGAR_YAML: dict[str, dict] = {
    'AuraSkills/messages/messages_es.yml': {
        'menus': {
            'common': {
                'trait': 'Rasgo',
                'trait_gain': '<1>Ganas {color}{level_modifier} {trait_name} <1>de nivel de rasgo por cada {color}1 {stat_name}',
                'trait_level': 'Nivel de rasgo',
                'base': 'Base',
                'modifiers_additive': 'Modificadores (suma)',
                'modifiers_multiplicative': 'Modificadores (multiplican)',
            },
            'skills': {'active_job': 'Trabajo activo'},
            'level_progression': {
                'job': 'Trabajo',
                'job_desc': 'Si elegis {skill} como trabajo, ganas plata mientras subis XP.',
                'job_select': 'Clic izquierdo para elegir {skill} como trabajo',
                'job_active': 'Estas trabajando en esto',
                'job_quit': 'Clic derecho para dejar este trabajo',
                'job_limit': 'Llegaste al limite de trabajos. Deja uno antes de elegir este.',
                'job_cooldown': 'Tenes que esperar para cambiar de trabajo. Podes en {time}.',
            },
            'stats': {'stat_info_click': 'Clic para ver el detalle'},
            'stat_info': {
                'stat_details': 'Estadistica {stat_name}',
                'stat': 'Estadistica',
                'stat_level': 'Nivel',
                'traits_leveled': 'Rasgos que sube',
                'stat_modifiers': 'Modificadores',
                'stat_reward_desc': 'Te lo da tu nivel de {skill}.',
                'stat_modifiers_click': 'Clic para ver los modificadores de la estadistica',
                'trait_modifiers_click': 'Clic para ver los modificadores de los rasgos',
                'showing_stat_modifiers': 'Mostrando modificadores de la estadistica',
                'showing_trait_modifiers': 'Mostrando modificadores de los rasgos',
                'base_level': 'Nivel base',
                'base_level_desc': 'Nivel base de Minecraft y otras fuentes.',
                'linked_stat_desc': 'Te lo da tu nivel de {stat}.',
                'ability_modifier_name': 'Habilidad {name}',
                'ability_modifier_desc': 'Te lo da la habilidad {ability}.',
                'custom_modifier_desc': 'Te lo da un modificador especial.',
                'item_hand_desc': 'Te lo da el objeto de la mano.',
                'item_off_hand_desc': 'Te lo da el objeto de la otra mano.',
                'helmet_desc': 'Te lo da el casco.',
                'chestplate_desc': 'Te lo da la pechera.',
                'leggings_desc': 'Te lo dan las grebas.',
                'boots_desc': 'Te lo dan las botas.',
                'effective_trait': '{trait_name} efectivo',
            },
        }
    },
}

# Mundos con WorldGuard: el aviso "Hey! Sorry, but you can't ... here." en espanol.
MUNDOS_WG = '''arena arenas_tft astral_bosque astral_minas battleship bosque bosque_2 bosque_3 bosque_4 bosque_5
bosque_6 cavernas cavernas_cristal colorescape cumbre cumbre_hielo cumbre_hielo_2 cumbre_hielo_3 cumbre_hielo_4
cumbre_hielo_5 cumbre_hielo_6 dropper_facil dropper_h4rs exp_desierto exp_hielo exp_nieve exp_santuario forja
forja_volcano forja_volcano_2 forja_volcano_3 forja_volcano_4 forja_volcano_5 forja_volcano_6 fosa fosa_2 fosa_3
infinita infinita_2 infinita_3 infinita_4 infinita_5 infinita_6 lobby magmarun mina mina_2 mina_3 mina_4 mina_5
mina_6 oceano parkour_paradise3 parkour_spiral parkour_spiral2 portales_astrales reino santuario
santuario_freemap9 santuario_interstellar towerdefence towerdefence_end tumba tumba_2 tumba_3 tumba_4 tumba_5
tumba_6 world world_minecraft_santuario_azeroth world_minecraft_santuario_azeroth_2
world_minecraft_santuario_azeroth_3 world_minecraft_santuario_azeroth_4 world_minecraft_santuario_azeroth_5
world_minecraft_santuario_azeroth_6 world_nether world_the_end'''.split()

WG_FLAGS = {
    'deny-message': '&c¡No podes hacer eso aca!',
    'entry-deny-message': '&cNo podes entrar aca.',
    'exit-deny-message': '&cNo podes salir de aca.',
}

RECARGAS = [
    'authme reload', 'essentials reload', 'nonchat reload', 'clearlag reload', 'axgraves reload',
    'axtrade reload', 'crates reload', 'ah reload', 'duels reload', 'sm reload', 'gpreload',
    'train reload', 'skills reload', 'bolt reload', 'sr reload',
]


def copiar_mensajes() -> list[Path]:
    destino = OUT / 'plugins'
    if destino.exists():
        shutil.rmtree(destino)
    hechos = []
    for f in sorted(SRC.rglob('*')):
        if f.is_file():
            rel = f.relative_to(SRC)
            yaml.safe_load(f.read_text(encoding='utf-8'))  # que no se suba un YAML roto
            d = destino / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, d)
            hechos.append(rel)
    return hechos


def mezclar(base: dict, extra: dict) -> int:
    n = 0
    for k, v in extra.items():
        if isinstance(v, dict):
            if not isinstance(base.get(k), dict):
                base[k] = {}
            n += mezclar(base[k], v)
        elif k not in base:
            base[k] = v
            n += 1
    return n


def parchar(orig: Path) -> None:
    if SUBIR.exists():
        shutil.rmtree(SUBIR)
    for rel, cambios in PARCHES.items():
        src = orig / rel
        if not src.exists() or src.stat().st_size == 0:
            sys.exit(f'Falta (o esta vacio) {src}: bajarlo del servidor (plugins/{rel})')
        t = src.read_text(encoding='utf-8')
        for viejo, nuevo in cambios:
            if viejo not in t:
                if nuevo in t:
                    continue  # ya estaba aplicado
                sys.exit(f'{rel}: no se encontro {viejo!r}')
            t = t.replace(viejo, nuevo)
        yaml.safe_load(t)
        d = SUBIR / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_bytes(t.encode('utf-8'))
        print('parchado', rel)
    for rel, extra in AGREGAR_YAML.items():
        src = orig / rel
        if not src.exists() or src.stat().st_size == 0:
            sys.exit(f'Falta (o esta vacio) {src}: bajarlo del servidor (plugins/{rel})')
        doc = yaml.safe_load(src.read_text(encoding='utf-8'))
        n = mezclar(doc, extra)
        d = SUBIR / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_bytes(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=1000).encode('utf-8'))
        print(f'agregadas {n} claves', rel)


def comandos() -> str:
    lineas = ['# Consola, despues de subir build/traducciones/plugins y .local/traduccion/subir']
    lineas += [f'rg flag -w {m} __global__ {flag} {msg}' for m in MUNDOS_WG for flag, msg in WG_FLAGS.items()]
    lineas += RECARGAS
    return '\n'.join(lineas) + '\n'


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--parchar', nargs='?', const=str(ORIG), help='carpeta con las configs bajadas')
    a = ap.parse_args()
    for rel in copiar_mensajes():
        print('mensajes', rel)
    (OUT / 'comandos.txt').write_text(comandos(), encoding='utf-8')
    if a.parchar:
        parchar(Path(a.parchar))


if __name__ == '__main__':
    main()
