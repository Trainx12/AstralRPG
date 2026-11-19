"""Reforja de gemas (7d, 19/11/2026): tabla, ranuras, costos, encantamientos, funciones y Skript."""
import json
import re
import unittest
import zipfile
from pathlib import Path

import economia as E
import gemas as G

ROOT = Path(__file__).resolve().parents[1]


class Tabla(unittest.TestCase):
    def test_siete_gemas_cinco_calidades(self):
        self.assertEqual(len(G.TIPOS), 7)
        self.assertEqual(len(G.todas()), 35)
        self.assertEqual([G.CALIDAD_NOMBRE[q] for q in G.CALIDADES], ['Cruda', 'Pulida', 'Impecable', 'Perfecta', 'Estelar'])

    def test_valores_suben_con_la_calidad(self):
        for v in G.VARIANTES:
            for t in G.TIPOS:
                principal = G.EFECTOS[v][t][0][1]
                self.assertTrue(all(a < b for a, b in zip(principal, principal[1:])), (v, t))
                self.assertTrue(all(x > 0 for x in principal), (v, t))
                for _, vals in G.EFECTOS[v][t][1:]:   # secundarios (los que empiezan en 0): solo Perfecta y Estelar
                    if vals[0] == 0:
                        self.assertEqual(vals[:3], (0, 0, 0), (v, t))
                        self.assertTrue(0 < vals[3] < vals[4], (v, t))
                    else:
                        self.assertTrue(all(a < b for a, b in zip(vals, vals[1:])), (v, t))

    def test_rubi_arma_del_plan(self):
        self.assertEqual(G.EFECTOS['arma']['rubi'][0], ('dano', (4, 7, 11, 16, 22)))

    def test_todos_los_stats_tienen_texto_y_lugar(self):
        for v in G.VARIANTES:
            for t in G.TIPOS:
                for s, _ in G.EFECTOS[v][t]:
                    self.assertIn(s, G.TEXTO)

    def test_ids_no_pisan_otros_items(self):
        from items import MATERIALS
        for t, q in G.todas():
            self.assertNotIn(G.item_id(t, q), MATERIALS)
        self.assertNotIn('gema_umbria', [G.item_id(t, q) for t, q in G.todas()])


class Ranuras(unittest.TestCase):
    def test_por_tier(self):
        self.assertEqual([G.ranuras(t) for t in range(1, 11)], [1, 1, 1, 2, 2, 2, 2, 3, 3, 3])


class Costos(unittest.TestCase):
    def test_extraer_cuesta_mas(self):
        for t in range(1, 11):
            for q in G.CALIDADES:
                self.assertEqual(E.gema_costo(t, q, True), E.gema_costo(t, q) * E.GEMA_EXTRAER_MULT)
                self.assertGreater(E.gema_costo(t, q, True), E.gema_costo(t, q))

    def test_suben_con_tier_y_calidad(self):
        for q in G.CALIDADES:
            c = [E.gema_costo(t, q) for t in range(1, 11)]
            self.assertEqual(c, sorted(c))
        self.assertEqual(E.gema_costo(1, 1), 10_000)
        self.assertEqual(E.gema_costo(10, 5), 52_500_000)

    def test_skript_usa_los_costos(self):
        sk = G.skript()
        for t in range(1, 11):
            for q in G.CALIDADES:
                self.assertIn(f'set {{-agem.poner::{t}::{q}}} to {E.gema_costo(t, q)}', sk)
                self.assertIn(f'set {{-agem.extraer::{t}::{q}}} to {E.gema_costo(t, q, True)}', sk)


