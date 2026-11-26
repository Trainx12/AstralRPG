"""Ensayo local de AstralEstadisticas con 2 clientes: golpes al jefe y a mobs, kills, caidas, curacion y resumen.
No toca el server real.

python tools/probar_estadisticas_paper.py --java <java25> --base .local/testsrv --node <node> --node-modules .local/asw-test/node_modules
"""
import argparse
import os
import re
import shutil
import subprocess
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = '''package astraltest;
import org.bukkit.*; import org.bukkit.entity.*;
public final class StatsProbe extends org.bukkit.plugin.java.JavaPlugin {
  public boolean onCommand(org.bukkit.command.CommandSender s, org.bukkit.command.Command c, String l, String[] a) {
    World w=Bukkit.getWorlds().get(0);
    switch(a[0]) {
      case "spawn" -> { var z=(LivingEntity)w.spawnEntity(new Location(w,0,-58,0),EntityType.valueOf(a[1]));
        z.setAI(false); z.addScoreboardTag(a[2]); var hp=z.getAttribute(org.bukkit.attribute.Attribute.MAX_HEALTH);
        hp.setBaseValue(Double.parseDouble(a[3])); z.setHealth(Double.parseDouble(a[3])); }
      case "hit" -> { var p=Bukkit.getPlayerExact(a[1]);
        for(var e:w.getEntitiesByClass(LivingEntity.class)) if(e.getScoreboardTags().contains(a[2])) { e.setNoDamageTicks(0); e.damage(Double.parseDouble(a[3]),org.bukkit.damage.DamageSource.builder(org.bukkit.damage.DamageType.PLAYER_ATTACK).withCausingEntity(p).withDirectEntity(p).build()); } }
      case "cura" -> { var st=Bukkit.getPluginManager().getPlugin("AstralEstadisticas");
        try { st.getClass().getMethod("curacion",java.util.UUID.class,Player.class,double.class)
          .invoke(st,Bukkit.getPlayerExact(a[1]).getUniqueId(),Bukkit.getPlayerExact(a[2]),Double.parseDouble(a[3])); }
        catch(Exception ex){ throw new RuntimeException(ex); } }
    }
    return true;
  }
}'''
BOT = '''const mc = require(process.argv[2] + '/minecraft-protocol');
const c = mc.createClient({host:'127.0.0.1',port:25623,username:process.argv[3],auth:'offline',version:'26.1.2'});
c.on('error',e=>console.log('BOT ERROR',e.message));
c.on('position',p=>c.write('teleport_confirm',{teleportId:p.teleportId}));
c.on('system_chat',m=>console.log('CHAT',JSON.stringify(m.content)));
'''


