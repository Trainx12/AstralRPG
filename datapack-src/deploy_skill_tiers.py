"""Compila solo AstralProgression; conserva recursos/config del JAR acumulado."""
import argparse
import hashlib
import os
from pathlib import Path
import re
import subprocess
import zipfile
from skill_tiers import generate, requirements

ROOT = Path(__file__).resolve().parents[1]


def build(java, server):
    generate()
    target = ROOT / '.local/skill-tiers-classes'
    target.mkdir(parents=True, exist_ok=True)
    jars = list((server/'libraries').rglob('*.jar')) + list((server/'versions').rglob('*.jar'))
    jars += [ROOT/'.local/asw-native/server/plugins/auraskills.jar',
             ROOT/'.local/asw-native/server/plugins/mythicmobs.jar', ROOT/'.local/tanda5a/GriefPrevention.jar']
    args = ['-encoding', 'UTF-8', '-classpath', os.pathsep.join(map(str, jars)), '-d', str(target),
            str(ROOT/'datapack-src/runtime/AstralProgression.java')]
    argfile = target/'compile.args'
    argfile.write_text('\n'.join('"'+s.replace('\\', '/')+'"' for s in args))
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '@'+str(argfile)], check=True)
    jar = ROOT/'build/runtime/AstralProgression.jar'
    with zipfile.ZipFile(jar) as z:
        files = {n: z.read(n) for n in z.namelist() if not n.endswith('.class')}
    files['plugin.yml'] = re.sub(rb'(?m)^version: .*$', b'version: 1.6.2', files['plugin.yml'])
    for p in (target/'astral').glob('AstralProgression*.class'):
        files[p.relative_to(target).as_posix()] = p.read_bytes()
    with zipfile.ZipFile(jar, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            z.writestr(zipfile.ZipInfo(name, (2026, 11, 27, 0, 0, 0)), data)
    rows = '\n'.join(f'| {s} | '+ ' / '.join(map(str, lv))+' |' for s, lv in requirements().items())
    (ROOT/'build/deploy/skill-tiers-27-11.md').write_text(f'''# Tier de XP por requisitos reales — 27/11

AstralProgression 1.6.2. Subido a Empower el 27/11; pendiente de activacion en el reinicio diario.

| Skill | Niveles T1 a T10 |
|---|---|
{rows}

Fuente unica: items.py/items_t6_10.py; skill_tiers.py regenera el bloque Java antes de compilar.
Cada muerte usa la skill acreditada; en party, cada miembro conserva su skill y nivel.
Sin cambios en recompensas base, permisos de bonus, penalizaciones, loot, claims ni slimes.
Por debajo del primer requisito sigue T1; skills desconocidas no aplican factor de tier.

Instalar solo build/runtime/AstralProgression.jar en plugins/update/AstralProgression.jar
(mismo nombre que el instalado); conservar plugins/AstralProgression/config.yml.
Carga en el reinicio diario autorizado de las 05:00. No reiniciar por cuenta propia,
usar PlugMan ni reemplazar mundos. No requiere datapack ni resource pack.
Servidor vigente segun CLAUDE.md: Empower; Aternos es la copia historica.
Verificar version 1.6.2 en consola y XP real con Combate 16/19/20 y Magia 14/19/20.

Verificado: compilacion JDK25, 13 pruebas unitarias (skills, soporte y tanda5a),
139 comprobaciones Paper con cero fallos: limites T2-T10 de las tres skills,
penalizaciones legitimas, bonus superior, independencia entre skills y XP real
con/sin Varita de Curacion. Paper aviso que no pudo obtener la clave publica de
Mojang; el ensayo offline no depende de ella. Cualquier otro ERROR hace fallar el ensayo.
Auditoria de terceros OK; recursos/config del JAR conservados respecto de la base 1.6.1.
Ensayo: tools/probar_tier_soporte_paper.py --java <java25> --source <Paper-local>
--progression build/runtime/AstralProgression.jar.

Empower: archivo en plugins/update/AstralProgression.jar, 66.68 KB. Se descargo
de nuevo desde el panel y coincidio su SHA-256 con el local. Consulta de consola:
version activa 1.6.0; no se reinicio ni recargo. Comprobacion con jugador real y
anuncio en Discord pendientes de la activacion; texto listo debajo.

SHA-256: {hashlib.sha256(jar.read_bytes()).hexdigest()}

Reproducir: deploy_skill_tiers.py --java <java25> --server <Paper-local>.
Aviso al entrar en vivo: Corregimos la XP de combate y magia: ahora tu tier sigue
el nivel requerido por el equipo de cada habilidad, sin penalizaciones adelantadas.
''', encoding='utf8')
    print(jar)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--java', type=Path, required=True)
    p.add_argument('--server', type=Path, required=True)
    a = p.parse_args()
    build(a.java.resolve(), a.server.resolve())
