"""Genera el parche de terreno para los veinte pozos en Aternos."""
import gzip
import json
from itertools import product
from zipfile import ZIP_DEFLATED, ZipFile

from mapas import NBT, nbt_payload, nbt_string
from minas import DIM, LOCAL, MAP, MINES, OUT, PASTE_X, PASTE_Z, PIT, ROOT, SPACING

ORIGIN = (75, 73, 76)
SIZE = (40, 21, 35)
NS = "astral_reparar_minas"


def repair_blocks(schematic):
    palette = {value: name for name, value in schematic["Palette"].items()}
    indices = []
    index = shift = 0
    for byte in schematic["BlockData"]:
        index |= (byte & 127) << shift
        if byte < 128:
            indices.append(index)
            index = shift = 0
        else:
            shift += 7

    width, length = schematic["Width"], schematic["Length"]

    def original(x, y, z):
        return palette[indices[x - PASTE_X + width * (z - PASTE_Z + length * (y - 64))]]

    changes = {}
    for x, y, z in product(range(75, 106), range(73, 93), range(76, 107)):
        if not (PIT["x1"] <= x <= PIT["x2"] and PIT["z1"] <= z <= PIT["z2"]):
            changes[x, y, z] = original(x, y, z)

    for y in range(73, 93):
        for x in range(81, 114):
            for z in (77, 109):
                changes[x, y, z] = "minecraft:bedrock"
        for z in range(78, 109):
            for x in (81, 113):
                changes[x, y, z] = "minecraft:bedrock"
        for x, z, neighbor_x, neighbor_z in (
            *((x, z, x, n) for x in range(94, 101) for z, n in ((76, 75), (110, 111))),
            *((x, z, n, z) for z in range(90, 97) for x, n in ((80, 79), (114, 115))),
        ):
            changes[x, y, z] = original(neighbor_x, y, neighbor_z) if y == 92 else "minecraft:stone"

    return changes


def structure(changes, data_version):
    palette, blocks = {}, []
    for position, block in sorted(changes.items()):
        index = palette.setdefault(block, len(palette))
        pos = [axis - origin for axis, origin in zip(position, ORIGIN, strict=True)]
        assert all(0 <= axis < size for axis, size in zip(pos, SIZE, strict=True))
        assert not (82 <= position[0] <= 112 and 78 <= position[2] <= 108)
        blocks.append((10, {"pos": (9, [(3, axis) for axis in pos]), "state": (3, index)}))

    states = []
    for state in palette:
        name, _, properties = state.rstrip("]").partition("[")
        tag = {"Name": (8, name)}
        if properties:
            tag["Properties"] = (10, {k: (8, v) for k, v in
                                      (pair.split("=") for pair in properties.split(","))})
        states.append((10, tag))
    root = (10, {"DataVersion": (3, data_version), "size": (9, [(3, axis) for axis in SIZE]),
                 "palette": (9, states), "blocks": (9, blocks), "entities": (9, [])})
    return gzip.compress(b"\x0a" + nbt_string("") + nbt_payload(root), mtime=0)


def generate():
    schematic = NBT(gzip.decompress((LOCAL / MAP).read_bytes())).root()
    changes = repair_blocks(schematic)
    with ZipFile(ROOT / "build/AstralRPG-Items.zip") as items:
        meta = json.loads(items.read("pack.mcmeta"))
    meta["pack"]["description"] = "Reparación del terreno de las 20 Minas Astrales"
    OUT.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUT / "Reparacion-Minas-Astrales.zip", "w", ZIP_DEFLATED) as pack:
        pack.writestr("pack.mcmeta", json.dumps(meta))
        pack.writestr(f"data/{NS}/structure/pozo.nbt", structure(changes, schematic["DataVersion"]))
        for i in range(1, len(MINES) + 1):
            x = (i - 1) * SPACING
            area = f"{x + 75} 76 {x + 114} 110"
            pack.writestr(f"data/{NS}/function/cargar_{i}.mcfunction",
                          f"execute in {DIM} run forceload add {area}\n")
            pack.writestr(f"data/{NS}/function/reparar_{i}.mcfunction",
                          f"execute in {DIM} run place template {NS}:pozo {x + 75} 73 76\n"
                          f"execute in {DIM} if block {x + 97} 92 77 bedrock\n")
            pack.writestr(f"data/{NS}/function/descargar_{i}.mcfunction",
                          f"execute in {DIM} run forceload remove {area}\n")
    print(f"{len(changes)} bloques por mina, {len(MINES)} minas")


if __name__ == "__main__":
    generate()
