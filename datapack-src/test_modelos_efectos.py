"""Modelos 3D y efectos del 16/11/2026: dibujos, plugin, bastones, Fenix, Trainx y (si esta) el circuito privado."""
import json
import sys
import unittest
import zipfile
import tempfile
from unittest.mock import patch
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'mobs'))

import efectos  # noqa: E402
from terceros import privado  # noqa: E402

FINAL = privado() / 'build/entregas/modelos-3d-efectos/AstralRPG-Textures.zip'


class Efectos(unittest.TestCase):
    def test_dibujos_completos(self):
        files = efectos.pack_files()
        for name, (_, n, size) in efectos.DIBUJOS.items():
            for f in range(n):
                body = files[f'textures/item/fx/{name}_{f}.png']
                self.assertEqual(body.size, (size, size), name)
                self.assertIn(f'items/fx/{name}_{f}.json', files)
                item = files[f'items/fx/{name}_{f}.json']['model']
                self.assertEqual(item['tints'][0]['type'], 'minecraft:dye')      # el color lo pone el plugin
        self.assertGreater(sum(1 for p in efectos._frame(7)[1].getdata() if p[3]), 40)   # centro blanco del hongo
        rayo = files['models/item/fx/rayo.json']
        self.assertEqual(len(rayo['elements']), 8)
        self.assertTrue(all(e['light_emission'] == 15 for e in rayo['elements']))

    def test_cuerpo_en_grises(self):
        """La capa que se tine tiene que ser gris: si no, el color del baston sale mal."""
        for name, (fn, n, _) in efectos.DIBUJOS.items():
            body, _ = fn(n - 1 if name != 'hongo' else 6)
            for r, g, b, a in body.getdata():
                if a:
                    self.assertTrue(r == g == b, name)

    def test_config_y_plugin(self):
        cfg = efectos.config()
        self.assertEqual(cfg['cuadros']['hongo'], efectos.FRAMES)
        java = (HERE / 'runtime/AstralEfectos.java').read_text(encoding='utf-8')
        for name in efectos.DIBUJOS:
            self.assertIn(f'"{name}"', java)
        for cmd in ('"golpe"', '"estallido"', '"rayo"', '"estela"'):
            self.assertIn(cmd, java)
        # Bajo no recibe nada nuevo: ningun dibujo ni particula se pide con nivel minimo Bajo.
        self.assertNotRegex(java, r'(fx|particula|hongo|onda|mancha|llamita)\([^;]*\bBAJO\b')
        self.assertIn('saveResource("config.yml", true)', java)

    def test_bastones_piden_rayo(self):
        with zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip') as z:
            cast = z.read('data/astral/function/spell/cast.mcfunction').decode()
            rayo = z.read('data/astral/function/spell/fx_rayo.mcfunction').decode()
            ray = z.read('data/astral/function/spell/ray.mcfunction').decode()
            hit = z.read('data/astral/function/spell/hit.mcfunction').decode()
        self.assertIn('spell/fx_rayo with storage', cast)
        self.assertIn('fx.rayo', rayo)
        self.assertIn('astral.fx=1..', rayo)                       # Medio y Alto; Bajo no genera el marcador
        self.assertIn('fx.estallido', hit)
        self.assertIn('particle minecraft:witch', ray)             # Bajo sigue viendo lo de siempre
        for t, color in efectos.COLOR_BASTON.items():
            self.assertIn(f'spell.fxh set value "{color.lstrip("#")}"', cast, t)

    def test_jefes_y_armas_especiales(self):
        from mobs import jefes_combate
        y = jefes_combate.metaskills()
        self.assertIn('astralfx estela <target.l.w>', y)
        self.assertEqual(y.count('astralfx golpe'), len(jefes_combate.TEMAS))
        sk = (HERE / 'special_weapons.sk').read_text(encoding='utf-8')
        self.assertIn('astralfx rayo', sk)
        self.assertGreaterEqual(sk.count('astralfx'), 5)


