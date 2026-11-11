"""Regresiones de aislamiento de salas, cola pendiente y visibilidad del progreso."""
import unittest
import yaml
from mobs.mazmorra import MINA
from mobs.mazmorras_data import catalog
from mobs.tanda2 import generate, path
from mobs.salas_seguras import FLOORS, safe, install_commands
from menus import principal_menu, comandos_menu
from lobby import TAB_SECTIONS


class AjustesTests(unittest.TestCase):
    def test_menu_only_adds_two_entries_and_trade_is_documented(self):
        items=yaml.safe_load(principal_menu())['items']
        self.assertEqual(set(items)-{'info','cerrar'},set(('bazar minas mazmorras expediciones portales parkour arenas misiones mascotas cosmeticos skills guia comandos spawn fragmentos duelos').split()))
        self.assertIn('/trade <jugador>',comandos_menu())

    def test_bow_limbs_are_joined_and_plush_section_is_enabled(self):
        from mobs.creatures_tanda3b import skeleton
        from mobs.tamanos import rotate
        from pathlib import Path
        import math
        m=skeleton('arquero')
        self.assertEqual(m.bones['bow_grip']['parent'],'arm_l')
        segments=[]
        for c in m.cubes:
            if c['bone']!='bow' or not c.get('rotation'):continue
            x=(c['from'][0]+c['to'][0])/2; z=(c['from'][2]+c['to'][2])/2
            ends=[rotate((x,y,z),c['origin'],c['rotation']) for y in (c['from'][1],c['to'][1])]
            segments.append(ends)
        self.assertEqual(len(segments),5)
        for left,right in zip(segments,segments[1:]):
            self.assertLess(math.dist(left[1],right[0]),1e-6)
        section=yaml.safe_load((Path(__file__).resolve().parents[1]/'build/shop/EconomyShopGUI/sections/Peluches.yml').read_text())
        self.assertTrue(section['enable']);self.assertEqual(section['slot'],39)

    def test_every_room_counts_queue_and_alive_entities_and_has_its_own_bar(self):
        ds=[MINA]+[d for d in catalog() if d['key']!='santuario']
        files={'data/astral/function/load.mcfunction':''};generate(files)
        prefix='data/astral/function/'
        load=files[prefix+'load.mcfunction']; tick=files[prefix+'tanda2/ui_tick.mcfunction']
        bars=[]
        for d in ds:
            for r in d['rooms']:
                p=path(d,r); bar='astral:'+p; bars.append(bar)
                self.assertIn('bossbar add '+bar,load)
                self.assertIn('bossbar set '+bar+' players\n',tick)
                ui=files[prefix+p+'/ui.mcfunction']
                self.assertIn('queue',ui)
                self.assertIn('ad.left += @s ad.pending',ui)
                self.assertIn('tag='+f'ad.{d["key"]}.{r["id"]}',ui)
                self.assertIn(f'tag={d["key"]}.fin',ui)
                self.assertIn('ad.room',ui)
                if r.get('boss_room'):
                    self.assertNotIn('bossbar set',ui)
                else:
                    for n in range(1,len(r['oleadas'])+1):
                        wave=files[prefix+p+f'/wave{n}.mcfunction']
                        self.assertIn(f'ad.wave {n}',wave)
                        self.assertIn('/ui_start',wave)
                    self.assertIn('ad.max',ui)
        self.assertEqual(len(bars),len(set(bars)))
        self.assertIn('sort=nearest,limit=1',files[prefix+'tanda2/cumbre/sala1/ui_join.mcfunction'])

    def test_sidebar_dungeon_priority_and_natural_floors(self):
        tab=yaml.safe_load(TAB_SECTIONS)
        boards=tab['scoreboard']['scoreboards']
        self.assertLess(list(boards).index('mazmorra'),list(boards).index('astral'))
        self.assertNotIn('Diarias',' '.join(boards['mazmorra']['lines']))
        self.assertFalse(any('Rango' in line for line in boards['astral']['lines']))
        self.assertEqual(tab['conditions']['ad_dungeon']['type'],'OR')
        self.assertEqual(install_commands(),[])
        for d in [MINA]+[d for d in catalog() if d['key']!='santuario']:
            for r,limits in zip(d['rooms'],FLOORS[d['key']],strict=True):
                for p in r['spawn_points']+r.get('golem_points',[])+([r['boss_spawn']] if r.get('boss_room') else []):
                    self.assertTrue(limits[0]<=p[1]<=limits[1])
                    self.assertTrue(safe(d['world'],p))


if __name__=='__main__':unittest.main()
