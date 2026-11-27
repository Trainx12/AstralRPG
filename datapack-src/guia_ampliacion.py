"""Ampliacion de la Guia Astral. Usa los fondos y controles de guia_cofre.

Catalogo de hechos, sin assets de terceros. Las secciones nuevas quedan para
prueba con astral.guia.ampliacion hasta la aprobacion del dueno.
"""
import json
from pathlib import Path

CATALOG = Path(__file__).with_name('guia_stellarity.json')
PERMISSION = 'astral.guia.ampliacion'

DESCRIPTIONS = {
    'book_of_conveyance': 'Lanza una chispa guiada con la mirada; te lleva al bloque donde impacta.',
    'book_of_jinx': 'Crea una nube que baja temporalmente la defensa de los enemigos.',
    'book_of_light': 'Invoca un aura que cura y protege a los jugadores cercanos.',
    'book_of_obstruct': 'Levanta una pared de shulker para cubrir una retirada.',
    'book_of_return': 'Te devuelve a tu punto de reaparicion.',
    'book_of_updraft': 'Te impulsa hacia arriba y permite planear brevemente.',
    'dragon_wings': 'Alas con proteccion a cambio de menor velocidad de vuelo.',
    'empress_wings': 'Alas rapidas y agiles, con estela de colores.',
    'phantom_wings': 'Alas de phantom; equipo de vuelo del End.',
    'dragonblade': 'Espada que empuja con fuerza; aprovecha paredes cercanas.',
    'call_of_the_void': 'Arco con flechas del vacio que reducen vida y se rompen al impactar.',
    'sharanga': 'Mejora las flechas espectrales y las hace viajar en linea recta.',
    'spectral_fury': 'Los disparos sobrecargados vuelven las flechas espectrales perseguidores.',
    'slayer_crossbow': 'Rayos de mucho dano que atraviesan enemigos, con alcance limitado.',
    'prismatic_punch': 'Dispara proyectiles con varias explosiones e incendio prismatico.',
    'prismember': 'Agachate para cargar un giro que incendia enemigos cercanos.',
    'kaleidoscope': 'Acumula energia y la libera al golpear.',
    'starless_scythe': 'Golpea varios enemigos y devuelve parte del dano como curacion.',
    'sandstorm_trident': 'Al lanzarlo crea tuneles de viento.',
    'tamaris': 'Al agacharte remata a un enemigo cercano con poca vida.',
    'stellar_striker': 'Junta estrellas al combatir. Agachate y ataca para lanzarlas juntas.',
    'harvester': 'Junta almas; aumenta su tamano y dano y puede ganar habilidades.',
    'spirit_dagger': 'Atrae espiritus al atacar y permite desplazamientos especiales.',
    'fisher_of_voids': 'Cana que acorta la espera en la pesca del vacio.',
    'bell_flower': 'Revela entidades cercanas mientras la sostenes.',
    'crest_of_the_end': 'Bloquear carga fuerza extra para el siguiente contraataque.',
    'starstruck_shield': 'Hace caer estrellas despues de bloquear dano.',
    'copper_elektra_shield': 'Agachate para una embestida electrica. Recarga hasta tres impulsos.',
    'decayed_clover': 'Mejora el botin y la suerte de pesca del vacio.',
    'duskberry': 'Sostenida mejora velocidad, vista y fuerza. Comerla o plantarla es peligroso.',
    'life_crystal': 'Regenera vida rapidamente mientras te quedas quieto.',
    'soaring_insignia': 'Permite vuelo continuo con maniobra limitada; agachate y mira arriba o abajo.',
    'satchel_of_voids': 'Dibuja un acceso al Altar Maldito. En un marco vertical permite un altar permanente.',
    'altar_of_the_sacred': 'Altar Sagrado: cambia minerales por bendiciones e invoca jefes con ofrendas.',
    'endonomicon': 'Libro de consulta de Stellarity. La disponibilidad de sus paginas depende de esta version.',
    'crystal_heartfish': 'Al comerlo suma 1 punto de vida maxima; limite propio de 10 puntos adicionales.',
    'goosh': 'Puede reemplazar bolas de slime en recetas compatibles.',
    'starlight_soot': 'Material para transmutacion en agua y ofrenda para Empress of Light.',
    'enderite_smithing_template': 'Plantilla para mejoras en el Altar Maldito; no se usa en herreria vanilla.',
    'chorus_plating': 'Material para mejorar equipo en el Altar Maldito.',
    'purpur_key': 'Abre bovedas de las ciudades del End.',
    'gilded_purpur_key': 'Abre bovedas ominosas de las ciudades del End.',
    'winged_key': 'Abre la boveda de elytras de los barcos del End.',
    'phantom_item_frame': 'Se vuelve invisible cuando colocas un objeto dentro.',
    'prismatic_pearl': 'Perla de teletransporte reutilizable: vuelve al inventario al terminar su espera.',
    'endermans_hand': 'Sostenida en una mano aumenta en 3 bloques el alcance para interactuar con bloques.',
    'void_locket': 'Accesorio con variantes internas de mejora. Este ZIP no aporta una receta accesible para aplicarlas.',
    'loaf_of_plenty': 'Pan que vuelve a tu mano despues de comerlo; espera de 10 segundos entre usos.',
    'fluffy_hammer': 'Martillo arrojadizo que golpea durante el vuelo y despues vuelve a su dueno.',
    'alpha_wooden_sword': 'Espada especial de aspecto antiguo; objeto de coleccion.',
    'frozen_carpaccio': 'Comida con un efecto positivo aleatorio.',
    'royal_jelly': 'Da absorcion y limpia efectos negativos.',
    'royal_jelly_ii': 'Version mejorada: absorcion y limpieza de efectos negativos.',
}
EFFECTS = dict(speed='Velocidad', jump_boost='Salto', regeneration='Regeneracion', absorption='Absorcion',
               strength='Fuerza', resistance='Resistencia', fire_resistance='Resistencia al fuego',
               health_boost='Vida extra', instant_health='Curacion instantanea', instant_damage='Dano instantaneo',
               slowness='Lentitud', weakness='Debilidad', blindness='Ceguera', poison='Veneno', wither='Wither',
               luck='Suerte', glowing='Brillo', water_breathing='Respiracion acuatica', night_vision='Vision nocturna',
               hunger='Hambre', nausea='Nauseas', levitation='Levitacion', haste='Prisa',
               dolphins_grace='Gracia del delfin', slow_falling='Caida lenta', mining_fatigue='Fatiga al minar')


