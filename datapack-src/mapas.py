"""Inspeccion local de mundos ZIP, sin importar sus datapacks ni modificar originales.

python mapas.py C:/Users/.../Downloads --out ../.local/mapas
Las vistas previas y los recortes de terceros deben quedar fuera del repo publico.
"""
import argparse
import gzip
import io
import json
import math
from pathlib import Path
import re
import struct
import zipfile
import zlib

from PIL import Image, ImageDraw

MAPS = {"bosque": "bosque.zip", "desierto": "desierto.zip", "nieve": "nieve.zip",
        "forja": "volcan gigante.zip", "santuario": "vacio.zip",
        "arena": "batalla_de_Jugadores.zip", "reserva": "volcan.zip"}


class NBT:
    """Lector NBT big-endian. No ejecuta comandos ni carga codigo de los mapas."""
    def __init__(self, data, typed=False):
        self.f = io.BytesIO(data)
        self.typed = typed

    def number(self, fmt):
        size = struct.calcsize(fmt)
        return struct.unpack(fmt, self.f.read(size))[0]

    def string(self): return self.f.read(self.number(">H")).decode("utf-8", errors="replace")

    def payload(self, typ):
        value = self._payload(typ)
        return (typ, value) if self.typed else value

    def _payload(self, typ):
        if typ in (1,2,3,4,5,6): return self.number({1:">b",2:">h",3:">i",4:">q",5:">f",6:">d"}[typ])
        if typ == 7: return self.f.read(self.number(">i"))
        if typ == 8: return self.string()
        if typ == 9:
            child = self.number(">B"); count = self.number(">i")
            return [self.payload(child) for _ in range(count)]
        if typ == 10:
            result = {}
            while (child := self.number(">B")) != 0:
                name = self.string(); result[name] = self.payload(child)
            return result
        if typ in (11,12):
            count = self.number(">i"); size, code = (4,"i") if typ == 11 else (8,"q")
            return list(struct.unpack(f">{count}{code}", self.f.read(count * size)))
        raise ValueError(f"Tag NBT no soportado: {typ}")

    def root(self):
        typ = self.number(">B"); self.string()
        return self.payload(typ)


def nbt_string(text):
    raw=text.encode("utf-8")
    return struct.pack(">H",len(raw))+raw


def nbt_payload(node):
    typ,value=node
    if typ in (1,2,3,4,5,6):return struct.pack({1:">b",2:">h",3:">i",4:">q",5:">f",6:">d"}[typ],value)
    if typ==7:return struct.pack(">i",len(value))+value
    if typ==8:return nbt_string(value)
    if typ==9:
        child=value[0][0] if value else 0
        return struct.pack(">Bi",child,len(value))+b"".join(nbt_payload(n) for n in value)
    if typ==10:
        return b"".join(bytes([n[0]])+nbt_string(k)+nbt_payload(n) for k,n in value.items())+b"\x00"
    if typ in (11,12):
        return struct.pack(">i",len(value))+struct.pack(f'>{len(value)}{"i" if typ==11 else "q"}',*value)
    raise ValueError(typ)


def sanitize(tree):
    """Conservar bloques del escenario; quitar logica y premios del minijuego original."""
    root=tree[1]
    chunk=root["Level"][1] if "Level" in root else root
    replacements=0
    forbidden={"minecraft:command_block","minecraft:chain_command_block","minecraft:repeating_command_block",
               "minecraft:structure_block","minecraft:jigsaw","minecraft:spawner","minecraft:trial_spawner"}
    sections=chunk.get("sections",chunk.get("Sections",(9,[])))[1]
    for _,section in sections:
        state=section.get("block_states",(10,{}))[1]
        palette=state.get("palette",section.get("Palette",(9,[])))[1]
        for _,entry in palette:
            if entry.get("Name",(8,""))[1] in forbidden:
                entry["Name"]=(8,"minecraft:stone_bricks")
                entry.pop("Properties",None)
                replacements+=1
    for key in ("block_entities","TileEntities"):
        if key not in chunk:continue
        keep=[]
        for entity in chunk[key][1]:
            data=entity[1]
            ident=data.get("id",(8,""))[1].lower()
            if "Command" in data or any(s in ident for s in ("command_block","mob_spawner","trial_spawner","structure_block","jigsaw")):
                continue
            for field in ("Items","LootTable","LootTableSeed"):
                data.pop(field,None)
            keep.append(entity)
        chunk[key]=(9,keep)
    chunk.pop("Entities",None) # versiones antiguas guardaban las entidades en la region
    for key in ("block_ticks","fluid_ticks","TileTicks","LiquidTicks"):
        chunk.pop(key,None)
    return replacements


