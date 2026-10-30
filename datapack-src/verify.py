"""Verificar artefactos y referencias antes de subir. No reemplaza probar en Minecraft.

python verify.py --client-jar C:/.../26.1.2.jar
"""
import argparse
import io
import json
from pathlib import Path
import re
import sys
import zipfile

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-jar",type=Path)
    args=parser.parse_args()
    with zipfile.ZipFile(ROOT/"build/AstralRPG-Items.zip") as pack:
        names=set(pack.namelist())
        for name in names:
            if name.endswith(".json"):json.loads(pack.read(name))
            if not name.endswith(".mcfunction"):continue
            text=pack.read(name).decode("utf-8")
            for ref in re.findall(r"\bfunction (astral:[a-z0-9_./-]+)",text):
                if "$" in ref:continue
                target="data/astral/function/"+ref.split(":",1)[1]+".mcfunction"
                if ref.endswith("/") or "$" in text[text.find(ref)+len(ref):text.find(ref)+len(ref)+2]:continue
                assert target in names,(name,"funcion faltante",ref)
            for item in re.findall(r"loot astral:item/([a-z0-9_]+)",text):
                assert f"data/astral/loot_table/item/{item}.json" in names,(name,item)
        print("Datapack: JSON y referencias de funciones/loot OK")
    sys.path.insert(0,str(HERE/"mobs"))
    import mazmorra
    from mazmorras_data import catalog
    from misiones import DAILIES
    assert len(DAILIES)==14 and len({d[0] for d in DAILIES})==14
    assert [sum(d[1]==i for d in DAILIES) for i in range(3)]==[5,5,4]
    assert mazmorra.MINA["world"]=="mina" and mazmorra.MINA["npc"]=="astral_npc_mina"
    ids=[]
    for path in (ROOT/"build/mythicmobs/mobs").glob("*.yml"):
        ids.extend(re.findall(r"^([a-zA-Z0-9_]+):",path.read_text(encoding="utf-8"),re.M))
    assert len(ids)==len(set(ids)),"IDs de mobs duplicados"
    for i in range(1,5):assert f"astral_mina_control_sala{i}" in ids
    skilltext="\n".join(p.read_text(encoding="utf-8") for p in (ROOT/"build/mythicmobs/skills").glob("*.yml"))
    for objective in re.findall(r"<target\.score\.([^>]+)>",skilltext):
        assert "." not in objective,("El placeholder interpreta puntos como metadatos",objective)
    skillids=set(re.findall(r"^([a-zA-Z0-9_]+):",skilltext,re.M))
    for path in (ROOT/"build/mythicmobs").rglob("*.yml"):
        for ref in re.findall(r"skill\{s=([A-Z][a-zA-Z0-9_]+)",path.read_text(encoding="utf-8")):
            assert ref in skillids,(path,"skill faltante",ref)
    for dungeon in catalog():
        if not dungeon["enabled"]:
            entry=mazmorra.skill_yml(dungeon).split(dungeon["key"].upper()+"_ENTRAR:\n",1)[1]
            assert "minecraft:tp" not in entry, "Entrada no revisada habilitada"
    sanctuary=next(d for d in catalog() if d["key"]=="santuario")
    assert len(sanctuary["rooms"])==1 and len(sanctuary["rooms"][0]["oleadas"])==5
    assert "AST_ANCESTRAL_SEVA_" not in sanctuary["mob_blocks"]
    print("Misiones y mazmorras: IDs unicos, skills, entradas y secuencia ancestral OK")
    if args.client_jar:
        from hud_rpg import hud
        with zipfile.ZipFile(args.client_jar) as vanilla,zipfile.ZipFile(ROOT/"build/AstralRPG-Textures.zip") as pack:
            for name,expected in hud().items():
                path="assets/minecraft/textures/gui/"+name
                assert path in vanilla.namelist() and path in pack.namelist(),path
                actual=Image.open(io.BytesIO(pack.read(path)))
                reference=Image.open(io.BytesIO(vanilla.read(path)))
                assert actual.size==reference.size==expected.size,(path,actual.size,reference.size)
                assert actual.mode=="RGBA",path
                assert path+".mcmeta" not in pack.namelist(),path
        print(f"HUD: {len(hud())} PNG RGBA con rutas y dimensiones del cliente OK")


if __name__=="__main__":main()
