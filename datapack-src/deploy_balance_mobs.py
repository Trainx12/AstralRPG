"""Entrega aislada: vida/XP de slimes y tier exacto de jefes de mundo."""
from pathlib import Path
import json
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/balance-mobs'


def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    # Ejecutar el generador verdadero en un destino privado, sin pisar el build de otras tareas.
    source = ROOT / 'datapack-src/build.py'
    temporary = ROOT / '.local/balance-mobs-generated'
    code = source.read_text(encoding='utf8').replace(
        'OUT = os.path.join(HERE, "..", "build", "AstralRPG-Items")',
        'OUT = '+repr(str(temporary)))
    namespace = {'__file__': str(source), '__name__': 'balance_mobs_build'}
    exec(compile(code, str(source), 'exec'), namespace)
    names = ['mob/roll', 'mob/jefe_mundo', 'mob/jefe_vida']
    with zipfile.ZipFile(OUT/'zz-AstralRPG-BalanceMobs.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        metadata=json.loads(namespace['files']['pack.mcmeta'])
        metadata['pack']['description']='AstralRPG: balance de slimes y tiers de jefes (27/11)'
        z.writestr('pack.mcmeta', json.dumps(metadata, ensure_ascii=False))
        for name in names:
            path='data/astral/function/'+name+'.mcfunction'
            z.writestr(path, namespace['files'][path])
    import ancestral_evento
    ancestral_evento.main()
    # Cambia exclusivamente la condicion de tags de los jefes, conserva el resto del script instalado.
    import gameplay
    old=ROOT/'build/gameplay/astral_gameplay.sk'
    text=old.read_text(encoding='utf8')
    for t in range(1,11):
        text=text.replace(f'if scoreboard tags of {{_e}} contains "astral.jm{t}":',
                          f'if {{_e}} has scoreboard tag "astral.jm{t}":')
    (OUT/'astral_gameplay.sk').write_text(text,encoding='utf8')
    package()


def package():
    paths={
        'world/datapacks/zz-AstralRPG-BalanceMobs.zip':OUT/'zz-AstralRPG-BalanceMobs.zip',
        'plugins/update/AstralProgression.jar':ROOT/'build/runtime/AstralProgression.jar',
        'plugins/Skript/scripts/astral_gameplay.sk':OUT/'astral_gameplay.sk',
        'plugins/Skript/scripts/astral_ancestral.sk':ROOT/'build/gameplay/astral_ancestral.sk',
    }
    with zipfile.ZipFile(OUT/'balance-mobs-instalar.zip','w',zipfile.ZIP_DEFLATED) as z:
        for dest,source in paths.items():
            z.writestr(zipfile.ZipInfo(dest,(2026,11,27,0,0,0)),source.read_bytes())


if __name__ == '__main__':
    if '--package-only' in sys.argv:
        package()
    else:
        generate()
