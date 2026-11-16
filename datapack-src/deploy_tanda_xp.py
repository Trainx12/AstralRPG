"""Entrega propia y FINAL privado por delta sobre armas-mod, sin regenerar arte ajeno."""
import hashlib
import io
import json
import subprocess
import zipfile
from pathlib import Path
from PIL import Image
from tanda_xp import ROOT, XP, PRECIOS
from terceros import privado

BASE_PUBLICO='ab6accdb42cc474e141c66acfe2264855182349e'
BASE_FINAL='build/entregas/armas-mod/AstralRPG-Textures.zip'


def final():
    import sys
    from final_base import select_base
    explicit=Path(sys.argv[sys.argv.index('--base')+1]) if '--base' in sys.argv else None
    base=select_base(privado()/BASE_FINAL,privado()/'build/entregas/tanda-xp-cuchillo',explicit)
    if not base.exists():raise FileNotFoundError('Falta el FINAL de armas-mod; no se sustituye por el publico.')
    public=ROOT/'build/AstralRPG-Textures.zip'
    old_blob=subprocess.check_output(['git','show',BASE_PUBLICO+':build/AstralRPG-Textures.zip'],cwd=ROOT)
    with zipfile.ZipFile(io.BytesIO(old_blob)) as old,zipfile.ZipFile(public) as new,zipfile.ZipFile(base) as z:
        old_names=set(old.namelist());files={n:z.read(n) for n in z.namelist()}
        delta={n:new.read(n) for n in new.namelist() if n not in old_names or old.read(n)!=new.read(n)}
        files.update(delta)
        # Los modelos ya elegidos de ballestas se conservan byte por byte.
        for t in (3,4,5):
            name=f'assets/astral/items/ballesta_{t}.json'
            if files[name]!=z.read(name):raise ValueError('Se perderia la ballesta privada '+str(t))
    out=privado()/'build/entregas/tanda-xp-cuchillo';out.mkdir(parents=True,exist_ok=True)
    target=out/'AstralRPG-Textures.zip'
    tmp=target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):z.writestr(zipfile.ZipInfo(name,(2026,11,16,0,0,0)),data,compress_type=zipfile.ZIP_DEFLATED)
    from pack_audit import audit
    audit(tmp);tmp.replace(target)
    digest=hashlib.sha1(target.read_bytes()).hexdigest()
    (out/'pack.sha1').write_text(digest+'\n')
    (out/'delta.json').write_text(json.dumps({'base_sha1':hashlib.sha1(base.read_bytes()).hexdigest(),'public_base':BASE_PUBLICO,'files':sorted(delta)},indent=2))
    return target,digest,len(delta),hashlib.sha1(base.read_bytes()).hexdigest()


