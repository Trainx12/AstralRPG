"""Compatibilidad del arsenal con el formato vanilla y las animaciones."""
import io
import json
import unittest
from PIL import Image
import varitas3d as v
from armas3d import SWORDS,AXES,BOWS,GAUNTLET,assets as weapon_assets
from guadanas3d import SCYTHES
from lanzas3d import SPEARS
from weapon_details import refine_axe,refine_bow,refine_scythe,refine_wand

ALL=v.WANDS+SWORDS+AXES+SCYTHES+SPEARS+GAUNTLET+[w for group in BOWS for w in group]


class Weapons3DTests(unittest.TestCase):
    def test_geometry_and_inventory_fit_client_limits(self):
        self.assertEqual(v.check(ALL),[])
        for w in ALL:
            self.assertLessEqual(len(w.palette),16,w.iid)
            for e in w.els:
                self.assertIn(e['sw'],w.palette,w.iid)
                self.assertTrue(all(b>a for a,b in zip(e['from'],e['to'])),w.iid)
                self.assertIn(e['glow'],range(16),w.iid)

    def test_models_resolve_atlases_and_valid_uvs(self):
        files=v.assets(v.WANDS+SWORDS+AXES+SCYTHES+SPEARS+GAUNTLET)
        files.update(weapon_assets())
        for w in ALL:
            model=json.loads(files[f'assets/astral/models/item/{w.iid}.json'])
            texpath='assets/astral/textures/'+model['textures']['t'].split(':')[1]+'.png'
            tex=Image.open(io.BytesIO(files[texpath]))
            self.assertEqual(tex.size[0],32)
            self.assertIn(tex.size[1],(32,256))
            for e in model['elements']:
                for face in e['faces'].values():
                    self.assertTrue(all(0<=c<=16 for c in face['uv']))
            self.assertEqual(len(model['elements']),len(w.els))

    def test_animation_has_consistent_frames_and_static_materials(self):
        for w in ALL:
            image,n=v.texture(w)
            for name,(color,kind) in w.palette.items():
                slot=w.slots[name];x,y=slot%4*8,slot//4*8
                frames=[image.crop((x,y+32*f,x+8,y+32*f+8)).tobytes() for f in range(n)]
                if kind=='s':self.assertEqual(len(set(frames)),1,(w.iid,name))
                else:self.assertGreater(len(set(frames)),1,(w.iid,name))

    def test_bow_states_keep_same_body_and_shared_texture(self):
        for group in BOWS:
            self.assertEqual(len(group),4)
            base=group[0]
            def body(w):
                return [e for e in w.els if e['sw'] not in {'string','ashaft','ahead','afletch'}]
            for pulled in group[1:]:
                self.assertEqual(pulled.tex_name,base.iid)
                self.assertEqual(pulled.palette,base.palette)
                self.assertEqual(body(pulled),body(base))
                self.assertTrue(any(e['sw']=='ahead' for e in pulled.els))
            self.assertFalse(any(e['sw']=='ahead' for e in base.els))

    def test_detail_pass_does_not_duplicate_when_called_again(self):
        for items,refine in ((v.WANDS,refine_wand),(AXES,refine_axe),
                             (SCYTHES,refine_scythe),([g[0] for g in BOWS],refine_bow)):
            for w in items:
                before=len(w.els);refine(w)
                self.assertEqual(len(w.els),before,w.iid)


if __name__=='__main__':unittest.main()