class Datapack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.z = zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip')
        cls.names = set(cls.z.namelist())

    def read(self, n):
        return self.z.read(n).decode('utf-8')

    def test_encantamientos(self):
        for t, q in G.todas():
            for v in G.VARIANTES:
                d = json.loads(self.read(f'data/astral/enchantment/{G.ench_id(t, v, q)}.json'))
                self.assertEqual(d['slots'], ['mainhand' if v == 'arma' else 'armor'])
                self.assertEqual(d['max_level'], 1)
                self.assertEqual(d['supported_items'], '#astral:sin_mesa')   # la mesa/yunque no las ofrecen

    def test_efectos_aplicados(self):
        rubi = json.loads(self.read('data/astral/enchantment/gema_rubi_arma_5.json'))['effects']
        self.assertEqual(rubi['minecraft:damage'][0]['effect']['factor'], 1.22)
        self.assertEqual(rubi['minecraft:attributes'][0]['operation'], 'add_multiplied_base')
        jade = json.loads(self.read('data/astral/enchantment/gema_jade_armadura_1.json'))['effects']
        self.assertEqual(jade['minecraft:attributes'][0]['attribute'], 'minecraft:movement_speed')
        # Robo, espinas y dano a jefes los hace AstralGemas: el encantamiento no los repite.
        for e in ('gema_onix_armadura_3', 'gema_onix_arma_2', 'gema_opalo_arma_5'):
            eff = json.loads(self.read(f'data/astral/enchantment/{e}.json'))['effects']
            self.assertNotIn('minecraft:post_attack', eff)
            self.assertNotIn('minecraft:damage' if e != 'gema_opalo_arma_5' else 'x', eff)
        opalo = json.loads(self.read('data/astral/enchantment/gema_opalo_arma_5.json'))['effects']['minecraft:damage']
        self.assertEqual(len(opalo), 1)   # solo el +3% general de Estelar, sin condicion
        self.assertNotIn('requirements', opalo[0])
        # Zafiro y Amatista no tienen efecto vanilla (los pone AstralGemas): no se suman dos veces.
        self.assertNotIn('minecraft:attributes', json.loads(self.read('data/astral/enchantment/gema_amatista_arma_3.json'))['effects'])

    def test_items_de_gema(self):
        for t, q in G.todas():
            loot = self.read(f'data/astral/loot_table/item/{G.item_id(t, q)}.json')
            self.assertIn(f'gema:\\"{t}\\"', loot)
            self.assertIn(f'astral:gemas/{t}_{q}', loot)

    def test_funciones(self):
        for t in G.TIPOS:
            self.assertIn(f'data/astral/function/gemas/quitar/{t}.mcfunction', self.names)
            for q in G.CALIDADES:
                f = self.read(f'data/astral/function/gemas/poner/{t}/{q}.mcfunction')
                self.assertIn(f'tag=asgem.has.{t}] run return 0', f)     # no repetir tipo
                self.assertIn('tag=asgem.lleno] run return 0', f)        # tope de ranuras
        ver = self.read('data/astral/function/gemas/gui/ver.mcfunction')
        for t in range(1, 11):
            self.assertIn(f'tag=asgem.t{t}] run tag @s add asgem.r{G.ranuras(t)}', ver)

    def test_ganchos(self):
        self.assertIn(G.DEFENSA_HOOK, self.read('data/astral/function/player/def.mcfunction'))
        give = self.read('data/astral/function/drop/give.mcfunction')
        self.assertIn('function astral:gemas/suerte', give)
        d = self.read('data/astral/function/player/def.mcfunction').splitlines()
        # despues del Talisman de Roca (no lo multiplica) y antes de guardar astraldef
        self.assertLess(max(i for i, l in enumerate(d) if 'talisman_roca' in l), d.index(G.DEFENSA_HOOK))
        self.assertLess(d.index(G.DEFENSA_HOOK), d.index('scoreboard players operation @s astraldef = #d astral.tmp'))

    def test_atlas_no_se_corre(self):
        icons = json.loads(self.read('data/astral/atlas/iconos.json'))
        self.assertFalse(any(k.startswith('gema_') and k[-1].isdigit() and k.count('_') == 2 for k in icons))


class Skript(unittest.TestCase):
    def test_sin_porcentajes_sueltos(self):
        # En Skript "%" abre una expresion: los textos con % van escritos %%.
        for line in G.skript().splitlines():
            if line.startswith('    set {-agem.efecto::') and ' to "' in line:
                texto = line.split(' to "', 1)[1]
                self.assertNotRegex(texto.replace('%%', ''), '%')

    def test_sin_dupes(self):
        sk = G.skript()
        for ev in ('on inventory close:', 'on quit:', 'on join:', 'on unload:', 'on inventory drag:'):
            self.assertIn(ev, sk)
        self.assertIn('agem_return(player)', sk)

    def test_herrero_tiene_boton(self):
        sk = (ROOT / 'build/services/astral_servicios.sk').read_text(encoding='utf-8')
        self.assertIn('astralreforja %name of player%', sk)
        self.assertIn('astral:servicios/gems_', sk)

    def test_drop_cofre(self):
        sk = (ROOT / 'build/mazmorras/astral_puntaje.sk').read_text(encoding='utf-8')
        self.assertIn('astralgema cofre', sk)
        self.assertEqual(set(G.DROP_COFRE), {'A', 'S'})

    def test_plata_topacio(self):
        sk = (ROOT / 'build/economia/Skript/scripts/astral_economia.sk').read_text(encoding='utf-8')
        self.assertNotIn('function astral:gemas/plata', sk)    # sin comandos por baja (lag)
        self.assertIn('astral.gp%loop-number - 1%', sk)



class Plugin(unittest.TestCase):
    def test_tabla_auraskills(self):
        tab = G.tabla_auraskills()
        self.assertEqual(tab['astral:gema_zafiro_arma_1'], [['max_mana', 'ADD_PERCENT', 4], ['mana_regen', 'ADD_PERCENT', 5]])
        self.assertEqual(tab['astral:gema_amatista_armadura_5'], [['crit_damage', 'ADD', 14], ['crit_chance', 'ADD', 1]])
        self.assertTrue(all(k.split(':')[1].split('_')[1] in ('zafiro', 'amatista') for k in tab))

    def test_tabla_runtime(self):
        r = G.tabla_runtime()
        self.assertEqual(r['robo_prob'], 0.40)
        self.assertEqual(r['efectos']['astral:gema_onix_arma_5']['robo'], 2.5)
        self.assertEqual(r['efectos']['astral:gema_onix_armadura_1']['espinas'], 0.2)
        self.assertEqual(r['efectos']['astral:gema_opalo_arma_3']['dano_jefes'], 15)
        self.assertEqual(r['efectos']['astral:gema_topacio_arma_5']['plata'], 25)
        self.assertEqual(r['efectos']['astral:gema_topacio_armadura_5']['plata'], 3)
        jar = zipfile.ZipFile(ROOT / 'build/gemas/AstralGemas.jar')
        self.assertEqual(json.loads(jar.read('gemas.json')), json.loads(json.dumps(r, sort_keys=True)))
        self.assertIn('softdepend: [MythicMobs]', jar.read('plugin.yml').decode())


class Pack(unittest.TestCase):
    def test_texturas_reemplazables(self):
        files = G.pack_assets()
        for t, q in G.todas():
            self.assertIn(f'assets/astral/textures/item/gemas/{t}_{q}.png', files)
            self.assertTrue((G.TEX / f'{t}_{q}.png').exists())


if __name__ == '__main__':
    unittest.main()