def delivery():
    target,digest,n,base_hash=final()
    # Solo archivos generados de la tarea, comparados con el estado publico de entrada.
    candidates=subprocess.check_output(['git','diff','--name-only',BASE_PUBLICO,'--','build'],cwd=ROOT,text=True).splitlines()
    candidates+= [p.relative_to(ROOT).as_posix() for p in (ROOT/'build/lobby/CrazyCrates/crates').glob('*_suerte.yml')]
    candidates+=['build/menus/DeluxeMenus/gui_menus/consumibles.yml','build/shop/EconomyShopGUI/sections/Consumibles.yml','build/shop/EconomyShopGUI/shops/Consumibles.yml']
    pairs=[]
    for rel in sorted(set(candidates)):
        dest=None
        if rel=='build/AstralRPG-Items.zip':dest='world/datapacks/AstralRPG-Items.zip'
        elif rel=='build/runtime/AstralDecor.jar':dest='plugins/AstralDecor.jar'
        elif rel.startswith('build/lobby/CrazyCrates/crates/'):dest=rel.replace('build/lobby/','plugins/',1)
        elif rel.startswith('build/mythicmobs/') and rel.endswith('.yml'):dest=rel.replace('build/mythicmobs/','plugins/MythicMobs/',1)
        elif rel.startswith('build/menus/DeluxeMenus/gui_menus/'):dest=rel.replace('build/menus/','plugins/',1)
        elif rel.startswith('build/shop/EconomyShopGUI/'):dest=rel.replace('build/shop/','plugins/',1)
        elif rel in ('build/minas/Skript/scripts/astral_minas.sk','build/infinita/astral_infinita.sk','build/rankings/astral_rankings.sk'):dest='plugins/Skript/scripts/'+Path(rel).name
        if dest:pairs.append((rel,dest))
    lines=['# Tanda XP, cuchillo, ballestas, mochilas y botones — 16/11/2026','',
           'Preparada localmente. Despliegue remoto pendiente; no se accedio a Aternos/Empower ni se subio a R2.',
           'Paper 26.1.2 / Java 25. La documentacion identifica Empower como principal desde el 07/11; Aternos es copia.',
           'Confirmar el panel y la version del pack actualmente instalado antes de aplicar. No sustituir mundos; nunca Worlds > Upload en world.','',
           '## Comportamiento','',
           'XP vanilla directa: frasco 550 puntos y barril 5.500. Stack 16; clic usa uno, Shift + clic todos los de esa mano. '
           'Un frasco lleva aproximadamente del nivel 0 al 20 (la barra usa redondeo flotante).',
           'Manzana comible incluso con hambre llena: cinco minutos reales, persiste al desconectar/reiniciar, otra renueva. '
           'No altera Luck vanilla ni permisos de OP. AstralDecor guarda el vencimiento en PDC y muestra segundos en actionbar/astral.suerte.',
           'CrazyCrates: tres tablas normales y tres de garantia, mas sus seis variantes _suerte. Pesos de raros/epicos/legendarios x1,5, '
           'normalizados: comun 55,81395%, poco comun 23,25581%, raro 15,34884%, epico 4,88372%, legendario 0,69767%. '
           'La garantia conserva 87,5% epico / 12,5% legendario. El runtime toma suerte al comprar el lote y la conserva para sus llaves diferidas. '
           'El menu y la vitrina normal anuncian probabilidades base; las variantes incluyen su chance individual en la ruleta.',
           'Fuentes: las tres gachas (frasco poco comun, barril epico; manzana rara solo Cosmeticos); todos los cofres de jefe '
           '(8% frasco, 1% barril, 3% manzana, tiradas independientes y mismo cooldown existente); podios semanales '
           '(1: barril+3 frascos+manzana; 2: 2 frascos+manzana; 3: frasco+manzana); eventos ancestrales existentes '
           '(20% frasco, 2,5% barril); Infinita VI+ cada 5 min presentes (8% frasco, 1% barril).',
           'Tienda: '+', '.join(f'{iid} ${price:,}' for iid,price in PRECIOS.items())+'. EconomyShopGUI gratuito abre un menu DeluxeMenus propio con Vault y espacio libre.',
           'Cuchillos T1-T10: Combate, 53% del dano de espada y velocidad 3,0: DPS 1,59 frente a 1,60. '
           'Se ajusto el 55% orientativo porque daria mas DPS que la espada. Costos/requisitos de la espada, mejora exige cuchillo anterior. Forja, mesa cuando cabe y guia incluidos.',
           'Ballestas T1-T10: 1,20 / 1,05 / 0,90 / 0,65 / 0,20 / 0,18 / 0,16 / 0,14 / 0,12 / 0,10 s. '
           'Punteria por tier; perforacion hasta IV y multidisparo desde IV; municion normal gratis desde V. Las armaduras de Arquero y los arcos ya tienen 10 tiers. '
           'No hay una familia de flechas Astral por tier: la municion vanilla escala con Punteria, sin hueco que completar.',
           'Mochilas: un cuerpo 3D comun con cuerpo, bolsillo, tapa y correas; seis texturas. El runtime cambia solo item_model '
           'de cabezas con expendablebackpacks:backpack_uuid y backpack_tier 1..6. Conserva UUID, contenido y el resto de los componentes.',
           'Lobby: Velocidad II. Botones: iconos provisorios en los slots existentes; no se movieron ventanas salvo Infinita VI-X+ '
           '(pasa de 36 a 54 slots, usa el marco y tarjetas del selector bajo; Volver 45, Cerrar 53). '
           'Los Proximamente comparten modelo. No se hizo arte final. Test de botones: sin excepciones clickeables; los rellenos y cabezas reales sin acciones pueden seguir vanilla.','',
           '## Instalacion (servidor apagado)','',
           '1. Apagar desde el panel y respaldar solo los archivos de esta lista que se reemplazan.',
           '2. Subir los siguientes archivos locales a sus destinos. No tocar regiones ni mapas.','',
           '| Archivo local | Destino |','|---|---|']
    lines += [f'| `{a}` | `{b}` |' for a,b in pairs]
    lines += ['', 'Agregar en `plugins/DeluxeMenus/config.yml`, dentro de `gui_menus`: `consumibles: {file: consumibles.yml}`. '
              'Conservar los registros anteriores; consultar `build/menus/DeluxeMenus/config-gui_menus.yml`.',
              'La seccion EconomyShopGUI Consumibles usa slot 43: comprobar que ese slot este libre en el panel actual antes de instalar; mover solo la nueva seccion si esta ocupado.','',
              '## Pack FINAL privado','',f'Base: `{BASE_FINAL}` (SHA-1 `{base_hash}`); se conservan todas sus entradas y las ballestas privadas III-V. '
              f'Delta publico contra `{BASE_PUBLICO}`: {n} entradas.',
              f'Local: `{target.relative_to(ROOT).as_posix()}`. SHA-1: `{digest}`.',
              'No instalar el ZIP publico: no lleva los modelos elegidos de mods. Este FINAL tampoco se publica en GitHub publico.',
              f'Con el servidor apagado: `python tools/subir_pack_r2.py "{target.relative_to(ROOT).as_posix()}"`. '
              'Verificar la descarga publica antes de actualizar `resource-pack-sha1` en server.properties. Mantener la URL fija existente.',
              'Si el FINAL instalado es posterior o no coincide con la base indicada, rehacer la combinacion con ese FINAL; no reemplazarlo ciegamente.','',
              '## Inicio y recargas','',
              'Iniciar con Java 25: reinicio completo obligatorio por JAR, datapack y hash del resource pack. '
              'Revisar consola: AstralDecor 1.11.0, recetas registradas, ningun error de enchantments/loot/functions.',
              'Las configs se cargan al iniciar. Si se corrige solo YAML despues: `crates reload`, `dm reload`, `mm reload`, `sreload`; '
              '`skript reload astral_minas`, `skript reload astral_infinita`, `skript reload astral_rankings`. No repetir recargas si ya cargo correctamente al iniciar.','',
              '## Pruebas de juego','',
              '`loot give JUGADOR loot astral:item/frasco_xp_gigante`, repetir 16 veces; usar clic y Shift + clic y verificar los puntos, tambien con mano secundaria. '
              '`loot give JUGADOR loot astral:item/barril_xp`.',
              '`loot give JUGADOR loot astral:item/manzana_esmeralda`; comer, mirar barra de accion y `scoreboard players get JUGADOR astral.suerte`; '
              'comer otra tras un minuto: vuelve a 300, no 540. Probar x1/x10, garantia, inventario lleno y efecto que vence durante la animacion.',
              '`execute as JUGADOR run function astral:admin/kit_cuchillos`; probar Combate, Forja, mesa y velocidades. '
              '`execute as JUGADOR run function astral:admin/kit_ballestas`; comprobar carga, proyectiles, perforacion, multidisparo y flechas desde T5.',
              '`backpack give JUGADOR leather` (y copper/iron/gold/diamond/netherite): conservar un objeto dentro, mirar mano/inventario, desconectar, mejorar y reiniciar. '
              'Entrar/salir del lobby: Velocidad II caduca a los 3 segundos de salir. Revisar todos los botones nuevos y ambas ventanas Infinita.','',
              '## Verificacion y limites','',
              'Verificado: suite completa de 293 pruebas OK, suite especifica ampliada de 8 pruebas OK; compilacion Java 25 OK; '
              'Paper 26.1.2 arranca y reinicia con XP RESULT failures=0 en ambos ciclos. Auditor de terceros OK. '
              'Los logs quedan en .local y no se publican. '
              'El ensayo usa un jugador NMS y dobles de los comandos CrazyCrates: verifica XP real, consumo, PDC, seleccion de caja y reinicio, '
              'no reemplaza un cliente visual, la animacion real de CrazyCrates ni las compras en el panel remoto.',
              'Pendiente remoto: subir archivos, R2, reiniciar, consola y pruebas con cliente. No se afirmo ningun despliegue.','',
              '## Texturas provisorias','',
              'Reemplazar estos PNG locales y regenerar `build_pack.py pack-source` y `deploy_tanda_xp.py`. '
              'Se crean una sola vez y no se pisan al regenerar. Los nombres de item_model quedan fijos. '
              'Cuchillo y ballestas pendientes de mod: tabla `PENDIENTES` en armas_mod.py, valores None.','',
              '| Item o boton | PNG local | Tamano esperado |','|---|---|---|']
    for p in sorted((ROOT/'datapack-src/pack-source/provisorias').glob('*.png')):
        with Image.open(p) as im: size=f'{im.width}x{im.height}'
        lines.append(f'| `{p.stem}` | `{p.relative_to(ROOT).as_posix()}` | {size} RGBA |')
    path=ROOT/'build/deploy/tanda-xp-cuchillo.md';path.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(path);print('FINAL SHA-1',digest)


if __name__=='__main__':delivery()
