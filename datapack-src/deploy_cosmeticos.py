"""Prepara la entrega aislada sobre Tienda/Yeti, sin subir archivos al servidor."""
import hashlib
import json
import zipfile
from terceros import ROOT, privado
from cosmeticos_privado import prepare
from cosmeticos_catalogo import catalog
from pack_audit import audit, relocate_model_textures

BASE_SHA = '18107d6003a7f9f190d604e67a9cdf6b6096e02f'
DOWNLOAD = 'https://cdn.modrinth.com/data/TsLS8Py5/versions/ziIzW16f/SkinsRestorer.jar'
SR_SHA = 'a995f863b5eb91338ddd56dc1c22c9f27b69b4ef'


def main():
    prepare()
    base = privado()/'build/entregas/yeti-bastones-guia/AstralRPG-Textures.zip'
    if hashlib.sha1(base.read_bytes()).hexdigest() != BASE_SHA:
        raise ValueError('La base Tienda/Yeti no coincide; revisar antes de combinar')
    with zipfile.ZipFile(base) as z:
        files = {n:z.read(n) for n in z.namelist()}
    original = dict(files)
    source = privado()/'build/item-pack'
    for folder in ('assets/astral_cosmeticos', 'assets/astral/items/cosmeticos'):
        for p in (source/folder).rglob('*'):
            if p.is_file():
                files[p.relative_to(source).as_posix()] = p.read_bytes()
    relocate_model_textures(files)
    dest = privado()/'build/entregas/cosmeticos-skins'
    dest.mkdir(parents=True,exist_ok=True)
    target = dest/'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for n,data in sorted(files.items()):
            z.writestr(zipfile.ZipInfo(n,(2026,11,11,0,0,0)),data,compress_type=zipfile.ZIP_DEFLATED)
    refs = audit(target)
    sha = hashlib.sha1(target.read_bytes()).hexdigest()
    (dest/'pack.sha1').write_text(sha+'\n')
    changed = sorted(n for n in files if original.get(n)!=files[n])
    if any(not n.startswith(('assets/astral_cosmeticos/','assets/astral/items/cosmeticos/')) for n in changed):
        raise ValueError('Se modifico un asset ajeno a los sombreros')
    (dest/'procedencia.json').write_text(json.dumps(dict(base_sha1=BASE_SHA,final_sha1=sha,
        changed=changed,removed=sorted(set(original)-set(files)),references=refs),indent=2),encoding='utf8')
    manifest(sha,refs,len(changed))
    print('FINAL',target,'SHA-1',sha,'referencias',refs)


