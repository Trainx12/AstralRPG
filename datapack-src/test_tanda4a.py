"""Integracion de contenidos privados, permisos, rarezas y aislamiento del arte."""
import base64
from collections import defaultdict
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import yaml
from terceros import PETS, ROOT, privado, sources
from mobs.mascotas import MASCOTAS, skill_yml, commands, beneficios_actuales
from mobs.mythic import MOBS, spawns, mob_block
from menus import mascotas_extra_menu, mascota_detalle_menu


class Tanda4aTests(unittest.TestCase):
    def test_catalog_and_permanent_scoreboard_ids(self):
        self.assertEqual(len(PETS), 17)
        self.assertEqual([d['n'] for d in MASCOTAS.values()], list(range(1, 24)))
        old = [MASCOTAS[p]['efectos'] for p in ('lobo', 'cuervo', 'golem', 'zorro', 'dragon', 'fenix')]
        sk = yaml.safe_load(skill_yml())
        for pid, *_ in PETS:
            self.assertNotIn(MASCOTAS[pid]['efectos'], old)
            for prefix in ('pxp_', 'plv_', 'pmod_'):
                self.assertLessEqual(len(prefix + pid), 16)
                self.assertIn('scoreboard objectives add ' + prefix + pid, commands())
            gain = ' '.join(sk['PET_GANAR_' + pid.upper()]['Skills'])
            self.assertIn('astral.mascota.' + pid, gain)
            self.assertEqual(len(beneficios_actuales(pid, 20)), 3)

    def test_all_new_pets_reachable_once_and_permission_guarded(self):
        seen = set()
        for page in (2, 3, 4):
            menu = yaml.safe_load(mascotas_extra_menu(page))
            # Varias capas por casilla (bloqueada / nivel 1-10-20), pero cada casilla es de una sola cosa.
            owner = {}
            for key, entry in menu['items'].items():
                base = key.split('_hit_')[0].removesuffix('_no').removesuffix('_nv10').removesuffix('_nv20')
                self.assertEqual(owner.setdefault(entry['slot'], base), base, key)
            for pid, *_ in PETS:
                if 'm_' + pid not in menu['items']:
                    continue
                self.assertNotIn(pid, seen); seen.add(pid)
                detail = yaml.safe_load(mascota_detalle_menu(pid))['items']
                req = detail['invocar']['click_requirement']['requirements']['tiene']
                self.assertEqual(req, {'type': 'has permission', 'permission': 'astral.mascota.' + pid})
                self.assertIn(f'mascota {MASCOTAS[pid]["n"]}', str(detail['invocar']['click_commands']))
                self.assertIn('Bloqueada', detail['estado_1_no']['display_name'])
                self.assertIn('Desbloqueada', detail['estado_1']['display_name'])
        self.assertEqual(seen, {p[0] for p in PETS})

    def test_rarity_totals_and_guarantee_unchanged(self):
        from lobby import RARITY_WEIGHT, PITY, mount_rewards
        self.assertEqual(PITY['gacha_monturas'], 40)
        for suffix, expected in [('', RARITY_WEIGHT), ('_garantia', {'epic': 87.5, 'legendary': 12.5})]:
            prizes = yaml.safe_load((ROOT / f'build/lobby/CrazyCrates/crates/gacha_monturas{suffix}.yml').read_text(encoding='utf-8'))['Crate']['Prizes']
            # Los premios se ordenan por rareza descendente, igual que el generador.
            rewards = sorted(mount_rewards(), key=lambda r: list(RARITY_WEIGHT).index(r[0]), reverse=True)
            if suffix:
                rewards = [r for r in rewards if r[0] in expected]
            sums = defaultdict(float)
            self.assertEqual(len(rewards), len(prizes))
            for reward, prize in zip(rewards, prizes.values()):
                sums[reward[0]] += prize['Weight']
            for rarity, weight in expected.items():
                self.assertAlmostEqual(sums[rarity], weight, delta=.002)

    def test_goblin_is_manual_only_and_keeps_tier_roll(self):
        self.assertNotIn('spawn', MOBS['astral_goblin'])
        self.assertNotIn('astral_goblin', spawns())
        mob = mob_block('astral_goblin', MOBS['astral_goblin'])
        self.assertIn('function astral:mob/roll', mob)
        self.assertNotIn('state{s=attack}', mob)
        self.assertEqual(MOBS['astral_abejorro']['name'], '&8Armored Grub')

    def test_admin_sword_has_no_recipe_or_enchantments(self):
        with zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip') as z:
            d = json.loads(z.read('data/astral/loot_table/item/espada_heroe_errante.json'))
            c = d['pools'][0]['entries'][0]['functions'][0]['components']
            self.assertIn('tier:3', c['minecraft:custom_data'])
            self.assertNotIn('minecraft:enchantments', c)
            self.assertEqual(c['minecraft:item_model'], 'astral:espada_heroe_errante')
            self.assertFalse(any('espada_heroe_errante' in name for name in z.namelist() if '/recipe/' in name))
            original = json.loads(z.read('data/astral/loot_table/item/espada_3.json'))['pools'][0]['entries'][0]['functions'][0]['components']
            def damage(comps):
                return next(m['amount'] for m in comps['minecraft:attribute_modifiers'] if m['type'] == 'minecraft:attack_damage')
            self.assertEqual(damage(c), damage(original))

    def test_missing_private_repository_is_optional(self):
        from build_privado import main
        with tempfile.TemporaryDirectory(dir=ROOT / '.local') as folder, patch.dict(os.environ, ASTRAL_PRIVADO=folder), patch.object(sys, 'argv', ['build_privado.py', '--prepare']):
            main()
            self.assertEqual(list(Path(folder).iterdir()), [])


