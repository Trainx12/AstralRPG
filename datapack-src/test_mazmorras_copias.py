"""6 copias por mazmorra, entrada a copia libre, parties y 8 minutos tras el jefe."""
import unittest

import instancias
import mazmorras_copias as mc


class CopiasTests(unittest.TestCase):
    def test_six_copies_per_dungeon_with_bukkit_names(self):
        self.assertEqual(instancias.copias('mina'), ['mina'] + [f'mina_{n}' for n in range(2, 7)])
        self.assertEqual(instancias.bukkit('santuario_azeroth_3'), 'world_minecraft_santuario_azeroth_3')
        self.assertEqual(instancias.bukkit('mina_3'), 'mina_3')
        self.assertEqual(len(mc.all_worlds()), 36)

    def test_lists_keyed_by_world_include_every_copy(self):
        from escala import TIER_MAZMORRA
        from gameplay import DUNGEONS, RESCUE_HEIGHTS
        for dim in [c for w in instancias.DUNGEON_WORLDS.values() for c in instancias.copias(w)]:
            self.assertIn(dim, TIER_MAZMORRA)
            self.assertIn(dim, DUNGEONS)
        self.assertEqual(RESCUE_HEIGHTS['mina_6'], RESCUE_HEIGHTS['mina'])
        self.assertEqual(TIER_MAZMORRA['forja_volcano_4'], TIER_MAZMORRA['forja_volcano'])

    def test_entry_script_free_copy_party_busy_and_timer(self):
        sk = mc.script()
        for d in mc.dungeons():
            self.assertIn(f'if {{_key}} is "{d["key"]}":', sk)
            for n, dim in enumerate(d['dims'], 1):
                self.assertIn(f'set {{_dim::{n}}} to "{dim}"', sk)
        self.assertIn('Mazmorra ocupada', sk)
        self.assertIn('execute in minecraft:%{_d}% run minecraft:tp', sk)
        self.assertIn(f'>= {mc.MINUTOS_FIN} minutes', sk)
        self.assertIn('execute console command "spawn %name of loop-player%"', sk)
        for sub in ('"invitar"', '"aceptar"', '"rechazar"', '"salir"', '"echar"'):
            self.assertIn(f'if arg-1 is {sub}:', sk)

    def test_generated_dungeons_never_teleport_into_a_fixed_world(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1] / 'build/mythicmobs/skills'
        for name in ('mazmorra', 'bosque', 'tumba', 'cumbre', 'forja', 'santuario'):
            text = (root / f'{name}.yml').read_text(encoding='utf8')
            for w in instancias.DUNGEON_WORLDS.values():
                self.assertNotIn(f'in minecraft:{w} run minecraft:tp', text)
            self.assertIn('mazentrar <trigger.name>', text)
            self.assertIn('mazfin <caster.l.w>', text)


if __name__ == '__main__':
    unittest.main()