def run(args):
    work = ROOT / '.local/estadisticas-probe'
    server = work / 'paper'
    server.mkdir(parents=True, exist_ok=True)
    for name in ('libraries', 'versions', 'cache'):
        if not (server / name).exists():
            shutil.copytree(args.base / name, server / name)
    shutil.copy2(args.base / 'paper.jar', server / 'paper.jar')
    (server / 'eula.txt').write_text('eula=true\n')
    (server / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25623\nonline-mode=false\n'
        'level-name=probe\nlevel-type=minecraft:flat\n'
        'generate-structures=false\nspawn-protection=0\nmanagement-server-enabled=false\nspawn-monsters=false\n')
    shutil.rmtree(server / 'probe', ignore_errors=True)   # mobs de corridas anteriores falsean los numeros
    plugins = server / 'plugins'
    if plugins.exists():
        shutil.rmtree(plugins)
    plugins.mkdir()
    shutil.copy2(ROOT / 'build/estadisticas/AstralEstadisticas.jar', plugins / 'AstralEstadisticas.jar')
    src = work / 'StatsProbe.java'
    src.write_text(PROBE, encoding='utf8')
    deps = [*server.joinpath('libraries').rglob('*.jar'), *server.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(args.java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-nowarn',
        '-classpath', os.pathsep.join(map(str, deps)), '-d', str(work), str(src)], check=True)
    with zipfile.ZipFile(plugins / 'StatsProbe.jar', 'w') as z:
        z.write(work / 'astraltest/StatsProbe.class', 'astraltest/StatsProbe.class')
        z.writestr('plugin.yml', "name: StatsProbe\nversion: 1\nmain: astraltest.StatsProbe\napi-version: '26.1.2'\n"
                   "depend: [AstralEstadisticas]\ncommands:\n  statsprobe: {}\n")
    bot = work / 'bot.cjs'
    bot.write_text(BOT, encoding='utf8')
    log = work / 'paper.log'
    bots, checks = [], 0
    with log.open('w', encoding='utf8') as out:
        process = subprocess.Popen([str(args.java), '-Xms512M', '-Xmx2G', '-jar', 'paper.jar', '--nogui'],
            cwd=server, stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True, encoding='utf8')

        def content():
            return re.sub(r'\x1b\[[0-9;]*m', '', log.read_text(encoding='utf8', errors='replace'))

        def cmd(c, delay=.4):
            process.stdin.write(c + '\n')
            process.stdin.flush()
            time.sleep(delay)

        def check(ok, label):
            nonlocal checks
            if not ok:
                raise AssertionError(label + '; ver ' + str(log))
            checks += 1
            print('STATS PASS ' + label, flush=True)
        try:
            for _ in range(180):
                if 'For help, type' in content():
                    break
                if process.poll() is not None:
                    raise RuntimeError('Paper termino: ' + str(log))
                time.sleep(1)
            else:
                raise TimeoutError('Paper no arranco')
            check('Error occurred while enabling' not in content(), 'plugin carga')
            for name in ('StatA', 'StatB'):
                botlog = (work / f'{name}.log').open('w', encoding='utf8')
                bots.append(subprocess.Popen([str(args.node), str(bot), str(args.node_modules), name],
                                             stdout=botlog, stderr=subprocess.STDOUT))
            for _ in range(60):
                if 'StatA joined the game' in content() and 'StatB joined the game' in content():
                    break
                time.sleep(1)
            else:
                raise TimeoutError('No conectaron los clientes')
            cmd('minecraft:gamemode survival StatA')
            cmd('minecraft:gamemode survival StatB')
            cmd('statsprobe spawn PIG previo 100')
            cmd('statsprobe hit StatA previo 10')          # antes de inicio: no cuenta
            cmd('astralstats inicio probe')
            cmd('statsprobe spawn PIG jefe 1000')
            cmd('minecraft:tag @e[tag=jefe] add cav.jefe')
            cmd('minecraft:execute if entity @e[tag=jefe] run say HAY_JEFE')
            for _ in range(3):
                cmd('statsprobe hit StatA jefe 100')
            cmd('statsprobe hit StatB jefe 50')
            cmd('minecraft:data get entity @e[tag=jefe,limit=1] Health')
            for i in range(3):
                cmd(f'statsprobe spawn PIG m{i} 20')
                cmd(f'statsprobe hit StatB m{i} 30')          # mata con 20 de dano real
            cmd('statsprobe spawn PIG ma 20')
            cmd('statsprobe hit StatA ma 30')
            cmd('astralstats muerte StatA')
            cmd('astralstats muerte StatA')
            cmd('statsprobe cura StatB StatA 42')
            cmd('astralstats fin probe', 7)
            text = content()
            line = next((l for l in text.splitlines() if 'Resumen probe' in l), '')
            print(line)
            check('StatA jefe=300 total=320 mobs=1 caidas=2 cura=0' in line, 'StatA (sin el golpe previo)')
            check('StatB jefe=50 total=110 mobs=3 caidas=0 cura=42' in line, 'StatB')
            time.sleep(1)
            def chat():
                return ''.join((work / f'{n}.log').read_text(encoding='utf8', errors='replace') for n in ('StatA', 'StatB'))
            check('Estadisticas de la mazmorra' not in chat(), 'oculto: jugadores comunes no lo ven')
            cmd('mazstats publico si')
            cmd('astralstats inicio probe')
            cmd('statsprobe spawn PIG jefe2 1000')
            cmd('minecraft:tag @e[tag=jefe2] add cav.jefe')
            cmd('statsprobe hit StatB jefe2 80')
            cmd('statsprobe hit StatA jefe2 20')
            cmd('astralstats fin probe', 7)
            t = chat()
            check('Estadisticas de la mazmorra' in t and 'Mas dano al jefe' in t and 'StatB' in t, 'publico: resumen y premios en el chat')
            check(not re.search(r'(ERROR|WARN)\]: \[Astral|at astral\.', content()), 'sin errores del plugin')
            print(f'STATS RESULT checks={checks} failures=0', flush=True)
        finally:
            for b in bots:
                if b.poll() is None:
                    b.terminate()
            if process.poll() is None:
                cmd('stop', 0)
                process.wait(timeout=60)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    for n in ('java', 'base', 'node', 'node-modules'):
        ap.add_argument('--' + n, type=Path, required=True)
    a = ap.parse_args()
    for k, v in vars(a).items():
        setattr(a, k, v.resolve())
    run(a)
