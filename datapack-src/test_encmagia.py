"""Contrato del paquete mágico; la integración con Paper está en probar_encmagia_paper.py."""
import json
from pathlib import Path
import unittest
import zipfile
from encmagia import MAGIA, DEFINITIVOS
import mesa_encantamientos as mesa

ROOT = Path(__file__).resolve().parents[1]


class MagiaTests(unittest.TestCase):
    def test_registros_y_exclusiones(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            for key, (name, maximum, _, _) in MAGIA.items():
                data=json.loads(z.read(f'data/astral/enchantment/{key}.json'))
                self.assertEqual(data['description']['text'], name)
                self.assertEqual(data['max_level'], maximum)
                self.assertEqual(data['supported_items'], '#astral:magia')
                self.assertEqual(data.get('exclusive_set'), '#astral:magia_definitivos' if key in DEFINITIVOS else None)
            tag=json.loads(z.read('data/astral/tags/enchantment/magia_definitivos.json'))
            self.assertEqual(set(tag['values']), {'astral:'+k for k in DEFINITIVOS})

    def test_bonus_del_cast_solo_habilitado(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            cast=z.read('data/astral/function/spell/cast.mcfunction').decode()
            for key, maximum, score, step in [('poder_arcano',5,'#pct',400),('fluidez',4,'#cdr',5)]:
                lines=[l for l in cast.splitlines() if 'astral:'+key in l]
                self.assertEqual(len(lines),maximum)
                for n,line in enumerate(lines,1):
                    self.assertIn('@s[tag=astral.encmagia]',line)
                    self.assertIn(f'levels:{n}',line)
                    self.assertTrue(line.endswith(f'{score} astral.tmp {step*n}'))
            self.assertLess(cast.index('encmagia/inicio'),cast.index('function astral:spell/trace'))
            self.assertLess(cast.index('encmagia/fin'),cast.index('tag @s remove astral.caster'))

    def test_mesa_y_descripciones(self):
        c=mesa.config()
        self.assertFalse(c['encmagia']['publico'])
        for k in MAGIA:
            self.assertEqual(c['nombres']['astral:'+k],MAGIA[k][0])
            self.assertIn('astral:'+k,c['descripciones'])
        for k in DEFINITIVOS:
            self.assertEqual(c['costos']['astral:'+k],mesa.MUY_BUENO)

    def test_cobro_sin_requisito_nuevo(self):
        sk=(ROOT/'build/gameplay/astral_armas_especiales.sk').read_text('utf8')
        pay=sk.split('function asw_pay(',1)[1].split('\nfunction ',1)[0]
        self.assertIn('astral.encmagia',pay)
        self.assertIn('astral:sabio_arcano',pay)
        self.assertIn('1 - 0.04 * {_lv}',pay)
        self.assertIn('min(5, {_lv})',pay)
        self.assertNotIn('asw_level(',pay)
        self.assertNotIn('asw_requirement(',pay)


if __name__ == '__main__':
    unittest.main()
