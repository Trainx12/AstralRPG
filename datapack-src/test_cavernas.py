"""Cavernas de Cristal (7e, 19/11/2026): vetas, tabla de botin, taladro, economia, mobs, menus y pack."""
import json
import unittest
import zipfile
from pathlib import Path

import yaml

import cavernas as C
import economia as E
import gemas as G

ROOT = Path(__file__).resolve().parents[1]


class Vetas(unittest.TestCase):
    def test_notas_unicas(self):
        self.assertEqual(len(C.NOTAS), len(set(C.NOTAS)))
        self.assertEqual(len(C.NOTAS), 16)
        self.assertTrue(all(0 <= n <= 24 for n in C.NOTAS))
        self.assertEqual(C.INSTRUMENTO, 'bell')   # el banjo (22-24) es del Oceano y de Asura

    def test_cada_zona_tiene_gemas(self):
        todas = [g for _, _, gs in C.ZONAS.values() for g in gs]
        self.assertEqual(sorted(todas), sorted(G.TIPOS))

    def test_java_coincide(self):
        java = (Path(C.__file__).parent / 'runtime/AstralCavernas.java').read_text(encoding='utf-8')
        self.assertIn('TIPOS = {"rubi", "zafiro", "jade", "topacio", "amatista", "opalo", "onix"}', java)
        self.assertEqual(list(G.TIPOS), ["rubi", "zafiro", "jade", "topacio", "amatista", "opalo", "onix"])
        self.assertIn('ZONAS = {"amatista", "jade", "rubi", "zafiro", "corazon"}', java)
        self.assertEqual(list(C.ZONAS), ["amatista", "jade", "rubi", "zafiro", "corazon"])
        for iid, n in C.MENAS.items():
            self.assertIn(f', {n}, false', java)

    def test_calidad(self):
        for k, pesos in C.CALIDAD.items():
            self.assertEqual(len(pesos), 3, k)          # solo Cruda, Pulida, Impecable
        self.assertGreater(C.CALIDAD['honda'][2], C.CALIDAD['normal'][2])
        self.assertGreater(C.CALIDAD['normal_polvo'][2], C.CALIDAD['normal'][2])


class Datapack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.z = zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip')

    def read(self, n):
        return self.z.read(n).decode('utf-8')

    def test_tabla_note_block(self):
        t = json.loads(self.read('data/minecraft/loot_table/blocks/note_block.json'))
        bell = [p for p in t['pools'] if any(c.get('properties', {}).get('instrument') == 'bell' for c in p.get('conditions', []))]
        self.assertEqual(len(bell), len(G.TIPOS) * 2 * 2 + len(C.MENAS))
        for p in bell:   # todas piden taladro tier 4+
            self.assertTrue(any(c.get('condition') == 'minecraft:any_of' and 'drill' in json.dumps(c) for c in p['conditions']))
        comun = [p for p in t['pools'] if any(e.get('name') == 'minecraft:note_block' for e in p['entries'])]
        self.assertEqual(len(comun), 1)
        excl = {c['term']['properties'].get('note') for c in comun[0]['conditions'] if c.get('condition') == 'minecraft:inverted'
                and c['term'].get('properties', {}).get('instrument') == 'bell'}
        self.assertEqual(excl, {str(n) for n in C.NOTAS})

    def test_taladro_y_conteo(self):
        f = self.read('data/astral/function/tool/mine.mcfunction')
        for n in C.NOTAS:
            self.assertIn(f'note_block[instrument=bell,note={n}] run scoreboard players add @s cav.n{n} 1', f)
        self.assertIn('execute unless dimension minecraft:cavernas_cristal', f)
        self.assertIn('cav.n0 dummy', self.read('data/astral/function/cavernas/load.mcfunction'))
        self.assertIn('function astral:cavernas/load', self.read('data/astral/function/load.mcfunction'))

    def test_tier(self):
        roll = self.read('data/astral/function/mob/roll.mcfunction')
        self.assertIn('if dimension minecraft:cavernas_cristal run scoreboard players set #mt astral.tmp 4', roll)
        self.assertIn(C.mob_roll_corazon(), roll)
        self.assertLess(roll.index('#mt astral.tmp 4'), roll.index(C.mob_roll_corazon()))
        from escala import VIDA_REF
        self.assertIn(f'base set {25 * VIDA_REF[5]}', self.read('data/astral/function/cavernas/jefe/5.mcfunction'))

    def test_items(self):
        for iid in C.ITEMS:
            self.assertIn(f'astral:cavernas/{iid}', self.read(f'data/astral/loot_table/item/{iid}.json'))
        icons = json.loads(self.read('data/astral/atlas/iconos.json'))
        self.assertFalse(set(C.ITEMS) & set(icons))     # el Atlas no se corre


