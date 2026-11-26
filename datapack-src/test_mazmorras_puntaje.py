"""Plan E2 (18/11/2026): puntaje S..F, ruleta invisible del cofre, tiradas de items y premio especial."""
import random
import re
import unittest
import zipfile
from pathlib import Path

import economia as E
import mazmorras_puntaje as M

ROOT = Path(__file__).resolve().parents[1]


class Puntaje(unittest.TestCase):
    def test_cuenta(self):
        self.assertEqual(E.puntos(0, 9 * 60, 10), 110)                 # sin muertes y a tiempo
        self.assertEqual(E.nota(E.puntos(0, 9 * 60, 10)), 'S')
        self.assertEqual(E.puntos(1, 10 * 60, 10), 88)                 # una caida: A
        self.assertEqual(E.nota(88), 'A')
        self.assertEqual(E.puntos(9, 10 * 60, 10), 40)                 # tope -60 por muertes
        self.assertEqual(E.puntos(0, 60 * 60, 10), 70)                 # tope -40 por tiempo (+10 sin muertes)
        self.assertEqual(E.puntos(0, 12 * 60 + 59, 10), 102)           # 2 minutos enteros de mas
        self.assertEqual(E.puntos(20, 99 * 60, 10), 0)
        self.assertEqual(E.nota(0), 'F')
        for n, lo in E.NOTA_MIN.items():
            self.assertEqual(E.nota(lo), n)

    def test_objetivo_para_cada_mazmorra(self):
        for key, _, tier, mundos in M.mazmorras():
            self.assertIn(key, E.TIEMPO_OBJETIVO)
            self.assertTrue(1 <= tier <= 5)
            self.assertTrue(mundos)


class Ruleta(unittest.TestCase):
    def test_esperanza_crece_con_la_nota_y_minimo_fijo(self):
        esp = [E.ruleta_esperanza(n) for n in E.NOTAS]
        self.assertEqual(esp, sorted(esp))
        for n in E.NOTAS:
            self.assertLess(E.ruleta_esperanza(n), (E.RULETA_MIN + E.RULETA_MAX[n]) / 2)   # sesgada a lo bajo

    def test_montecarlo_coincide(self):
        rnd = random.Random(7)
        for n in E.NOTAS:
            lo, hi, k = E.RULETA_MIN, E.RULETA_MAX[n], E.RULETA_K[n]
            vals = [lo + (hi - lo) * rnd.random() ** k for _ in range(40000)]
            self.assertAlmostEqual(sum(vals) / len(vals) / E.ruleta_esperanza(n), 1, delta=0.03)
            self.assertGreaterEqual(min(vals), lo)
            self.assertLessEqual(max(vals), hi)

    def test_multiplicadores(self):
        self.assertEqual(E.ruleta_mult('bosque', 1), 1)
        self.assertEqual(E.ruleta_mult('forja', 5), 12)
        self.assertEqual(E.ruleta_mult('santuario', 5), 18)
        self.assertEqual(E.RULETA_MAX['S'] * E.ruleta_mult('santuario', 5), 9_000_000)  # 25/11


class Items(unittest.TestCase):
    def test_mejor_nota_mas_raro(self):
        for t in range(1, 6):
            pool = E.pool(t)
            def raro(n):
                w = E.pesos(t, n)
                return sum(x for x, it in zip(w, pool) if it[4] == 2) / sum(w)
            share = [raro(n) for n in E.NOTAS]
            self.assertEqual(share, sorted(share))
            self.assertGreater(share[0], 0)          # lo raro es posible con cualquier nota
            self.assertGreater(E.pesos(t, 'S')[0], 0)  # y lo comun sigue posible con S

    def test_especial_solo_a_y_s(self):
        self.assertEqual(set(E.ESPECIAL_PROB), {'A', 'S'})
        self.assertLess(E.ESPECIAL_PROB['A'], E.ESPECIAL_PROB['S'])
        self.assertLessEqual(E.ESPECIAL_PROB['S'], 0.02)
        self.assertEqual([E.ITEM_TIRADAS[n] for n in E.NOTAS], [1, 1, 2, 2, 3, 3])

    def test_ids_existen_en_el_datapack(self):
        z = zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip')
        ids = {n.split('/')[-1][:-5] for n in z.namelist() if n.startswith('data/astral/loot_table/item/')}
        for t in range(1, 6):
            for iid in E.equipo(t + 1):
                self.assertIn(iid, ids)
            for iid, astral, *_ in E.pool(t):
                if astral:
                    self.assertIn(iid, ids)
                else:
                    self.assertIn(iid, M.VANILLA)
        self.assertNotIn('ballesta_6', E.equipo(6))
        self.assertIn('berserker_6_helmet', E.equipo(6))


class Skript(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sk = M.script()

    def test_generado_al_dia(self):
        self.assertEqual(self.sk, M.OUT.read_text(encoding='utf-8'))

    def test_una_ruleta_por_victoria(self):
        cobro = self.sk.split('command /astralcofre')[1]
        self.assertLess(cobro.index('delete {pz.pend.key::'), cobro.index('pz_cofre({_p}'))
        self.assertIn('if {pz.pend.key::%{_u}%} is not arg-2:', cobro)
        self.assertIn('{-pz.hecho::%{_w}%} is not set', self.sk)

    def test_ganchos(self):
        import mazmorras_copias, oceano_fosa
        cop = mazmorras_copias.script()
        self.assertIn('mazpuntaje inicio %{_mundo::%{_elegida}%}%', cop)
        self.assertIn('mazpuntaje fin %arg-1%', cop)
        self.assertIn('mazpuntaje fin <caster.l.w>', oceano_fosa.boss_block())
        self.assertIn('scoreboard tags of player contain "astral.party.fallen"', self.sk)
        self.assertIn('set {-pz.key::world_minecraft_santuario_azeroth_2} to "santuario"', self.sk)

    def test_cofre_usa_el_cobro_nuevo(self):
        from cofre_mazmorra import cofre_menu
        from mobs.mazmorra import MINA
        d = cofre_menu(MINA)
        self.assertEqual(d['items']['reclamar_0']['click_commands'], ['[close]', '[console] astralcofre %player_name% mina'])
        self.assertNotIn('eco give', str(d))
        self.assertEqual(sum(1 for k in d['items'] if k.startswith('nota_')), 7)
        self.assertIn('astral:xp/cofre', self.sk)
        self.assertTrue(re.search(r'lp user .* permission settemp astral\.%\{_key\}%\.cd true \{@cooldown\}', self.sk))


if __name__ == '__main__':
    unittest.main()
