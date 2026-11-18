"""Economia E1 (18/11/2026): x100, topes de Netherita, anti-arbitraje, Banco y perdida al morir."""
import json
import re
import unittest
from pathlib import Path

import economia as E

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'


def _textos():
    for p in BUILD.rglob('*'):
        if p.suffix in ('.yml', '.sk', '.txt') and p.is_file() and 'deploy' not in p.parts:
            yield p, p.read_text(encoding='utf-8', errors='ignore')


class Cobertura(unittest.TestCase):
    def test_mobs_pagan_por_categoria(self):
        for p, t in _textos():
            for m in re.findall(r'astralplatamob <(?:trigger|target)\.name> (\S+?)["\s]', t):
                self.assertIn(m, ('hostil', 'elite', 'jefe', 'ancestral'), f'{p}: astralplatamob {m}')

    def test_sin_cifras_viejas(self):
        """eco give / takemoney / has money: nunca cifras de la escala vieja (menos de 1.000)."""
        pat = re.compile(r'eco give \S+ (\d+)|\[takemoney\] (\d+)|type: has money\s+amount: (\d+)')
        for p, t in _textos():
            if 'economia_tienda' in p.parts:
                continue
            for g in pat.findall(t):
                n = int(next(x for x in g if x))
                self.assertGreaterEqual(n, 1000, f'{p}: {n}')

    def test_tablas_del_plan(self):
        from items import MEJORAS
        import lobby, minas, renacimiento
        self.assertEqual([m for m, _, _ in MEJORAS.values()], E.MEJORAS_PLATA)
        self.assertEqual({k: g['cost'] for k, g in lobby.GACHAS.items()}, E.GACHA_TIRADA)
        self.assertEqual(minas.MINES[-1][-1], 2_500_000_000)
        self.assertEqual(minas.PRICES['netherite_block'], 15_000)
        self.assertEqual(minas.PRICES['diamond_block'], 7_200)
        self.assertEqual(renacimiento.tope(), 2_500_000_000)
        self.assertEqual(renacimiento.tope_lite(), 625_000_000)
        self.assertEqual(E.PLATA_MOB_TIER[10], 800_000)


class Tienda(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shops = E.tienda()
        buy, sell = {}, {}
        for data in cls.shops.values():
            for _, it in E._items_tienda(data):
                n = it.get('stack-size') or 1
                if it.get('buy') not in (None, -1) and it.get('sell') not in (None, -1):
                    assert it['sell'] <= it['buy'], (it['material'], it)
                if set(it) & {'enchantments', 'potiontypes', 'spawnertype', 'ominous-strength', 'instrument', 'colors'}:
                    continue  # mismo material, objeto distinto (libros, pociones, spawners, cohetes)
                m = str(it['material']).lower()
                if it.get('buy') not in (None, -1):
                    buy[m] = min(buy.get(m, 1e30), it['buy'] / n)
                if it.get('sell') not in (None, -1):
                    sell[m] = max(sell.get(m, 0), it['sell'] / n)
        cls.buy, cls.sell = buy, sell

    def test_x100(self):
        self.assertAlmostEqual(self.buy['copper_block'], 386)
        self.assertEqual(len(self.shops), 28)

    def test_venta_menor_que_compra(self):
        for m, s in self.sell.items():
            if m in self.buy:
                self.assertLessEqual(s, self.buy[m], m)

    def test_anti_arbitraje_cadenas(self):
        for bloque, unidad, n in E.CADENAS:
            if bloque in self.sell and unidad in self.buy:
                self.assertLessEqual(self.sell[bloque], n * self.buy[unidad] + 1e-6, bloque)
            if unidad in self.sell and bloque in self.buy:
                self.assertLessEqual(n * self.sell[unidad], self.buy[bloque] + 1e-6, unidad)

    def test_topes_netherita(self):
        self.assertLessEqual(self.sell['netherite_block'], E.NETHERITA_BLOQUE)
        self.assertLessEqual(self.sell['netherite_ingot'] * 9, E.NETHERITA_BLOQUE + 0.1)
        tpl = self.sell['netherite_upgrade_smithing_template']
        for neth, dia in E.NETHERITA_EQUIPO.items():
            if neth in self.sell:
                self.assertLessEqual(self.sell[neth], self.sell[dia] + E.NETHERITA_LINGOTE + tpl + 0.1, neth)

    def test_catalogo_por_unidad(self):
        cat = json.loads((Path(E.__file__).parent / 'services_catalog.json').read_text())
        self.assertEqual(cat['ROTTEN_FLESH']['min'], 125)
        self.assertEqual(cat, E.catalogo(self.shops))


class Skript(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sk = E.skript()

    def test_generado_al_dia(self):
        self.assertEqual(self.sk, (BUILD / 'economia/Skript/scripts/astral_economia.sk').read_text(encoding='utf-8'))

    def test_perdida_mundos(self):
        mundos = E.mundos_con_perdida()
        for w in ('world', 'world_nether', 'astral_minas', 'astral_bosque', 'oceano', 'tumba', 'infinita', 'santuario'):
            self.assertIn(w, mundos)
        for w in ('lobby', 'arena', 'arenas_tft', 'colorescape', 'portales_astrales'):
            self.assertNotIn(w, mundos)
        self.assertIn('on death of player:', self.sk)
        self.assertIn('scoreboard tags of player contain "astral.party.fallen"', self.sk)
        self.assertIn('perdida: 0.5', self.sk)

    def test_banco(self):
        for frag in ('command /banco:', 'command /astralbanco', 'every 1 minute:', '{astral.banco.saldo::',
                     'log "', 'set {-eco.banco.lim::5} to 1000000000', 'set {-eco.banco.costo::5} to 200000000'):
            self.assertIn(frag, self.sk)
        self.assertNotIn('{-astral.banco.saldo', self.sk)  # persistente, nunca en memoria

    def test_rebase_unica_vez(self):
        self.assertIn('if {astral.eco.rebase} is set:', self.sk)
        self.assertIn('executable by: console', self.sk.split('command /astraleconomia')[1])

    def test_astralplatamob_solo_aca(self):
        ren = (BUILD / 'renacimiento/astral_renacimiento.sk').read_text(encoding='utf-8')
        self.assertNotIn('command /astralplatamob', ren)
        self.assertIn('delete {astral.banco.saldo::', ren)
        self.assertIn('command /astralplatamob', self.sk)

    def test_npc_banco(self):
        import lobby
        from mobs.mythic import NPCS
        import menus
        self.assertNotIn('astral_npc_banco', lobby.NPC_POS)   # sin NPC aparte: va en el aldeano de Subastas
        self.assertIn('dm open subastas_inicio', NPCS['astral_npc_subastas'][2][0])
        m = menus.subastas_inicio_menu()
        self.assertIn('[openguimenu] subastas', m)
        self.assertIn('[player] banco', m)


if __name__ == '__main__':
    unittest.main()
