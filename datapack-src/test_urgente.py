"""Regresiones de mascotas, atlas FINAL, rutas y muerte BetterModel."""
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
import yaml
from mobs.mascotas import MASCOTAS,mob_yml,skill_yml
from mobs.tanda3b import WEIGHTS,definitions
from mobs.rutas_mazmorras import ROUTES
from mobs.mazmorra import MINA,skill_yml as dungeon_skills
from mobs.mazmorras_data import catalog
from mobs.tamanos import SPECIAL,scale,dimensions
from pack_audit import audit
from terceros import privado

ROOT=Path(__file__).resolve().parents[1]


class UrgenteTests(unittest.TestCase):
    def test_pet_invoker_is_player_without_shared_owner_name(self):
        mobs=yaml.safe_load(mob_yml());skills=yaml.safe_load(skill_yml())
        self.assertNotIn('global.pet_owner',mob_yml()+skill_yml())
        for pid,d in MASCOTAS.items():
            self.assertNotIn('setowner',str(mobs['astral_pet_'+pid]))
            self.assertIn(f'sudoskill{{s=MASC_CREAR_{pid}}}',skills['MASC_INVOCAR_'+pid]['Skills'])
            appear=skills['MASC_APARECER_'+pid]
            self.assertIn(f'score{{o=petsel;v={d["n"]}}} true',appear['Conditions'])
            self.assertIn('summonerIsOwner=true',appear['Skills'][0])
            self.assertIn('onSurface=false',appear['Skills'][0])
            self.assertTrue(appear['Skills'][0].endswith('@self'))

    def test_no_swordsman_spawns_and_probability_is_conserved(self):
        self.assertEqual(sum(WEIGHTS.values()),100)
        self.assertNotIn('espadachin',str(definitions()))
        self.assertTrue((ROOT/'build/models/astral_esq_espadachin.bbmodel').exists())

    def test_all_routes_match_generated_npc_and_room_teleports(self):
        from viajes_mazmorras import script
        skript=script()
        for d in [MINA]+catalog():
            text=dungeon_skills(d)
            for room,route in zip(d['rooms'],ROUTES[d['key']]):
                self.assertEqual((*room['llegada'],room.get('yaw',0)),route)
                xyz=' '.join(map(str,route[:3]))
                self.assertIn(xyz,text)
            xyz=' '.join(map(str,ROUTES[d['key']][0][:3]))
            self.assertIn(xyz,skript)
        cumbre=next(d for d in catalog() if d['key']=='cumbre')
        self.assertEqual(cumbre['rooms'][-1]['boss_spawn'],(-101.8,30,56.9))

    def test_yeti_twice_ancestral_with_matching_height(self):
        model,size=SPECIAL['astral_yeti_cumbre']
        self.assertEqual(size,4)
        self.assertAlmostEqual(dimensions(model,size)[1],2*dimensions(model,2)[1])
        self.assertAlmostEqual(2.2*scale(model,size,'RAVAGER'),dimensions(model,size)[1],places=5)
        from mobs.entrega_tanda2 import collision,movement
        sc=scale(model,size,'RAVAGER')
        for p in ((-101.8,30,56.9),(-54.9,30,6.5)):
            self.assertEqual(collision('cumbre_hielo',p,'RAVAGER',sc)['bloques_no_aire'],0)
        for samples in movement('cumbre_hielo',(-101.8,30,56.9),'RAVAGER',sc).values():
            self.assertTrue(all(p['bloques_no_aire']==0 for p in samples))

    def test_final_pack_and_equipment_are_complete(self):
        pack=privado()/'build/AstralRPG-Textures.zip'
        if not pack.exists():self.skipTest('Sin pack privado local')
        self.assertGreater(audit(pack),100)
        with zipfile.ZipFile(pack) as z:
            sword=json.loads(z.read('assets/privado/models/item/espada_heroe_errante.json'))
            faces=[f for e in sword['elements'] for f in e['faces'].values()]
            self.assertTrue(faces)
            self.assertTrue(all(0<=v<=16 for f in faces for v in f.get('uv',[])))

    def test_audit_rejects_old_atlas_paths_and_missing_equipment(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'bad.zip'
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('assets/test/models/item/a.json',json.dumps({'textures':{'layer0':'test:old/a'}}))
                z.writestr('assets/test/equipment/a.json',json.dumps({'layers':{'humanoid':[{'texture':'test:a'}]}}))
            with self.assertRaisesRegex(ValueError,'fuera del atlas'):audit(path)

    def test_death_once_for_all_creatures_and_not_pets(self):
        from mobs.muerte import MODELS
        for mid in MODELS:
            data=json.loads((ROOT/'build/models'/f'{mid}.bbmodel').read_text(encoding='utf8'))
            death=next(a for a in data['animations'] if a['name']=='death')
            self.assertEqual(death['loop'],'once');self.assertEqual(death['length'],.8)
        for p in (ROOT/'build/models').glob('astral_pet_*.bbmodel'):
            self.assertNotIn('death',[a['name'] for a in json.loads(p.read_text())['animations']])


if __name__=='__main__':unittest.main()
