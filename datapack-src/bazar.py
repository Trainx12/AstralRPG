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


def generate():
    ns = fuentes()
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
            cat, ref = PRODUCTOS[iid]
            if not re.search(r'type:"(?:material|gem|gema|cavernas|vacio|consumable)"', raw):
                raise ValueError(f'Producto no fungible: {iid}: {raw}')
            catalogo[iid] = dict(nombre=it['name'], categoria=cat, referencia=ref,
                                 minimo=max(ref / 10, PISOS.get(iid, 0)), maximo=ref * 10,
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
version: 1.0.0
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


def build(jdk, server):
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
    lines = ['# Bazar fase 1 — privado, sin desplegar', '',
        'No se instaló nada en el servidor. El principal documentado es Empower; Aternos es copia.', '',
        '## Archivos y destinos', '', '| Local | Destino | SHA-256 |', '|---|---|---|']
    for name in ('AstralBazar.jar', 'config.yml', 'productos.yml'):
        p = OUT / name
        if p.exists():
            dest = 'plugins/'+name if name.endswith('.jar') else 'plugins/AstralBazar/'+name
            lines.append(f'| `build/bazar/{name}` | `{dest}` | `{hashlib.sha256(p.read_bytes()).hexdigest()}` |')
    lines += ['', 'Apagar, respaldar los archivos actuales de AstralBazar si existen, subir los tres archivos y arrancar con Java 25 / Paper 26.1.2, Vault y EssentialsX. El JAR necesita REINICIO completo; no usar reload de JAR ni PlugMan.',
        'Conservar siempre `plugins/AstralBazar/bazar.sqlite`, sus archivos WAL/SHM, `backups/` y datos de Essentials/jugadores. Nunca reemplazar mundos ni usar Worlds > Upload en world.',
        'Si Aternos no permite instalar este JAR propio, queda bloqueado en esa plataforma; usar el panel autorizado de Empower. No usar APIs privadas.', '',
        'Mantener `publico: false`. Solo para el dueño: `lp user ByTrainx permission set astral.bazar.usar true`.',
        'Verificar consola: `Bazar privado listo`, sin errores del plugin. ByTrainx prueba `/bazar` en `/modo admin` y `/sala`. Otro jugador debe recibir Próximamente. Aldeano y DeluxeMenus siguen iguales.',
        'Después, `/bazar admin pausar`, `/bazar admin reanudar`. Cambios operativos de config: `/bazar admin recargar`; cambios del catálogo requieren reinicio y mantener los IDs de órdenes existentes.', '',
        '## Verificación', '', resultado, '',
        'El ensayo es aislado con Paper real, Essentials, Vault y los registros reales de encantamientos del datapack; no ejecuta funciones/ticks de otras tareas locales. La prueba de caída usa Runtime.halt y vuelve a abrir el mismo servidor.',
        'El catálogo se generó sobre las fuentes locales vigentes. Clases, Vacio, manzanas e historia y los ajustes recientes de economia/build son trabajo previo que no se publica en esta tarea. Hasta que se publique por separado, un checkout limpio puede recompilar este JAR y catálogo versionado con `python bazar.py --solo-compilar --jdk <bin Java 25>`; regenerar el catálogo desde todos los generadores requiere esas fuentes locales.',
        'La prueba del dueño, el conjunto completo de plugins remotos y su consola siguen pendientes. No se certifica despliegue.', '',
        '## Catálogo final', '', 'Todos usan custom_data Astral, material y componentes canónicos completos. Versiones antiguas deben pasar por la migración del datapack. Nombre cambiado, encantamientos, daño o componentes adicionales se rechazan como producto.', '',
        '| Categoría | ID | Nombre | Referencia | Mínimo | Máximo | Piso servidor |', '|---|---|---|---:|---:|---:|---:|']
    for iid, p in sorted(data['productos'].items(), key=lambda kv:(kv[1]['categoria'],kv[0])):
        lines.append(f"| {p['categoria']} | `{iid}` | {p['nombre']} | {p['referencia']:g} | {p['minimo']:g} | {p['maximo']:g} | {p['piso_server']:g} |")
    lines += ['', 'Minas vende minerales vanilla: quedan fuera del catálogo. Los cuatro pisos propios vienen de `economia.CAVERNAS_PRECIO` y `VACIO_PRECIO`. Comprar en el Bazar cuesta al menos el precio de venta al servidor, sin ganancia de arbitraje. No existen pescados Astrales fungibles registrados actualmente: no se inventan IDs. Las monedas Asura sí son materiales registrados.', '',
        'Referencias de materiales sin venta NPC: valores iniciales editables, requieren revisión de balance del dueño. No se compra ni vende equipo entre jugadores en este bazar.', '',
        '## Equipo al servidor', '', '| Tier | Pago por pieza |', '|---|---:|']
    lines += [f'| {t} | ${n:,} |' for t,n in EQUIPO_POR_TIER.items()]
    lines += ['', 'Fórmula: `economia.PLATA_MOB_TIER[tier] * 2`. Sin impuesto para esta liquidación al servidor. Mismo valor con mejoras. Toda venta pide confirmación y la mejorada advierte que en Subastas vale más. El pago queda en saldo para retirar a Vault.',
        'Lista positiva de armas/armaduras; incluye bastones, guadañas, lanzas, cuchillos, ballestas, guantes y libros de clase. Excluye historia, mochilas, mascotas, cosméticos, taladros, motosierras y oficios.', '',
        '## Persistencia y operación', '',
        'SQLite FULL/WAL guarda órdenes, custodia, saldo, trades y audit en transacciones. El registro de movimientos es la tabla `audit` (y `trades`), dentro del archivo SQLite, no un log público. Impuesto 125 puntos base, acumulado por oferta y redondeado al centavo; no se evita fraccionando ventas.',
        'Cada cruce procesa hasta 256 contrapartes; la cola restante continúa una vez por segundo, también para desconectados. Ninguna tarea corre cada tick. Acceso a inventarios y Vault solo en hilo principal; respaldo diario a las 04:45 Argentina mediante SQLite VACUUM INTO en tarea asíncrona.',
        'Vault y el archivo del jugador no comparten transacción con SQLite. El journal escribe intención antes de tocar recursos. Inventario y recibo se guardan juntos con saveData; al entrar se concilia una vez. Vault se concilia por saldo previo/esperado. Si no coincide, pausa persistente y revisión manual con Essentials; no se repite el pago a ciegas. No editar/borrar journal ni restaurar solo una de las bases durante conciliación.',
        'No se promete atomicidad distribuida absoluta: cambios externos coincidentes de saldo o fallos de disco requieren conciliación. Para producción pública hace falta la prueba del dueño y revisión de recuperación con los respaldos operativos.', '',
        '## Ventanas para diseño (fase 3)', '', 'Slots desde 0. Títulos fijos; sin glifos ni arte en esta fase. Slots no listados vacíos. Entradas manuales por `/bazar entrada <valor>`: no hay una ventana adicional de chat/yunque.', '',
        '| Título exacto | Filas | Casilleros y botones |', '|---|---:|---|']
    lines += [f'| {title} | {rows} | {layout} |' for title,rows,layout in VENTANAS]
    dest = ROOT / 'build/deploy/bazar-fase1.md'
    dest.write_text('\n'.join(lines)+'\n', encoding='utf8')


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