def manifest(sha,refs,count):
    private='.local/terceros/AstralRPG-privado/build/entregas/cosmeticos-skins'
    rows=[('build/runtime/AstralDecor.jar','plugins/AstralDecor.jar'),
          ('.local/cosmeticos-deps/SkinsRestorer.jar','plugins/SkinsRestorer.jar')]
    rows += [(f'build/lobby/CrazyCrates/crates/{n}.yml',f'plugins/CrazyCrates/crates/{n}.yml')
             for n in ('gacha_cosmeticos','gacha_cosmeticos_garantia')]
    rows += [(f'build/menus/DeluxeMenus/gui_menus/{n}.yml',f'plugins/DeluxeMenus/gui_menus/{n}.yml')
             for n in ('cosmeticos','cosmeticos_sombreros','cosmeticos_alas','gacha_cosmeticos','principal')]
    lines=['# Cosmeticos y SkinsRestorer: entrega sin desplegar','',
        'Generado por `python datapack-src/deploy_cosmeticos.py`. Servidor activo: Empower / Paper 26.1.2 / Java 25; Aternos es la copia antigua.',
        'Requiere haber instalado la entrega `yeti-bastones-guia.md` (incluye Tienda). No reemplazarla por los derivados globales privados.','',
        '## Archivos exactos','', '| Local | Destino |','|---|---|']
    lines += [f'| `{a}` | `{b}` |' for a,b in rows]
    lines += ['',f'Pack FINAL privado: `{private}/AstralRPG-Textures.zip`; SHA-1 `{sha}`.',
        f'Base Tienda/Yeti `{BASE_SHA}`; {count} entradas nuevas/cambiadas, ninguna eliminada, {refs} referencias auditadas. Los assets anteriores se conservan byte por byte.',
        f'Publicar durante el despliegue: `python tools/subir_pack_r2.py {private}/AstralRPG-Textures.zip`. Verificar descarga publica y luego fijar `resource-pack-sha1={sha}`. No usar el ZIP publico.', '',
        '## SkinsRestorer 15.12.6','',
        f'[Descarga exacta del JAR]({DOWNLOAD}); SHA-1 `{SR_SHA}`. El JAR de terceros queda solo en `.local/`, fuera del repo publico.',
        '[Version oficial y compatibilidad Paper 26.1.2](https://modrinth.com/plugin/skinsrestorer/version/ziIzW16f).',
        'Conservar toda la carpeta plugins/SkinsRestorer, skins guardadas y base de datos; respaldarla antes del primer arranque. No cambiar online-mode=false, AuthMe, /premium ni las configuraciones TAB/nonchat.',
        'Integrar estas claves en plugins/SkinsRestorer/config.yml existente (no reemplazarlo completo):','',
        '```yaml','advanced:','  disableOnJoinSkins: true','  enablePaperJoinListener: false',
        '  playerHeadChatObjects: false','server:','  resourcePackFix: false','  proxyMode:',
        '    detection: DISABLED','login:','  noSkinIfLoginCanceled: true','```','',
        'AstralDecor aplica `sr applyskin <jugador>` una vez despues de que AuthMe confirme autenticacion y otra vez si termina de cargar el pack. Conserva la seleccion guardada de SkinsRestorer; sin seleccion usa la skin de la cuenta. No cambia prefijos ni formato del chat.',
        'Si AstralDecor/config.yml existe: el JAR integra automaticamente cosmetics conservando npc-models/npc-skills/hidden-npcs. Mantener `skins-after-login: true` (valor por defecto).',
        'Antes del primer arranque con jugadores, editar las claves anteriores con el servidor apagado. Para generar una config nueva, hacer un arranque de mantenimiento sin jugadores y volver a apagar.', '',
        'Permisos de LuckPerms, consola sin / (no dar skinsrestorer.player ni comodines):','', '```text',
        'lp group default permission set skinsrestorer.command true',
        'lp group default permission set skinsrestorer.command.set true',
        'lp group default permission set skinsrestorer.command.clear true',
        'lp group default permission set skinsrestorer.command.set.other false',
        'lp group default permission set skinsrestorer.command.clear.other false',
        'lp group default permission set skinsrestorer.admin false',
        'lp group default permission set skinsrestorer.admincommand false',
        '```','',
        'Revisar permisos heredados con `lp user <jugador> permission check skinsrestorer.command.set.other`; debe ser false para un usuario normal. Probar /skin <nombre>, /skin set <nombre>, /skin clear; intentar cambiar otro jugador debe denegarse. No agregar skin/sr a allowedCommands de AuthMe antes del login.',
        '[Comandos y permisos oficiales](https://skinsrestorer.net/docs/configuration/commands-permissions), [configuracion de login](https://skinsrestorer.net/docs/reference/server).','',
        '## Instalacion y consola','',
        '1. Medir memoria ANTES con `spark healthreport` y `spark heapsummary` en el servidor activo, tras calentamiento y con la misma cantidad de jugadores. Guardar heap usado, Metaspace y hora solo en el registro privado.',
        '2. Esperar sala vacia, respaldar archivos/configs afectados y server.properties; apagar. Reemplazar los dos JAR y YAML de la tabla. No copiar plugins de prueba ni configs del Paper local.',
        '3. Integrar cosmeticos_sombreros y cosmeticos_alas en gui_menus de plugins/DeluxeMenus/config.yml conservando las entradas existentes; referencia: build/menus/DeluxeMenus/config-gui_menus.yml.',
        '4. Cambiar solo la descripcion del holograma de cosmeticos a Titulos, sombreros y alas (linea exacta abajo); no ejecutar todo build/lobby/comandos.txt. Publicar el pack FINAL en R2 y verificar SHA-1.',
        '5. Encender y revisar Done, AstralDecor 1.3.0, SkinsRestorer 15.12.6 y ausencia de errores. Un reinicio es obligatorio por los JAR; no usar /reload. El arranque carga los YAML.',
        '6. Para ajustes de YAML posteriores: `dm reload`, `crates reload`, `sr reload`. Repetir medicion spark tras el mismo calentamiento/jugadores; no inferir consumo comparando dos servidores distintos.',
        '7. No sustituir mundos ni usar Worlds > Upload en world. Esta tarea no necesita datapack ni copiar mundos.', '',
        'Comando de holograma:','', '```text']
    from lobby import holo_cmds, NPC_POS, WORLD
    x,y,z,_ = NPC_POS['astral_npc_gacha_cosmeticos']
    lines += [f'execute in minecraft:{WORLD} positioned {x} {y+1.55} {z} run minecraft:kill @e[type=minecraft:text_display,tag=astral_holo,distance=..1]']
    lines += [c for c in holo_cmds() if 'Titulos, sombreros y alas' in c]
    lines += ['```','', '## Catalogo y comportamiento','', '| Tipo | Premio | Rareza |','|---|---|---|']
    lines += [f'| {k} | {n} | {r} |' for k,_,n,r,_ in catalog()]
    lines += ['', '19 sombreros de los dos ZIP nuevos y el sombrero de Carnivora existente. Asura aporta alas; no se encontraron otro sombrero, capa o aura para sumar. Armas, herramientas, armaduras y escudo de esos sets siguen fuera de esta gacha.',
        'Permisos permanentes astral.cosmetico.<sombrero|alas>.<clave>; equipar/sacar desde /cosmeticos, sin ocupar inventario ni dar proteccion/estadisticas/vuelo. Sombreros visibles solo sin casco; el display se oculta a su propio portador para no tapar la primera persona. Ver ajuste visual desde otro jugador.',
        'Seleccion en PDC del jugador: conserva reconexion/muerte. Los displays no son items ni drops y se eliminan al morir/salir. No se toca AxGraves. Alas seleccionadas dejan libres ambas manos; se conserva el soporte anterior de alas fisicas en segunda mano.',
        'Los repetidos conservan el comportamiento de titulos: reotorgan el mismo permiso, sin compensacion. Totales de rareza sin cambiar; cada categoria comparte su peso entre mas premios, por lo que bajan probabilidades individuales. La gacha sigue dando titulos y conserva su garantia.',
        'Los sombreros de aldeanos usan astral_cosmeticos:; no se reemplazan texturas vanilla de aldeanos, illagers ni NPC. El pack publico contiene reservas vanilla.', '',
        '## Verificaciones y pendientes','',
        'Resultados reproducibles y limites se documentan en docs/SERVIDOR.md, seccion Cosmeticos y SkinsRestorer preparados. No se ejecutaron acciones en remoto ni se subio a R2.',
        'Memoria spark ANTES/DESPUES en Empower: pendiente; no hay medicion remota ni cifra atribuible al plugin. Completar los pasos 1 y 6 al instalar.',
        'Pendiente con cliente real: tirar gacha normal/garantia; desbloquear, equipar y quitar; ver cabeza e inventario y desde segundo jugador; reconectar; morir con AxGraves y verificar sin drops/duplicados; probar premium/no premium tras AuthMe y TAB/nonchat. La simulacion NMS no certifica el render del cliente ni integraciones remotas.', '']
    (ROOT/'build/deploy/cosmeticos-skins.md').write_text('\n'.join(lines),encoding='utf8')


if __name__=='__main__':
    main()
