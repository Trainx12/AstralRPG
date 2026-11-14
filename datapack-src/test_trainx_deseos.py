"""Jefe final Trainx, Renacimiento, Deseos y Rankings (14/11/2026)."""
import unittest

import yaml


class TestTrainx(unittest.TestCase):
    def test_ultima_oleada_es_trainx(self):
        from santuario_azeroth import WAVES
        self.assertEqual(WAVES[-1], 'trainx')
        from mobs.mazmorras_data import catalog
        sant = next(d for d in catalog() if d['key'] == 'santuario')
        ultima = sant['rooms'][0]['oleadas'][-1]
        self.assertEqual(ultima[0][0], 'astral_santuario_trainx')
        self.assertIn('astral_trainx_estrella', sant['rooms'][0]['extra'])

    def test_bloque_yaml_valido_y_sin_barra_amarilla(self):
        from mobs.trainx import mob_block, skills_yaml, vida
        mid, block, _ = mob_block()
        data = yaml.safe_load(block)
        boss = data[mid]
        self.assertEqual(boss['Health'], vida())
        self.assertNotEqual(boss['BossBar']['Color'], 'YELLOW')
        self.assertIn('Tier V+', boss['BossBar']['Title'])
        self.assertIn('Trainx', boss['Display'])
        skills = yaml.safe_load(skills_yaml())
        for name in ('TRAINX_MODELO', 'TRAINX_COMBO', 'TRAINX_RAYO', 'TRAINX_LLUVIA', 'TRAINX_MUERE'):
            self.assertIn(name, skills)
        self.assertTrue(any('nombre_vplus' in s for s in skills['TRAINX_MODELO']['Skills']))
        self.assertTrue(any('trainxfin' in s for s in skills['TRAINX_MUERE']['Skills']))

    def test_vida_para_cuatro(self):
        from escala import VIDA_JEFE
        from mobs.trainx import vida
        self.assertGreater(vida(), VIDA_JEFE['forja'] * 4)

    def test_modelo_cinco_bloques(self):
        from mobs.trainx import ALTO_BLOQUES
        self.assertAlmostEqual(ALTO_BLOQUES, 5.0)


class TestRenacimiento(unittest.TestCase):
    def test_topes_de_plata(self):
        from renacimiento import tope, tope_lite
        from minas import MINES
        self.assertEqual(tope(), MINES[-1][-1])
        self.assertEqual(tope(), 25_000_000)
        self.assertEqual(tope_lite(), 6_250_000)

    def test_script_valida_fragmentos_y_trainx(self):
        from renacimiento import skript, FRAGMENTOS
        sk = skript()
        for f in FRAGMENTOS:
            self.assertIn(f'astral.fragmento.{f}', sk)
        self.assertIn('astral_renacer_listo(player) is false', sk)
        self.assertIn('astral.trainx.vencido', sk)
        self.assertIn('{@tope}', sk)

    def test_ventanas_y_reglas(self):
        from renacimiento import menus, REGLAS
        m = menus()
        self.assertEqual(set(m), {'renacer', 'deseo', 'deseo_lite'})
        self.assertIn('revisa el Admin', ' '.join(REGLAS))
        lore = ' '.join(m['deseo_lite']['items']['reglas']['lore'])
        self.assertIn('revisa el Admin', lore)
        self.assertNotIn('personalizada', ' '.join(m['deseo_lite']['items']))
        self.assertIn('personalizada', m['deseo']['items'])

    def test_epilogo_da_deseo_lite(self):
        from pathlib import Path
        src = (Path(__file__).parent / 'misiones.py').read_text(encoding='utf-8')
        self.assertIn('aq.deseo_lite', src)


class TestRankings(unittest.TestCase):
    def test_rankings_y_titulos(self):
        from rankings import RANKINGS, titulos, skript
        ids = [r[0] for r in RANKINGS]
        self.assertEqual(ids, ['parkour_spiral', 'parkour_spiral2', 'parkour_paradise3', 'infinita', 'trainx', 'minas', 'bosque'])
        self.assertIn('rey_del_parkour', titulos())
        sk = skript()
        self.assertIn('- 10800 - 345600) / 604800', sk)   # lunes 00:00 UTC-3
        self.assertIn('astral.mascota.fenix', sk)

    def test_titulos_fuera_de_gachas(self):
        from rankings import titulos
        from lobby import TITLES
        gacha = {n.lower() for _, n, _ in TITLES}
        for _, (n, _) in titulos().items():
            self.assertNotIn(n.lower(), gacha)

    def test_carteles_detras_de_la_llegada(self):
        from rankings import carteles, llegadas
        lleg = llegadas()
        for rid, dim, x, y, z in carteles():
            if rid.startswith('parkour_'):
                d = lleg[rid.removeprefix('parkour_')]
                self.assertLess(z, d['arrival'][2])   # yaw 0 mira al sur: atras es -Z


if __name__ == '__main__':
    unittest.main()
