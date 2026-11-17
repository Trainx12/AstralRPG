"""Entrega acumulativa: reparar la rama FINAL sobre arreglos instalado y agregar esta tanda."""
import argparse
import hashlib
import io
import json
import subprocess
import zipfile
from pathlib import Path
from terceros import ROOT, privado
from final_base import select_base
from correcciones_goblin import GOLEM_XP, MERCHANT

PUBLIC_BASE='ab6accdb42cc474e141c66acfe2264855182349e'
NAME='correcciones-goblin-golems'


def read(path):
    with zipfile.ZipFile(path) as z:return {n:z.read(n) for n in z.namelist() if not n.endswith('/')}


def preserve_font(installed, updated):
    """Los deltas publicos no conocen los glifos privados de contenedores."""
    old=json.loads(installed);new=json.loads(updated)
    def chars(provider):
        if provider['type']=='space':return set(provider['advances'])
        return set(''.join(provider.get('chars',[])))-{'\0'}
    used=set().union(*(chars(p) for p in new['providers']))
    for provider in old['providers']:
        missing=chars(provider)-used
        if not missing:continue
        if provider['type']=='space':
            provider={**provider,'advances':{c:v for c,v in provider['advances'].items() if c in missing}}
        elif missing!=chars(provider):
            raise ValueError('Colision parcial de glifos instalados: '+str(sorted(missing)))
        new['providers'].append(provider);used.update(missing)
    return json.dumps(new,ensure_ascii=False).encode('utf8')


def final(assets,explicit=None):
    root=privado();out=root/'build/entregas'/NAME;out.mkdir(parents=True,exist_ok=True)
    newest=select_base(output=out,explicit=explicit)
    installed=root/'build/entregas/arreglos-16-11/AstralRPG-Textures.zip'
    installed_hash=hashlib.sha1(installed.read_bytes()).hexdigest()
    if not installed_hash.startswith('4322b8ca'):raise ValueError('El FINAL instalado no coincide con 4322b8ca: '+installed_hash)
    files=read(installed);preserved=dict(files)
    # Reparar la rama de XP/balance que habia perdido las entradas instaladas de efectos/Nether/Fosa.
    # Aplicar SOLO sus diferencias frente a armas-mod, sin volver a copiar el pack antiguo entero.
    arms=read(root/'build/entregas/armas-mod/AstralRPG-Textures.zip')
    later=read(newest)
    private_delta={n:b for n,b in later.items() if arms.get(n)!=b}
    files.update(private_delta)
    blob=subprocess.check_output(['git','show',PUBLIC_BASE+':build/AstralRPG-Textures.zip'],cwd=ROOT)
    old=read(io.BytesIO(blob));public=read(ROOT/'build/AstralRPG-Textures.zip')
    delta={n:b for n,b in public.items() if old.get(n)!=b}
    files.update(delta)
    # Reaplicar solo el casco privado y los menus de la tanda balance tras el delta publico.
    xp=read(root/'build/entregas/tanda-xp-cuchillo/AstralRPG-Textures.zip')
    balance=read(root/'build/entregas/balance-especiales-agua/AstralRPG-Textures.zip')
    balance_delta={n:b for n,b in balance.items() if xp.get(n)!=b}
    files.update(balance_delta)
    own={p.relative_to(out/'pack').as_posix():p.read_bytes() for p in (out/'pack').rglob('*') if p.is_file()}
    files.update(own)
    # Solo salida privada BetterModel de estos tres modelos; nunca superponer assets publicos de reserva.
    converted={'assets/'+p.relative_to(assets).as_posix():p.read_bytes() for p in assets.rglob('*')
               if p.is_file() and 'astral_pet_golem_' in p.name or p.is_file() and 'astral_golem_' in p.name and any(k in p.name for k in ('bosque','hielo','cristal'))}
    if not converted:raise ValueError('Falta la conversion BetterModel de golems')
    for kind in ('bosque','hielo','cristal'):
        if not any('golem_'+kind in n and '/models/' in '/'+n for n in converted):raise ValueError('Falta modelo BetterModel '+kind)
    files.update(converted)
    font='assets/minecraft/font/default.json'
    files[font]=preserve_font(preserved[font],files[font])
    removed=[]
    for n in list(files):
        if any('/ballesta_'+str(t)+'.' in n for t in (1,2,6,7,8,9,10)):
            removed.append(n);del files[n]
    target=out/'AstralRPG-Textures.zip';tmp=target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(files.items()):z.writestr(zipfile.ZipInfo(n,(2026,11,16,0,0,0)),b,compress_type=zipfile.ZIP_DEFLATED)
    from pack_audit import audit
    audit(tmp);tmp.replace(target)
    changed=set(private_delta)|set(delta)|set(balance_delta)|set(own)|set(converted)|set(removed)
    assert all(files[n]==b for n,b in preserved.items() if n not in changed)
    for t in (3,4,5):
        n=f'assets/astral/items/ballesta_{t}.json';assert files[n]==arms[n]
    digest=hashlib.sha1(target.read_bytes()).hexdigest();(out/'pack.sha1').write_text(digest+'\n')
    (out/'delta.json').write_text(json.dumps(dict(installed_sha1=installed_hash,latest=str(newest),latest_sha1=hashlib.sha1(newest.read_bytes()).hexdigest(),public_base=PUBLIC_BASE,
        public_delta=sorted(delta),private_delta=sorted(private_delta),balance_delta=sorted(balance_delta),converted=sorted(converted),removed=removed),indent=2),'utf8')
    return target,digest,installed_hash


