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
        start = skills['TUMBA_SALA3_INICIO']['Skills']
        self.assertLess(start.index('addtag{tag=tumba.espera} @self'), next(i for i,s in enumerate(start) if s.startswith('summon{')))
        self.assertIn('delay 10', start)


if __name__ == "__main__":
    unittest.main()
