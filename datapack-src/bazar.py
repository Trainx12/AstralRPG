"""Bazar privado: catálogo canónico y JAR. No regenera salidas ajenas.

python bazar.py --jdk <bin JDK25> [--server ../.local/testsrv]
"""
import argparse
import json
import os
import re
import subprocess
import zipfile
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'build/bazar'

# Compilation of the published catalog must not import unrelated, unpublished
# generators. The normal generation command reads the live source tables below.
if '--solo-compilar' not in sys.argv:
    import economia as E
    from items import MATERIALS
    import gemas
    import manzanas
    from tanda4b import COINS
    EQUIPO_POR_TIER = {t: E.PLATA_MOB_TIER[t] * 2 for t in range(1, 11)}
# Tabla editable: id -> (categoría, referencia). Nombre/material/componentes se leen
# de los generadores reales, nunca se inventan duplicados de los ítems.
    PRODUCTOS = {iid: ('Combate', 15000) for iid in MATERIALS}
    PRODUCTOS.update({
    'netherita_fundida': ('Mineria', 10000),
    'netherita_reforzada': ('Mineria', 20000),
    'madera_estelar': ('Bosque y pesca', 5000),
    'palo_reforzado': ('Bosque y pesca', 10000),
    'perla_abisal': ('Bosque y pesca', 15000),
    'coral_astral': ('Bosque y pesca', 10000),
    'cristal_caverna': ('Especiales', E.CAVERNAS_PRECIO['cristal_caverna'] * 2),
    'geoda_estelar': ('Especiales', E.CAVERNAS_PRECIO['geoda_estelar'] * 2),
    'polvo_cristal': ('Especiales', 100000),
    'fragmento_estelar': ('Especiales', E.VACIO_PRECIO['fragmento_estelar'] * 2),
    'nucleo_meteorito': ('Especiales', E.VACIO_PRECIO['nucleo_meteorito'] * 2),
    'colmillo_carnivoro': ('Combate', 30000),
    })
    for tipo in gemas.TIPOS:
        for q in gemas.CALIDADES:
            PRODUCTOS[f'gema_{tipo}_{q}'] = ('Especiales', 10000 * 4 ** (q - 1))
    for t in manzanas.TIERS:
        PRODUCTOS[manzanas.iid(t)] = ('Consumibles', E.PLATA_MOB_TIER[t] * 4)
    for coin in COINS:
        PRODUCTOS['asura_moneda_' + coin] = ('Combate', 30000)
    PISOS = {**E.CAVERNAS_PRECIO, **E.VACIO_PRECIO}


def fuentes():
    # build.py registra todos los ítems antes de mesa/export_mesa (que escribe
    # archivos compartidos). Ejecutar SOLO esa sección, enteramente en memoria.
    source = (HERE / 'build.py').read_text(encoding='utf8')
    source = source.split('from mesa import prepare as prepare_mesa', 1)[0]
    ns = {'__file__': str(HERE / 'build.py'), '__name__': 'bazar_catalogo'}
    exec(compile(source, str(HERE / 'build.py'), 'exec'), ns)
    from balance_equipo import finalize
    finalize(ns['ITEMS'], ns['FICHAS'])
    return ns


