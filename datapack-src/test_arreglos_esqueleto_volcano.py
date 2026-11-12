"""Regresiones de rig, publicidad, salas, cofres e interfaces completas."""
from pathlib import Path
import json
import math
import re
import subprocess
import unittest
import zipfile
import yaml
from minijuegos_datapack import Adapter, MAPS
from mobs.mazmorra import MINA, skill_yml, mob_yml
from mobs.mazmorras_data import catalog
from mobs.salas_seguras import safe, overlay, install_commands, FLOORS
from mobs.tanda2 import generate
from mobs.tamanos import rotate
from mobs.creatures_tanda3b import skeleton, VARIANTS
from mobs.preview_arreglos import posed
from mobs.mascotas import MASCOTAS
from menus import principal_menu, mascotas_extra_menu, mascota_detalle_menu

ROOT=Path(__file__).resolve().parents[1]


class ArreglosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds=[MINA]+[d for d in catalog() if d['key']!='santuario']
        cls.files={'data/astral/function/load.mcfunction':''};generate(cls.files)

    def test_advertising_has_no_entry_point_or_chat_in_either_map(self):
        for world in ('parkour_paradise3','parkour_spiral2'):
            a=Adapter(world,ROOT/'.local/mapas'/MAPS[world]['source'],MAPS[world]['prefix'])
            files=a.build(); prefix=MAPS[world]['prefix']+'_more_maps'
            funcs=[v for p,v in files.items() if p.startswith(f'data/{prefix}/function/')]
            self.assertTrue(funcs)
            for text in funcs:self.assertFalse([l for l in text.splitlines() if l and not l.startswith('#')])
            for p,text in files.items():
                if p.startswith(f'data/{prefix}/advancement/'):
                    data=json.loads(text)
                    self.assertNotIn('rewards',data)
                    self.assertEqual(data['criteria']['disabled']['trigger'],'minecraft:impossible')
            # Tick, load, premio, llamada directa y schedule quedan inertes:
            # ni fuera ni dentro del mapa pueden producir un LINK.
            self.assertNotIn('run tellraw', '\n'.join(funcs))

    def test_all_room_spawns_have_floor_air_and_minimum_arrival_height(self):
        for d in self.ds:
            for room in d['rooms']:
                points=list(room['spawn_points'])+list(room.get('golem_points',[]))
                if room.get('boss_room'):points.append(room['boss_spawn'])
                for point in points:
                    with self.subTest(d=d['key'],r=room['id'],point=point):
                        self.assertTrue(room['floor_range'][0]<=point[1]<=room['floor_range'][1])
                        self.assertTrue(safe(d['world'],point))
                prefix=f'data/astral/function/tanda2/{d["key"]}/{room["id"]}/'
                for p,text in self.files.items():
                    if not p.startswith(prefix):continue
                    for x,y,z in re.findall(r'summon minecraft:\w+ (-?[\d.]+) (-?[\d.]+) (-?[\d.]+)',text):
                        point=tuple(map(float,(x,y,z)))
                        self.assertTrue(room['floor_range'][0]<=point[1]<=room['floor_range'][1],p)
                        self.assertTrue(safe(d['world'],point),p)
        from mobs.tanda3a import PLANT_POINTS
        bosque=next(d for d in self.ds if d['key']=='bosque')
        for p in PLANT_POINTS:
            self.assertTrue(97<=p[1]<=102);self.assertTrue(safe('bosque',p))

    def test_supports_are_explicit_install_only_and_keep_existing_blocks(self):
        self.assertEqual(install_commands(),[])
        self.assertFalse(any(' run fill ' in text for text in self.files.values()))

    def test_every_chest_uses_platform_or_exact_boss_spawn(self):
        for d in self.ds:
            r=d['rooms'][-1];p=r['final_npcs']['cofre']
            self.assertTrue(safe(d['world'],p))
            self.assertTrue(all(overlay(d['world'],p[0],p[1]+dy,p[2]) not in ('minecraft:lava','minecraft:barrier') for dy in (0,1)))
            if not r['chest_platform']:self.assertEqual(p,r['boss_spawn'])
            text=skill_yml(d)
            self.assertIn('x=%s;y=%s;z=%s'%p,text)

    def test_model_glow_is_explicit_and_scoped_to_dungeon_copies(self):
        from mobs.tanda3b import definitions
        mobs,_=definitions()
        for d in self.ds:
            data=yaml.safe_load(mob_yml(d));boss=d['rooms'][-1]['oleadas'][0][0][0]
            self.assertIn('glowbone{g=true;c=FFFFFF} @self ~onTimer:20',data[boss]['Skills'])
        for mid,data in mobs.items():
            glowing=any(s.startswith('glowbone{') for s in data['Skills'])
            self.assertEqual(glowing, mid.startswith('astral_esq_') and mid.removeprefix('astral_esq_') not in VARIANTS)
        wild=yaml.safe_load((ROOT/'build/mythicmobs/mobs/tanda4b.yml').read_text(encoding='utf8'))
        self.assertFalse(any(s.startswith('glowbone{') for s in wild['astral_planta_salvaje']['Skills']))

    def test_bow_stays_in_hand_and_arrow_faces_forward_for_whole_cycle(self):
        def transform(m,b,p):
            while b:
                info=m.bones[b];p=rotate(p,info['origin'],info['rotation']);b=info['parent']
            return p
        model=skeleton('arquero')
        self.assertEqual(model.bones['bow']['parent'],'bow_grip')
        self.assertEqual(model.bones['bow_grip']['parent'],'arm_l')
        for animation in ('idle','walk','attack'):
            length=model.anims[animation][0]
            for i in range(25):
                m=posed(model,animation,length*i/24)
                origin=m.bones['bow_grip']['origin']
                hand=transform(m,'arm_l',origin);grip=transform(m,'bow',origin)
                self.assertLess(math.dist(hand,grip),1e-6)
                arrow=transform(m,'bow',(origin[0]-1,origin[1],origin[2]))
                self.assertLess(arrow[2]-grip[2],-.85)
                self.assertLess(hand[2],-10)

    def test_skeleton_art_is_preserved_for_every_variant(self):
        for kind in VARIANTS:
            data=json.loads(subprocess.check_output(['git','show',f'c3d4af8:build/models/astral_esq_{kind}.bbmodel'],cwd=ROOT))
            if kind!='arquero':self.assertEqual(skeleton(kind).export()[0]['textures'][0]['source'],data['textures'][0]['source'])
            if kind in ('guardian','espadachin'):self.assertEqual(skeleton(kind).bones['weapon']['parent'],'arm_r')

    def test_principal_keeps_old_buttons_and_adds_all_services(self):
        data=yaml.safe_load(principal_menu());items=data['items']
        expected={'bazar','minas','mazmorras','expediciones','portales','parkour','arenas','misiones',
                  'mascotas','cosmeticos','skills','guia','comandos','spawn','fragmentos','duelos'}
        self.assertEqual(set(items)-{'info','cerrar'},expected)
        self.assertEqual(len({v['slot'] for v in items.values()}),len(items))

    def test_pet_pages_details_crates_and_guide_cover_new_catalog(self):
        seen=set()
        for page in (2,3):
            menu=yaml.safe_load(mascotas_extra_menu(page))['items']
            for pid,d in MASCOTAS.items():
                if pid not in menu:continue
                seen.add(pid)
                self.assertEqual(menu[pid]['item_model'],f'astral:mascotas/catalogo_{pid}')
                self.assertIn('astral:companero/nivel_1_0',mascota_detalle_menu(pid))
        self.assertEqual(seen,{pid for pid,d in MASCOTAS.items() if d['n']>6})
        from lobby import mount_rewards, icon
        for rarity,weight,name,commands in mount_rewards():
            if commands[0].startswith('lp user %player% permission set astral.mascota.'):
                pid=commands[0].split('astral.mascota.')[1].split()[0]
                self.assertEqual(icon(commands)[1],f'mascotas/catalogo_{pid}')
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            guide=''.join(z.read(f'data/astral/dialog/guia/mascotas_{p}.json').decode() for p in (1,2,3))
            for d in MASCOTAS.values():self.assertIn(d['nombre'],guide)


if __name__=='__main__':unittest.main()
