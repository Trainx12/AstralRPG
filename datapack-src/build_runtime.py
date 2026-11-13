"""Compila exclusivamente codigo propio con un JDK y librerias Paper locales."""
import argparse
import os
from pathlib import Path
import subprocess
import zipfile
import yaml

ROOT=Path(__file__).resolve().parents[1]


def build(jdk,server):
    target=ROOT/'.local/tanda4b-classes'
    target.mkdir(parents=True,exist_ok=True)
    jars=list((server/'libraries').rglob('*.jar')) + [server/'plugins/bettermodel.jar',server/'plugins/mythicmobs.jar']
    if not jars:
        raise FileNotFoundError('Faltan dependencias Paper locales')
    compiler = [str(jdk/('java.exe' if os.name=='nt' else 'java')), '-m','jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*compiler, '-encoding','UTF-8','-source','25','-target','25',
        '-classpath',os.pathsep.join(str(p) for p in jars),'-d',str(target),str(ROOT/'datapack-src/runtime/AstralDecor.java')],check=True)
    dest=ROOT/'build/runtime/AstralDecor.jar'; dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted((target/'astral').glob('AstralDecor*.class')):
            z.writestr(zipfile.ZipInfo(p.relative_to(target).as_posix(),(2026,11,10,0,0,0)),p.read_bytes())
        z.writestr(zipfile.ZipInfo('mesa.json',(2026,11,10,0,0,0)), (ROOT/'build/runtime/mesa.json').read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml',(2026,11,10,0,0,0)), 'name: AstralDecor\nversion: 1.8.0\nmain: astral.AstralDecor\napi-version: \'26.1.2\'\nsoftdepend: [WorldGuard, MythicMobs, BetterModel, Vault, EconomyShopGUI, AuthMe, SkinsRestorer, AuraSkills]\ncommands:\n  astralcosmetic:\n    usage: /astralcosmetic <sombrero> <clave|quitar>\n')
        from mobs.tanda3c import NPC_MODELOS, MAQUINAS, MAZMORRAS
        models={mid:'astral_npc_'+name for mid,name in NPC_MODELOS.items()}
        skills={mid:'AST_NPC_'+name for mid,name in NPC_MODELOS.items()}
        for mid in MAQUINAS:
            models[mid]=mid; skills[mid]='AST_MODELO_'+mid
        for suffix in ('venta','mina_venta','bosque_venta'):
            mid='astral_npc_'+suffix; models[mid]='astral_vendedor'; skills[mid]='AST_VENDEDOR_PRIVADO'
        for dungeon in MAZMORRAS:
            for mid,name in [('astral_npc_'+dungeon,'bruja'),('astral_'+dungeon+'_guia','mago')]:
                models[mid]='astral_npc_'+name; skills[mid]='AST_NPC_'+name
        from cosmeticos_catalogo import catalog
        cosmetics={kind:{key:model for k,key,_,_,model in catalog() if k==kind} for kind in ('sombrero','alas')}
        config={'skins-after-login':True,'cosmetics':cosmetics,'npc-models':models,'npc-skills':skills,'hidden-npcs':['astral_npc_'+d for d in MAZMORRAS]}
        z.writestr(zipfile.ZipInfo('config.yml',(2026,11,10,0,0,0)),yaml.safe_dump(config,sort_keys=False))
    print(dest)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jdk',required=True,type=Path,help='Carpeta bin del JDK 25')
    parser.add_argument('--server',required=True,type=Path)
    args=parser.parse_args(); build(args.jdk.resolve(),args.server.resolve())
