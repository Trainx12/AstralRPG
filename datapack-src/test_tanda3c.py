"""Tanda 3c: maquinas de Mini juegos, NPC 3D y listas con minecraft:kill."""
import json
from pathlib import Path
import re
import unittest
import yaml
from mobs.tanda3c import definitions, npc_skills, NPC_MODELOS, MAQUINAS, PERSONAJES, LUCES, MAZMORRAS

ROOT = Path(__file__).resolve().parents[1]


class Tanda3cTests(unittest.TestCase):
    def model(self, name):
        return json.loads((ROOT / 'build/models' / f'{name}.bbmodel').read_text(encoding='utf-8'))

    def test_models_have_click_box_name_bone_and_idle(self):
        for name in list(MAQUINAS) + ['astral_npc_' + p for p in PERSONAJES]:
            with self.subTest(model=name):
                d = self.model(name)
                groups = {g['name'] for g in d['groups']}
                self.assertIn('b_astral_hitbox', groups)
                self.assertIn('mtag_nombre', groups)
                self.assertIn('idle', {a['name'] for a in d['animations']})
                box = next(e for e in d['elements'] if e['name'] == 'astral_hitbox')
                self.assertTrue(all(face['texture'] is None for face in box['faces'].values()))
                self.assertLessEqual(d['resolution']['width'], 256)

    def test_lit_parts_exist_as_bones(self):
        for mid, parts in MAQUINAS.items():
            self.assertLessEqual(set(parts), {g['name'] for g in self.model(mid)['groups']})
        for person, parts in LUCES.items():
            self.assertLessEqual(set(parts), {g['name'] for g in self.model('astral_npc_' + person)['groups']})

    def test_machines_open_the_minigames_panel(self):
        mobs, skills = definitions()
        for mid in MAQUINAS:
            mob = mobs[mid]
            self.assertEqual(mob['Display'], '&a&lMini juegos')
            self.assertTrue(mob['Options']['NoAI'] and mob['Options']['Invincible'])
            self.assertIn('command{c="dm open parkour <trigger.name>"} @self ~onInteract', mob['Skills'])
            self.assertEqual(skills['AST_MODELO_' + mid]['Skills'][0], f'model{{m={mid}}} @self')

    def test_every_npc_keeps_villager_and_gets_its_model(self):
        mobs = {}
        for f in (ROOT / 'build/mythicmobs/mobs').glob('*.yml'):
            mobs.update(yaml.safe_load(f.read_text(encoding='utf-8')) or {})
        for mid, person in NPC_MODELOS.items():
            with self.subTest(npc=mid):
                self.assertEqual(mobs[mid]['Type'], 'VILLAGER')
                self.assertIn(f'skill{{s=AST_NPC_{person}}} @self ~onSpawn', mobs[mid]['Skills'])
                self.assertIn(f'skill{{s=AST_NPC_{person}}} @self ~onLoad', mobs[mid]['Skills'])
        for key in MAZMORRAS:
            self.assertIn('skill{s=AST_NPC_bruja} @self ~onSpawn', mobs['astral_npc_' + key]['Skills'])
            self.assertIs(mobs['astral_npc_' + key]['Options']['AlwaysShowName'], False)
        # Tienda usa el comerciante propio; Venta sigue con su modelo privado.
        for mid in ('astral_npc_santuario', 'astral_npc_venta', 'astral_npc_gacha_rpg', 'astral_npc_parkour'):
            self.assertFalse(any('AST_NPC_' in s for s in mobs[mid]['Skills']), mid)
        self.assertEqual(npc_skills('entrada', 'santuario'), [])

    def test_console_lists_use_minecraft_kill(self):
        bad = re.compile(r'(?:^|run )kill @')
        files = list((ROOT / 'build/deploy').glob('*.md')) + [ROOT / 'build/lobby/comandos.txt', ROOT / 'build/minijuegos/despliegue.txt',
                                                              ROOT / 'build/minijuegos/astral_minijuegos.sk']
        for f in files:
            for n, line in enumerate(f.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
                self.assertIsNone(bad.search(line), f'{f.name}:{n}: {line[:80]}')


if __name__ == '__main__':
    unittest.main()