def item_description(key):
    if key in DESCRIPTIONS:
        return DESCRIPTIONS[key]
    for prefix, desc in [('hallowed_', 'El conjunto completo permite esquivar golpes y retroceso.'),
                         ('champion_', 'El conjunto completo aumenta el dano al encadenar ataques.'),
                         ('floral_', 'El conjunto completo hace florecer explosiones al disparar y permite camuflarte entre plantas.'),
                         ('shulker_', 'Equipo de shulker. El conjunto de armadura reduce dano y responde con proyectiles.')]:
        if key.startswith(prefix):
            return desc
    return ''


def effect_lines(row):
    out = []
    food = row.get('food')
    if food:
        out.append(f"Hambre: {food['nutrition']} puntos. Saturacion: {food['saturation']}.")
    effects = list((row.get('potion') or {}).get('custom_effects', []))
    base = (row.get('potion') or {}).get('potion')
    if base and base != 'minecraft:water':
        out.append('Pocion base: ' + EFFECTS.get(base.split(':')[-1], base.split(':')[-1].replace('_', ' ')) + '.')
    if row.get('cooldown'):
        out.append(f"Espera entre usos: {row['cooldown']['seconds']:g} s.")
    for action in (row.get('consumable') or {}).get('on_consume_effects', []):
        effects += action.get('effects', []) if isinstance(action.get('effects', []), list) else []
        if action['type'].endswith('teleport_randomly'):
            out.append(f"Teletransporte aleatorio: diametro {action.get('diameter', 16)} bloques.")
    for e in effects:
        name = e['id'].split(':')[-1]
        out.append(f"{EFFECTS.get(name, name.replace('_', ' ').capitalize())} {e.get('amplifier', 0) + 1}: {e.get('duration', 0) / 20:g} s.")
    return out