def prepare(path,out,bounds):
    """Exportar solo chunks dentro de un rectangulo XZ a un ZIP privado de regiones."""
    x0,z0,x1,z1=bounds
    if x1<x0 or z1<z0 or (x1-x0+1)*(z1-z0+1)>4_194_304:
        raise ValueError("Rectangulo invalido o mayor a 2048x2048 bloques")
    count=replacements=0
    with zipfile.ZipFile(path) as source,zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as dest:
        level=next(n for n in source.namelist() if n.endswith("level.dat"))
        prefix=level[:-9]
        pattern=re.compile(re.escape(prefix)+r"(?:dimensions/minecraft/overworld/)?region/r\.(-?\d+)\.(-?\d+)\.mca")
        for name in source.namelist():
            match=pattern.fullmatch(name)
            if not match:continue
            rx,rz=map(int,match.groups())
            if rx*512>x1 or rx*512+511<x0 or rz*512>z1 or rz*512+511<z0:continue
            raw=source.read(name)
            header=bytearray(8192);sectors=[];sector=2
            for slot in range(1024):
                cx,cz=rx*32+slot%32,rz*32+slot//32
                if not (x0//16<=cx<=x1//16 and z0//16<=cz<=z1//16):continue
                offset=int.from_bytes(raw[slot*4:slot*4+3],"big")*4096
                if not offset:continue
                length=int.from_bytes(raw[offset:offset+4],"big");kind=raw[offset+4]
                payload=raw[offset+5:offset+4+length]
                if kind==2:payload=zlib.decompress(payload)
                elif kind==1:payload=gzip.decompress(payload)
                elif kind!=3:raise ValueError(f"Compresion no soportada: {kind} en {name}")
                tree=NBT(payload,typed=True).root();replacements+=sanitize(tree)
                encoded=zlib.compress(bytes([tree[0]])+nbt_string("")+nbt_payload(tree))
                record=struct.pack(">I",len(encoded)+1)+b"\x02"+encoded
                blocks=math.ceil(len(record)/4096)
                if blocks>255:raise ValueError("Chunk demasiado grande")
                header[slot*4:slot*4+4]=sector.to_bytes(3,"big")+bytes([blocks])
                sectors.append(record.ljust(blocks*4096,b"\x00"));sector+=blocks;count+=1
            if sectors:dest.writestr(f"region/r.{rx}.{rz}.mca",bytes(header)+b"".join(sectors))
    return {"chunks":count,"paletas_de_logica_reemplazadas":replacements,"archivo":str(out)}


def packed(data, index, bits):
    per = 64 // bits
    return (data[index // per] >> ((index % per) * bits)) & ((1 << bits) - 1)


def block(chunk, x, y, z):
    for section in chunk.get("sections", chunk.get("Sections", [])):
        if section["Y"] != y // 16: continue
        state = section.get("block_states", {})
        palette = state.get("palette", section.get("Palette", []))
        if not palette: return "minecraft:air"
        data = state.get("data", section.get("BlockStates", []))
        idx = (y % 16) * 256 + z * 16 + x
        val = packed(data, idx, max(4,(len(palette)-1).bit_length())) if len(palette) > 1 else 0
        entry = palette[val]
        return entry["Name"]
    return "minecraft:air"


def top(chunk, x, z):
    hmap = chunk.get("Heightmaps", {}).get("WORLD_SURFACE", [])
    if hmap:
        ymin = int(chunk.get("yPos", -4)) * 16
        y = packed(hmap, z*16+x, 9) + ymin - 1
        return y, block(chunk, x, y, z)
    for section in sorted(chunk.get("sections", chunk.get("Sections", [])), key=lambda s:s["Y"], reverse=True):
        for y in range(section["Y"]*16+15,section["Y"]*16-1,-1):
            name = block(chunk,x,y,z)
            if name not in ("minecraft:air", "minecraft:cave_air", "minecraft:void_air"):
                return y,name
    return -64,"minecraft:air"


def chunk_records(data):
    for slot in range(1024):
        offset = int.from_bytes(data[slot*4:slot*4+3],"big") * 4096
        if not offset: continue
        length = int.from_bytes(data[offset:offset+4],"big")
        kind = data[offset+4]
        raw = data[offset+5:offset+4+length]
        if kind == 2: raw = zlib.decompress(raw)
        elif kind == 1: raw = gzip.decompress(raw)
        elif kind != 3: continue
        nbt = NBT(raw).root()
        yield nbt.get("Level",nbt)


def color(name, y):
    name = name.removeprefix("minecraft:")
    if "air" in name: return (20,24,32)
    if "lava" in name: base = (240,88,22)
    elif any(s in name for s in ("snow","ice","quartz")): base = (208,225,235)
    elif any(s in name for s in ("leaves","grass","moss","fern")): base = (58,107,59)
    elif "water" in name: base = (42,91,156)
    elif any(s in name for s in ("sand","terracotta")): base = (192,164,106)
    elif any(s in name for s in ("log","wood","planks")): base = (117,85,49)
    elif any(s in name for s in ("nether","blackstone","basalt")): base = (77,51,55)
    elif any(s in name for s in ("gold","yellow")): base = (204,170,59)
    elif "amethyst" in name or "purpur" in name: base = (150,97,190)
    else: base = (118,121,122)
    shade = max(0.5,min(1.35,0.65+(y+64)/350))
    return tuple(min(255,int(c*shade)) for c in base)


def inspect(path, out, radius=512, center=None):
    with zipfile.ZipFile(path) as archive:
        levels = [n for n in archive.namelist() if n.endswith("level.dat") and "/DIM" not in n]
        if len(levels) != 1: raise ValueError(f"Se esperaba un mundo en {path}, hay {levels}")
        levelpath = levels[0]; prefix = levelpath[:-len("level.dat")]
        level = NBT(gzip.decompress(archive.read(levelpath))).root()["Data"]
        spawn = [level.get("SpawnX"), level.get("SpawnY"), level.get("SpawnZ")]
        # 26.1 usa un compuesto spawn (pos, dimension, yaw, pitch).
        if spawn[0] is None:
            spawn = level.get("spawn", {}).get("pos", [0,80,0])
        roots = [prefix+"region/", prefix+"dimensions/minecraft/overworld/region/"]
        regions = [n for n in archive.namelist() if any(re.fullmatch(re.escape(r)+r"r\.-?\d+\.-?\d+\.mca",n) for r in roots)]
        report = {"archivo": path.name, "nombre":level.get("LevelName"), "version":level.get("Version"),
                  "spawn":spawn, "region_files":len(regions), "zip_MB":round(path.stat().st_size/1e6,1),
                  "regiones_MB":round(sum(archive.getinfo(n).file_size for n in regions)/1e6,1),
                  "datapacks_excluidos":sum("/datapacks/" in n for n in archive.namelist()),
                  "nota":"Vista topografica, no confirma accesibilidad a pie ni posiciones de combate."}
        # Mapa 1 pixel cada 4 bloques alrededor del spawn original, con cuadricula.
        cx, _, cz = spawn
        if center is not None: cx,cz=center
        cx,cz=int(cx),int(cz)
        x0,z0=(cx-radius)//16*16,(cz-radius)//16*16
        side=radius*2; image=Image.new("RGB",(side//4,side//4),(20,24,32))
        heights=[]
        for reg in regions:
            rx,rz=map(int,Path(reg).stem.split(".")[1:])
            if rx*512>=x0+side or rx*512+512<=x0 or rz*512>=z0+side or rz*512+512<=z0: continue
            for chunk in chunk_records(archive.read(reg)):
                bx,bz=chunk["xPos"]*16,chunk["zPos"]*16
                if not (x0<=bx<x0+side and z0<=bz<z0+side): continue
                for z in range(0,16,4):
                    for x in range(0,16,4):
                        y,name=top(chunk,x,z)
                        image.putpixel(((bx+x-x0)//4,(bz+z-z0)//4),color(name,y))
                        if bx<=cx<bx+16 and bz<=cz<bz+16: heights.append(y)
        report["superficie_cerca_spawn"] = [min(heights),max(heights)] if heights else None
        report["vista_limites_xz"]=[x0,z0,x0+side-1,z0+side-1]
        image=image.resize((768,768),Image.Resampling.NEAREST)
        draw=ImageDraw.Draw(image)
        for pos in range(0,side+1,128):
            u=int(pos/side*768)
            draw.line((u,0,u,767),fill=(110,110,110),width=1)
            draw.line((0,u,767,u),fill=(110,110,110),width=1)
            draw.text((u+2,4),str(x0+pos),fill="white")
            draw.text((4,u+16),str(z0+pos),fill="white")
        sx,sz=int((cx-x0)/side*768),int((cz-z0)/side*768)
        draw.ellipse((sx-6,sz-6,sx+6,sz+6),outline="red",width=2)
        draw.text((sx+10,sz),"centro" if center is not None else "spawn",fill="red")
        image.save(out/(path.stem+".png"))
        return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",type=Path)
    parser.add_argument("--out",type=Path,default=Path(__file__).resolve().parent.parent/".local/mapas")
    parser.add_argument("--map",choices=MAPS)
    parser.add_argument("--center",type=int,nargs=2,metavar=("X","Z"))
    parser.add_argument("--radius",type=int,default=512)
    parser.add_argument("--prepare",type=int,nargs=4,metavar=("XMIN","ZMIN","XMAX","ZMAX"),
                        help="Recortar y limpiar regiones; necesita --map. No incluye level.dat, datapacks ni entidades")
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    if args.prepare:
        if not args.map:parser.error("--prepare necesita --map")
        print(json.dumps(prepare(args.directory/MAPS[args.map],args.out/(args.map+"-regiones.zip"),args.prepare)))
        return
    reports=[]
    for key,name in MAPS.items():
        if args.map and args.map!=key: continue
        report=inspect(args.directory/name,args.out,args.radius,args.center)
        reports.append(report);print(json.dumps(report,ensure_ascii=False),flush=True)
    (args.out/"informe.json").write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding="utf-8")


if __name__=="__main__":main()