def precios_referencia(ns):
    """Costo de reposición; supuestos de recolección explícitos, sin escribir otras salidas."""
    from items import MOB_DROPS, ELITE_DROPS
    from items_t6_10 import MATERIAL_TIER, DROP_MATERIAL
    import cavernas
    refs, notes = {}, {}
    vanilla = {}
    for data in E.tienda().values():
        for _, it in E._items_tienda(data):
            # Usar venta NPC cuando existe; compra de Tienda como alternativa.
            value = it.get('sell', -1)
            if value is None or value < 0:
                value = it.get('buy', 0)
            if value and value > 0:
                key = 'minecraft:' + str(it['material']).lower()
                vanilla[key] = max(vanilla.get(key, 0), value / (it.get('stack-size') or 1))
    def setref(iid, value, note):
        refs[iid] = round(max(value, PISOS.get(iid, 0), .1), 2)
        notes[iid] = note
    # El tier del survival se adapta al jugador; no hay tier fijo por especie.
    # Convención de balance revisable: Nether/End T5, vindicator Overworld T3.
    for group, (_, drops) in MOB_DROPS.items():
        tier = 3 if group == 'vindicator' else 5
        for iid, chance, condition in drops:
            value = E.PLATA_MOB_TIER[tier] / chance
            if iid not in refs or value < refs[iid]:
                setref(iid, value, f'items.MOB_DROPS/{group}: PLATA_MOB_TIER[{tier}] / {chance}; tier supuesto (survival adaptable)')
    for tier, drops in enumerate(ELITE_DROPS, 1):
        for iid, chance, qty in drops:
            if iid not in refs:
                setref(iid, E.PLATA_MOB_TIER[tier] / (chance * qty), f'items.ELITE_DROPS T{tier}: PLATA_MOB_TIER / ({chance} × {qty})')
    for tier, iid in MATERIAL_TIER.items():
        setref(iid, E.PLATA_MOB_TIER[tier] / DROP_MATERIAL['comun'], f'items_t6_10: T{tier} / probabilidad común {DROP_MATERIAL["comun"]}')
    for tier in manzanas.TIERS:
        setref(manzanas.iid(tier), E.PLATA_MOB_TIER[tier] / manzanas.PROB['comun'], f'manzanas.PROB común: T{tier} / {manzanas.PROB["comun"]}')
    setref('netherita_fundida', vanilla.get('minecraft:netherite_ingot', 0), 'Horno: 1 lingote netherita; precio venta NPC/Tienda (combustible sin precio = 0)')
    # Bloques/cofres no tienen pago de mob: unidad de esfuerzo explícita T5.
    for iid, chance, label in [('madera_estelar', .35, 'chorus End'), ('fragmento_cristal', .04, 'end stone'), ('gema_luminica', .25, 'cofre Overworld')]:
        setref(iid, E.PLATA_MOB_TIER[5] / chance, f'build.py {label}, probabilidad {chance}; supuesto unidad de esfuerzo T5 por bloque/cofre')
    for iid in ('perla_abisal', 'coral_astral'):
        setref(iid, E.PLATA_MOB_TIER[2], 'Veta Océano (escala.TIER_FIJO=2), 1 unidad; supuesto esfuerzo de un mob T2 por veta')
    for iid, value in PISOS.items():
        if iid in PRODUCTOS:
            setref(iid, value, 'Precio de venta NPC en economia.CAVERNAS_PRECIO/VACIO_PRECIO (piso y referencia)')
    setref('polvo_cristal', E.PLATA_MOB_TIER[cavernas.TIER] / .02, 'cavernas.py mob exterior T4 / drop 0.02')
    for tipo in gemas.TIPOS:
        for q in gemas.CALIDADES:
            weights = cavernas.CALIDAD['honda']
            prob = weights[q-1] / sum(weights)
            setref(f'gema_{tipo}_{q}', E.PLATA_MOB_TIER[cavernas.TIER] / prob,
                   f'Veta honda de {tipo}: CALIDAD {weights[q-1]}/{sum(weights)}; supuesto esfuerzo de un mob T4 por veta, sin polvo')
    # No existe una tabla de drops publicada para estas seis monedas/materiales.
    # Conservar referencia previa identificada, nunca presentarla como precio medido.
    for iid in ['colmillo_carnivoro', *['asura_moneda_' + c for c in COINS]]:
        setref(iid, PRODUCTOS[iid][1], 'PENDIENTE: referencia previa conservada; sin drop/receta monetizable en generadores')
    recipes = {out: (n, ings) for out, n, ings, _ in ns['RECIPES'] if out in PRODUCTOS}
    visiting = set()
    def cost(iid):
        if iid not in recipes:
            if iid not in refs:
                raise ValueError(f'Sin fuente de precio: {iid}')
            return refs[iid]
        if iid in visiting:
            raise ValueError(f'Ciclo de recetas: {iid}')
        visiting.add(iid)
        n, ingredients = recipes[iid]
        value = sum((cost(item) if kind == 'c' else vanilla.get(item, 0)) * qty for kind, item, qty in ingredients) / n
        visiting.remove(iid)
        desc = ' + '.join(f'{qty} × {item}' + (f' (${vanilla.get(item, 0):g} NPC/Tienda)' if kind == 'v' else '') for kind, item, qty in ingredients)
        setref(iid, value, f'Receta: ({desc}) / {n}; vanilla sin precio = 0')
        return refs[iid]
    for iid in PRODUCTOS:
        cost(iid)
    return refs, notes