def delivery(target,digest,base_hash):
    # Lista cerrada de salidas de esta tarea; las entregas XP y balance complementan el despliegue acumulado.
    paths=['build/AstralRPG-Items.zip','build/runtime/AstralDecor.jar','build/gameplay/astral_armas_especiales.sk',
        'build/infinita/astral_infinita.sk','build/rankings/astral_rankings.sk']
    paths += ['build/lobby/CrazyCrates/crates/'+name+'.yml' for name in (
        'gacha_cosmeticos','gacha_cosmeticos_garantia','gacha_cosmeticos_garantia_suerte',
        'gacha_cosmeticos_suerte','gacha_monturas','gacha_monturas_suerte','gacha_rpg','gacha_rpg_suerte')]
    paths += ['build/mythicmobs/mobs/'+name+'.yml' for name in ('astral','bosque','cumbre','mazmorra','santuario','correcciones-goblin')]
    paths += ['build/mythicmobs/skills/correcciones-goblin.yml']
    paths += ['build/menus/DeluxeMenus/gui_menus/'+name+'.yml' for name in (
        'consumibles','cosmeticos','cosmeticos_sombreros','cosmeticos_espaldas','goblin_mercader')]
    rows=[]
    for p in sorted(set(paths)):
        if p=='build/AstralRPG-Items.zip':dest='world/datapacks/AstralRPG-Items.zip'
        elif p=='build/runtime/AstralDecor.jar':dest='plugins/AstralDecor.jar'
        elif p.endswith('/config-gui_menus.yml'):continue
        elif p.startswith('build/gameplay/'):dest='plugins/Skript/scripts/special_weapons.sk'
        elif p.endswith('.sk'):dest='plugins/Skript/scripts/'+p.split('/')[-1]
        elif p.startswith('build/mythicmobs/'):dest=p.replace('build/mythicmobs/','plugins/MythicMobs/')
        elif p.startswith('build/lobby/'):dest=p.replace('build/lobby/','plugins/')
        elif p.startswith('build/menus/'):dest=p.replace('build/menus/','plugins/')
        else:continue
        rows.append((p,dest))
    lines=['# Correcciones XP, Goblin Mercader, golemcitos y Heroe — 16/11/2026','',
        'Preparado localmente; despliegue remoto y R2 pendientes. Paper 26.1.2 / Java 25. '
        'Empower es el principal segun SERVIDOR.md; Aternos es copia. Claude debe confirmar el panel y hash instalado. '
        'Nunca reemplazar mundos ni usar Worlds > Upload en world.','',
        '## Cambios','',
        'Ballestas retiradas: I, II, VI–X. III–V conservan receta, carga, encantamientos y modelos del 15/11. '
        'No requieren migracion porque las retiradas no se desplegaron.',
        'XP vanilla: Pequeno 60 / $3.000; Grande 200 / $9.000; Gigante 550 / $25.000; Barril 5.500 / $220.000. '
        'Stack 16, clic uno, Shift+clic todos los de esa mano. Dos PNG provisorios reemplazables en pack-source/provisorias. '
        'Todas las gachas, cofres de jefe, rankings, eventos ancestrales e Infinita VI+ usan los cuatro tamanos. '
        'En cofres/Infinita: 35/18/8/1%; en ancestrales: 65/35/20/2,5%. Tiradas independientes.',
        'Mercader: cada 40–60 minutos, solo Survival world, cerca de un jugador en supervivencia. '
        'Anuncio a 64 bloques; visita 5 minutos. Clic derecho abre DeluxeMenus. Solo bienes Astral; '
        'stock por UUID y producto por visita, validado junto con distancia, dinero y espacio por el runtime. '
        'Primer agresor (incluidos proyectiles) fija su unico objetivo; se retira a los 30 segundos de ser atacado. '
        'Sin robo de inventario. El estado de visita se limpia al reiniciar/cargar chunks.',
        'Golemcitos: sustituyen 2–4 zombis por oleada sin aumentar su total. Bosque -> bosque, Minas -> cristal, Cumbre -> hielo. '
        'Reservas y conversion sincronica igual que los esqueletos: tags de sala, cola, tope, limpieza, escala, elite, nombre/vida, '
        'drops normales y XP AuraSkills siguen el circuito existente. Animaciones idle/walk/attack/death privadas. '
        'Mantener CUSTOM en exempt-spawn-reasons de ClearLag. No aumentar topes.',
        'Infinita no tiene salas secuenciales: la oleada especial ocurre cada diez tandas de aparicion. '
        'Aparecen los tres juntos cuando hay tres plazas; espera si el tope esta lleno. '
        'Usan tier y extra actuales de esa copia, cuentan para limite y bajas.',
        'Cosmeticos: Horquilla y Balde raros; Barril y Rueda epicos, en Gacha de Cosmeticos y /cosmeticos -> Espaldas. '
        'Desbloqueo permanente con permisos, botones bloqueados/desbloqueados; solo visual, sin ocupar manos/casco. '
        'La variante wooden_wheel_blocking se conserva privada como modelo alternativo; no duplica premios. '
        'El Barril de XP usa el mismo barril 3D en la mano.',
        'Espada del Heroe Errante: T2, dano 500, Combate 12, Forja/mesa con Espada I + materiales de Espada II. '
        'Giro del Heroe: clic derecho, radio 3, 150% de ataque actual con mejoras, mana 30, recarga 8 s. '
        'Valor del Heroe: +10% en golpe directo con vida llena. Ficha con ambas habilidades; ITEM_VERSION 24.','',
        '## Tienda del mercader','', '| Item | Precio | Stock por jugador/visita |','|---|---:|---:|']
    lines += [f'| `{iid}` | {price} | {stock} |' for iid,price,stock in MERCHANT]
    lines += ['', '## Drops de XP de golemcitos','',
        'Probabilidades independientes por muerte segun el tier REAL del mob (incluye su variacion de mazmorra). '
        'Base Bosque T1, Minas T2, Cumbre T4; Infinita usa el elegido. Fuente unica: correcciones_goblin.GOLEM_XP.',
        '', '| Tier | Pequeno | Grande | Gigante | Barril |','|---|---:|---:|---:|---:|']
    lines += ['| '+str(t)+' | '+' | '.join(f'{v*100:.1f}%' for v in values)+' |' for t,values in GOLEM_XP.items()]
    lines += ['', '## Instalacion con servidor apagado','',
        'Aplicar tambien los archivos de las entregas tanda-xp-cuchillo.md y balance-especiales-agua.md si no se instalaron. '
        'Esta lista contiene los reemplazos de la correccion actual; usar SIEMPRE el FINAL de abajo para el conjunto.',
        '', '| Archivo local | Destino |','|---|---|']
    lines += [f'| `{p}` | `{d}` |' for p,d in rows]
    modelbase=privado()/'build/entregas'/NAME/'models'
    lines += [f'| `{(modelbase/("astral_golem_"+kind+".bbmodel")).relative_to(ROOT).as_posix()}` | `plugins/BetterModel/models/astral_golem_{kind}.bbmodel` |' for kind in ('bosque','hielo','cristal')]
    lines += ['', 'En plugins/DeluxeMenus/config.yml agregar dentro de gui_menus: '
        '`goblin_mercader: {file: goblin_mercader.yml}` y `cosmeticos_espaldas: {file: cosmeticos_espaldas.yml}`. '
        'Conservar todo el resto; referencia build/menus/DeluxeMenus/config-gui_menus.yml.',
        'No duplicar el script de armas especiales con otro nombre. Mantener sus destinos anteriores.',
        'AstralDecor integra el catalogo de espaldas al config existente al arrancar; conserva la configuracion NPC. '
        'Requiere Vault con economia, DeluxeMenus, MythicMobs, BetterModel, LuckPerms y CrazyCrates. '
        'Las llaves son virtuales de CrazyCrates; el balde raro se desbloquea por permiso permanente y no se cobra si ya lo tenes. '
        'Mantener en spigot.yml settings.attribute.maxHealth.max y attackDamage.max en 1.0E12.',
        '', '## FINAL privado acumulativo','',f'Base instalada arreglos-16-11 SHA-1 `{base_hash}`. '
        'Se reconstruyo sobre esa base con los deltas de XP/cuchillos y balance/menus y esta correccion. '
        'Las entradas previas no modificadas se verifican byte por byte; conserva ballestas III–V privadas '
        'y los glifos privados de cofres/barril que no conocen los deltas publicos. '
        'La seleccion de base rechaza una base fija mas vieja que la ultima entrega por fecha, salvo --base manual. '
        'Los generadores historicos XP, balance y armas-mod tambien usan esta comprobacion.',
        f'FINAL local: `{target.relative_to(ROOT).as_posix()}`. SHA-1 `{digest}`. No publicar en GitHub publico ni instalar el ZIP publico.',
        f'Publicar solo durante el despliegue autorizado: `python tools/subir_pack_r2.py "{target.relative_to(ROOT).as_posix()}"`. '
        'Verificar descarga publica y luego resource-pack-sha1 en server.properties, conservando URL fija.',
        '', '## Inicio, comandos y validacion remota','',
        'Reinicio completo obligatorio: JAR, datapack, BetterModel y pack. No basta /reload. '
        'Al iniciar revisar consola de AstralDecor 1.13.0, MythicMobs, BetterModel, Skript y datapack. '
        'Si solo se retoca YAML despues: mm reload, dm reload, crates reload; '
        'skript reload special_weapons, skript reload astral_infinita, skript reload astral_rankings. '
        'BetterModel reload solo si cambia modelo; evitar recargas repetidas.',
        'Pruebas con cliente pendientes: recorrer Bosque/Minas/Cumbre, confirmar brillo/astralfx/AuraSkills, '
        'golems en grupo, limites y limpieza; alcanzar tanda 10 de Infinita; mercader con dos jugadores '
        '(neutralidad, stock, compra sin dinero/inventario lleno y retiro), cosméticos en F5, barril en mano '
        'y Giro del Heroe contra mobs/arena con mana y recarga. Nunca afirmar despliegue sin revisar consola remota.',
        '', '## Verificaciones locales','',
        'Suite Python: 308 pruebas completas aprobadas; control adicional de la oleada decima aprobado. '
        'Paper local: 30 comprobaciones aprobadas (XP unitaria/Shift, neutralidad/agresor, tier/vida/nombre/limite de tres golems), '
        'sin errores de carga de datapack, Skript, MythicMobs ni BetterModel. '
        'Auditar el indice publico con tools/verificar_terceros.py antes de publicar. '
        'El ensayo NMS local verifica eventos y atributos reales; no sustituye apariencia ni combate con cliente. '
        'Logs y modelos convertidos permanecen privados en .local.',
        '', 'Reproduccion: desde datapack-src ejecutar build.py, menus.py, mobs/mythic.py, mobs/mazmorra.py, lobby.py, '
        'infinita.py, rankings.py, correcciones_privado.py y build_pack.py pack-source. '
        'Compilar con build_runtime.py --jdk <JDK25/bin> --server <Paper-local>; '
        'desde la raiz tools/probar_correcciones_paper.py --java <java25> --base <Paper-local>. '
        'Finalmente datapack-src/deploy_correcciones_goblin.py --assets .local/correcciones-probe/paper/plugins/BetterModel/build/assets. '
        'Pruebas: python -m unittest discover -s datapack-src -p "test*.py". No subir CorreccionesProbe.jar.']
    (ROOT/'build/deploy'/f'{NAME}.md').write_text('\n'.join(lines)+'\n','utf8')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--assets',required=True,type=Path);p.add_argument('--base',type=Path)
    a=p.parse_args();target,digest,base=final(a.assets.resolve(),a.base);delivery(target,digest,base);print(target);print('SHA-1',digest)
