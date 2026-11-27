"""Entrega aislada: una funcion generada y runtime, sin reconstruir salidas ajenas."""
import argparse, json, os, subprocess, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/tier-soporte-27-11'

DELIVERY = """# Soporte excluido del tier - 27/11

Pendiente de instalacion por Claude. No se accedio al servidor remoto.

| Local | Destino |
|---|---|
| `build/tier-soporte-27-11/AstralRPG-TierSoporte.zip` | `world/datapacks/z-AstralRPG-TierSoporte.zip` |
| `build/tier-soporte-27-11/AstralProgression.jar` | `plugins/update/AstralProgression.jar` |

Conservar el datapack principal instalado y los complementos existentes. Este ZIP solo contiene
`pack.mcmeta` y `data/astral/function/player/lvl.mcfunction`; no contiene mapas ni items nuevos.
Comprobar que no haya otro complemento posterior que reemplace esa funcion.
Conservar `plugins/AstralProgression/config.yml` y el nombre del JAR instalado;
el mecanismo plugins/update requiere el mismo nombre. Si difiere, usar ese nombre.

Subir ambos antes del reinicio diario autorizado de las 05:00. No activar reinicio por vacio.
Alternativa con el servidor apagado: sustituir el JAR en `plugins/` y arrancar.
No usar PlugMan, `/reload`, ni reemplazar mundos. No requiere R2 ni resource pack.
Si el complemento no esta activo con prioridad, ejecutar en consola:
`datapack enable "file/z-AstralRPG-TierSoporte.zip" last`.
Comprobar `datapack list enabled`, AstralProgression 1.5.0 sin errores y ejecutar como jugador
`function astral:player/lvl`; con espada T2, varita en inventario y talisman en secundaria,
`scoreboard players get <jugador> astral.wt` debe dar 2 (sin equipo superior).
Matar mobs nuevos T2 con Combate de nivel 10 debe conservar XP completa con varita en mano.
No instalar SupportTierProbe ni configuraciones del ensayo en remoto.
Aternos no permite subir este plugin propio si no esta en su catalogo: no instalar a medias ni eludir restricciones.

La exclusion central corrige mobs (`wt`), elites (`lvl`), dano/PvP (`ht`) y premios de secretos que leen `wt`.
Economia no lee esos scores; conserva sus reglas. Stellarity conserva su etiquetado de equipo.
El tier de XP sigue siendo el de la skill acreditada, con las penalizaciones legitimas existentes.
La varita ya no puede elegir Hechiceria por requisitos heredados; el golpe directo usa Combate
como sin arma Astral, salvo un hechizo real marcado `astral.caster`.

Reproducir: `python datapack-src/deploy_tier_soporte.py --java <java25> --server <Paper-local>`;
`python datapack-src/test_tier_soporte.py`;
`python tools/probar_tier_soporte_paper.py --java <java25> --source <Paper-local>`;
`python tools/verificar_terceros.py`.

Verificado localmente: compilacion JDK 25, 3 pruebas unitarias, 26 comprobaciones Paper
(sin fallos): wt/lvl=2 con espada T2 y los soportes; 132 XP de Combate en los tres
casos sin varita, varita en inventario y varita en mano, factor 1. Auditoria de terceros OK.
La espada Astral T2 exige Combate 16: el ensayo de XP a nivel 10 usa espada vanilla
para evitar ese bloqueo, y conserva la espada Astral T2 para las pruebas de scores.
Estas pruebas locales con jugador simulado no sustituyen la comprobacion remota.

Aviso sugerido para Claude cuando este en vivo: La Varita de Curacion y los talismanes
ya no suben el tier de los mobs ni alteran la skill de tus golpes.
"""

def level_function():
    source = (ROOT/'datapack-src/build.py').read_text(encoding='utf8')
    start = source.index('TIER_EXCLUSIONS =')
    end = source.index('fn("player/lvl", lvl)', start)
    scope = {'NS': 'astral', 'TIER_MAX': 10}
    exec(compile(source[start:end], 'build.py:player/lvl', 'exec'), scope)
    return '\n'.join(scope['lvl'])+'\n'

def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT/'AstralRPG-TierSoporte.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,data in {'pack.mcmeta':json.dumps({'pack':{'min_format':101,'max_format':101,'description':'Astral: soporte no eleva tier'}}), 'data/astral/function/player/lvl.mcfunction':level_function()}.items():
            z.writestr(zipfile.ZipInfo(name,(2026,11,27,0,0,0)),data)
    (ROOT/'build/deploy/tier-soporte-27-11.md').write_text(DELIVERY,encoding='utf8')

def build(java, server):
    from skill_tiers import generate as generate_skill_tiers
    generate_skill_tiers()
    target=ROOT/'.local/tier-soporte-classes';target.mkdir(parents=True,exist_ok=True)
    jars=list((server/'libraries').rglob('*.jar')) + list((server/'versions').rglob('*.jar')) + [ROOT/'.local/asw-native/server/plugins/auraskills.jar',ROOT/'.local/asw-native/server/plugins/mythicmobs.jar',ROOT/'.local/tanda5a/GriefPrevention.jar']
    args=['-encoding','UTF-8','-classpath',os.pathsep.join(map(str,jars)),'-d',str(target),str(ROOT/'datapack-src/runtime/AstralProgression.java')]
    argfile=target/'compile.args';argfile.write_text('\n'.join('"'+s.replace('\\','/')+'"' for s in args))
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','@'+str(argfile)],check=True)
    base=subprocess.check_output(['git','show','HEAD:build/runtime/AstralProgression.jar'],cwd=ROOT)
    import io
    with zipfile.ZipFile(io.BytesIO(base)) as z: files={n:z.read(n) for n in z.namelist() if not n.endswith('.class')}
    import re
    from minijuegos import parkour_worlds
    files['plugin.yml']=re.sub(rb'(?m)^version: .*$',b'version: 1.6.2',files['plugin.yml'])
    files['split-excluded-worlds.txt']=('\n'.join(parkour_worlds())+'\n').encode()
    for p in (target/'astral').glob('AstralProgression*.class'):files[p.relative_to(target).as_posix()]=p.read_bytes()
    with zipfile.ZipFile(OUT/'AstralProgression.jar','w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(files.items()):z.writestr(zipfile.ZipInfo(n,(2026,11,27,0,0,0)),b)
    (ROOT/'build/runtime/AstralProgression.jar').write_bytes((OUT/'AstralProgression.jar').read_bytes())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--java',type=Path);p.add_argument('--server',type=Path);a=p.parse_args()
    generate()
    if a.java:build(a.java.resolve(),a.server.resolve())
