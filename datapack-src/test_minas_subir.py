"""Salida del pozo: generacion, avisos y protecciones de minas."""
import re
import unittest
from pathlib import Path

import minas


class SalirDelPozo(unittest.TestCase):
    def test_salida_generada(self):
        text = minas.script()
        self.assertEqual(text, (minas.OUT / 'Skript/scripts/astral_minas.sk').read_text(encoding='utf8'))
        for command in ('command /subir:', 'command /minassubir [<text>]:'):
            self.assertEqual(text.count(command), 1)
        self.assertIn('set {am.subir} to "privado"', text)
        self.assertIn('difference between now and {-am.subir.uso::%{_id}%} < 3 seconds', text)
        self.assertIn('difference between now and {-am.subir.aviso::%{_id}%} < 5 minutes', text)
        self.assertIn('send action bar "&e⬆ Usa &f/subir &epara volver arriba" to loop-player', text)

    def test_aviso_solo_cerca_del_fondo(self):
        template = Path(minas.__file__).with_suffix('.sk').read_text(encoding='utf8')
        self.assertIn('if y-coordinate of loop-player < @PIT_Y1@ + 3:', template)
        text = minas.script()
        threshold = f"if y-coordinate of loop-player < {minas.PIT['y1']} + 3:"
        notice = text.split(threshold, 1)[1].split('# Minutos de mineria activa', 1)[0]
        self.assertIn('if am_in_pit(location of loop-player, {_i}) is true:', notice)
        self.assertIn('if am_subir_enabled(loop-player) is true:', notice)
        self.assertIn('difference between now and {-am.subir.aviso::%{_id}%} < 5 minutes:', notice)
        self.assertIn('set {-am.subir.aviso::%{_id}%} to now', notice)
        self.assertIn('send action bar ', notice)

    def test_panel_y_aviso_privados(self):
        import yaml
        from lobby import TAB_SECTIONS
        data = yaml.safe_load(TAB_SECTIONS)
        rows = data['scoreboard']['scoreboards']['minas']['lines']
        self.assertLessEqual(len(rows), 15)
        self.assertTrue(any('am_location' in row for row in rows))
        regen = next(i for i, row in enumerate(rows) if 'Regeneración' in row)
        self.assertEqual(rows[regen + 1], '%condition:am_subir_row%')
        rule = data['conditions']['am_subir_row']
        self.assertEqual(rule['conditions'], ['%objective_score_{am_subir}%=1'])
        self.assertIn('/subir', rule[True])
        self.assertEqual(rule[False], '')
        text = minas.script()
        self.assertIn('"am_subir"', text.split('loop all players:', 1)[0])
        sync = text.split('function am_sync(', 1)[1].split('\nfunction ', 1)[0]
        self.assertIn('am_subir_score({_p})', sync)
        toggle = text.split('command /minassubir', 1)[1].split('\n# Dentro', 1)[0]
        self.assertIn('loop all players:\n                am_subir_score(loop-player)', toggle)
        visibility = text.split('function am_subir_score(', 1)[1].split('\ncommand ', 1)[0]
        self.assertIn('if name of world of {_p} is "astral_minas":', visibility)
        self.assertIn('if am_subir_enabled({_p}) is true:', visibility)
        enabled = text.split('function am_subir_enabled(', 1)[1].split('\n# TAB', 1)[0]
        self.assertIn('if {am.subir} is "publico":', enabled)
        self.assertIn('if name of {_p} is "ByTrainx":', enabled)
        notice = text.split('every 10 minutes:', 1)[1].split('\nevery ', 1)[0]
        self.assertIn('loop all players in am_world():', notice)
        self.assertIn('if am_subir_enabled(loop-player) is true:', notice)
        self.assertEqual(notice.count('send '), 1)
        self.assertIn('send "&e⬆ &fCon &e/subir &fapareces arriba, en la plataforma de tu mina." to loop-player', notice)
        self.assertEqual(len(re.findall(r'^command /', text, re.M)), len(set(re.findall(r'^command /[^ :]+', text, re.M))))
        self.assertEqual(len(re.findall(r'^function ', text, re.M)), len(set(re.findall(r'^function [^(]+', text, re.M))))

    def test_sin_bloques_de_salida(self):
        text = minas.script()
        self.assertNotIn('ladder', text)
        self.assertNotIn('am_escaleras', text)
        toggle = text.split('command /minassubir', 1)[1].split('\n# Dentro', 1)[0]
        self.assertNotIn('probar', toggle)
        self.assertIn('/minassubir publico|privado)', toggle)
        reset = text.split('function am_reset(', 1)[1].split('\nevery ', 1)[0]
        self.assertIn('run clone', reset)
        self.assertNotIn('run fill', reset)

    def test_taladros_y_vetas_respetan_proteccion(self):
        text = minas.script()
        for name in ('am_drill', 'am_vein'):
            body = text.split(f'function {name}(', 1)[1].split('\nfunction ', 1)[0]
            self.assertLess(body.index('am_can_break('), body.index('to air'))
        self.assertTrue(all('ladder' not in (m[1], m[2]) for m in minas.MINES))


if __name__ == '__main__':
    unittest.main()
