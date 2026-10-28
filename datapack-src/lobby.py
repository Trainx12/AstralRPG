# -*- coding: utf-8 -*-
"""
Lobby de AstralRPG (isla de Parrot Spawn, mundo 'lobby' de Multiverse).

Genera en ../build/lobby/:
  Essentials/spawn.yml                    /spawn y reaparicion sin cama -> plaza del lobby
  comandos.txt                            comandos de consola para dejar todo armado

y en ../build/mythicmobs/skills/gachas.yml las 3 gachas, hechas con MythicMobs (cobran con Vault,
sortean rareza y premio, y entregan por comando). Los vendedores son mobs de MythicMobs: NPCS en mobs/mythic.py.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "build", "lobby")
WORLD = "lobby"

# Plaza: el piso del centro esta en y=97, el anillo de edificios en y=99.
SPAWN = (180.5, 98, 190.5, 180)          # x, y, z, yaw (mirando al edificio grande del norte)

# id: (x, y, z, yaw)  -> yaw 0 = sur, 90 = oeste, -90 = este, 180 = norte
NPC_POS = {
    "astral_npc_tienda": (178.5, 100, 166.5, 0),        # edificio grande del norte
    "astral_npc_venta": (158.5, 100, 177.5, -90),       # noroeste
    "astral_npc_gacha_rpg": (195.5, 100, 177.5, 90),    # noreste
    "astral_npc_gacha_monturas": (158.5, 100, 205.5, -90),   # suroeste
    "astral_npc_gacha_cosmeticos": (196.5, 100, 206.5, 90),  # sureste
    "astral_npc_viajero": (180.5, 100, 212.5, 180),     # junto al banco del sur
}

RARITY_WEIGHT = {"common": 60, "uncommon": 25, "rare": 11, "epic": 3.5, "legendary": 0.5}
def loot(item, n=1):
    return [f"loot give %player% loot astral:item/{item}"] * n


def nice(item):
    return item.replace("_", " ").title()


# ------------------------------------------------------------------ gacha RPG (materiales, armas, talismanes)
def rpg_rewards():
    R = []
    common = [("cuero_tratado", 4), ("palo_reforzado", 2), ("fragmento_cristal", 4), ("gema_umbria_fragmentada", 2),
              ("polvo_astral", 2), ("fragmento_umbrio", 3), ("netherita_fundida", 1), ("esencia_nether", 2)]
    for it, n in common:
        R.append(("common", 10, f"{nice(it)} x{n}", loot(it, n)))
    uncommon = [("cristal_arcano", 1), ("gema_umbria", 1), ("esencia_elite", 2), ("nucleo_furia", 1),
                ("fragmento_astral", 3), ("nucleo_eolico", 1), ("madera_estelar", 4), ("shadowsteel", 2)]
    for it, n in uncommon:
        R.append(("uncommon", 10, f"{nice(it)} x{n}", loot(it, n)))
    for t in ("vida", "furia", "roca", "viento"):
        R.append(("uncommon", 6, f"Talisman de {t.title()} I", loot(f"talisman_{t}_1")))
    rare = [("cristal_refinado", 1), ("gema_luminica", 1), ("corazon_shulker", 1), ("alma_corrupta", 1),
            ("netherita_reforzada", 1)]
    for it, n in rare:
        R.append(("rare", 10, f"{nice(it)} x{n}", loot(it, n)))
    for w in ("espada", "baston", "arco", "hacha", "lanza", "guadana"):
        R.append(("rare", 6, f"{nice(w)} II", loot(f"{w}_2")))
        R.append(("rare", 3, f"{nice(w)} III", loot(f"{w}_3")))
    for t in ("vida", "furia", "roca", "viento"):
        R.append(("rare", 5, f"Talisman de {t.title()} II", loot(f"talisman_{t}_2")))
    for it in ("nucleo_astral", "gema_umbria_perfecta", "gema_luminica_perfecta"):
        R.append(("epic", 10, nice(it), loot(it)))
    for w in ("espada", "baston", "arco", "hacha", "lanza", "guadana"):
        R.append(("epic", 6, f"{nice(w)} IV", loot(f"{w}_4")))
    for t in ("vida", "furia", "roca", "viento"):
        R.append(("epic", 5, f"Talisman de {t.title()} III", loot(f"talisman_{t}_3")))
    for w in ("espada", "baston", "arco", "hacha", "lanza", "guadana"):
        R.append(("legendary", 10, f"{nice(w)} V", loot(f"{w}_5")))
    R.append(("legendary", 10, "Chispa Astral x2", loot("chispa_astral", 2)))
    R.append(("legendary", 8, "Nucleo de Furia Pura", loot("nucleo_furia_pura")))
    R.append(("legendary", 6, "Guadana Umbria", loot("guadana_umbria")))
    return R


# ------------------------------------------------------------------ gacha de monturas y mascotas
def mount_rewards():
    def egg(mob, saddle=True):
        c = [f"mm egg give %player% {mob} 1"]
        if saddle:
            c.append("give %player% minecraft:saddle 1")
        return c
    return [
        ("common", 20, "Mascota: Mapache", egg("astral_mapache", False)),
        ("common", 20, "Mascota: Pinguino de Cristal", egg("astral_pinguino", False)),
        ("common", 10, "Montura extra (silla)", ["give %player% minecraft:saddle 2"]),
        ("uncommon", 10, "Montura: Lagarto (nada)", egg("astral_lagarto")),
        ("uncommon", 10, "Montura: Escarabajo Azul", egg("astral_escarabajo")),
        ("rare", 10, "Montura: Grillo Saltarin", egg("astral_grillo")),
        ("rare", 8, "Montura: Chocobo", egg("astral_chocobo")),
        ("epic", 10, "Montura voladora: Gran Ave", egg("astral_ave")),
        ("legendary", 10, "Montura voladora: Pterodactilo", egg("astral_pterodactilo")),
    ]


# ------------------------------------------------------------------ gacha de cosmeticos (titulos y adornos)
TITLES = [
    ("common", "Aventurero", "&7"), ("common", "Explorador", "&a"), ("common", "Lenador", "&6"), ("common", "Minero", "&8"),
    ("uncommon", "Cazador", "&2"), ("uncommon", "Herrero", "&c"), ("uncommon", "Alquimista", "&d"),
    ("rare", "Domador", "&e"), ("rare", "Arcano", "&5"), ("rare", "Berserker", "&4"), ("rare", "Arquero", "&a"),
    ("epic", "Campeon", "&6&l"), ("epic", "Senor del Abismo", "&5&l"),
    ("legendary", "ASTRAL", "&b&l"),
]


def cosmetic_rewards():
    R = []
    for rar, name, col in TITLES:
        R.append((rar, 10, f"Titulo «{name}»", [f'lp user %player% meta setprefix 100 {col}«{name}»']))
    R.append(("common", 8, "Cohetes x16", ["give %player% minecraft:firework_rocket 16"]))
    R.append(("common", 6, "Etiquetas x3", ["give %player% minecraft:name_tag 3"]))
    for t in ("coast", "dune", "wild", "sentry"):
        R.append(("uncommon", 4, f"Molde de adorno: {t}", [f"give %player% minecraft:{t}_armor_trim_smithing_template 1"]))
    for t in ("vex", "tide", "ward", "eye"):
        R.append(("rare", 4, f"Molde de adorno: {t}", [f"give %player% minecraft:{t}_armor_trim_smithing_template 1"]))
    R.append(("epic", 6, "Molde de adorno: silence", ["give %player% minecraft:silence_armor_trim_smithing_template 1"]))
    R.append(("legendary", 6, "Cabeza de Dragon", ["give %player% minecraft:dragon_head 1"]))
    return R


GACHAS = {
    "gacha_rpg": dict(name="<gradient:#B07CFF:#4FD1FF><b>Gacha RPG</b></gradient>", cost=1000,
                      desc=["<gray>Materiales de forja, armas,", "<gray>talismanes y premios legendarios."],
                      rewards=rpg_rewards),
    "gacha_monturas": dict(name="<gradient:#F4D24A:#E07A2A><b>Gacha de Monturas</b></gradient>", cost=2500,
                           desc=["<gray>Monturas y mascotas de AstralRPG.", "<gray>Las monturas traen silla."],
                           rewards=mount_rewards),
    "gacha_cosmeticos": dict(name="<gradient:#FF7BD5:#7EC8FF><b>Gacha de Cosmeticos</b></gradient>", cost=500,
                             desc=["<gray>Titulos para el chat y", "<gray>adornos para tu armadura."],
                             rewards=cosmetic_rewards),
}


def q(s):
    """Texto entre comillas simples para YAML."""
    return "'" + str(s).replace("'", "''") + "'"


RARITY_LABEL = {"common": "&fComun", "uncommon": "&aPoco comun", "rare": "&bRaro", "epic": "&dEpico",
                "legendary": "&6&lLegendario"}
GACHA_LABEL = {"gacha_rpg": "&dGacha RPG", "gacha_monturas": "&eGacha de Monturas", "gacha_cosmeticos": "&bGacha de Cosmeticos"}


def mm_cmd(c):
    """Comando de consola dentro de un skill de MythicMobs."""
    return "command{c=\"" + c.replace("%player%", "<trigger.name>") + "\"} @self"


def gacha_skills():
    """Gachas hechas con MythicMobs: cobra con Vault, sortea la rareza, despues el premio, y lo entrega por comando."""
    L = ["# Gachas del lobby (generado por datapack-src/lobby.py)", ""]
    for gid, g in GACHAS.items():
        G = gid.upper()
        cost = g["cost"]
        rewards = g["rewards"]()
        by_rar = {}
        for i, r in enumerate(rewards):
            by_rar.setdefault(r[0], []).append((i, r))
        # tirada
        L += [f"AST_{G}:", "  Cooldown: 1", "  Skills:",
              f"  - {q(f'currencytake{{a={cost}}} @trigger')}",
              f"  - {q('sound{s=block.amethyst_block.chime;p=1.2} @trigger')}",
              f"  - {q('particles{p=end_rod;a=25;hs=0.4;vs=0.6;s=0.05;y=1} @self')}",
              "  - " + q("randomskill{skills=" + ",".join(f"AST_{G}_{rar.upper()} {RARITY_WEIGHT[rar]}" for rar in by_rar) + "} @trigger"),
              ""]
        # info (shift + clic)
        odds = ", ".join(f"{RARITY_LABEL[r]} &7{RARITY_WEIGHT[r]}%" for r in by_rar)
        L += [f"AST_{G}_INFO:", "  Skills:",
              f"  - {q('message{m="' + GACHA_LABEL[gid] + ' &7- cada tirada cuesta &e' + str(cost) + '$"} @trigger')}",
              f"  - {q('message{m="&7Probabilidades &8- ' + odds + '"} @trigger')}"]
        for rar, lst in by_rar.items():
            names = ", ".join(r[2] for _, r in lst[:6]) + (" ..." if len(lst) > 6 else "")
            L.append(f"  - {q('message{m="' + RARITY_LABEL[rar] + ' &8- &7' + names + '"} @trigger')}")
        L.append("")
        # rareza -> premio
        for rar, lst in by_rar.items():
            L += [f"AST_{G}_{rar.upper()}:", "  Skills:",
                  "  - " + q("randomskill{skills=" + ",".join(f"AST_{G}_R{i:02d} {r[1]}" for i, r in lst) + "} @trigger"), ""]
        for i, (rar, w, name, cmds) in enumerate(rewards):
            L += [f"AST_{G}_R{i:02d}:", "  Skills:"]
            L += [f"  - {q(mm_cmd(c))}" for c in cmds]
            L.append(f"  - {q('message{m="' + GACHA_LABEL[gid] + ' &8- ' + RARITY_LABEL[rar] + '&8: &f' + name + '"} @trigger')}")
            if rar in ("epic", "legendary"):
                L.append(f"  - {q('message{m="&6&l(!) &e<trigger.name> &7saco ' + RARITY_LABEL[rar] + ' &7en la ' + GACHA_LABEL[gid] + '&7: &f' + name + '"} @Server')}")
                L.append(f"  - {q('sound{s=ui.toast.challenge_complete} @trigger')}")
            L.append("")
    return "\n".join(L) + "\n"


def spawn_yml():
    x, y, z, yaw = SPAWN
    return "\n".join(["spawns:", "  default:", f"    world-name: {WORLD}", f"    world: {WORLD}",
                      f"    x: {x}", f"    y: {float(y)}", f"    z: {z}", f"    yaw: {float(yaw)}", "    pitch: 0.0"]) + "\n"


def commands():
    x, y, z, yaw = SPAWN
    C = ["# Comandos de consola (sin /) para dejar armado el lobby. Se pueden repetir sin problema.",
         "# El mundo se crea una sola vez con:",
         f"#   mv create {WORLD} normal --world-type FLAT --no-structures --no-adjust-spawn "
         "--generator-settings {\"layers\":[{\"block\":\"minecraft:air\",\"height\":1}],\"biome\":\"minecraft:the_void\"}",
         f"#   y despues se reemplaza world/dimensions/minecraft/{WORLD}/region/r.0.0.mca por el de la isla (con el server apagado).",
         "# --- mundo lobby: sin mobs, sin hambre, protegido",
         f"mvsetspawn {WORLD}:{x},{y},{z},{yaw},0",
         f"mv modify {WORLD} set difficulty peaceful",
         f"mv modify {WORLD} set pvp false",
         f"mv modify {WORLD} set hunger false",
         f"mv modify {WORLD} set gamemode adventure",
         f"mv modify {WORLD} set allow-weather false",
         f"mv gamerule set minecraft:advance_time false {WORLD}",
         f"mv gamerule set minecraft:spawn_mobs false {WORLD}",
         f"execute in minecraft:{WORLD} run minecraft:time set noon",
         f"execute in minecraft:{WORLD} run worldborder center 178 192",
         f"execute in minecraft:{WORLD} run worldborder set 190",
         f"rg flag -w {WORLD} __global__ build deny",
         f"rg flag -w {WORLD} __global__ pvp deny",
         f"rg flag -w {WORLD} __global__ mob-spawning deny",
         f"rg flag -w {WORLD} __global__ fall-damage deny",
         f"rg flag -w {WORLD} __global__ invincible allow",
         f"rg flag -w {WORLD} __global__ item-drop deny",
         f"rg flag -w {WORLD} __global__ interact allow",
         f"rg flag -w {WORLD} __global__ chest-access deny",
         "# --- primera vez que entra alguien: aparece en el lobby",
         "mv config first-spawn-override true",
         f"mv config first-spawn-location {WORLD}",
         "mv config enforce-respawn-at-world-spawn false",
         "# --- titulos de la gacha en el chat (%luckperms_prefix%)",
         "papi ecloud download LuckPerms",
         "papi reload",
         "# --- permisos de jugador",
         "lp group default permission set essentials.spawn true",
         "lp group default permission set essentials.balance true",
         "lp group default permission set essentials.balancetop true",
         "lp group default permission set essentials.pay true",
         "lp group default permission set essentials.worth true",
         "lp group default permission set essentials.help true",
         "# --- vendedores (MythicMobs). WorldGuard no deja aparecer mobs en el lobby: se habilita un momento",
         f"rg flag -w {WORLD} __global__ mob-spawning allow"]
    for mid, (nx, ny, nz, nyaw) in NPC_POS.items():
        C.append(f"mm mobs spawn {mid} 1 {WORLD},{nx},{ny},{nz},{nyaw},0")
    C.append(f"rg flag -w {WORLD} __global__ mob-spawning deny")
    return "\n".join(C) + "\n"


def main():
    os.makedirs(os.path.join(OUT, "Essentials"), exist_ok=True)
    mm = os.path.join(HERE, "..", "build", "mythicmobs", "skills")
    os.makedirs(mm, exist_ok=True)
    with open(os.path.join(mm, "gachas.yml"), "w", encoding="utf-8") as f:
        f.write(gacha_skills())
    with open(os.path.join(OUT, "Essentials", "spawn.yml"), "w", encoding="utf-8") as f:
        f.write(spawn_yml())
    with open(os.path.join(OUT, "comandos.txt"), "w", encoding="utf-8") as f:
        f.write(commands())
    n = sum(len(g["rewards"]()) for g in GACHAS.values())
    print(f"lobby: {len(GACHAS)} gachas ({n} premios), {len(NPC_POS)} vendedores -> {os.path.abspath(OUT)}")


if __name__ == "__main__":
    main()
