"""Plan E3 (18/11/2026): Secretos de Astral."""
import unittest
import zipfile
from pathlib import Path

import economia as E
import mazmorras_puntaje
import secretos as S

ROOT = Path(__file__).resolve().parents[1]


class Secretos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sk = S.script()

    def test_generado_al_dia(self):
        self.assertEqual(self.sk, S.OUT.read_text(encoding='utf-8'))

    def test_cifras_de_economia(self):
        self.assertIn(f'prob_dorado: {E.SECRETO_DORADO_PROB}', self.sk)
        self.assertIn(f'mult_dorado: {E.SECRETO_DORADO_MULT}', self.sk)
        self.assertLess(E.SECRETO_PROB_EQUIPO, 0.05)                  # muy raro
        self.assertEqual(sorted(E.SECRETO_PLATA_TIER), list(range(1, 11)))
        self.assertEqual(E.SECRETO_PLATA_TIER[1], 450_000)
        self.assertEqual(E.SECRETO_PLATA_TIER[5], 7_500_000)
        for t, v in E.SECRETO_PLATA_TIER.items():
            self.assertIn(f'set {{-sec.plata::{t}}} to {v}', self.sk)
        self.assertNotIn('balance of {_p} *', self.sk)                # ya no depende de lo que lleva encima

    def test_plata_siempre(self):
        f = self.sk.split('function sec_reclamar')[1].split('on right click')[0]
        self.assertLess(f.index('add {_v} to balance'), f.index('if {_r} < {@prob_equipo}:'))

    def test_una_vez_por_jugador(self):
        f = self.sk.split('function sec_reclamar')[1]
        self.assertLess(f.index('if {secretos.tiene::%{_u}%::%{_id}%} is set:'), f.index('set {secretos.tiene::'))
        self.assertLess(f.index('set {secretos.tiene::'), f.index('set {_r} to random number'))
        self.assertNotIn('{-secretos.tiene', self.sk)                 # persistente

    def test_equipo_un_tier_mas_y_existe(self):
        z = zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip')
        ids = {n.split('/')[-1][:-5] for n in z.namelist() if n.startswith('data/astral/loot_table/item/')}
        for t in range(1, 11):
            self.assertIn(f'set {{-sec.eqn::{t}}}', self.sk)
            for iid in E.equipo(min(t + 1, 10)):
                self.assertIn(iid, ids)
        self.assertIn('set {-sec.eq::1::1} to "espada_2"', self.sk)
        self.assertIn('if score @s astral.wt matches %loop-number%', self.sk)

    def test_premios_del_cofre(self):
        self.assertIn('pz_tirada({_p}, min({_t}, 5), {@nota}, "un secreto")', self.sk)
        self.assertIn('function pz_tirada(p: player, t: number, n: number, maz: text):', mazmorras_puntaje.script())
        self.assertEqual(E.ESPECIAL_PROB.get(E.SECRETO_NOTA_PESOS, 0), 0)   # el equipo solo sale por la rama rara

    def test_comandos_y_proteccion(self):
        for frag in ('command /secretos:', 'command /secreto <text> [<text>]:', 'permission: astral.admin.secretos',
                     'on break:', 'on right click:', 'cancel event'):
            self.assertIn(frag, self.sk)
        self.assertEqual(len(S.PROPUESTAS), 10)
        for sid, w, x, y, z, pista in S.SECRETOS:
            self.assertIn(f'set {{secreto.idx::{w}|{x}|{y}|{z}}} to "{sid}"', self.sk)


if __name__ == '__main__':
    unittest.main()
