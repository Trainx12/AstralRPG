"""Verifica el YAML que ejecutara MythicMobs, incluidas las llamadas de refuerzos."""
from collections import Counter
import math
import re
import unittest

import yaml
from mobs.mazmorras_data import catalog
from mobs.mazmorra import commands, mob_yml, skill_yml


class TumbaSala2Tests(unittest.TestCase):
    room_index = 1
    prefix = "astral_tumba_s2_"

    def setUp(self):
        self.dungeon = next(d for d in catalog() if d["key"] == "tumba")
        self.room = self.dungeon["rooms"][self.room_index]
        self.skills = yaml.safe_load(skill_yml(self.dungeon))
        self.mobs = yaml.safe_load(mob_yml(self.dungeon))

    def simulate_wave(self, wave, players):
        """Interpreta condiciones, contador, summons y llamadas del YAML generado.

        La eleccion aleatoria solo cambia la posicion: todas las ramas invocan
        exactamente el mismo mob. No simula combate ni sustituye una prueba en Paper.
        """
        counts, points = Counter(), []
        score = 0

        def execute(name):
            nonlocal score
            skill = self.skills[name]
            for condition in skill.get("Conditions", []):
                match = re.fullmatch(r"score\{o=ad.party;v=>(\d+)\} true", condition)
                self.assertIsNotNone(match, condition)
                if score <= int(match[1]):
                    return
            for line in skill["Skills"]:
                if line.startswith("command{"):
                    if "store result score" in line:
                        self.assertIn("gamemode=!spectator", line)
                        score = players
                    elif "scoreboard players remove" in line:
                        score -= int(re.search(r"ad.party (\d+)", line)[1])
                elif line.startswith("summon{"):
                    mob, amount = re.search(r"type=([^;]+);amount=(\d+)", line).groups()
                    self.assertIn(mob, self.mobs)
                    counts[mob.removeprefix(self.prefix)] += int(amount)
                    location = re.search(r"@Location\{x=([^;]+);y=([^;]+);z=([^}]+)\}", line)
                    self.assertIsNotNone(location, line)
                    points.append((mob, tuple(map(float, location.groups()))))
                elif line.startswith("skill{"):
                    execute(re.search(r"s=([^}]+)", line)[1])
                elif line.startswith("randomskill{"):
                    execute(re.search(r"skills=([^,}]+)", line)[1])

        execute("TUMBA_" + self.room["id"].upper() + "_" + ("INICIO" if wave == 1 else f"OLA{wave}"))
        return counts, points

    def test_quantities_and_scaling_from_generated_skills(self):
        for players in range(1, 21):
            extra = max(0, players - 2)
            expected = [dict(arana=5, momia=5 + 3 * extra, esqueleto=4, cara=2, espantapajaros=1),
                        dict(arana=7, momia=6, esqueleto=5 + 4 * extra),
                        dict(golem=2 + extra // 2)]
            for wave, counts in enumerate(expected, 1):
                with self.subTest(players=players, wave=wave):
                    self.assertEqual(self.simulate_wave(wave, players)[0], counts)

    def test_every_spawn_branch_inside_selection(self):
        low, high = self.room["spawn_bounds"]
        for skill in self.skills.values():
            for line in skill.get("Skills", []):
                if not line.startswith("summon{type=" + self.prefix):
                    continue
                coords = tuple(map(float, re.search(r"@Location\{x=([^;]+);y=([^;]+);z=([^}]+)\}", line).groups()))
                self.assertTrue(all(a <= value <= b + 1 for a, value, b in zip(low, coords, high)))
                self.assertIn("radius=0", line)
                if "type=astral_tumba_s2_golem;" in line:
                    self.assertIn(coords, self.room["golem_points"])

    def test_activation_progression_and_models(self):
        self.assertLess(math.dist(self.room["centro"], self.room["llegada"]), self.room["r"])
        control = self.mobs["astral_tumba_control_sala2"]["Skills"]
        for mob in self.dungeon["mobs"]:
            if mob.startswith(self.prefix):
                self.assertTrue(any(mob in line and "LIMPIA" in line for line in control))
        self.assertTrue(any("OLA3" in line and "ola2" in line for line in control))
        for mob in ("cara", "espantapajaros"):
            self.assertIn(f"TUMBA_MODELO_astral_tumba_s2_{mob}", self.skills)
        golem = self.mobs["astral_tumba_s2_golem"]
        self.assertIn("players", golem["AITargetSelectors"])
        self.assertIn("meleeattack", golem["AIGoalSelectors"])
        self.assertEqual(self.mobs["astral_tumba_s2_arana"]["Type"], "CAVE_SPIDER")
        self.assertNotIn("BossBar", self.mobs["astral_tumba_s2_momia"])
        self.assertEqual(self.dungeon["rooms"][2]["centro"], (0.568, 72, 0.512))
        self.assertIn("scoreboard objectives add ad.party dummy", commands(self.dungeon))

    def test_other_dungeons_do_not_use_new_scaling(self):
        for dungeon in catalog():
            if dungeon["key"] != "tumba":
                self.assertNotIn("ad.party", skill_yml(dungeon))
                self.assertNotIn("astral_tumba_s2_", mob_yml(dungeon))


class TumbaSala1Tests(TumbaSala2Tests):
    room_index = 0
    prefix = "astral_tumba_s1_"

    def test_quantities_and_scaling_from_generated_skills(self):
        for players in range(1, 21):
            extra = max(0, players - 2)
            for wave, expected in enumerate([
                dict(arana=3, momia=3 + 3 * extra, esqueleto=2, cara=1),
                dict(arana=4, momia=3, esqueleto=3 + 4 * extra)], 1):
                with self.subTest(players=players, wave=wave):
                    self.assertEqual(self.simulate_wave(wave, players)[0], expected)

    def test_activation_progression_and_models(self):
        self.assertEqual(self.room["llegada"], (-148.426, 62, -97.473))
        self.assertLess(math.dist(self.room["centro"], self.room["llegada"]), self.room["r"])
        self.assertIn("-148.426 62 -97.473", self.skills["TUMBA_ENTRAR"]["Skills"][1])
        control = self.mobs["astral_tumba_control_sala1"]["Skills"]
        self.assertTrue(any("OLA2" in line and "ola1" in line for line in control))
        self.assertTrue(any("LIMPIA" in line and "ola2" in line for line in control))
        self.assertIn("TUMBA_MODELO_astral_tumba_s1_cara", self.skills)
        for mob in self.dungeon["mobs"]:
            if mob.startswith(self.prefix):
                self.assertTrue(any(mob in line and "LIMPIA" in line for line in control))


class TumbaBossVictoryTests(unittest.TestCase):
    def test_absence_or_despawn_cannot_complete_boss_room(self):
        dungeon = next(d for d in catalog() if d['key'] == 'tumba')
        skills = yaml.safe_load(skill_yml(dungeon))
        mobs = yaml.safe_load(mob_yml(dungeon))
        victory = skills['TUMBA_SALA3_LIMPIA']['Conditions']
        self.assertIn('hastag{tag=tumba.jefe.derrotado} true', victory)
        self.assertIn('hastag{tag=tumba.fin} false', victory)
        timer = next(s for s in mobs['astral_tumba_control_sala3']['Skills'] if 'LIMPIA' in s)
        self.assertIn('?hastag{tag=tumba.jefe.derrotado}', timer)
        # Los husks que invoca el jefe (o los del desierto) no pueden trabar el final.
        self.assertNotIn('mobsinradius', timer)
        aviso = next(s for s in mobs['astral_tumba_momia']['Skills'] if 'tumba.jefe.derrotado' in s)
        self.assertTrue(aviso.startswith('command{') and aviso.endswith('~onDeath'))
        # El comando busca al control por su nombre visible: tienen que coincidir.
        self.assertIn("name='" + mobs['astral_tumba_control_sala3']['Display'] + "'", aviso)
        self.assertTrue(any(s.startswith('remove @MobsInRadius') for s in skills['TUMBA_SALA3_LIMPIA']['Skills']))
        for state in ('INICIO', 'RESET'):
            self.assertIn('removetag{tag=tumba.jefe.derrotado} @self', skills['TUMBA_SALA3_' + state]['Skills'])
        # Al ganar no se teletransporta: aparecen el cofre y el guia de Expediciones.
        fin = skills['TUMBA_SALA3_LIMPIA']['Skills']
        self.assertFalse(any('spawn <target.name>' in s for s in fin))
        self.assertTrue(any(s.startswith('summon{type=astral_tumba_cofre') for s in fin))
        self.assertTrue(any(s.startswith('summon{type=astral_tumba_guia') for s in fin))
        cofre = mobs['astral_tumba_cofre']['Skills']
        self.assertIn('command{c="dm open cofre_tumba <trigger.name>"} @self ~onInteract', cofre)
        self.assertIn('command{c="dm open expediciones <trigger.name>"} @self ~onInteract', mobs['astral_tumba_guia']['Skills'])
        self.assertIn('astral_tumba_cofre', skills['TUMBA_SALA3_RESET']['Skills'][0])
        start = skills['TUMBA_SALA3_INICIO']['Skills']
        self.assertLess(start.index('addtag{tag=tumba.espera} @self'), next(i for i,s in enumerate(start) if s.startswith('summon{')))
        self.assertIn('delay 10', start)



class EsperaCofreTests(unittest.TestCase):
    """Sin el false explicito, el cofre le dice 'ya cobraste' a los OP."""

    def test_every_dungeon_sets_cooldown_false_for_default_group(self):
        for dungeon in [None] + catalog():
            key = dungeon["key"] if dungeon else "mina"
            self.assertIn(f"lp group default permission set astral.{key}.cd false", commands(dungeon))


class CofreMenuTests(unittest.TestCase):
    """El cofre abre su ventana; el fragmento se guarda solo la primera vez."""

    def test_every_dungeon_spawns_a_chest_that_opens_its_window(self):
        for dungeon in [None] + catalog():
            key = dungeon["key"] if dungeon else "mina"
            mobs = yaml.safe_load(mob_yml(dungeon))
            skills = yaml.safe_load(skill_yml(dungeon))
            P = key.upper()
            self.assertIn(f'command{{c="dm open cofre_{key} <trigger.name>"}} @self ~onInteract',
                          mobs[f"astral_{key}_cofre"]["Skills"])
            final = [k for k in skills if k.endswith("_LIMPIA")][-1]
            fin = skills[final]["Skills"]
            self.assertTrue(any(s.startswith(f"summon{{type=astral_{key}_cofre") for s in fin))
            self.assertFalse(any("spawn <target.name>" in s for s in fin))
            self.assertFalse(any(f"{P}_PREMIO}}" in s for s in fin))

    def test_window_gives_fragment_only_first_time(self):
        from cofre_mazmorra import cofre_menu, PREMIOS, permiso, espera
        for dungeon in [None] + catalog():
            from mobs.mazmorra import MINA
            dungeon = dungeon or MINA
            key = dungeon["key"]
            frag = PREMIOS[key][0]
            items = cofre_menu(dungeon)["items"]
            primera, despues = items["reclamar_0"], items["reclamar_ya_0"]
            set_frag = f"[console] lp user %player_name% permission set {permiso(frag)} true"
            self.assertIn(set_frag, primera["click_commands"])
            self.assertNotIn(set_frag, despues["click_commands"])
            self.assertEqual(primera["view_requirement"]["requirements"]["r"]["type"], "!has permission")
            self.assertLess(primera["priority"], despues["priority"])
            for boton in (primera, despues):
                self.assertEqual(boton["click_commands"][0], "[close]")
                self.assertEqual(boton["click_requirement"]["requirements"]["libre"]["permission"], espera(key))
                self.assertTrue(any(f"settemp {espera(key)} true 30m" in c for c in boton["click_commands"]))
            self.assertIn("&7Solo se puede reclamar la primera vez.", items["fragmento_apagado"]["lore"])

    def test_collection_permissions_default_to_false(self):
        from cofre_mazmorra import FRAGMENTOS
        texto = commands()
        for frag, *_ in FRAGMENTOS:
            self.assertIn(f"lp group default permission set astral.fragmento.{frag} false", texto)


if __name__ == "__main__":
    unittest.main()