class Modelos(unittest.TestCase):
    def test_entrega_usa_recursos_actuales_y_limita_el_delta(self):
        import deploy_modelos_efectos as deploy
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'build').mkdir()
            expected = {n: b'arte-final' for n in deploy.ARTE_FINAL}
            expected['assets/astral/items/fx/rayo.json'] = b'efecto'
            expected['assets/bettermodel/items/model/astral_pet_fenix_tail_3.json'] = b'fenix'
            with zipfile.ZipFile(root / 'build/AstralRPG-Textures.zip', 'w') as z:
                for n, data in expected.items():
                    z.writestr(n, data)
                z.writestr('assets/astral/items/cuchillo_1.json', b'reserva-publica')
                z.writestr('assets/astral/textures/item/mascotas/fenix.png', b'retrato-publico')
            with patch.object(deploy, 'ROOT', root):
                self.assertEqual(deploy.cambios_publicos(), expected)
                self.assertEqual(deploy.cambios_publicos(), expected)

    def test_fenix(self):
        import pet_models
        m = pet_models.mascota_fenix()
        for bone in ('body', 'neck', 'head', 'crest', 'wing_l', 'wing_l_tip', 'wing_r', 'wing_r_tip', 'tail', 'tail_2',
                     'tail_3', 'brasas'):
            self.assertIn(bone, m.bones)
        self.assertEqual({'walk', 'idle'} - set(m.anims), set())
        # Un solo par de ojos: dos pupilas en total.
        self.assertEqual(sum(1 for c in m.cubes if c['bone'] == 'head' and c['color'] == '#151822'), 2)
        data = m.export()[0]
        for anim in data['animations']:
            for an in anim['animators'].values():
                for k in an['keyframes']:
                    for v in k['data_points'][0].values():
                        self.assertNotRegex(str(v), r'\.\d{5,}')      # BetterModel no lee decimales largos

    def test_trainx_animaciones(self):
        import inspect
        from mobs import trainx
        src = inspect.getsource(trainx.animations)
        for name in ('idle', 'walk', 'attack', 'combo', 'barrido', 'cast', 'lluvia', 'dash', 'aparece', 'furia', 'death'):
            self.assertIn(f"m.anim('{name}'", src)
        y = trainx.skills_yaml()
        self.assertIn('state{s=aparece}', y)
        self.assertEqual(y.count('state{s=furia}'), 2)
        import yaml
        self.assertEqual(len(yaml.safe_load(y)), 14)


@unittest.skipUnless(FINAL.exists(), 'sin circuito privado')
class Privado(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.z = zipfile.ZipFile(FINAL)
        cls.names = set(cls.z.namelist())

    def modelo_3d(self, iid):
        item = json.loads(self.z.read(f'assets/astral/items/{iid}.json'))['model']
        text = json.dumps(item)
        refs = [r for r in text.split('"') if r.startswith('astral:item/')]
        con_volumen = []
        for ref in refs:
            m = json.loads(self.z.read(f'assets/astral/models/{ref.split(":")[1]}.json'))
            for tex in m.get('textures', {}).values():
                self.assertIn(f'assets/astral/textures/{tex.split(":")[1]}.png', self.names, ref)
            if m.get('elements'):
                con_volumen.append(ref)
        self.assertTrue(con_volumen, iid)
        return item

    def test_mochilas(self):
        for mat in ('leather', 'copper', 'iron', 'gold', 'diamond', 'netherite'):
            self.modelo_3d('mochila_' + mat)
            m = json.loads(self.z.read(f'assets/astral/models/item/mochila_{mat}.json'))
            self.assertGreaterEqual(len(m['elements']), 20)
            self.assertIn('gui', m['display'])

    def test_cuchillos_y_mareas(self):
        for iid in [f'cuchillo_{t}' for t in range(1, 11)] + ['agua_espada', 'agua_hacha', 'agua_pico', 'agua_arco']:
            item = self.modelo_3d(iid)
            self.assertEqual(item['property'], 'minecraft:display_context')      # plano en el inventario
        icono = self.z.read('assets/astral/textures/item/armas_mod/cuchillo_5_icono.png')
        mod = Path('C:/Users/Trainx/Desktop/mods/Revisar/mcdw-9.0.4/assets/mcdw/textures/item/daggers/dagger_void_touched_blade.png')
        if mod.exists():
            from PIL import Image
            import io
            self.assertEqual(Image.open(io.BytesIO(icono)).convert('RGBA').tobytes(), Image.open(mod).convert('RGBA').tobytes())

    def test_final_conserva_base_y_trae_efectos(self):
        delta = json.loads((FINAL.parent / 'delta.json').read_text())
        for n in ('assets/astral/items/fx/rayo.json', 'assets/astral/items/fx/hongo_11.json',
                  'assets/astral/items/fx/onda_2.json', 'assets/bettermodel/items/model/astral_pet_fenix_tail_3.json'):
            self.assertIn(n, self.names)
        from deploy_modelos_efectos import ARTE_FINAL, PROPIOS
        self.assertTrue(all(n.startswith(PROPIOS) or n in ARTE_FINAL for n in delta['publicos']))
        for n in ARTE_FINAL:
            with zipfile.ZipFile(ROOT / 'build/AstralRPG-Textures.zip') as public:
                self.assertEqual(self.z.read(n), public.read(n))


if __name__ == '__main__':
    unittest.main()
