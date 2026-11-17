"""Regresiones de la tanda: estados, contextos, migracion y preservacion del FINAL."""
import hashlib
import io
import json
import unittest
import zipfile

from PIL import Image

import armas_mod as A
import cascos_planos as C
import varitas3d as V
from deploy_pack_1711 import BASE, BASE_SHA, OUT, ROOT
from pack_audit import audit


def pack(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def refs(tree):
    if isinstance(tree, dict):
        if tree.get('type') == 'minecraft:model':
            yield tree['model']
        for val in tree.values():
            yield from refs(val)
    elif isinstance(tree, list):
        for val in tree:
            yield from refs(val)


class Tanda(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = pack(BASE)
        cls.after = pack(OUT / 'AstralRPG-Textures.zip')
        cls.public = pack(ROOT / 'build/AstralRPG-Textures.zip')
        cls.data = pack(ROOT / 'build/AstralRPG-Items.zip')

    def test_base_y_preservacion(self):
        self.assertEqual(hashlib.sha1(BASE.read_bytes()).hexdigest(), BASE_SHA)
        self.assertFalse(set(self.before) - set(self.after))
        delta = json.loads((OUT / 'delta.json').read_bytes())
        changes = {n for n in self.after if self.after[n] != self.before.get(n)}
        self.assertEqual(changes, set(delta['changed']))
        for n in changes:
            self.assertTrue(n.startswith(('assets/astral/items/', 'assets/astral/models/item/',
                                          'assets/astral/models/servicios/repair_',
                                          'assets/astral/textures/font/servicios/herrero_',
                                          'assets/astral/textures/item/')), n)
        # Guante, mochilas, resto del arte privado, shaders y fuentes deben permanecer identicos.
        for n, blob in self.before.items():
            if any(k in n for k in ('guantes_meteoro', 'mochila', 'bettermodel', '/shaders/', '/font/')):
                if n.startswith('assets/astral/textures/font/servicios/herrero_'):
                    continue
                self.assertEqual(self.after[n], blob, n)

    def test_varita_item_animacion_y_geometria(self):
        loot = json.loads(self.data['data/astral/loot_table/item/varita_curacion.json'])
        self.assertIn('astral:varita_curacion', json.dumps(loot))
        for files in (self.public, self.after):
            self.assertEqual(json.loads(files['assets/astral/items/varita_curacion.json'])['model']['model'],
                             'astral:item/varita_curacion')
            prefix = 'assets/astral/textures/item/varitas/varita_curacion.png'
            im = Image.open(io.BytesIO(files[prefix]))
            self.assertGreater(im.height, im.width)
            self.assertIn('animation', json.loads(files[prefix+'.mcmeta']))
        self.assertFalse(V.check([V.curacion()]))
        # La hendidura del corazon no debe rellenarse con el lobulo perpendicular.
        top = [e for e in V.curacion().els if e['sw'] == 'heart' and e['to'][1] == 21]
        self.assertEqual(len(top), 4)
        self.assertTrue(all(not (e['from'][0] < 8 < e['to'][0]) and
                            not (e['from'][2] < 8 < e['to'][2]) for e in top))

    def test_migracion_puntual(self):
        prefix = 'data/astral/'
        modifier = json.loads(self.data[prefix+'item_modifier/varita_curacion_modelo.json'])
        self.assertEqual(set(modifier['components']), {'minecraft:item_model', 'minecraft:enchantment_glint_override'})
        check = self.data[prefix+'function/upgrade/check.mcfunction'].decode()
        self.assertIn('function astral:upgrade/varita_curacion_modelo', check)
        migration = self.data[prefix+'function/upgrade/varita_curacion_modelo.mcfunction'].decode()
        self.assertNotIn('clear ', migration)
        self.assertIn('container.35', migration)
        self.assertIn('weapon.offhand', migration)
        self.assertIn('id:"varita_curacion"', migration)

    def test_todos_los_cascos_fuera_de_cabeza_planos(self):
        count = 0
        for n, blob in self.after.items():
            iid = n.rsplit('/', 1)[-1][:-5]
            if not (n.startswith('assets/astral/items/') and n.endswith('.json') and
                    (iid.endswith('_helmet') or iid.startswith(('sombrero_', 'casco_')))):
                continue
            count += 1
            tree = json.loads(blob)['model']
            old = json.loads(self.before[n])['model']
            self.assertEqual(C.context(tree, 'head'), C.context(old, 'head'), n)
            for ctx in ('gui', 'ground', 'fixed', 'firstperson_righthand', 'firstperson_lefthand',
                        'thirdperson_righthand', 'thirdperson_lefthand'):
                for ref in refs(C.context(tree, ctx)):
                    model = C.resolve(self.after, ref)
                    self.assertFalse(model.get('elements'), (n, ctx, ref))
                    if not ref.startswith('minecraft:'):
                        self.assertEqual(model['parent'], 'minecraft:item/generated', ref)
        self.assertGreater(count, 60)

    def test_estados_ambas_manos_y_tercera_intacta(self):
        for iid, spec in list(A.ARMAS.items()) + [('agua_arco', ('arco',))]:
            if spec[0] not in ('arco', 'ballesta'):
                continue
            states = ['', '_pulling_0', '_pulling_1', '_pulling_2']
            if spec[0] == 'ballesta':
                states += ['_arrow', '_firework']
            tree = json.loads(self.after[f'assets/astral/items/{iid}.json'])['model']
            for ctx in ('firstperson_righthand', 'firstperson_lefthand'):
                used = set(refs(C.context(tree, ctx)))
                self.assertEqual(used, {f'astral:item/{iid}{s}_primera_persona' for s in states})
                for ref in used:
                    model = C.resolve(self.after, ref)
                    self.assertEqual(model['parent'], 'minecraft:item/generated')
                    self.assertGreaterEqual(model['display'][ctx]['scale'][0], .60)
                    self.assertEqual(model['display'][ctx]['rotation'], A.VANILLA['item/crossbow' if spec[0]=='ballesta' else 'item/bow'][ctx]['rotation'])
            for s in states:
                path = f'assets/astral/models/item/{iid}{s}.json'
                self.assertEqual(json.loads(self.after[path]), json.loads(self.before[path]), path)

    def test_auditoria_y_aislamiento(self):
        self.assertGreater(audit(OUT / 'AstralRPG-Textures.zip'), 0)
        self.assertGreater(audit(ROOT / 'build/AstralRPG-Textures.zip'), 0)
        self.assertFalse(any('/armas_mod/' in n or '/cascos_planos/' in n for n in self.public))
        for family in ('ballestas', 'arcos'):
            self.assertTrue((OUT / f'previews/{family}_primera_persona.png').exists())

    def test_medidas_ambas_manos_todos_estados(self):
        measurements=json.loads((OUT/'previews/primera_persona_medidas.json').read_text())
        self.assertEqual(len(measurements),84)
        self.assertEqual({m['side'] for m in measurements},{'righthand','lefthand'})
        for m in measurements:
            self.assertTrue(.70 <= m['area_ratio'] <= 1.20,m)
            self.assertLessEqual(m['center_distance'],40,m)
            self.assertEqual(m['after'][3],225,m)

    def test_reparar_pack_y_click(self):
        import services as S
        import services_ui as UI
        script=S.script()
        self.assertEqual(S.REPARAR_SLOT,48)
        self.assertIn('if {_slot} is between 48 and 50:',script)
        self.assertNotIn('__REP_',script)
        self.assertNotIn('anvil named',script)
        self.assertEqual(script,(ROOT/'build/services/astral_servicios.sk').read_text(encoding='utf8'))
        self.assertIn('item modify entity @s weapon.mainhand astral:reparar',self.data['data/astral/function/mejora/gui/reparar.mcfunction'].decode())
        ui,_=UI.assets()
        for n,blob in ui.items():
            if '/repair_' in n or n.startswith('assets/astral/textures/font/servicios/herrero_'):
                self.assertEqual(self.after[n],blob,n)
                self.assertEqual(self.public[n],blob,n)
        self.assertTrue({48,49,50}.issubset(UI.USED['herrero']))
        self.assertTrue({48,49,50}.isdisjoint({20,23,24,25,26,39,40,41,45,53}))


if __name__ == '__main__':
    unittest.main()
