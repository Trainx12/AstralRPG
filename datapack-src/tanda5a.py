"""Entrega reproducible de XP, claims, mochilas y loot. Terceros solo en .local.

python tanda5a.py --java <JDK25/bin/java.exe> --server <Paper local>
Requiere build.py y mobs/*.py ya generados. No conecta al servidor remoto.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile
import yaml
from escala import XP_MOB, XP_ELITE, XP_JEFE, xp_skill_level, TIER_MAZMORRA
from items_t6_10 import MATERIALES as MATERIALES_ALTOS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/tanda5a'
PROBABILIDADES = {1: .15, 2: .03, 3: .005, 4: .0004, 5: .000003}
PAQUETES = [(25, 15000), (100, 50000), (1225, 500000), (2500, 950000), (10000, 3500000)]
# ExpendableBackpacks 1.2.0 (unico plugin de mochilas): nivel, nombre, espacios, precio.
# La mochila es un item; tambien se fabrica/mejora con su receta. Netherite solo en herreria.
MOCHILAS = [('leather', 'Cuero', 9, 5000), ('copper', 'Cobre', 18, 20000), ('iron', 'Hierro', 27, 50000),
            ('gold', 'Oro', 36, 100000), ('diamond', 'Diamante', 45, 175000)]
SLOT_MOCHILAS = 42  # 40 Proteccion, 41 misc (ocupados en el server)
STRUCTURE_NAMESPACES = ['nova_structures', 'explorify', 'structory', 'structory_towers']
MATERIAL_TIERS = {
    'netherita_fundida': 2, 'netherita_reforzada': 4, 'shadowsteel': 2,
    'esencia_nether': 1, 'madera_estelar': 2, 'palo_reforzado': 2, 'cuero_tratado': 1,
    'cristal_arcano': 2, 'fragmento_cristal': 1, 'cristal_refinado': 3,
    'fragmento_umbrio': 1, 'gema_umbria_fragmentada': 1, 'gema_umbria': 3,
    'gema_umbria_perfecta': 5, 'gema_luminica': 2, 'gema_luminica_perfecta': 5,
    'fragmento_astral': 1, 'polvo_astral': 2, 'nucleo_astral': 5,
    'nucleo_furia': 2, 'nucleo_furia_pura': 5, 'corazon_shulker': 3, 'nucleo_eolico': 2,
    'esencia_elite': 2, 'alma_corrupta': 3, 'chispa_astral': 4,
}


def loot_tier(key):
    """Las estructuras desconocidas futuras reciben T3; solo contenedores generados."""
    if any(s in key for s in ('stronghold', 'bastion', 'ancient_city', 'end_city',
                              'catacomb', 'toxic_lair', 'illager_mansion', 'wizard', 'keep',
                              'structory_towers:')):
        return 5
    if key.startswith('structory:') or any(s in key for s in ('village', 'shipwreck', 'tavern', 'cabin', 'ruin', 'camp', 'supply_cache')):
        return 2
    return 3


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf8')


def catalog():
    result = {}
    # Leer las mismas tablas de items que usa /loot; nunca fabricar copias incompletas.
    with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
        for name in sorted(z.namelist()):
            if not re.fullmatch(r'data/astral/loot_table/item/[a-z0-9_]+\.json', name):
                continue
            iid = Path(name).stem
            if iid == 'espada_heroe_errante':  # solo administracion
                continue
            entry = json.loads(z.read(name))['pools'][0]['entries'][0]
            comp = entry['functions'][0]['components']
            data = comp.get('minecraft:custom_data', '')
            match = re.search(r'type:"(material|weapon|staff|armor|talisman)"', data)
            if not match:
                continue
            tier = re.search(r'tier:(\d+)', data)
            if tier and int(tier[1]) > 5 or iid in MATERIALES_ALTOS:
                continue  # T6-T10 (14/11/2026): solo se forjan o caen de mobs de su tier, nunca en cofres
            if iid.startswith(('agua_', 'minero_', 'talador_')) or iid in ('perla_abisal', 'coral_astral'):
                continue  # Oceano y oficios tienen su propia forma de conseguirse (no estaban en cofres)
            tier = min(5, int(tier[1])) if tier else MATERIAL_TIERS.get(iid, 1)
            # Materiales sin tier reciben uno explicito segun su progresion existente.
            result[iid] = {'tier': tier, 'chance': PROBABILIDADES[tier]}
    if not result:
        raise ValueError('Catalogo vacio: revisar formato de custom_data')
    return result


def mythic_catalog():
    result = {}
    for path in sorted((ROOT/'build/mythicmobs/mobs').glob('*.yml')):
        for iid, mob in (yaml.safe_load(path.read_text(encoding='utf8')) or {}).items():
            if not isinstance(mob, dict):
                continue
            if mob.get('Options', {}).get('Invincible') or not mob.get('Damage'):
                continue
            skills = '\n'.join(mob.get('Skills', []))
            tier = re.search(r'astral[.:]mt([1-5])|astral:mob/t([1-5])', skills)
            fixed = next((t for w, t in TIER_MAZMORRA.items() if w in iid), 0)
            # Mundo abierto: la etiqueta del datapack manda; fallback T1 hasta su primer tick.
            result[iid] = {'tier': int(next(g for g in tier.groups() if g)) if tier else fixed or 1,
                           'boss': bool(mob.get('BossBar', {}).get('Enabled')) or any(s in iid for s in ('guardian', 'ancestral', 'jefe')),
                           'elite': 'elite' in iid}
    return result


def generate():
    config = {'survival-world': 'world', 'xp': {str(t): v for t, v in XP_MOB.items()},
              'elite-bonus': XP_ELITE, 'boss-bonus': XP_JEFE,
              'dungeon-tiers': TIER_MAZMORRA, 'mythic': mythic_catalog(),
              'structure-namespaces': STRUCTURE_NAMESPACES,
              'loot': catalog(), 'claim-packages': [{'blocks': b, 'price': p} for b, p in PAQUETES],
              'backpack-packages': [{'tier': k, 'name': nombre, 'slots': n, 'price': p} for k, nombre, n, p in MOCHILAS]}
    dump(OUT/'AstralProgression/config.yml', config)
    # Los modos se refuerzan al cargar cada mundo desde el runtime, incluyendo mundos futuros.
    dump(OUT/'GriefPreventionData/config.yml', {'GriefPrevention': {
        'Claims': {'Mode': {'world': 'Survival', 'lobby': 'Disabled'}, 'InitialBlocks': 36,
                   'Claim Blocks Accrued Per Hour': {'Default': 0}, 'BlocksAccruedPerHour': 0,
                   'AccruedIdlePercent': 0, 'MinimumWidth': 6, 'MinimumArea': 36,
                   'ExtendIntoGroundDistance': 1000000, 'MaximumDepth': -2147483648,
                   'AutomaticNewPlayerClaimsRadius': -1, 'CreationRequiresWorldGuardBuildPermission': True,
                   'ModificationTool': 'GOLDEN_SHOVEL', 'Expiration': {'AllClaims': {'DaysInactive': 0}}},
        'Economy': {'ClaimBlocksPurchaseCost': 0, 'ClaimBlocksSellValue': 0},
        'ProtectItemsDroppedOnDeath': {'PvPWorlds': False, 'NonPvPWorlds': False},
        'PvP': {'ProtectFreshSpawns': False, 'PunishLogout': False},
        'Spam': {'Enabled': False}, 'SmartBan': False, 'MaxPlayersPerIpAddress': 0}})
    messages = {'CreateClaimSuccess': 'Zona protegida de fondo a techo. /trust <jugador> para compartir.',
                'NoBuildPermission': 'No tenes permiso de {0} para construir aqui.',
                'NoContainersPermission': 'Este contenedor pertenece a {0}.',
                'ClaimStart': 'Primera esquina marcada. Marca la esquina opuesta con clic derecho.',
                'ClaimTooNarrow': 'El ancho minimo es {0} bloques.',
                'CreateClaimInsufficientBlocks': 'No tenes bloques suficientes. Compra area en /shop, Proteccion.',
                'ResizeClaimTooNarrow': 'El ancho minimo es {0} bloques.',
                'ResizeClaimInsufficientArea': 'El area minima es {0} bloques.',
                'ClaimsDisabledWorld': 'Las zonas solo se protegen en survival.',
                'NotEnoughBlocksForMinClaim': 'Necesitas al menos 36 bloques disponibles (6x6).',
                'SuccessfulAbandon': 'Zona liberada. Te quedan {0} bloques.',
                'NoBuildOutsideClaims': 'Protege tu terreno con una pala de oro.',
                'TrustListHeader': 'Permisos de esta zona:',
                'RemainingBlocks': 'Te quedan {0} bloques de proteccion.',
                'ResizeNeedMoreBlocks': 'Necesitas {0} bloques mas. Compra area en /shop, Proteccion.',
                'ClaimResizeSuccess': 'Zona redimensionada. Te quedan {0} bloques.',
                'ResizeStart': 'Marca la nueva posicion de esta esquina con la pala.',
                'CreateClaimFailOverlap': 'La zona se superpone con otra tuya. Usa /abandonclaim o cambia las esquinas.',
                'CreateClaimFailOverlapOtherPlayer': 'La zona se superpone con una de {0}.',
                'CreateClaimFailOverlapShort': 'La zona se superpone con otra existente.',
                'ResizeFailOverlap': 'No se puede ampliar: hay otra zona protegida.',
                'CreateClaimFailOverlapRegion': 'WorldGuard no permite construir en parte de esa zona.',
                'ResizeFailOverlapRegion': 'No podes construir alli; no podes proteger esa area.',
                'ClaimsExtendToSky': 'Las zonas protegen hasta el techo del mundo.',
                'ClaimsAutoExtendDownward': 'En Astral las zonas ya protegen hasta el fondo del mundo.',
                'BuildingOutsideClaims': 'Este terreno no esta protegido. Usa una pala de oro para marcar dos esquinas.',
                'ChestClaimConfirmation': 'Este cofre esta protegido.',
                'TrustListNoClaim': 'Parate dentro de tu zona para consultar los permisos.',
                'ClaimsListHeader': 'Zonas protegidas:', 'BuildPermission': 'construir',
                'AccessPermission': 'acceder', 'ContainersPermission': 'usar contenedores',
                'PermissionTrust': 'compartir permisos', 'NoPermissionTrust': 'No podes dar permisos aqui.',
                'OnlyOwnersModifyClaims': 'Solo el propietario puede modificar esta zona.',
                'OnlyOwnersAbandonClaims': 'Solo el propietario puede liberar esta zona.',
                'YouHaveNoClaims': 'Todavia no tenes zonas protegidas.',
                'NotYourClaim': 'Esta zona no es tuya.',
                'UntrustIndividualAllClaims': 'Se retiro el acceso de {0} a tus zonas.',
                'UntrustEveryoneAllClaims': 'Se retiraron los permisos compartidos de tus zonas.'}
    dump(OUT/'GriefPreventionData/messages.yml', {'Messages': {k: {'Text': v} for k, v in messages.items()}})
    dump(OUT/'ExpendableBackpacks/config.yml', {
        'allow-backpack-inception': False, 'give-backpack-on-first-join': False,
        'starter-backpack-message': '&dAstralRPG &8» &eRecibiste una mochila de cuero. Clic derecho para abrirla.'})
    for section, slot, material in [('Proteccion', 40, 'GOLDEN_SHOVEL'), ('Mochilas', SLOT_MOCHILAS, 'CHEST')]:
        dump(OUT/f'EconomyShopGUI/sections/{section}.yml', {
            'enable': True, 'slot': slot, 'title': 'Astral - '+section,
            'item': {'material': material, 'name': '&6'+section, 'lore': ['&7Click para ver las opciones.']}})
        dump(OUT/f'EconomyShopGUI/shops/{section}.yml', {'pages': {'page1': {'gui-rows': 3,
            'items': {'1': {'material': material, 'displayname': '&6Abriendo...', 'buy': -1, 'sell': -1}}}}})
    (OUT/'permisos.txt').write_text('lp group default permission set griefprevention.buysellclaimblocks false\n'
        'lp group default permission set griefprevention.createclaims true\n', encoding='utf8')
    write_delivery(config)
    return config


def write_delivery(config):
    lines = ['# Tanda 5a — preparada, NO desplegada', '',
             'Generar: `python build.py`, despues `python tanda5a.py --java <java25> --server <Paper-local>` desde datapack-src.',
             'Conserva cosmeticos/skins y el pack FINAL privado: esta tanda no modifica texturas.', '',
             '## Instalacion (Empower; si se usa Aternos, solo mediante funciones publicas permitidas)', '',
             'Apagar. Respaldar archivos afectados y datos de plugins. No reemplazar mundos ni usar Worlds > Upload.',
             'El runtime AstralProgression es propio: esta entrega requiere Empower u otro hosting que permita subir JAR. En Aternos, sin ese plugin en su catalogo, queda bloqueada; no instalar a medias ni usar APIs privadas.',
             'Subir las siguientes rutas, conservando el resto de cada carpeta:', '',
             '| Local | Destino |', '|---|---|',
             '| `build/runtime/AstralProgression.jar` | `plugins/AstralProgression.jar` |',
             '| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |']
    for path in sorted(OUT.rglob('*.yml')):
        lines.append(f'| `build/tanda5a/{path.relative_to(OUT).as_posix()}` | `plugins/{path.relative_to(OUT).as_posix()}` |')
    lines += ['', 'GriefPreventionData/config.yml y messages.yml son ajustes: si ya existen, combinar las claves, no borrar claims ni PlayerData.',
              'Comprobar que el mundo survival se llama `world`; si difiere, ajustar `survival-world` y Claims.Mode antes de arrancar.',
              f'Slots de tienda: 40 Proteccion, {SLOT_MOCHILAS} Mochilas (41 lo usa misc en el server).', '',
              '## Descargas verificadas en Modrinth (26.1.2, formato datapack o Paper)', '']
    versions = json.loads((ROOT/'datapack-src/tanda5a-versions.json').read_text(encoding='utf8'))
    for slug in ['griefprevention', 'dungeons-and-taverns', 'explorify', 'structory', 'structory-towers']:
        v = versions[slug]
        assert '26.1.2' in v['game_versions']
        f = next(f for f in v['files'] if f['primary'])
        is_plugin = slug == 'griefprevention'
        dest = 'plugins/' if is_plugin else 'world/datapacks/'
        lines += [f'- [{slug} {v["version_number"]}](https://modrinth.com/{"plugin" if is_plugin else "datapack"}/{slug}/version/{v["id"]}): '
                  f'[{f["filename"]}]({f["url"]}) → `{dest}{f["filename"]}`. Local: `.local/tanda5a/{f["filename"]}`. SHA-1 `{f["hashes"]["sha1"]}`.']
    lines += ['', 'Terceros nunca al Git publico. Mochilas: ExpendableBackpacks 1.2.0 (ya instalado en el server).',
              'Structory y Towers son de Stardust Labs. No se superponen estructuras ni loot entre los cuatro packs. El tag load compartido se combina (sin replace).',
              'Structory/Towers comparten data/c/worldgen/structure_icons.json: metadatos de iconos, ignorados por vanilla/Paper, prevalece el pack de mayor prioridad. No altera estructuras ni cofres; una futura integracion que lea esos iconos debe combinar ambos mapas.',
              'Solo chunks nuevos. Paper comparte datapacks entre mundos; AstralProgression cancela AsyncStructureSpawnEvent de los cuatro namespaces fuera del survival.',
              'No cambia estructuras ya existentes ni las vanilla. Nunca copiar ZIP a mundos de lobby/minas/mazmorras.',
              'No apilar otra version de D&T si ya existe: reemplazar solo su ZIP anterior tras respaldo. Conservar Stellarity instalado.', '',
              'Iniciar (Java 25). Requiere AuraSkills con preset legacy, MythicMobs, Vault, proveedor de economia, LuckPerms y EconomyShopGUI ya existentes.',
              'Ejecutar `build/tanda5a/permisos.txt`; despues `sreload` y `skills reload`. Un reinicio carga el JAR y los datapacks; no usar PlugMan ni /reload general.',
              'Verificar consola: AstralProgression habilitado, GriefPrevention y ExpendableBackpacks cargados, sin errores de datapacks.', '',
              '## XP y ritmo', '',
              'Copia local de AuraSkills: `.local/asw-native/server/plugins/AuraSkills/xp_requirements.yml`; corroborada con fichas-paper y testsrv.',
              'Preset legacy no reemplaza xp_requirements. Formula: `100*(nivel_destino-2)^2+100`. No se pudo leer la configuracion remota en esta tarea: comparar antes de instalar.',
              '25→26: 57.700 / 250 = 230,8 XP T5. A 200–300 mobs/h: 75–50 minutos. Estimacion sin bonus ni multiplicadores de permisos.',
              'AuraSkills conserva los bonus Fighter/Archer: al nivel 25, el ensayo midio +50%. En esas skills 25→26 baja a 50–33,3 minutos (40 a 250 mobs/h). Hechiceria conserva ~60 minutos. Objetivo orientativo; medir ritmo real antes de retocar la tabla.', '',
              '| Tier | Normal | Elite x1,5 | Jefe x8 |', '|---|---:|---:|---:|']
    from escala import xp_skill_mob
    for t in range(1, 6):
        lines.append(f'| {t} | {xp_skill_mob(t)} | {xp_skill_mob(t, elite=True)} | {xp_skill_mob(t, jefe=True)} |')
    lines += ['', '| Progreso | Tier supuesto | XP total | Minutos a 250 mobs/h |', '|---|---:|---:|---:|']
    for start, end, tier in [(1, 5, 1), (10, 11, 2), (25, 26, 5)]:
        xp = sum(xp_skill_level(n) for n in range(start+1, end+1))
        lines.append(f'| {start}→{end} | {tier} | {xp} | {xp/XP_MOB[tier]/250*60:.1f} |')
    lines += ['', 'Listener unico: mob tier por etiqueta astral.mt#, luego definicion Mythic generada, luego mundo de mazmorra.',
              'Fighting/archery/sorcery se leen del PDC de requisitos del arma Astral. Flechas guardan skill al disparar; magia atribuida por /damage by jugador.',
              'Se reemplaza la XP de EntityXpGainEvent solo para bajas gestionadas: sin premio fighting/archery duplicado. Sorcery por gastar mana del preset se conserva (fuente diferente).',
              'Tier 0 y mobs vanilla sin escala conservan fuentes AuraSkills: zombi/esqueleto 7 XP base en fighting.yml y archery.yml. T1 gestionado da 20 (x2,86), T5 230,8 (x32,97). No inflar animales para farmear.',
              'Jefe T3: 640 XP, menor que un nivel medio (14→15: 17.000); T5: 1.846,4 < 57.700. No se acumula bonus elite+jefe.', '',
              '## Proteccion y mochila', '',
              'Pala de oro: clic derecho en dos esquinas. Minimo 6x6, area 36. Todo de fondo a techo desde crear la zona; solo se cobra X*Z.',
              'Inicio 36, sin bloques por tiempo. Comprar SUMA: 36+25=61, no 11x11. Se reparte entre varias zonas (cada una minimo 36).',
              '`/trust jugador`, `/untrust jugador`, `/abandonclaim`; Bolt sigue controlando cofres y WorldGuard sigue controlando regiones.',
              '`/buyclaimblocks` y venta de bloques desactivados. Precio unico en tanda5a.py; compra desde EconomyShopGUI abre menu propio y ejecuta `adjustbonusclaimblocks jugador cantidad` desde consola.',
              'Paquetes: '+', '.join(f'{b} bloques = ${p:,}' for b,p in PAQUETES)+'. Caros frente a minas: $80 → $700.000 → $25M.',
              'Mochilas (ExpendableBackpacks): '+', '.join(f'{nombre} {n} espacios ${p:,}' for k,nombre,n,p in MOCHILAS)+'.',
              'La tienda ejecuta `backpack give jugador nivel` desde consola: la mochila es un item (clic derecho abre). Pide un espacio libre antes de cobrar.',
              'Tambien se fabrican (cuero+hilo+cofre) y se mejoran rodeandolas con 8 lingotes; Netherite en herreria. `allow-backpack-inception: false`.',
              'Al morir la mochila cae como item (AxGraves la guarda en la tumba); el contenido queda ligado a la mochila.', '',
              '## Loot aditivo por item y cofre', '', '| Rareza | Probabilidad | Porcentaje |', '|---|---:|---:|']
    for t, name in enumerate(['Comun/material', 'Poco comun', 'Rara', 'Epica', 'Legendaria'], 1):
        lines.append(f'| {name} | {PROBABILIDADES[t]} | {PROBABILIDADES[t]*100:g}% |')
    lines += ['', f'Catalogo: {len(config["loot"])} items; una tirada independiente por item elegible, sin limite que cambie su probabilidad.',
              'Rareza del equipo: ficha.py (T1..T5). Materiales sin rareza reciben tier explicito en MATERIAL_TIERS (tanda5a.py); nucleos/perfectas endgame son T5. Talismanes: tier existente.',
              'La probabilidad es por item, tambien para equipo comun: puede haber varias piezas comunes en un cofre; no hay tirada global ni multiplicador oculto por categoria.',
              'LootGenerateEvent conserva la lista original y agrega items desde astral:item/*. Solo contenedores naturales sin marca de colocacion, primera generacion, survival.',
              'Aldeas/naufragios/tabernas/cabanas/Structory: max T2; templos/minas y desconocidos futuros T3; stronghold/bastion/ancient_city/end_city, D&T catacumbas/magos/mansion y Towers T5.',
              'Tablas con namespace astral se excluyen para evitar recursion. Cofres colocados despues de instalar se marcan y excluyen; cofres previos de jugadores no tienen loot table y no generan evento.', '',
              '## Verificaciones locales', '',
              'Suite existente: 227 pruebas OK. Regresion final focalizada: 23 pruebas OK. Compilacion con JDK25 y Paper 26.1.2 build 74.',
              'Ensayo Paper: XP real de baston, espada, arco con cambio de arma, elite y jefe Mythic; una sola recompensa, bonus nativos conservados; claims 6x6 y area acumulativa; filtro de estructuras; loot aditivo de vanilla y los cuatro packs, sin repetir; mochila y persistencia tras reinicio.',
              'Prueba reproducible: `python tools/probar_tanda5a_paper.py --java <java25> --source <Paper-local>` desde la raiz. Logs solo en `.local/tanda5a/`. Nunca instalar ProgressionProbe en remoto.',
              'Jugador NMS simulado: overlays de AuraSkills/PacketEvents apagados solo en el ensayo. No sustituye un cliente real ni valida AxGraves/WorldGuard/Bolt/EconomyShopGUI en remoto.',
              'Comparacion ZIP contra HEAD previo: solo guia.json y la pagina nueva guia/proteccion.json; sin otros cambios de items ni assets.', '',
              '## Verificacion remota pendiente', '',
              '- Comparar curva activa con la copia local y comprobar que el preset legacy tenga sorcery.',
              '- Espada, arco (cambiar arma en vuelo), baston directo/area y guadana: una sola recompensa de la skill correcta; matar elite/jefe y mob vanilla escalado.',
              '- Dos cuentas sin OP: proteger 6x6; intentar romper fondo/techo, varias zonas, comprar 25 y comprobar 61; WG y Bolt siguen negando acceso.',
              '- Mochilas: comprar niveles, abrir con clic derecho, desconexion/reinicio; morir con AxGraves, recuperar tumba una vez, revisar que no se duplique contenido.',
              '- Abrir cofres nuevos de cada pack (tambien vagoneta), conservar loot vanilla; reabrir no duplica. Generar chunks en mundo excluido y confirmar que no aparecen estructuras de los packs.',
              '- Revisar consola y medir memoria/TPS con spark. No afirmar estas pruebas remotas como realizadas.']
    path = ROOT/'build/deploy/tanda5a.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines)+'\n', encoding='utf8')


def build(java, server):
    config = generate()
    target = ROOT/'.local/tanda5a/classes'
    target.mkdir(parents=True, exist_ok=True)
    jars = list((server/'libraries').rglob('*.jar')) + [ROOT/'.local/asw-native/server/plugins/auraskills.jar',
            ROOT/'.local/asw-native/server/plugins/mythicmobs.jar', ROOT/'.local/tanda5a/GriefPrevention.jar']
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8',
                    '-classpath', os.pathsep.join(map(str, jars)), '-d', str(target),
                    str(ROOT/'datapack-src/runtime/AstralProgression.java')], check=True)
    dest = ROOT/'build/runtime/AstralProgression.jar'
    dest.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((target/'astral').glob('AstralProgression*.class')):
            z.writestr(zipfile.ZipInfo(p.relative_to(target).as_posix(), (2026,11,11,0,0,0)), p.read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml', (2026,11,11,0,0,0)),
                   "name: AstralProgression\nversion: 1.0.0\nmain: astral.AstralProgression\napi-version: '26.1.2'\ndepend: [AuraSkills, MythicMobs, GriefPrevention]\nsoftdepend: [Vault, LuckPerms, EconomyShopGUI, ExpendableBackpacks, AxGraves]\n")
        z.writestr(zipfile.ZipInfo('config.yml', (2026,11,11,0,0,0)), yaml.safe_dump(config, sort_keys=False))
    print(dest)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--java', type=Path)
    p.add_argument('--server', type=Path)
    args = p.parse_args()
    if args.java and args.server:
        build(args.java.resolve(), args.server.resolve())
    else:
        generate()