def generate():
    ns = fuentes()
    referencias, calculos = precios_referencia(ns)
    items = ns['ITEMS']
    snbt = ns['snbt']
    catalogo, equipo, identities = {}, {}, {}
    for iid, it in items.items():
        raw = it['components']['minecraft:custom_data']
        actual = re.search(r'\bid:"([^"]+)"', raw)[1]
        # Algunos clones heredan id: no reconocerlos por ese campo aislado.
        identity = (it['base'], actual, raw)
        if identity in identities:
            raise ValueError(f'Identidad duplicada: {iid}/{identities[identity]}')
        identities[identity] = iid
        arg = it['base'] + '[' + ','.join(k + '=' + (v if k == 'minecraft:custom_data' else snbt(v))
                                        for k, v in it['components'].items()) + ']'
        if iid in PRODUCTOS:
            cat, _ = PRODUCTOS[iid]
            ref = referencias[iid]
            if not re.search(r'type:"(?:material|gem|gema|cavernas|vacio|consumable)"', raw):
                raise ValueError(f'Producto no fungible: {iid}: {raw}')
            catalogo[iid] = dict(nombre=it['name'], categoria=cat, referencia=ref,
                                 calculo=calculos[iid], minimo=max(round(ref / 10, 2), PISOS.get(iid, 0), .01), maximo=round(ref * 20, 2),
                                 piso_server=PISOS.get(iid, 0), material=it['base'], item=arg)
        # Lista positiva de equipo; historia, oficios, taladros y cosméticos jamás entran.
        tier = re.search(r'\btier:(\d+)', raw)
        typ = re.search(r'\btype:"([^"]+)"', raw)
        if tier and typ and typ[1] in ('armor', 'weapon', 'staff') and it['kind'] in ('weapon', 'armor'):
            if not re.search(r'\btool:"(?:drill|saw)"', raw) and iid not in __import__('historia_items').ITEMS_HISTORIA:
                equipo[iid] = dict(tier=int(tier[1]), item=arg, identidad=raw.split(',v:', 1)[0])
    missing = set(PRODUCTOS) - set(catalogo)
    if missing:
        raise ValueError(f'IDs ausentes: {sorted(missing)}')
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = {'publico': False, 'pausado': False, 'respaldo-zona': 'America/Argentina/Buenos_Aires',
           'respaldo-hora': '04:45', 'equipo-precios': EQUIPO_POR_TIER}
    # JSON es YAML válido; evita depender de PyYAML para generar.
    (OUT / 'config.yml').write_text(json.dumps(cfg, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    data = {'productos': catalogo, 'equipo': equipo}
    (OUT / 'productos.yml').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    return cfg, data


PLUGIN = """name: AstralBazar
version: 1.2.0
main: astral.AstralBazar
api-version: '26.1.2'
depend: [Vault]
softdepend: [Essentials]
commands:
  bazar:
    description: Bazar Astral privado
permissions:
  astral.bazar.usar:
    default: false
  astral.bazar.admin:
    default: op
"""


def ventanas_yml():
    """Titulos-dibujo de las 11 ventanas (ventanas_bazar.py) -> build/bazar/ventanas.yml (va dentro del jar)."""
    import ventanas_bazar
    data = {k: ventanas_bazar.titulo_ventana(k) for k in ventanas_bazar.ORDEN}
    (OUT / 'ventanas.yml').write_text(json.dumps(data, ensure_ascii=True, indent=2) + '\n', encoding='utf8')


def build(jdk, server):
    ventanas_yml()
    classes = ROOT / '.local/bazar-classes'
    classes.mkdir(parents=True, exist_ok=True)
    jars = list(Path(server).joinpath('libraries').rglob('*.jar')) + [Path(server) / 'plugins/Vault.jar']
    java = Path(jdk) / ('java.exe' if os.name == 'nt' else 'java')
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8',
                    '-classpath', os.pathsep.join(map(str, jars)), '-d', str(classes),
                    str(HERE / 'runtime/BazarStore.java'), str(HERE / 'runtime/AstralBazar.java')], check=True)
    with zipfile.ZipFile(OUT / 'AstralBazar.jar', 'w', zipfile.ZIP_DEFLATED) as z:
        entries = {'plugin.yml': PLUGIN.encode(), **{f.name: f.read_bytes() for f in OUT.glob('*.yml')}}
        entries.update({p.relative_to(classes).as_posix(): p.read_bytes() for p in (classes/'astral').glob('BazarStore*.class')})
        entries.update({p.relative_to(classes).as_posix(): p.read_bytes() for p in (classes/'astral').glob('AstralBazar*.class')})
        for name, payload in sorted(entries.items()):
            z.writestr(zipfile.ZipInfo(name, (2026, 11, 25, 0, 0, 0)), payload)
    count = len(json.loads((OUT/'productos.yml').read_text(encoding='utf8'))['productos'])
    print(f'Bazar: {count} productos; {OUT / "AstralBazar.jar"}')


