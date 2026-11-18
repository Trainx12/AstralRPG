"""Pruebas de preservacion y reversion; sin mapas privados ni conexiones."""
import gzip
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
from mapas import NBT, nbt_payload, nbt_string
import lobby_terreno as terrain


def read_schem(path):
    # Decodificador distinto del escritor: verifica orden x/z/y y varints.
    tree=NBT(gzip.decompress(path.read_bytes())).root()
    s=tree['Schematic']; palette={i:n for n,i in s['Blocks']['Palette'].items()}
    values=[];value=shift=0
    for b in s['Blocks']['Data']:
        value |= (b & 127) << shift
        if b & 128:shift+=7
        else:values.append(palette[value]);value=shift=0
    if shift:raise ValueError('Varint incompleto')
    if len(values)!=s['Width']*s['Length']*s['Height']:raise ValueError('Volumen incorrecto')
    return s,values


def put(world,x,y,z,state):
    world.chunks.add((x//16,z//16))
    a=world.sections.setdefault((x//16,y//16,z//16),np.zeros((16,16,16),dtype=np.uint16))
    a[y%16,z%16,x%16]=world.ident(state)


class TerrainTest(unittest.TestCase):
    def test_sponge_v3_full_backup_keeps_air_and_states(self):
        w=terrain.World();w.chunks.add((0,0));w.version=4790
        put(w,1,98,1,'minecraft:grass_block[snowy=false]')
        changes={(1,98,1):'minecraft:coarse_dirt',(2,99,2):'minecraft:stone'}
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);sectors=terrain.export(w,changes,out)
            self.assertEqual(len(sectors),1)
            s,before=read_schem(out/sectors[0]['local_before'])
            _,after=read_schem(out/sectors[0]['local_after'])
            self.assertEqual(s['Version'],3)
            self.assertEqual(s['DataVersion'],4790)
            self.assertEqual(s['Offset'],[0,0,0])
            self.assertNotIn('Entities',s)
            self.assertNotIn('Biomes',s)
            self.assertIn('minecraft:grass_block[snowy=false]',before)
            self.assertEqual(before.count(terrain.AIR),7)
            self.assertEqual(after.count(terrain.AIR),6)
            self.assertNotIn('-a',(out/'restaurar.txt').read_text())
            self.assertIn('//paste -a',(out/'pegar.txt').read_text())
            report=terrain.verify_export(w,out,sectors,len(changes))
            self.assertEqual(report['air_blocks_in_rollback'],1)
            self.assertEqual(report['changed_blocks'],2)

    def test_corrupted_schematic_is_rejected(self):
        w=terrain.World();w.chunks.add((0,0));w.version=4790
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);delta={(1,98,1):'minecraft:stone'}
            sectors=terrain.export(w,delta,out)
            (out/sectors[0]['local_after']).write_bytes(b'incomplete')
            with self.assertRaisesRegex(ValueError,'Hash distinto'):
                terrain.verify_export(w,out,sectors,1)

    def test_sector_split_does_not_copy_chest_between_changes(self):
        w=terrain.World();w.chunks.add((0,0));w.version=4790
        w.tiles.add((2,100,2));put(w,2,100,2,'minecraft:chest[facing=north,type=single,waterlogged=false]')
        delta={(0,100,0):'minecraft:stone',(4,100,4):'minecraft:stone'}
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);sectors=terrain.export(w,delta,out)
            self.assertEqual(len(sectors),2)
            for s in sectors:
                _,before=read_schem(out/s['local_before'])
                self.assertFalse(any('chest' in n for n in before))

    def test_unknown_chunk_is_not_air(self):
        with self.assertRaisesRegex(ValueError,'Chunk sin descargar'):
            terrain.World().get(0,80,0)

    def test_private_output_rejects_public_preview_directory(self):
        with self.assertRaisesRegex(ValueError,'exclusivamente'):
            terrain.private(terrain.ROOT/'build/previews/lobby')

    def test_noise_is_continuous_and_deterministic(self):
        a=terrain.noise(5.,7.,4.,17)
        self.assertEqual(a,terrain.noise(5.,7.,4.,17))
        self.assertLess(abs(a-terrain.noise(5.001,7.,4.,17)),.01)
        self.assertGreaterEqual(a,0);self.assertLess(a,1)

    def test_decode_modern_region_negative_coordinates_and_properties(self):
        import zlib
        state=(10,{'palette':(9,[(10,{'Name':(8,'minecraft:air')}),
                                        (10,{'Name':(8,'minecraft:grass_block'),'Properties':(10,{'snowy':(8,'false')})})]),
                   'data':(12,[1]*256)})
        root=(10,{'DataVersion':(3,4790),'xPos':(3,-1),'zPos':(3,-1),
                  'sections':(9,[(10,{'Y':(1,6),'block_states':state})])})
        raw=zlib.compress(b'\x0a'+nbt_string('')+nbt_payload(root))
        record=(len(raw)+1).to_bytes(4,'big')+b'\x02'+raw
        header=bytearray(8192);header[:4]=b'\x00\x00\x02\x01'
        w=terrain.World();w.add_region('fixture',bytes(header)+record,(-16,-16,-1,-1))
        self.assertEqual(w.get(-16,96,-16),'minecraft:grass_block[snowy=false]')
        self.assertEqual(w.get(-15,96,-16),terrain.AIR)

    def scene(self):
        w=terrain.World();o=terrain.World()
        for world in (w,o):
            world.version=4790
            world.chunks={(x,z) for x in range(4) for z in range(4)}
            for x in range(20,35):
                for z in range(20,35):put(world,x,97,z,'minecraft:grass_block[snowy=false]')
            for x in range(40,45):
                for z in range(20,25):put(world,x,124,z,'minecraft:cobbled_deepslate')
        # Extension ausente del original y una construccion con cartel protegido.
        for x in range(20,35):
            for z in range(35,42):put(w,x,97,z,'minecraft:grass_block[snowy=false]')
        put(w,30,98,30,'minecraft:stone_bricks')
        w.tiles.add((30,99,30))
        config={'seed':17,'soil_scale':None,'ring':[[10,10],[53,10],[53,53],[10,53]],
                'width':3,'floor_y':97,'foundation_depth':2,'exclude':[[20,36,24,41]]}
        return w,o,config

    def test_proposal_preserves_building_and_explicit_exclusion(self):
        w,o,c=self.scene();changes,report=terrain.propose(w,o,(0,0,63,63),c)
        self.assertTrue(changes)
        self.assertFalse(any(20<=x<=24 and 36<=z<=41 for x,y,z in changes))
        self.assertFalse(any(abs(x-30)+abs(z-30)<=5 for x,y,z in changes if y>97))
        for (x,y,z),state in changes.items():
            self.assertNotIn((x,y,z),w.tiles)
            if w.get(x,y,z)!=terrain.AIR:self.assertEqual(terrain.base(w.get(x,y,z)),'grass_block')
        self.assertEqual(report['peak_reference_y'],124)

    def test_clipped_ring_is_rejected(self):
        w,o,c=self.scene();c['ring']=[[0,0],[53,10],[53,53],[10,53]]
        with self.assertRaisesRegex(ValueError,'Anillo cortado'):
            terrain.propose(w,o,(0,0,63,63),c)

    def test_varints_more_than_128_palette_entries(self):
        w=terrain.World();w.version=4790;w.chunks={(0,0)}
        delta={(x,80+y,z):f'minecraft:stone[fixture={y*64+z*8+x}]'
               for y in range(3) for z in range(8) for x in range(8)}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'fixture.schem'
            terrain.schematic(path,w,(0,80,0,7,82,7),delta,True)
            _,values=read_schem(path)
            self.assertEqual(len(set(values)),192)
            self.assertEqual(values[-1],'minecraft:stone[fixture=191]')


if __name__=='__main__':unittest.main()
