"""Nucleo privado: item sin arte y receta reservada, desactivada por defecto."""
import json
from pathlib import Path

# No registrar en RECIPES: eso habilitaria la Forja y lo publicaria en la Guia.
# Al abrirlo, integrar esta receta al sistema Astral en una tarea de publicacion.
RECIPE = ("autoventa", 1, [
    ("c", "cristal_refinado", 16),
    ("v", "minecraft:netherite_block", 64),
    ("v", "minecraft:diamond_block", 64),
    ("c", "esencia_nether", 16),
    ("v", "minecraft:nether_star", 2),
    ("v", "minecraft:emerald_block", 32),
    ("v", "minecraft:ender_eye", 16),
    ("c", "netherita_reforzada", 16),
    ("c", "nucleo_furia", 16),
], "Minas")


def register(add_item, txt, aura_pdc, req_line, fn):
    add_item("autoventa", "minecraft:heart_of_the_sea", "Nucleo de Venta Automatica", "gold",
             [txt("Cuando se te llena el inventario en las Minas Astrales,"),
              txt("vende solo tus minerales al precio de la Venta rapida."),
              txt("Funciona llevandolo en el inventario."),
              txt("El equipo y los objetos con nombre no se venden."),
              req_line("mining", 100)], {"type": "utility"},
             extra={"minecraft:max_stack_size": 1},
             pdc=aura_pdc("item", "mining", 100), glint=True)
    pred = '*[minecraft:custom_data~{astral:{id:"autoventa"}}]'
    fn("autoventa/identify", [
        "tag @s remove astral.autoventa",
        *[f"execute if items entity @s {slot} {pred} run tag @s add astral.autoventa"
          for slot in ("hotbar.*", "inventory.*", "weapon.offhand")]])
    target = Path(__file__).resolve().parents[1] / "build/autoventa/receta-desactivada.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(dict(out=RECIPE[0], count=1, ingredients=RECIPE[2],
                                     group=RECIPE[3], enabled=False), indent=2) + "\n", encoding="utf8", newline="\n")