VENTANAS = [
    ('Bazar - Categorias', 4, '10–14 categorías; 20 buscar; 22 Mis órdenes; 24 vender equipo; 35 cerrar.'),
    ('Bazar - Productos', 6, '0–44 productos de categoría/búsqueda; 45 volver; 48 anterior; 50 siguiente; 53 cerrar.'),
    ('Bazar - Producto', 6, '4 producto, rango e historial; 10–16 siete compras; 19–25 siete ventas; 28 comprar instante; 30 vender instante; 32 orden compra; 34 oferta venta; 40 Mis órdenes; 45 volver; 53 cerrar.'),
    ('Bazar - Cantidad', 3, '10/11/12/13 = 1/16/64/160; 15 todo; 16 a mano; 18 volver; 26 cerrar.'),
    ('Bazar - Precio', 3, '11 igual al mejor; 13 mejorar $0,10 (compra suma, venta resta); 15 a mano; 18 volver; 26 cerrar.'),
    ('Bazar - Confirmar orden', 3, '11 confirmar; 13 resumen cantidad, límite e impuesto; 15 volver. El resto vacío.'),
    ('Bazar - Mis ordenes', 6, '0–35 órdenes (activas primero); 39 retiros de objetos; 41 retirar saldo; 45 volver; 48 anterior; 50 siguiente; 53 cerrar.'),
    ('Bazar - Orden', 3, '11 cancelar y devolver restante; 13 avance, plata e impuesto; 18 volver; 26 cerrar.'),
    ('Bazar - Retiros', 6, '0–44 lotes para retirar; 45 volver; 48 anterior; 50 siguiente; 53 cerrar.'),
    ('Bazar - Vender equipo', 6, '0–44 vista del lote en custodia; clic simple en inventario inferior deposita pieza; 45 volver; 49 total/confirmar; 53 cerrar. Cerrar devuelve, exceso queda para retirar.'),
    ('Bazar - Confirmar equipo', 3, '11 vender definitivamente; 13 advertencia de mejoras/valor; 15 cancelar y devolver. El resto vacío.'),
]


