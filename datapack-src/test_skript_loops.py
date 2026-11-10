"""Guardia de regresion para referencias ambiguas en los Skript generados."""
from pathlib import Path
import re
import unittest

import bosque_talar

ROOT = Path(__file__).resolve().parents[1]
ENTITY_LOOP = re.compile(
    r"loop (?:all )?(?:players|entities|living entities|dropped items|mobs|animals|monsters)\b",
    re.IGNORECASE,
)
REFERENCE = re.compile(r"\bloop-(entity|value)\b(?!-\d)", re.IGNORECASE)


def ambiguous_references(script):
    """Rastrea bucles por indentacion; conserva referencias en comandos interpolados.

    Reconoce selectores explicitos de entidades, no infiere tipos de variables.
    loop-value requiere numero ante cualquier par de bucles anidados.
    """
    loops = []
    errors = []
    for number, raw in enumerate(script.splitlines(), 1):
        line = raw.expandtabs(4)
        code = line.lstrip()
        if not code or code.startswith('#'):
            continue
        indent = len(line) - len(code)
        while loops and loops[-1][0] >= indent:
            loops.pop()
        for match in REFERENCE.finditer(code):
            count = (sum(entity for _, entity in loops)
                     if match[1].lower() == 'entity' else len(loops))
            if count >= 2:
                errors.append((number, match[0]))
        # La expresion de un nuevo loop pertenece al ambito exterior.
        if code.lower().startswith('loop ') and code.endswith(':'):
            loops.append((indent, bool(ENTITY_LOOP.match(code))))
    return errors


class SkriptLoops(unittest.TestCase):
    def test_rejects_original_bosque_regression(self):
        broken = bosque_talar.script().replace('loop-dropped item', 'loop-entity')
        self.assertEqual(len(ambiguous_references(broken)), 7)

    def test_nested_entities_and_values(self):
        for reference in ('loop-entity', 'loop-value'):
            script = ('every 2 ticks:\n'
                      '    loop all players:\n'
                      '        if loop-player is online:\n'
                      '            loop all dropped items in radius 48 around loop-player:\n'
                      f'                delete {reference}\n')
            self.assertEqual(ambiguous_references(script), [(5, reference)])
            self.assertEqual(ambiguous_references(script.replace(reference, reference + '-2')), [])
        self.assertEqual(ambiguous_references(
            'loop 2 times:\n    loop {_items::*}:\n        set {_x} to loop-value\n'),
            [(3, 'loop-value')])

    def test_scopes_comments_and_specific_types(self):
        self.assertEqual(ambiguous_references(
            'loop all players:\n'
            '    loop all dropped items:\n'
            '        # delete loop-entity\n'
            '        delete loop-dropped item\n'
            '    set {_p} to loop-entity\n'
            'loop all living entities:\n'
            '    delete loop-entity\n'), [])

    def test_all_generated_skripts(self):
        paths = sorted((ROOT / 'build').rglob('*.sk'))
        self.assertTrue(paths, 'No se encontraron Skript generados')
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual(ambiguous_references(path.read_text(encoding='utf-8')), [])

    def test_bosque_matches_generator(self):
        self.assertEqual((ROOT / 'build/bosque/astral_bosque.sk').read_text(encoding='utf-8'),
                         bosque_talar.script())


if __name__ == '__main__':
    unittest.main()