def catalog():
    return json.loads(CATALOG.read_text(encoding='utf8'))


def extend_source(source):
    """Copia: no modifica la captura compartida ni los datos del llamador."""
    data = json.loads(json.dumps(source))
    for e in data['index']:
        if e.get('dialog') == 'atlas/seccion/cocina':
            e['caption'] = 'Comida'
    existing = {e.get('dialog') for e in data['index']}
    for key, caption in [('crafteos', 'Crafteos'), ('stellarity', 'Stellarity (El End)')]:
        target = 'atlas/seccion/' + key
        if target not in existing:
            data['index'].append(dict(caption=caption, dialog=target))
    return data


def menus(data):
    import guia_cofre as g
    cat = catalog()
    out = {}

    def link(name):
        return ['[openguimenu] ' + name]

    def icon(material, name, lore=(), model=None):
        it = dict(material=material, name='&b' + name, lore=g.wrap(['&7' + s for s in lore], 38))
        if model:
            it['model'] = model
        return it

    def stack(key, count=1):
        if isinstance(key, list):
            it = stack(key[0], count)
            it['lore'] += g.wrap(['&7Alternativas: ' + ', '.join(key)])
            return it
        if key.startswith('stellarity:'):
            key = key.split(':', 1)[1]
        row = cat['items'].get(key)
        if row:
            it = icon(row['material'].split(':')[-1].upper(), row['name'], row['description'], row.get('model'))
        else:
            if key.startswith('#'):
                tag = key
                candidates = cat['tags'].get(tag, [])
                it = stack(candidates[0] if candidates else 'minecraft:paper', count)
                it['lore'] += g.wrap(['&7Grupo: ' + tag, '&7Admite: ' + ', '.join(candidates)])
                return it
            it = icon(key.split(':')[-1].upper(), cat.get('vanilla_names', {}).get(key, key.split(':')[-1].replace('_', ' ').capitalize()))
        it['amount'] = min(count, 64)
        if count > 1:
            it['lore'].insert(0, f'&fCantidad exacta: {count}')
        return it

    def requirement():
        return ['open_requirement:', '  requirements:', '    prueba:', '      type: has permission',
                '      permission: ' + PERMISSION, '    dueno:', '      type: string equals',
                "      input: '%player_name%'", "      output: 'ByTrainx'", '  deny_commands:',
                "  - '[message] &eEsta ampliacion esta en prueba con el dueno.'"]

    def page(name, caption, content, parent=None, prev=None, next=None, recipe=False):
        bg = 'receta_stellarity' if recipe else 'general'
        lines = [f'menu_title: {g.q(g.title(g.BG_CHARS[bg], caption))}', 'size: 54'] + requirement() + ['items:']
        if recipe:
            pairs = content
        else:
            pairs = list(zip(g.content_slots(len(content), False), content))
        for n, (slot, (it, cmds)) in enumerate(pairs):
            lines += g.yaml_item('material' + str(n) if recipe else 'c' + str(n), slot, it, cmds)
        nav = dict(back=link(parent or g.MENU))
        if prev:
            nav['prev'] = link(prev)
        if next:
            nav['next'] = link(next)
        lines += g.nav_items(nav, name)
        out[name] = '\n'.join(lines) + '\n'

    comida = 'g_atlas_seccion_cocina'
    crafteos = 'g_atlas_seccion_crafteos'
    end = 'g_atlas_seccion_stellarity'
    page(comida, 'Comida', [
        (icon('COOKED_BEEF', 'Comida y curacion', ['La comida llena hambre y saturacion. La curacion natural rinde 20% del ajuste Astral anterior; no reemplaza las manzanas de tu tier.']), []),
        (icon('CAULDRON', 'Crop & Kettle 1.3.12', ['Integracion preparada: despliegue actual sin confirmar. No se promete disponible.', 'Cuando se habilite: olla = caldero + fogata; recetario y avances para empezar.']), link('g_guia_comida_cnk')),
        (icon('APPLE', 'Manzanas de mazmorra', ['T2 a T10: curan 45% de la vida del set de su tier. Mitad al comer y mitad en 5 s. Espera compartida: 20 s.', 'Caen de mobs de mazmorra del mismo tier: comunes 3%, elites 12%.']), []),
        (icon('GOLDEN_APPLE', 'XP y Suerte Astral', ['Manzana de la Suerte y frascos de experiencia: ver Consumibles.']), link('g_atlas_seccion_consumibles')),
        (icon('CHORUS_FRUIT', 'Comida del End', ['Platos, peces y sus recetas de Stellarity.']), link('g_guia_stellarity_food_1')),
        (icon('GOLDEN_CARROT', 'Fuera de pelea', ['Sistema preparado en prueba: tras 20 s sin combatir, cura 4% de vida maxima por segundo sin gastar comida.', 'Solo ByTrainx hasta que el dueno lo abra; no se promete activo para todos.']), []),
    ])
    page('g_guia_comida_cnk', 'Cocina preparada', [
        (icon('CAULDRON', 'Olla', ['Caldero + fogata. Integracion pendiente de confirmar en vivo.']), []),
        (icon('KNOWLEDGE_BOOK', 'Recetario', ['El recetario y los avances propios muestran las recetas descubiertas.']), []),
        (icon('WHEAT_SEEDS', 'Cultivos nuevos', ['Hay semillas y cultivos de cocina. Cultivalos en survival cuando se habilite la integracion.']), []),
        (icon('IRON_SWORD', 'Tabla y cuchillo', ['Permiten cortar ingredientes. Tambien hay un bol para mezclas.']), []),
        (icon('MUSHROOM_STEW', 'Platos y bebidas', ['Ejemplo: Wellington combina masa, hongos y carne en la olla. En la tabla, carne de vaca da cortes y masa da fideos.', 'Incluye sopas, cafe y vinos. Consulta el recetario propio al habilitarlo.']), []),
        (icon('LEATHER_HELMET', 'Gorro de chef', ['Mesa: dos lanas blancas en la primera fila, otras dos debajo y dos hilos en la tercera. Usa las mismas dos columnas.', 'Solo cuando Crop & Kettle este instalado.']), []),
    ], comida)
    links = [('SMITHING_TABLE', 'Forja Astral', 'Cerca de una mesa de herreria, abri la receta en la guia y usa Forjar. Toma materiales del inventario y exige los niveles del resultado.', 'g_atlas_berserker'),
             ('CRAFTING_TABLE', 'Mesa y libro verde', 'AstralDecor registra recetas en la mesa. Tener un ingrediente desbloquea su receta en el libro verde. Exige los mismos objetos y niveles. Mas de 9 unidades: solo Forja.', 'g_atlas_seccion_materiales'),
             ('ENCHANTING_TABLE', 'AstralMesa', 'Usa la mesa de encantamientos para elegir mejoras compatibles y pagar experiencia. Las mejoras del Herrero Astral quedan aparte.', None),
             ('AMETHYST_SHARD', 'Reforja de gemas', 'En el Herrero, entra a Gemas. Las ranuras dependen del tier del equipo; la reforja no es una receta de mesa.', None),
             ('CHEST', 'Mochilas', 'Recetas y mejoras conservando el contenido. Netherite usa mesa de herreria vanilla, no el boton de Forja Astral.', g.MOCHILAS_MENU),
             ('DIAMOND_PICKAXE', 'Taladros', 'Abri cada herramienta para consultar sus materiales, niveles y receta.', 'g_atlas_seccion_taladros'),
             ('IRON_AXE', 'Motosierras', 'Consulta las mejoras encadenadas y los materiales exactos.', 'g_atlas_seccion_motosierras'),
             ('END_STONE', 'Stellarity', 'Sus altares y caldero son sistemas propios. No se fabrican con Forjar de Astral.', end)]
    page(crafteos, 'Crafteos', [(icon(mat, name, [desc]), link(target) if target else []) for mat, name, desc, target in links])
    groups = [('weapons', 'Armas', 'DIAMOND_SWORD'), ('armor', 'Armaduras y alas', 'ELYTRA'),
              ('books', 'Libros de hechizos', 'ENCHANTED_BOOK'), ('tools', 'Herramientas', 'DIAMOND_PICKAXE'),
              ('trinkets', 'Accesorios', 'AMETHYST_SHARD'), ('food', 'Comidas y peces', 'CHORUS_FRUIT'),
              ('potions', 'Pociones', 'POTION'), ('materials', 'Materiales y bloques', 'PURPUR_BLOCK')]
    page(end, 'Stellarity - El End', [
        (icon('END_PORTAL_FRAME', 'Explorar el End', ['Entra por el portal de una fortaleza del survival.', 'En Astral el dragon esta retirado y los accesos exteriores estan abiertos. Explora sin sustituir ni reiniciar el mundo.']), []),
        (icon('SHIELD', 'Equipo y dificultad', ['El dano fijo de Stellarity no recibe automaticamente la escala Astral x5 por tier. Puede rendir poco contra mobs escalados.', 'Alas y vuelo pueden generar avisos de GrimAC; no cambies protecciones para usarlos.']), []),
    ] + [(icon(mat, label, ['Objetos, usos y efectos.']), link('g_guia_stellarity_' + key + '_1')) for key, label, mat in groups] + [
        (icon('WITHER_SKELETON_SKULL', 'Jefes y criaturas', ['Apariciones y botin del End.']), link('g_guia_stellarity_jefes')),
        (icon('END_STONE', 'Biomas y estructuras', ['Donde explorar.']), link('g_guia_stellarity_mundo_1')),
        (icon('ENCHANTING_TABLE', 'Altares', ['Ofrendas y mecanismos propios.']), link('g_guia_stellarity_altares')),
        (icon('CRAFTING_TABLE', 'Todas las recetas', ['Mesa, horno, fogata, altar y caldero.']), link('g_guia_stellarity_recetas_1')),
    ])
    for group, label, _ in groups:
        rows = [(k, v) for k, v in cat['items'].items() if v['group'] == group]
        chunks = [rows[i:i + 21] for i in range(0, len(rows), 21)] or [[]]
        for n, chunk in enumerate(chunks, 1):
            name = f'g_guia_stellarity_{group}_{n}'
            content = []
            for key, row in chunk:
                matches = [r for r in cat['recipes'] if r['result'].get('item') == key]
                it = stack(key)
                if matches:
                    it['lore'] += ['', '&eClic para ver su receta.']
                content.append((it, link('g_guia_stellarity_r_' + matches[0]['id']) if matches else []))
            page(name, label + f' {n}/{len(chunks)}', content, end,
                 f'g_guia_stellarity_{group}_{n-1}' if n > 1 else None,
                 f'g_guia_stellarity_{group}_{n+1}' if n < len(chunks) else None)
    all_recipes = cat['recipes']
    chunks = [all_recipes[i:i + 21] for i in range(0, len(all_recipes), 21)]
    for n, chunk in enumerate(chunks, 1):
        content = []
        for recipe in chunk:
            result = recipe['result']
            it = stack(result.get('item', result.get('id')), result.get('count', 1))
            it['lore'] = ['&6' + recipe['station'], '&eClic: ingredientes y cantidades']
            content.append((it, link('g_guia_stellarity_r_' + recipe['id'])))
        page(f'g_guia_stellarity_recetas_{n}', f'Recetas del End {n}/{len(chunks)}', content, end,
             f'g_guia_stellarity_recetas_{n-1}' if n > 1 else None,
             f'g_guia_stellarity_recetas_{n+1}' if n < len(chunks) else None)
        for recipe in chunk:
            result = recipe['result']
            result_item = stack(result.get('item', result.get('id')), result.get('count', 1))
            for effect in result.get('components', {}).get('minecraft:suspicious_stew_effects', []):
                key = effect['id'].split(':')[-1]
                result_item['lore'] += [f"&7{EFFECTS.get(key, key)}: {effect['duration'] / 20:g} s."]
            content = [(g.OUTPUT, (result_item, []))]
            content += [(slot, (stack(ing['item'], ing['count']), [])) for slot, ing in zip(g.INGREDIENTS, recipe['grid']) if ing]
            tips = [recipe['station']]
            if recipe['station'] == 'Altar Maldito':
                tips += ['Tira los ingredientes juntos sobre el altar activado. Sin forma. No usa la Forja Astral.']
            elif recipe['station'] == 'Caldero de dragon':
                tips += ['Caldero con agua y aliento de dragon. Tira los ingredientes; sin forma.', f"Consume {recipe['breath']} cargas de aliento (7 por carga inicial)."]
            elif recipe.get('seconds'):
                tips += [f"Tiempo: {recipe['seconds']:g} s. Experiencia: {recipe['experience']:g}."]
            if recipe.get('warning'):
                tips += ['ATENCION: ' + recipe['warning']]
            if recipe.get('note'):
                tips += [recipe['note']]
            info = icon('KNOWLEDGE_BOOK', recipe['station'], tips)
            # Misma plantilla; la cinta inferior dice METODO y no ejecuta crafteos.
            content += [(slot, (info if slot == 40 else dict(material='PAPER', model='astral:viajes/blank', name=' '), [])) for slot in g.FORGE]
            page('g_guia_stellarity_r_' + recipe['id'], g.plain(result_item['name']), content,
                 f'g_guia_stellarity_recetas_{n}', recipe=True)
    page('g_guia_stellarity_altares', 'Altares del End', [
        (icon('END_PORTAL_FRAME', 'Altar Maldito', ['Se activa por la progresion del dragon. Tira cantidades exactas juntas; sirve para mejoras, libros y colores de elytra.', 'Astral retira al dragon: verificar que el altar este activo antes de prometer que todas las mejoras se pueden obtener.']), []),
        (icon('ENCHANTING_TABLE', 'Altar Sagrado', ['Ofrendas: hierro = Resistencia; oro = Prisa; esmeralda = Heroe de la aldea; diamante = Velocidad; netherite = Resistencia al fuego.']), []),
        (icon('GLOWSTONE_DUST', 'Empress of Light', ['Ofrenda Starlight Soot al Altar Sagrado. No en Pacifico ni con otra Empress activa.']), []),
        (icon('SHULKER_SHELL', 'Shulking', ['Ofrenda Cuerpo de Shulker al Altar Sagrado. No en Pacifico ni con otro Shulking cerca.']), []),
        (icon('DRAGON_BREATH', 'Caldero de dragon', ['Caldero con agua + aliento de dragon: 7 cargas. Cada receta consume cargas. No es la olla de Crop & Kettle.']), link('g_guia_stellarity_recetas_1')),
    ], end)
    page('g_guia_stellarity_jefes', 'Jefes y criaturas', [(icon(mat, name, [desc]), []) for mat, name, desc in cat['mobs']], end)
    worlds = [('Bioma: ' + s.replace('_', ' ').title(), 'Bioma propio de Stellarity.') for s in cat['world']['biome']]
    worlds += [('Estructura: ' + s.replace('_', ' ').title(), 'Explora zonas nuevas del End para encontrarla; no se regeneran chunks existentes.') for s in cat['world']['structure']]
    for offset in range(0, len(worlds), 21):
        n = offset // 21 + 1
        page(f'g_guia_stellarity_mundo_{n}', f'Explorar el End {n}', [(icon('END_STONE', a, [b]), []) for a, b in worlds[offset:offset + 21]], end,
             f'g_guia_stellarity_mundo_{n-1}' if n > 1 else None,
             f'g_guia_stellarity_mundo_{n+1}' if offset + 21 < len(worlds) else None)
    return out