@unittest.skipUnless((privado() / 'x').is_dir(), 'Assets privados no disponibles')
class PrivateAssetsTests(unittest.TestCase):
    def test_models_are_portable_and_have_real_hitboxes(self):
        from build_privado import adapted
        from mobs.tamanos import bounds_data
        for mid, path in sources().items():
            original = json.loads(path.read_text(encoding='utf-8'))
            copy = deepcopy(original)
            d = adapted(original, mid)
            self.assertEqual(original, copy)
            for t in d['textures']:
                self.assertNotIn('path', t)
                self.assertTrue(t['source'].startswith('data:image/png;base64,'))
            if mid in ('astral_goblin', 'astral_abejorro', 'astral_vendedor'):
                box = next(e for e in d['elements'] if e['name'] == 'astral_hitbox')
                expected = bounds_data(original) if mid != 'astral_vendedor' else ((-.3, .3), (0, 1.8), (-.3, .3))
                for axis in range(3):
                    self.assertAlmostEqual(box['from'][axis] / 16, expected[axis][0])
                    self.assertAlmostEqual(box['to'][axis] / 16, expected[axis][1])
            if mid == 'astral_goblin':
                self.assertIn('idle', [a['name'] for a in d['animations']])

    def test_public_files_and_nested_zip_are_private_art_free(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        from verificar_terceros import audit, inspect, fingerprints
        prints = fingerprints()
        png = json.loads(next(iter(sources().values())).read_text(encoding='utf-8'))['textures'][0]['source']
        raw = base64.b64decode(png.split(',', 1)[1])
        self.assertTrue(inspect('renombrada.png', raw, prints))
        from PIL import Image
        reencoded = io.BytesIO()
        Image.open(io.BytesIO(raw)).save(reencoded, 'PNG', compress_level=0)
        self.assertTrue(inspect('reexportada.png', reencoded.getvalue(), prints))
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, 'w') as z:
            z.writestr('assets/astral/renombrada.png', raw)
        self.assertTrue(inspect('pack.zip', archive.getvalue(), prints))
        final = privado() / 'build/AstralRPG-Textures.zip'
        if final.is_file():
            self.assertTrue(inspect('pack-final.zip', final.read_bytes(), prints))
        self.assertEqual(audit(), [])


if __name__ == '__main__':
    unittest.main()
