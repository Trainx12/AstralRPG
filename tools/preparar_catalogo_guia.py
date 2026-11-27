"""Reproduce el catalogo de hechos y el informe privado a partir de ZIP locales."""
import collections
import json
from pathlib import Path
import re
import sys
import zipfile
from inventariar_stellarity import ROOT, inventory, walk

sys.path.insert(0, str(ROOT / 'datapack-src'))
from guia_ampliacion import item_description, effect_lines


def prepare():
    data, evidence = inventory(ROOT / '.local/dp-server/Stellarity-5.4.2.zip', ROOT / 'datapack-src/pack-source/terceros/Stellarity-6.0.1-RP.zip')
    z = zipfile.ZipFile(ROOT / '.local/dp-server/Stellarity-5.4.2.zip')
    names = z.namelist()
    rp = zipfile.ZipFile(ROOT / 'datapack-src/pack-source/terceros/Stellarity-6.0.1-RP.zip')
    resource_names = set(rp.namelist())
    public = {k: data[k] for k in ['version', 'sha256', 'recipes', 'world']}
    public['items'] = {}
    stat_names = dict(attack_damage='Dano', attack_speed='Velocidad de ataque', armor='Armadura', armor_toughness='Dureza',
                      knockback_resistance='Resistencia al empuje', max_health='Vida maxima', movement_speed='Velocidad',
                      luck='Suerte', safe_fall_distance='Caida segura')
    for key, row in data['items'].items():
        source = row['source'].split('/loot_table/')[1]
        group = ('armor' if '/armor/' in source else 'weapons' if '/weapon/' in source else 'books' if '/spellbook/' in source
                 else 'tools' if '/tool/' in source else 'trinkets' if '/trinket/' in source else 'potions' if '/potion/' in source
                 else 'food' if '/food/' in source else 'materials')
        description = [item_description(key)] if item_description(key) else []
        description += effect_lines(row)
        for s in row['stats']:
            attr = s.get('attribute', s.get('type', '')).split(':')[-1]
            amount = s['amount']
            op = s['operation']
            value = f'{amount * 100:+g}%' if 'multiplied' in op else f'{amount:+g}'
            description.append(f"{stat_names.get(attr, attr.replace('_', ' ').capitalize())}: {value} ({s.get('slot', 'equipo')}).")
        if not description:
            description = [{'materials': 'Material, bloque u objeto de exploracion del End. Su obtencion depende del botin y la progresion.',
                            'food': 'Pez o comida del End. Tambien puede usarse como ingrediente.',
                            'potions': 'Pocion del recetario del End.', 'armor': 'Equipo de proteccion del End.',
                            'trinkets': 'Accesorio del End. Revisa la descripcion del objeto al obtenerlo.'}.get(group, 'Objeto especial del End; disponibilidad segun botin y progresion.')]
        if 'Donator' in ' '.join(row['lore']) or 'Developer' in ' '.join(row['lore']):
            description.append('Objeto especial del autor: figurar en el catalogo no garantiza conseguirlo en survival.')
        clean_name = row['name']
        if clean_name.startswith(('item.', 'block.')):
            clean_name = key.replace('_', ' ').title()
        model = row['model']
        if model and 'assets/' + model.replace(':', '/items/') + '.json' not in resource_names:
            model = None
        public['items'][key] = dict(name=clean_name, material=row['material'], model=model, original_model=row['model'], group=group,
                                    description=description, source=row['source'])
    # Resolver los grupos de ingredientes para mostrar alternativas reales, no PAPER ficticio.
    public['tags'] = {}
    def tag_values(tag, seen=()):
        if tag in seen:
            raise ValueError('Tag circular: ' + tag)
        ns, key = tag[1:].split(':')
        path = f'data/{ns}/tags/item/{key}.json'
        if path not in names:
            defaults = {'#minecraft:planks': ['minecraft:' + wood + '_planks' for wood in
                                             ('oak', 'spruce', 'birch', 'jungle', 'acacia', 'dark_oak', 'mangrove', 'cherry', 'pale_oak', 'bamboo', 'crimson', 'warped')],
                        '#minecraft:stone_crafting_materials': ['minecraft:cobblestone', 'minecraft:blackstone', 'minecraft:cobbled_deepslate'],
                        '#minecraft:smelts_to_glass': ['minecraft:sand', 'minecraft:red_sand']}
            if tag not in defaults:
                raise ValueError('Falta resolver tag ' + tag)
            return defaults[tag]
        vals = []
        for v in json.loads(z.read(path))['values']:
            v = v.get('id') if isinstance(v, dict) else v
            vals += tag_values(v, (*seen, tag)) if v.startswith('#') else [v]
        return list(dict.fromkeys(vals))
    for r in public['recipes']:
        for ing in r['grid']:
            if ing and isinstance(ing['item'], str) and ing['item'].startswith('#'):
                public['tags'][ing['item']] = tag_values(ing['item'])
    vanilla = dict(chorus_fruit='Fruta chorus', chorus_plant='Planta de chorus', chorus_flower='Flor de chorus',
                   end_stone='Piedra del End', blaze_powder='Polvo de blaze', glass='Vidrio', gunpowder='Polvora',
                   popped_chorus_fruit='Fruta chorus horneada', leather='Cuero', phantom_membrane='Membrana de phantom',
                   paper='Papel', water_bucket='Balde de agua', sugar='Azucar', bowl='Cuenco', ender_eye='Ojo de ender',
                   iron_ingot='Lingote de hierro', gold_block='Bloque de oro', netherite_ingot='Lingote de netherite',
                   netherite_helmet='Casco de netherite', netherite_chestplate='Pechera de netherite', netherite_leggings='Pantalones de netherite',
                   netherite_boots='Botas de netherite', red_mushroom='Hongo rojo', brown_mushroom='Hongo marron',
                   glass_bottle='Botella de vidrio', nether_wart='Verruga del Nether', redstone='Redstone', glowstone_dust='Polvo de piedra luminosa')
    public['vanilla_names'] = {'minecraft:' + k: v for k, v in vanilla.items()}
    locations = dict(empress_of_light='Ofrenda Starlight Soot en el Altar Sagrado; botin distinto de dia y noche.',
                     shulking='Ofrenda Cuerpo de Shulker en el Altar Sagrado.', ender_dragon='Jefe original del End, retirado por Astral: su botin no se promete disponible.',
                     flesh_piglin='Criatura de las zonas de carne del End.', frosted_stray='Esqueleto de las zonas heladas del End.',
                     phantom_buffed='Phantom modificado del End.', pixie='Criatura de las zonas Hallow.',
                     voided_silverfish='Lepisma del vacio.', voided_skeleton='Esqueleto del vacio.',
                     voided_slime='Slime del vacio.', voided_zombie='Zombi del vacio.', kohara='Entidad especial del autor; no se promete aparicion natural.')
    mobs = []
    loot_details = []
    for n in names:
        if n.startswith('data/stellarity/loot_table/entity/') and n.endswith('.json'):
            key = n.split('/entity/')[1][:-5]
            obj = json.loads(z.read(n))
            drops = list(dict.fromkeys(v.get('value', v.get('name')) for v in walk(obj)
                                      if v.get('type') in ('loot_table', 'item', 'minecraft:loot_table', 'minecraft:item')
                                      and isinstance(v.get('value', v.get('name')), str)))
            loot_details.append((key, drops, obj))
            if key.startswith('empress_of_light/'):
                continue
            pretty = [d.split('/')[-1].replace('_', ' ') for d in drops if isinstance(d, str)]
            desc = locations.get(key, 'Habitante de las fortalezas renovadas.') + ' Botin posible: ' + ', '.join(pretty) + '. No todos los premios son garantizados.'
            mat = 'SHULKER_SHELL' if key == 'shulking' else 'DRAGON_HEAD' if key == 'ender_dragon' else 'ZOMBIE_HEAD'
            mobs.append([mat, key.replace('_', ' ').replace('/', ' - ').title(), desc])
    empress = 'Empress of Light: Altar Sagrado + Starlight Soot. Botin posible: Prismatic Punch, Prismember, Starstruck Shield y Prismatic Pearl; de dia tambien Soaring Insignia y Kaleidoscope. Dificultad y premios cambian segun la pelea.'
    mobs.insert(0, ['NETHER_STAR', 'Empress of Light', empress])
    public['mobs'] = mobs
    (ROOT / 'datapack-src/guia_stellarity.json').write_text(json.dumps(public, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    report = ['# Stellarity, comida y crafteos de AstralRPG — 26/11/2026',
              'Informe local. Describe los originales encontrados, no certifica el estado remoto. No contiene mapas ni credenciales.',
              '## Fuentes y alcance',
              'ZIP: `.local/dp-server/Stellarity-5.4.2.zip`; copia tambien en Downloads. SHA-256: `' + data['sha256'] + '`.',
              'La version proviene del archivo y docs/SERVIDOR.md. pack.mcmeta no declara una version semantica. Traducciones contrastadas con el RP local 6.0.1: faltan claves y hay textos en ingles; los efectos numericos provienen del datapack, no de ese RP.',
              f"Inventario: {len(data['items'])} objetos, {len(data['recipes'])} recetas/transformaciones. Se incluyen las recetas vanilla sobreescritas. Se excluyen cinco recetas tecnicas de barrera/structure_void usadas por eventos de libros: no son crafteos para jugadores.",
              '## Diferencias y choques con Astral',
              'Stellarity es expansion del End. Se llega por una fortaleza del survival. Astral retira el dragon y deja salida y gateways abiertos (build.py). Su muerte original activa el Altar Maldito: comprobar la activacion real; no se reactiva ni se invoca un dragon desde esta tarea.',
              'El dano de Astral y la vida de mobs usan escala.py (x5 por tier). Armas de Stellarity conservan valores propios: no asumir que compiten con las armas Astral de tiers altos. No cambiamos el balance.',
              'GrimAC 2.3.74 esta documentado en solo avisa. Las alas y encantamientos de vuelo de Stellarity pueden generar falsos avisos. No se encontraron pruebas de una exclusion total de alas; no presentarla como existente ni apagar anticheat. AstralMesa excluye encantamientos internos/tecnicos y mejoras del namespace astral.',
              'La receta Frost Cloud exige amount=6 pero lista cinco ingredientes (incluido hielo duplicado). Se conserva como advertencia, no se corrige el datapack de terceros sin encargo.',
              'Los modelos stellarity:bell_flower y stellarity:chorus_petal no existen en el RP local 6.0.1 ni en el FINAL publicado descargado. Sus tarjetas usan la base vanilla; se conserva el ID original en el catalogo como evidencia, sin inventar arte.',
              '## Objetos: usos, atributos y efectos',
              'Hambre y saturacion se expresan en puntos, no en corazones curados. Un efecto de regeneracion no equivale a una cura fija bajo los ajustes de Astral. Los atributos muestran el modificador del objeto, no el dano final del jugador.']
    for key, row in public['items'].items():
        report += [f"### {row['name']} (`{key}`)", ' '.join(row['description']), f"Base: `{row['material']}`; modelo: `{row['model'] or 'vanilla (sin modelo propio)'}`. Fuente: `{row['source']}`."]
        raw = data['items'][key]
        # Complemento local completo del tooltip original para los casos sin traduccion.
        if raw['lore']:
            report += ['Texto del original (puede estar en ingles): ' + ' / '.join(raw['lore'])]
    report += ['## Todas las recetas y transformaciones',
               'Mesa con forma: cada fila se lee de izquierda a derecha; VACIO conserva el hueco. Altares y caldero: la grilla es una lista sin forma, se tiran objetos en el mecanismo. Cantidades exactas. La plantilla de enderita se duplica a DOS unidades.']
    for r in public['recipes']:
        result = r['result']; key = result.get('item', result.get('id'))
        report += [f"### {r['id']} — {result.get('count', 1)} x {key}", f"Metodo: **{r['station']}**. Fuente: `{r['source']}`."]
        for offset in range(0, len(r['grid']), 3):
            report += [' | '.join('VACIO' if not i else f"{i['count']} x {i['item']}" for i in r['grid'][offset:offset + 3])]
        if r.get('breath'):
            report += [f"Gasta {r['breath']} cargas; un aliento en caldero con agua habilita 7."]
        if r.get('seconds'):
            report += [f"Coccion: {r['seconds']:g} segundos, XP {r['experience']:g}."]
        for k in ('warning', 'note'):
            if r.get(k): report += [r[k]]
        if result.get('components'):
            report += ['Efectos del resultado: ' + json.dumps(result['components'], ensure_ascii=False)]
    report += ['## Jefes, criaturas y botin', empress,
               'Las listas siguientes incluyen variantes de botin y condiciones; una entrada no significa que todos esos objetos caigan siempre.']
    report += [f'### {key}\n' + ', '.join(map(str, drops)) + '\nCondiciones y cantidades: `' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '`' for key, drops, obj in loot_details]
    report += ['## Biomas y estructuras', 'Biomas: ' + ', '.join(public['world']['biome']),
               'Estructuras: ' + ', '.join(public['world']['structure']),
               'Los bloques nuevos incluyen tierras del End, caminos, pasto, tierra con raices, bloque de enderita, luz de rana ceniza, altares y marco fantasma. Se implementan con bloques/entidades vanilla y modelos, no agregan IDs de bloques nuevos al cliente. Los chunks ya generados no se reemplazan.']
    report += ['## Altares y mecanismos',
               'Altar Maldito: fabricar con objetos tirados cerca del altar activado, no en mesa de herreria. Sus controles usan radio 1,5 bloques y cantidad exacta de tipos. Ofrece mejoras de netherite, libros, duplicado de plantillas y tintes de elytra. Conserva componentes del objeto base en mejoras craft_weapon.',
               'Altar Sagrado: se puede colocar. Hierro da Resistencia; oro Prisa; esmeralda Heroe de la aldea; diamante Velocidad; netherite Resistencia al fuego. La duracion depende de la ofrenda: base 300 + 2*n^2/100 segundos (n es el conteo escalado que prepara cada funcion), por multiplicador 0,6 / 0,7 / 0,85 / 1,1 / 3,8 respectivamente. Ver funciones de evidencia, no estimar duracion a partir de stacks sin aplicar el conteo real.',
               'Starlight Soot invoca Empress; Cuerpo de Shulker invoca Shulking. No funciona en Pacifico; hay controles para evitar jefes duplicados. El reroll de Treasure Head tiene su llamada a loot comentada en este ZIP: no prometer premios.',
               'Caldero con agua + aliento de dragon (7 cargas), hasta seis ingredientes. Es distinto a la olla de CNK. Pesca del vacio: utiliza el mecanismo de Stellarity, con peces, ingredientes y tesoros; Fisher of Voids acelera la espera.']
    report += ['## Comida — Crop & Kettle 1.3.12 y Astral',
               'La documentacion dice sin desplegar, pero existe una copia en backup-server-17-11/world/datapacks: eso prueba una instalacion historica, no su presencia actual. No se consulto el panel. La guia dice preparado, despliegue actual sin confirmar.',
               'Olla = caldero + fogata; tabla de cortar y cuchillo para cortes; bol para mezclas. Recetario/avances para descubrir platos. Gorro de chef: mesa con dos columnas de lana blanca en filas 1 y 2, y dos hilos en fila 3 (4 lana + 2 hilos).',
               'Integracion limitada al survival y namespace cnk en AstralProgression para evitar estructuras fuera de survival. Los originales y derivados CNK son privados.',
               'Astral: comida natural multiplicada por REGEN_COMIDA=0.2. Fuera de pelea: regen_fuera_pelea.py prepara 20 segundos de espera y 4%/s sin comida, privado para ByTrainx hasta abrirlo. No se certifica variable remota.',
               'Manzanas T2-T10: cura fija = 45% de VIDA_SET del tier, mitad inmediata y mitad en 5 segundos; cooldown compartido 20 segundos. Drops: 3% comunes, 12% elites de mazmorra del mismo tier. Manzana de Suerte: cinco minutos acumulables para compras de gachas; no es una manzana de curacion. Frascos XP son consumibles de experiencia.',
               'No se encontro otro plugin de comida especifico documentado; Stellarity y CNK son datapacks, AstralDecor/Skript implementan los consumibles y la curacion propios.',
               '### Cultivos y recetario CNK exacto (anexo privado)',
               'Se listan las definiciones originales de recetas y funciones de cocina. Los metodos son los directorios; no confundir las recetas auxiliares con platos terminados.']
    cnk = zipfile.ZipFile(ROOT / '.local/terceros/crop-kettle/CropAndKettle-v1.3.12-Data-Pack.zip')
    plants = [n for n in cnk.namelist() if n.startswith('data/cnk/loot_table/') and any(s in n for s in ['/seed', '/crop']) and n.endswith('.json')]
    report += ['Cultivos/semillas presentes: ' + ', '.join(n.split('/loot_table/')[1][:-5] for n in plants)]
    for n in cnk.namelist():
        if (n.startswith('data/cnk/recipe/') and n.endswith('.json')) or (n.startswith('data/cnk/function/recipes/') and n.endswith('.mcfunction')):
            report += ['#### ' + n, '```' + ('json' if n.endswith('.json') else 'text') + '\n' + cnk.read(n).decode() + '\n```']
    report += ['## Crafteos de AstralRPG',
               'Forja Astral: al lado de mesa de herreria, abrir receta en Guia y pulsar Forjar. Usa inventario, objetos exactos y niveles requeridos. Las recetas de mas de nueve unidades quedan solo en Forja.',
               'AstralDecor: registra en mesa las recetas elegibles; ingrediente nuevo desbloquea receta en libro verde. No cualquier objeto vanilla reemplaza un material Astral. Generador build.py y tabla build/runtime/mesa.json; el runtime debe corresponder al datapack.',
               'AstralMesa: mesa de encantamientos y XP; opciones compatibles vanilla, ExcellentEnchants y datapacks; excluye internos y mejoras del Herrero (astral). Reforja de gemas: boton Gemas en Herrero; ranuras por tier, no mesa vanilla.',
               'Mochilas ExpendableBackpacks: cuero LSL/LCL/LLL, L=cuero S=hilo C=cofre. Mejoras con mochila anterior en el centro y ocho materiales alrededor; netherite con plantilla de netherite + mochila de diamante + lingote en herreria vanilla. Ender: EPE/PCP/EIE, E=ojo de ender P=perla C=cofre I=bloque hierro; copia sin forma mochila Ender + perla. Contenido y permisos dependen del plugin; consultar ventanas existentes.',
               'Taladros y motosierras: mejoras encadenadas y requisitos propios. No se duplican cantidades en este informe: consultar las recetas reales capturadas de build.py en la Guia. Las ventanas nuevas enlazan a esos catalogos.',
               '## Evidencia mecanica',
               'Las funciones completas consultadas se guardan solo localmente en stellarity-evidencias.json. No se publica codigo, lang ni arte del datapack de terceros.']
    private = ROOT / '.local/coordination'
    (private / 'stellarity-informe.md').write_text('\n\n'.join(report) + '\n', encoding='utf8')
    (private / 'stellarity-evidencias.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf8')
    print('Catalogo publico:', len(public['items']), 'objetos,', len(public['recipes']), 'recetas. Informe privado generado.')


if __name__ == '__main__':
    prepare()
