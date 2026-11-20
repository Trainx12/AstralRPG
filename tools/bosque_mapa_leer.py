"""Lector minimo de mundos de Minecraft (Anvil 1.18+) para el Bosque Astral.

Carga una caja de bloques a un arreglo numpy de indices + paleta global. Sin dependencias raras
(solo numpy). Lo usan tools/bosque_mapa.py y las pruebas del bosque.
"""
import gzip
import io
import struct
import zlib
from pathlib import Path

import numpy as np


def _rd(f, n):
    b = f.read(n)
    if len(b) != n:
        raise EOFError
    return b


def _tag(f, t):
    if t == 1: return struct.unpack('>b', _rd(f, 1))[0]
    if t == 2: return struct.unpack('>h', _rd(f, 2))[0]
    if t == 3: return struct.unpack('>i', _rd(f, 4))[0]
    if t == 4: return struct.unpack('>q', _rd(f, 8))[0]
    if t == 5: return struct.unpack('>f', _rd(f, 4))[0]
    if t == 6: return struct.unpack('>d', _rd(f, 8))[0]
    if t == 7:
        n = struct.unpack('>i', _rd(f, 4))[0]; return _rd(f, n)
    if t == 8:
        n = struct.unpack('>H', _rd(f, 2))[0]; return _rd(f, n).decode('utf-8', 'replace')
    if t == 9:
        et = _rd(f, 1)[0]; n = struct.unpack('>i', _rd(f, 4))[0]
        return [_tag(f, et) for _ in range(n)]
    if t == 10:
        d = {}
        while True:
            tt = _rd(f, 1)[0]
            if tt == 0: return d
            k = _tag(f, 8); d[k] = _tag(f, tt)
    if t == 11:
        n = struct.unpack('>i', _rd(f, 4))[0]; return np.frombuffer(_rd(f, 4 * n), '>i4')
    if t == 12:
        n = struct.unpack('>i', _rd(f, 4))[0]; return np.frombuffer(_rd(f, 8 * n), '>i8')
    raise ValueError(t)


def nbt(data):
    f = io.BytesIO(data); t = _rd(f, 1)[0]; _tag(f, 8); return _tag(f, t)


def read_chunk(region_dir, cx, cz):
    path = Path(region_dir) / f'r.{cx >> 5}.{cz >> 5}.mca'
    if not path.exists():
        return None
    with open(path, 'rb') as fh:
        i = (cx & 31) + (cz & 31) * 32
        fh.seek(i * 4); head = fh.read(4)
        off = int.from_bytes(head[:3], 'big')
        if off == 0:
            return None
        fh.seek(off * 4096); ln, comp = struct.unpack('>iB', fh.read(5)); raw = fh.read(ln - 1)
    raw = zlib.decompress(raw) if comp == 2 else gzip.decompress(raw) if comp == 1 else raw
    return nbt(raw)


def _states(longs, bits):
    longs = np.asarray(longs).astype(np.uint64)
    per = 64 // bits
    shifts = (np.arange(per, dtype=np.uint64) * np.uint64(bits))
    vals = (longs[:, None] >> shifts[None, :]) & np.uint64((1 << bits) - 1)
    return vals.reshape(-1)[:4096].astype(np.int32)


def state_key(entry):
    """'minecraft:name[prop=v,...]' ordenado, como lo escribe WorldEdit."""
    name = entry['Name']
    props = entry.get('Properties')
    if props:
        name += '[' + ','.join(f'{k}={v}' for k, v in sorted(props.items())) + ']'
    return name


def load_box(region_dir, x0, x1, z0, z1, y0, y1):
    """Bloques en x0..x1, z0..z1, y0..y1 (inclusive). Devuelve (arr[y,z,x] int32, paleta list)."""
    W, L, H = x1 - x0 + 1, z1 - z0 + 1, y1 - y0 + 1
    arr = np.zeros((H, L, W), np.int32)
    palette = ['minecraft:air']; index = {'minecraft:air': 0}
    for cx in range(x0 >> 4, (x1 >> 4) + 1):
        for cz in range(z0 >> 4, (z1 >> 4) + 1):
            c = read_chunk(region_dir, cx, cz)
            if c is None:
                continue
            for s in c.get('sections', []):
                sy = s['Y'] * 16
                if sy + 15 < y0 or sy > y1 or 'block_states' not in s:
                    continue
                bs = s['block_states']
                gl = []
                for e in bs['palette']:
                    k = state_key(e)
                    if k not in index:
                        index[k] = len(palette); palette.append(k)
                    gl.append(index[k])
                gl = np.array(gl, np.int32)
                if 'data' in bs:
                    idx = _states(bs['data'], max(4, (len(bs['palette']) - 1).bit_length()))
                else:
                    idx = np.zeros(4096, np.int32)
                blk = gl[idx].reshape(16, 16, 16)  # y, z, x
                bx, bz = cx * 16, cz * 16
                xa, xb = max(x0, bx), min(x1, bx + 15)
                za, zb = max(z0, bz), min(z1, bz + 15)
                ya, yb = max(y0, sy), min(y1, sy + 15)
                if xa > xb or za > zb or ya > yb:
                    continue
                arr[ya - y0:yb - y0 + 1, za - z0:zb - z0 + 1, xa - x0:xb - x0 + 1] = \
                    blk[ya - sy:yb - sy + 1, za - bz:zb - bz + 1, xa - bx:xb - bx + 1]
    return arr, palette
