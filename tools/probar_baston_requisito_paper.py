"""Ensayo aislado con cliente de protocolo local, Skript, AuraSkills, PAPI y DeluxeMenus.

No toca servidores remotos. Dependencias Java y DeluxeMenus se pasan explicitamente.
El modulo minecraft-protocol debe estar instalado en --node-modules.
"""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]

PROBE = '''command /reqprobe <player> <text>:
    executable by: console
    trigger:
        asw_identify(arg-1)
        wait 1 tick
        if arg-2 is "staff":
            asw_staff(arg-1)
            wait 4 ticks
            execute console command "execute if score %name of arg-1% astral.cd matches 1.. run say REQ_CAST yes"
        else:
            asw_request(arg-1)
            wait 2 ticks
            if arg-2 is "missing":
                delete {-asw.skill::%uuid of arg-1%::*}
            set {_ok} to asw_requirement(arg-1)
            send "REQ_CHECK %{_ok}%" to console
        execute console command "dm execute %name of arg-1% [console] say REQ_MANA %%auraskills_mana_int%%"
'''


def run(args):
    work = ROOT/'.local/baston-requisito-probe'
    server = work/'paper'
    server.mkdir(parents=True, exist_ok=True)
    for name in ('libraries', 'versions', 'cache'):
        if not (server/name).exists():
            shutil.copytree(args.base/name, server/name)
    shutil.copy2(args.base/'paper.jar', server/'paper.jar')
    (server/'eula.txt').write_text('eula=true\n')
    (server/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25619\nonline-mode=false\n'
        'level-name=probe\nlevel-type=minecraft:flat\n'
        'generator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\n'
        'generate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\n')
    plugins = server/'plugins'
    plugins.mkdir(exist_ok=True)
    for name in ('skript.jar', 'auraskills.jar', 'nightcore.jar', 'excellentenchants.jar', 'packetevents.jar'):
        shutil.copy2(args.base/'plugins'/name, plugins/name)
    shutil.copy2(args.papi, plugins/'placeholderapi.jar')
    shutil.copy2(args.deluxemenus, plugins/'DeluxeMenus.jar')
    # Solo configuracion: no copiar cuentas/variables de otros jugadores.
    aura = plugins/'AuraSkills'
    aura.mkdir(exist_ok=True)
    for p in (args.base/'plugins/AuraSkills').glob('*.yml'):
        shutil.copy2(p, aura/p.name)
    # El servidor real usa legacy: sin el preset no existen Sorcery ni Forging.
    with zipfile.ZipFile(args.base/'plugins/AuraSkills/presets/legacy.zip') as z:
        for name in z.namelist():
            if name.startswith('files/') and name.endswith('.yml'):
                target = (aura/name.removeprefix('files/')).resolve()
                if not target.is_relative_to(aura.resolve()):
                    raise ValueError(name)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read(name))
    # Evita que una regeneracion entre muestras oculte el debito exacto de 200.
    # Plugin exclusivo del ensayo; no se instala en el servidor real.
    source = work/'ManaProbe.java'
    source.write_text('''package astraltest;
public final class ManaProbe extends org.bukkit.plugin.java.JavaPlugin implements org.bukkit.event.Listener {
  public void onEnable() { getServer().getPluginManager().registerEvents(this,this); }
  @org.bukkit.event.EventHandler public void regen(dev.aurelium.auraskills.api.event.mana.ManaRegenerateEvent e) {
    if(e.getPlayer().getName().equals("ReqProbe")) e.setCancelled(true);
  }
}''', encoding='utf8')
    deps = [*server.joinpath('libraries').rglob('*.jar'), *server.joinpath('versions').rglob('*.jar'), plugins/'auraskills.jar']
    subprocess.run([str(args.java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8',
        '-classpath', os.pathsep.join(map(str, deps)), '-d', str(work), str(source)], check=True)
    with zipfile.ZipFile(plugins/'ManaProbe.jar', 'w') as z:
        z.write(work/'astraltest/ManaProbe.class', 'astraltest/ManaProbe.class')
        z.writestr('plugin.yml', "name: ManaProbe\nversion: 1\nmain: astraltest.ManaProbe\napi-version: '26.1.2'\ndepend: [AuraSkills]\n")
    scripts = plugins/'Skript/scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT/'build/gameplay/astral_armas_especiales.sk', scripts/'special_weapons.sk')
    (scripts/'reqprobe.sk').write_text(PROBE, encoding='utf8')
    packs = server/'probe/datapacks'
    packs.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT/'build/AstralRPG-Items.zip', packs/'AstralRPG-Items.zip')
    bot = work/'bot.cjs'
    bot.write_text('''const mc = require(process.argv[2] + '/minecraft-protocol');
const c = mc.createClient({host:'127.0.0.1',port:25619,username:'ReqProbe',auth:'offline',version:'26.1.2'});
c.on('error',e=>console.log('BOT ERROR',e.message));
c.on('login',()=>console.log('BOT LOGIN'));
c.on('position',p=>c.write('teleport_confirm',{teleportId:p.teleportId}));
c.on('end',r=>console.log('BOT END',r));
''', encoding='utf8')
    log = work/'paper.log'
    bot_process = None
    checks = 0
    with log.open('w', encoding='utf8') as out, (work/'bot.log').open('w', encoding='utf8') as botout:
        process = subprocess.Popen([str(args.java), '-Xms512M', '-Xmx2G', '-jar', 'paper.jar', '--nogui'],
            cwd=server, stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)
        def content():
            return re.sub(r'\x1b\[[0-9;]*m', '', log.read_text(encoding='utf8', errors='replace'))
        def cmd(c, delay=.5):
            start = len(content())
            process.stdin.write(c+'\n')
            process.stdin.flush()
            time.sleep(delay)
            return content()[start:]
        def check(ok, label):
            nonlocal checks
            if not ok:
                raise AssertionError(label+'; ver '+str(log))
            checks += 1
            print('REQ PASS '+label, flush=True)
        def mana():
            result = cmd('dm execute ReqProbe [console] say REQ_MANA %auraskills_mana_int%')
            values = re.findall(r'REQ_MANA (\d+)', result)
            if not values:
                raise AssertionError('No se leyo mana; '+result)
            return int(values[-1])
        def equip(iid):
            cmd('minecraft:clear ReqProbe')
            cmd(f'loot give ReqProbe loot astral:item/{iid}', 1)
            cmd('scoreboard players set ReqProbe astral.cd 0')
        try:
            for _ in range(180):
                if 'For help, type' in content():
                    break
                if process.poll() is not None:
                    raise RuntimeError('Paper termino: '+str(log))
                time.sleep(1)
            else:
                raise TimeoutError('Paper no arranco')
            check('Encountered ' not in content() and 'Error occurred while enabling' not in content(), 'plugins y Skript cargan')
            bot_process = subprocess.Popen([str(args.node), str(bot), str(args.node_modules)], stdout=botout, stderr=subprocess.STDOUT)
            for _ in range(60):
                if 'ReqProbe joined the game' in content():
                    break
                time.sleep(1)
            else:
                raise TimeoutError('No conecto cliente; ver bot.log')
            cmd('minecraft:gamemode survival ReqProbe')
            cmd('minecraft:effect give ReqProbe minecraft:resistance infinite 255 true')
            cmd('auraskills:skills modifier add ReqProbe wisdom reqprobe 1000')
            equip('baston_5')
            cmd('auraskills:skills skill setlevel ReqProbe sorcery 20')
            cmd('auraskills:mana set ReqProbe 500 true')
            parsed = cmd('papi parse ReqProbe %auraskills_sorcery%')
            check(bool(re.search(r'INFO\]: 20\s', parsed)), 'placeholder sorcery devuelve 20')
            before = mana()
            check(before >= 200, 'mana suficiente para T5')
            result = cmd('reqprobe ReqProbe staff')
            after = mana()
            check('REQ_CAST yes' not in result and after == before, 'T5 nivel20 no lanza ni cobra')
            cmd('auraskills:skills skill setlevel ReqProbe sorcery 32')
            cmd('auraskills:mana set ReqProbe 500 true')
            before = mana()
            result = cmd('reqprobe ReqProbe staff')
            after = mana()
            check('REQ_CAST yes' in result and before-after == 200, 'T5 nivel32 lanza y cobra exactamente 200')
            cmd('scoreboard players set ReqProbe astral.cd 0')
            cmd('auraskills:mana set ReqProbe 0 true')
            result = cmd('reqprobe ReqProbe staff')
            check('REQ_CAST yes' not in result, 'mana insuficiente no lanza')
            result = cmd('reqprobe ReqProbe missing')
            check('REQ_CHECK false' in result, 'lectura de habilidad ausente bloquea')
            for iid, req in (('agua_espada', 20), ('espada_heroe_errante', 16)):
                equip(iid)
                cmd(f'auraskills:skills skill setlevel ReqProbe fighting {req-1}')
                check('REQ_CHECK false' in cmd('reqprobe ReqProbe check'), iid+' debajo del requisito bloquea')
                cmd(f'auraskills:skills skill setlevel ReqProbe fighting {req}')
                check('REQ_CHECK true' in cmd('reqprobe ReqProbe check'), iid+' al requisito permite')
            equip('espada_destello')
            check('REQ_CHECK true' in cmd('reqprobe ReqProbe missing'), 'especial sin requisito sigue permitido')
            check(not any(s in content() for s in ('Failed to load', 'Error loading', "Couldn't parse data file")), 'datapack sin errores de carga')
            print(f'REQ RESULT checks={checks} failures=0', flush=True)
        finally:
            if bot_process and bot_process.poll() is None:
                bot_process.terminate()
                bot_process.wait(timeout=15)
            if process.poll() is None:
                cmd('stop', 0)
                process.wait(timeout=60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('java', 'base', 'papi', 'deluxemenus', 'node', 'node-modules'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    for key, value in vars(args).items():
        setattr(args, key, value.resolve())
    run(args)