def entrega(data, resultado):
    import hashlib
    lines = ['# AstralBazar 1.2.0 — flujo tipo Hypixel (privado)', '',
             'Entrega local. No se desplegó en Empower ni Aternos. No cambia el resource pack.', '',
             '## Archivos y destinos', '', '| Local | Destino | SHA-256 |', '|---|---|---|']
    for name in ('AstralBazar.jar', 'config.yml', 'productos.yml'):
        p = OUT / name
        dest = 'plugins/' + name if name.endswith('.jar') else 'plugins/AstralBazar/' + name
        lines.append(f'| `build/bazar/{name}` | `{dest}` | `{hashlib.sha256(p.read_bytes()).hexdigest()}` |')
    lines += ['', '`ventanas.yml` va embebido en el JAR; no subir al pack ni reemplazar el existente.', '',
        '1. `/bazar admin pausar`. Respaldar juntos SQLite/WAL/SHM, carpeta AstralBazar, Essentials y jugadores.',
        '2. Subir el JAR a `plugins/update/AstralBazar.jar` (si el panel admite update), y productos.yml a su destino. Conservar la config operativa actual: `publico: false`; el config.yml generado es plantilla privada, no sobreescribir permisos/pausa del servidor.',
        '3. Requiere un reinicio completo; no PlugMan ni reload de JAR. En Empower, cuando todo esté subido: `reiniciopendiente Bazar 1.2.0`. Alternativa: apagar, reemplazar `plugins/AstralBazar.jar` y arrancar con Java 25.',
        '4. Consola: `Bazar privado listo: 88 productos. publico=false`, versión 1.2.0 sin errores. `/bazar admin reanudar`; probar con ByTrainx en `/modo admin` y `/sala`. Otro jugador sin permiso debe ver Próximamente.',
        '5. Config operativa: `/bazar admin recargar`. Catálogo/JAR requieren reinicio. No borrar IDs existentes ni reemplazar bazar.sqlite; la migración agrega `claims.order_id` y `order_credit` sin eliminar tablas/órdenes.',
        'Aternos puede impedir instalar JAR propios: no eludir restricciones ni usar APIs privadas. No subir mundos ni usar Worlds > Upload en world.', '',
        '## Verificación', '', resultado, '',
        'SQLite/Vault/inventarios conservan el journal y los recibos durables. Los nuevos cobros tienen relación con su orden. Los cobros 1.1.0 no tienen esa relación: se recuperan con Cobrar todo (también devuelve equipo antiguo). Nunca al piso.', '',
        '## Referencias de precio', '',
        'No son cotizaciones del mercado: son referencias de reposición para límites. Mínimo=max(ref/10, piso NPC, $0,01); máximo=ref×20. Recetas se calculan recursivamente y se dividen por la cantidad producida. Ingredientes vanilla sin precio=0.',
        'El survival adapta su tier al jugador: se asume T5 para Nether/End y T3 para vindicator. Para bloques/cofres sin pago se usa una unidad de esfuerzo explícita, no una medición de tiempo real. Las seis referencias sin fuente monetizable quedan marcadas PENDIENTE; requieren revisión del dueño.', '',
        '| ID | Nombre | Cálculo | Referencia | Mínimo | Máximo |', '|---|---|---|---:|---:|---:|']
    def fmt(n):
        return f'{n:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')
    for iid, p in data['productos'].items():
        lines.append(f"| `{iid}` | {p['nombre']} | {p['calculo']} | {fmt(p['referencia'])} | {fmt(p['minimo'])} | {fmt(p['maximo'])} |")
    lines += ['', '## Fichas para Gemini', '', 'Casilleros desde 0, izquierda a derecha. No dibujar nombres/precios/cantidades variables; van en el tooltip. Los espacios no listados quedan libres. Inicio, Producto, Cantidad, Precio, Mis órdenes y Vender inventario usan título simple hasta aprobar arte nuevo.', '',
        '| Ventana | Filas | Casilleros / texto |', '|---|---:|---|',
        '| Inicio | 6 | Columna categorías 0 Minería, 9 Combate, 18 Bosque y pesca, 27 Consumibles, 36 Especiales. Productos: columnas 2–8 de filas 0–4 (35 por página). 45 Buscar, 46 Mis órdenes, 47 Vender inventario, 48 Vender equipo al server, 49 Anterior, 50 Siguiente, 51 Página, 53 Cerrar. |',
        '| Producto | 6 | Comprar al instante 10/11/19/20; Vender al instante 14/15/23/24; Crear orden de compra 28/29/37/38; Crear oferta de venta 32/33/41/42; 45 Volver; 49 Mis órdenes. Lore: mejor precio, hasta siete puntas, inventario y clic. |',
        '| Cantidad | 5 | Instantánea: 10 Una unidad, 12 Un stack, 15 Llenar inventario. Órdenes: 10 64, 12 160, 14 1024; venta: 15 Todo lo que tengo. Siempre: 16 A mano, 36 Volver, 44 Cerrar. |',
        '| Precio | 5 | 10 Igual a la mejor, 12 Mejor +/-$0,10, 14 5% del margen, 16 A mano. 36 Volver, 44 Cerrar. Sin margen positivo el botón 14 queda deshabilitado y lo explica. |',
        '| Mis órdenes | 6 | 0–44 órdenes; clic cobra, derecho cancela/devuelve. 45 Cobrar todo, 48 Anterior, 49 Página, 50 Siguiente, 51 Volver, 53 Cerrar. No Retiros ni Retirar plata. |',
        '| Vender inventario | 6 | 0–44 productos/cantidad/estimado neto; 45 Volver, 49 Confirmar con total neto, 53 Cerrar. Lo que exceda las 45 tarjetas sigue incluido en el total. No equipo. |', '',
        'Confirmar orden y las dos ventanas de equipo mantienen sus botones del diseño 1.1.0. Orden/Retiros ya no se abren. Si `diseno: false`, todas son simples.', '',
        'El tooltip oculta atributos/encantamientos en las copias de UI, sin modificar los ítems comerciables. Las líneas avanzadas del cliente (`minecraft:paper`, número de componentes, F3+H) no pueden ocultarse selectivamente desde Paper sin esconder también nombre/lore; desactivar F3+H en el cliente.', '',
        'El catálogo depende de generadores locales previos no publicados (economía, Clases, Vacío, historia, manzanas); la tarea no autoriza publicar esas fuentes. Recompilar el catálogo versionado con `--solo-compilar` evita ejecutarlas. Arte previo del Bazar también existe sin publicar y debe separarse antes de publicar esta tarea.']
    (ROOT / 'build/deploy/bazar-hypixel.md').write_text('\n'.join(lines)+'\n', encoding='utf8')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--jdk')
    ap.add_argument('--server', default=str(ROOT / '.local/testsrv'))
    ap.add_argument('--solo-compilar', action='store_true', help='compila el catálogo versionado sin importar generadores de otras tareas')
    ap.add_argument('--resultado-pruebas', default='Verificación pendiente; ejecutar tools/probar_bazar_paper.py y test_economia.py antes de publicar.')
    args = ap.parse_args()
    if args.solo_compilar:
        if not args.jdk:
            ap.error('--solo-compilar requiere --jdk')
        build(args.jdk, args.server)
        raise SystemExit(0)
    _, data = generate()
    if args.jdk:
        build(args.jdk, args.server)
    entrega(data, args.resultado_pruebas)
