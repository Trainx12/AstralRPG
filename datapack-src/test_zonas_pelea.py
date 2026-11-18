"""Deteccion sin mapas externos y contratos de medidas versionadas."""
import math
import unittest
from zonas_pelea import catalog, load, detect, boxes


class Zonas(unittest.TestCase):
    def test_bosque_measured(self):
        zones=load()
        self.assertEqual(zones['bosque/1'][:5],[1411,1512,1495,1603,1])
        self.assertEqual(zones['bosque/2'][:5],[1543,1356,1649,1425,1])
        for r in catalog():
            if r['key']!='bosque':continue
            x1,z1,x2,z2,detected,radius=zones[r['id']]
            self.assertEqual(r['radius'],radius)
            self.assertGreater(x2,x1);self.assertGreater(z2,z1)
            for x in (x1,x2):
                for z in (z1,z2):
                    self.assertLessEqual(math.dist(r['center'],[x,r['center'][1]+70,z]),radius)

    def fixture(self):
        room=dict(center=[10,20,10],arrival=[12,20,12],radius=15)
        wall={(x,y,z) for x in range(0,31) for z in range(0,21)
              if x in (0,30) or z in (0,20) for y in range(15,36)}
        return room,wall

    def test_closed_fence_ignores_paths_and_other_room(self):
        r,p=self.fixture()
        p|={(x,y,0) for x in range(-30,0) for y in range(15,36)}
        p|={(x,y,z) for x in range(50,71) for z in range(0,21)
            if x in (50,70) or z in (0,20) for y in range(15,36)}
        rect,selected,_=detect(r,p)
        self.assertEqual(rect,[1,1,30,20])
        self.assertTrue(selected)
        self.assertTrue(all(-3<=x<=33 and -3<=z<=23 for x,z in selected))

    def test_open_side_and_roof_fallback(self):
        r,p=self.fixture()
        p={v for v in p if v[0]!=30}
        p|={(x,40,z) for x in range(-30,50) for z in range(-30,50)}
        rect,selected,_=detect(r,p)
        self.assertEqual(rect,[-5,-5,25,25]);self.assertFalse(selected)

    def test_arrival_in_different_room_fallback(self):
        r,p=self.fixture();r['arrival']=[60,20,10]
        self.assertFalse(detect(r,p)[1])

    def test_boxes_reconstruct_exact_blocks_without_air(self):
        p={(x,y,z) for x in range(4) for y in range(2,9) for z in range(3)}
        p.remove((2,5,1))
        output=boxes(p);allpoints=[]
        for lo,hi in output:
            allpoints.extend((x,y,z) for x in range(lo[0],hi[0]+1)
                             for y in range(lo[1],hi[1]+1) for z in range(lo[2],hi[2]+1))
        self.assertEqual(set(allpoints),p);self.assertEqual(len(allpoints),len(p))

    def test_bosque_source_when_available(self):
        from zonas_pelea import ROOT,read_barriers
        folder=ROOT/'.local/mapas/server-18-11'
        if not (folder/'bosque/region').is_dir():self.skipTest('Mapas privados no disponibles')
        rooms=[r for r in catalog() if r['key']=='bosque']
        points=read_barriers(folder,'bosque',rooms)
        for r,expected in zip(rooms,([1415,1516,1491,1599],[1547,1360,1645,1421])):
            rect,selected,_=detect(r,points)
            self.assertEqual(rect,expected)
            self.assertTrue(selected)
            # Las ramas que continuan hacia caminos no se incluyen.
            self.assertTrue(all(expected[0]-3<=x<=expected[2]+3 and expected[1]-3<=z<=expected[3]
                                for x,z in selected))


if __name__=='__main__':unittest.main()
