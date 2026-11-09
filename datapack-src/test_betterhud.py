"""Pruebas del panel de BetterHud (betterhud.py) y de su lugar en TAB."""
import re
import unittest
from pathlib import Path

import yaml

import betterhud
from lobby import TAB_SECTIONS

OUT = betterhud.OUT


class PanelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        betterhud.main()
        cls.files = {sub: yaml.safe_load((OUT / sub / "astral.yml").read_text(encoding="utf-8"))
                     for sub in ("images", "texts", "layouts", "huds")}

    def test_referencias(self):
        images, texts, layouts, huds = (self.files[k] for k in ("images", "texts", "layouts", "huds"))
        for image in images.values():
            self.assertTrue((OUT / "assets" / image["file"]).exists())
        for layout in huds[betterhud.HUD_ID]["layouts"].values():
            self.assertIn(layout["name"], layouts)
            self.assertEqual((layout["gui"]["x"], layout["gui"]["y"]), (100, 50))
        for layout in layouts.values():
            for entry in layout.get("images", {}).values():
                self.assertIn(entry["name"], images)
            for entry in layout.get("texts", {}).values():
                self.assertIn(entry["name"], texts)

    def test_barras_escapadas_y_minas(self):
        for layout in self.files["layouts"].values():
            for kind in ("images", "texts"):
                for entry in layout.get(kind, {}).values():
                    first = entry["conditions"][1]
                    self.assertEqual((first["first"], first["operation"]), ("world", "!="))
                    self.assertIn(betterhud.MINES_WORLD, first["second"])
                    if kind == "texts":
                        # "/" sola desaparece en BetterHud: tiene que ir doble
                        self.assertNotRegex(entry["pattern"], r"(?<!/)/(?!/)")

    def test_un_valor_por_estado(self):
        texts = self.files["layouts"]["astral_panel_textos"]["texts"].values()
        story = [t for t in texts if "objective_score_aq.state" in str(t["conditions"])]
        self.assertEqual(len(story), len(betterhud.CHAPTERS) + 1)
        daily = [t for t in texts if "aq.done0" in str(t["conditions"])]
        self.assertEqual(len(daily), 8)

    def test_panel_entra_en_pantalla(self):
        self.assertLessEqual(betterhud.H, 200)
        self.assertLessEqual(betterhud.W, 160)

    def test_config(self):
        original = "pack-type: zip\ndefault-hud:\n- test_hud\nmetrics: true\nenable-self-host: false\n"
        result = yaml.safe_load(betterhud.config_yml(original))
        self.assertEqual(result["default-hud"], [betterhud.HUD_ID])
        self.assertEqual(result["pack-type"], "folder")
        self.assertFalse(result["enable-self-host"])

    def test_tab_solo_minas(self):
        board = TAB_SECTIONS.split("\nscoreboard:\n", 1)[1].split("\nconditions:\n", 1)[0]
        self.assertIn("toggle-command: /sbtab", board)
        names = re.findall(r"^    (\w+):$", board, re.M)
        self.assertEqual(names, ["minas"])


if __name__ == "__main__":
    unittest.main()