class Economia(unittest.TestCase):
    def test_plata_hora(self):
        sel = C.plata_hora()
        self.assertTrue(20_000_000 <= sel <= 60_000_000, sel)
        import minas
        ii_diamante = next(minas.mine_value(m[1], m[2], m[3]) for m in minas.MINES if m[0].startswith('II') and 'Diamante' in m[0])
        self.assertGreater(C.plata_hora('ciegas'), 0)
        self.assertLess(C.plata_hora('ciegas'), ii_diamante * C.BLOQUES_HORA)

    def test_perdida_al_morir(self):
        self.assertIn(C.WORLD, E.mundos_con_perdida())

    def test_comisiones(self):
        cfg = C.config()
        self.assertGreaterEqual(len(cfg['comisiones']), 3)
        objetivos = set(cfg['notas']) | {k.replace('gema_', '') for k in cfg['notas']}
        for c in cfg['comisiones']:
            if c['tipo'] == 'veta':
                self.assertTrue(c['objetivo'] in G.TIPOS or c['objetivo'] in C.MENAS, c)
            self.assertIn(c['plata'], E.CAVERNAS_COMISION.values())
        del objetivos


class Mobs(unittest.TestCase):
    def test_yaml(self):
        y = yaml.safe_load(C.mythic_yaml())
        self.assertEqual(set(y), set(C.MOBS) | set(C.JEFES))
        for mid in C.JEFES:
            self.assertTrue(y[mid]['BossBar']['Enabled'])   # AstralGemas (Opalo) reconoce la barra de jefe
            self.assertNotEqual(y[mid]['BossBar']['Color'], 'YELLOW')   # BetterHud la vuelve invisible
        for mid in C.MOBS:
            self.assertTrue(any('mob/roll' in s for s in y[mid]['Skills']))
        cfg = C.config()
        for z in C.ZONAS:
            self.assertTrue(any(z in v['zonas'] for v in cfg['mobs'].values() if v['clase'] == 'golem'), z)
            self.assertIn(z, [v['zona'] for v in cfg['jefes'].values()])


class Menus(unittest.TestCase):
    def test_portales(self):
        import portales
        items = portales.menu_data()['items']
        # Tarjeta de Cavernas (columnas 5-6, filas 0-3) que abre su aviso; mini juegos, Oceano y arenas en 48-50.
        self.assertIn('[openguimenu] cavernas_aviso', items['cavernas']['click_commands'])
        self.assertEqual([items[k]['slot'] for k in ('parkour', 'oceano', 'arenas')], [48, 49, 50])
        lista = (ROOT / 'build/menus/DeluxeMenus/config-gui_menus.yml').read_text(encoding='utf-8')
        self.assertIn('cavernas_aviso:', lista)


class Pack(unittest.TestCase):
    def test_note_block(self):
        z = zipfile.ZipFile(ROOT / 'build/AstralRPG-Textures.zip')
        bs = json.loads(z.read('assets/minecraft/blockstates/note_block.json'))
        comun = next(p for p in bs['multipart'] if p['apply']['model'] == 'minecraft:block/note_block')
        ors = comun['when']['OR']
        self.assertNotIn('bell', next(o for o in ors if set(o) == {'instrument'})['instrument'].split('|'))
        self.assertIn({'instrument': 'bell', 'note': '|'.join(str(n) for n in range(25) if n not in C.NOTAS)}, ors)
        vetas = [p for p in bs['multipart'] if '/cavernas/' in p['apply']['model']]
        self.assertEqual(len(vetas), len(C.NOTAS))
        for p in vetas:
            self.assertIn('assets/astral/models/block/cavernas/' + p['apply']['model'].split('/')[-1] + '.json', z.namelist())


if __name__ == '__main__':
    unittest.main()
