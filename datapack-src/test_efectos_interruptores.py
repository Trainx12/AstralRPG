"""Contrato de configuracion, comandos y filtrado por espectador."""
from pathlib import Path
import unittest
import zipfile
import yaml
from menus import configuraciones_menu, EFECTOS_CATEGORIAS
from efectos import PLUGIN_YML

ROOT = Path(__file__).resolve().parents[1]


class Interruptores(unittest.TestCase):
    def test_menu_estados_y_actualizacion(self):
        menu = yaml.safe_load(configuraciones_menu())
        self.assertEqual(menu['size'], 45)
        self.assertEqual(menu['update_interval'], 1)
        self.assertEqual(menu['items']['volver']['slot'], 40)
        self.assertNotIn('\uf100', menu['menu_title'])  # fondo generico, sin pack nuevo
        for slot, (clave, objetivo, _, _) in enumerate(EFECTOS_CATEGORIAS, 29):
            for estado in ('true', 'false'):
                item = menu['items'][f'interruptor_{clave}_{estado}']
                self.assertEqual(item['slot'], slot)
                self.assertIn(estado.upper(), item['display_name'])
                self.assertTrue(item['update'])
                self.assertEqual(item['material'], 'LIME_DYE' if estado == 'true' else 'GRAY_DYE')
                self.assertEqual(item['click_commands'], [f'[player] efectos {clave} {"off" if estado == "true" else "on"}', '[refresh]'])
                if estado == 'false':
                    req = item['view_requirement']['requirements']['activo']
                    self.assertEqual(req, {'type': '==', 'input': f'%objective_score_{{astral.fx.{objetivo}}}%', 'output': '0'})
                else:
                    self.assertNotIn('view_requirement', item)
        self.assertEqual(sum(k.startswith('interruptor_') for k in menu['items']), 10)
        for n, nivel in enumerate(('bajo', 'medio', 'alto')):
            item = menu['items'][f'efectos_{nivel}_activo']
            self.assertEqual(item['view_requirement']['requirements']['activo']['output'], str(n))
            self.assertIn('[refresh]', item['click_commands'])

    def test_jar_comandos_y_categorias(self):
        java = (ROOT/'datapack-src/runtime/AstralEfectos.java').read_text('utf8')
        with zipfile.ZipFile(ROOT/'build/runtime/AstralEfectos.jar') as z:
            self.assertEqual(z.read('plugin.yml').decode(), PLUGIN_YML)
            self.assertIn('astral/AstralEfectos$Categoria.class', z.namelist())
        for clave, obj, _, _ in EFECTOS_CATEGORIAS:
            self.assertIn(f'"{clave}"', java)
            self.assertIn(clave, PLUGIN_YML)
        self.assertIn('return List.of("on", "off")', java)
        self.assertIn('if (!score.isScoreSet()) score.setScore(1)', java)
        for method in ('fx', 'particula', 'hayVisor', 'hayVisorExacto', 'incendio', 'elemento'):
            self.assertIn(f'{method}(Categoria categoria,', java)
        self.assertIn('origen.setYaw(0); origen.setPitch(0)', java)
        self.assertIn('spawn(origen, ItemDisplay.class', java)
        self.assertIn('ojos.getWorld().rayTrace(ojos, dir, 25', java)
        self.assertIn('multiply(0.36)', java)

    def test_datapack_solo_filtra_particulas_nuevas_de_bastones(self):
        with zipfile.ZipFile(ROOT/'build/AstralRPG-Items.zip') as z:
            for nombre in ('ray', 'hit', 'pared'):
                text = z.read(f'data/astral/function/spell/{nombre}.mcfunction').decode()
                for linea in text.splitlines():
                    if 'particle minecraft:' in linea:
                        if '$(fxp)' in linea:
                            self.assertIn('astral.fx.bastones=1..', linea)
                        else:
                            self.assertNotIn('astral.fx', linea)
                            self.assertNotIn('@a', linea)
            for nombre in ('fx_perfora', 'hit', 'pared'):
                self.assertIn('astral.fx.bastones=1..', z.read(f'data/astral/function/spell/{nombre}.mcfunction').decode())

    def test_menu_aclara_que_solo_apaga_efectos_nuevos(self):
        text = configuraciones_menu()
        self.assertIn('Solo apagan efectos nuevos.', text)
        self.assertIn('Las particulas de siempre siguen visibles.', text)


if __name__ == '__main__':
    unittest.main()
