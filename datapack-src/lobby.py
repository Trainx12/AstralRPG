# -*- coding: utf-8 -*-
"""
Lobby de AstralRPG (isla de Parrot Spawn, mundo 'lobby' de Multiverse).

Genera en ../build/lobby/:
  Essentials/spawn.yml                    /spawn y reaparicion sin cama -> plaza del lobby
  comandos.txt                            comandos de consola para dejar todo armado

  CrazyCrates/crates/<gacha>.yml         las 3 gachas: ruleta tipo CS:GO con los premios girando
y en ../build/mythicmobs/skills/gachas.yml lo que hace el vendedor: cobra con Vault y abre la ruleta
('crates forceopen'). Shift + clic abre la vitrina de premios. Vendedores: NPCS en mobs/mythic.py.
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
# Pity (garantia): cada tirada suma 1 al contador del jugador (scoreboard 'pity_<gacha>').
# Al llegar al numero, esa tirada sale de la caja "<gacha>_garantia" (solo Epico o Legendario).
# Sacar Epico o Legendario (con o sin garantia) vuelve el contador a 0.
PITY = {"gacha_rpg": 30, "gacha_monturas": 20, "gacha_cosmeticos": 30}
PITY_RARITIES = ("epic", "legendary")


def pity_obj(gid):
    return "pity_" + gid.replace("gacha_", "")
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


RARITY_MINI = {"common": "<white>Comun", "uncommon": "<green>Poco comun", "rare": "<aqua>Raro",
               "epic": "<light_purple>Epico", "legendary": "<gold><bold>Legendario"}
RARITY_AMP = {"common": "&fComun", "uncommon": "&aPoco comun", "rare": "&bRaro", "epic": "&dEpico",
              "legendary": "&6&lLegendario"}
GACHA_MINI = {"gacha_rpg": "<light_purple><bold>Gacha RPG", "gacha_monturas": "<yellow><bold>Gacha de Monturas",
              "gacha_cosmeticos": "<aqua><bold>Gacha de Cosmeticos"}
GACHA_AMP = {"gacha_rpg": "&dGacha RPG", "gacha_monturas": "&eGacha de Monturas", "gacha_cosmeticos": "&bGacha de Cosmeticos"}
GACHA_FRAME = {"gacha_rpg": ("purple_stained_glass_pane", "amethyst_shard"),
               "gacha_monturas": ("yellow_stained_glass_pane", "saddle"),
               "gacha_cosmeticos": ("light_blue_stained_glass_pane", "name_tag")}
EGG_ICON = {"astral_mapache": "fox_spawn_egg", "astral_pinguino": "chicken_spawn_egg", "astral_lagarto": "frog_spawn_egg",
            "astral_escarabajo": "endermite_spawn_egg", "astral_grillo": "silverfish_spawn_egg",
            "astral_chocobo": "camel_spawn_egg", "astral_ave": "parrot_spawn_egg", "astral_pterodactilo": "phantom_spawn_egg"}


def icon(cmds):
    """(material, modelo astral o None, cantidad) que se muestra en la ruleta."""
    c0 = cmds[0]
    if "loot astral:item/" in c0:
        return "paper", c0.split("astral:item/")[1], len(cmds)
    if c0.startswith("mm egg give"):
        return EGG_ICON.get(c0.split()[4], "egg"), None, 1
    if c0.startswith("give "):
        p = c0.split()
        return p[2].replace("minecraft:", ""), None, int(p[3]) if len(p) > 3 else 1
    return "name_tag", None, 1


def dq(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def crate_yml(gid, g, garantia=False):
    """Caja de CrazyCrates tipo CSGO: la ruleta gira en un inventario y frena en el premio.
    garantia=True: misma caja pero solo con Epicos y Legendarios (la tirada garantizada del pity)."""
    rewards = g["rewards"]()
    if garantia:
        rewards = [r for r in rewards if r[0] in PITY_RARITIES]
    scale = 100 / sum(RARITY_WEIGHT[r] for r in PITY_RARITIES) if garantia else 1
    tot = {}
    for rar, w, _, _ in rewards:
        tot[rar] = tot.get(rar, 0) + w
    glass, frame = GACHA_FRAME[gid]
    L = ["# " + gid + " (generado por datapack-src/lobby.py). Lo abre el vendedor del lobby con 'crates forceopen'.",
         "Crate:", "  CrateType: CSGO", "  StartingKeys: 0", "  RequiredKeys: 0", "  Max-Mass-Open: 1",
         "  InGUI: false", "  Slot: 0", "  OpeningBroadCast: false", "  BroadCast: " + dq(""),
         "  opening-command:", "    toggle: false", "    commands: []",
         "  sound:",
         "    cycle-sound:", "      toggle: true", "      value: " + dq("block.note_block.pling"), "      volume: 0.6", "      pitch: 1.4",
         "    click-sound:", "      toggle: true", "      value: " + dq("ui.button.click"), "      volume: 1.0", "      pitch: 1.0",
         "    stop-sound:", "      toggle: true", "      value: " + dq("ui.toast.challenge_complete"), "      volume: 1.0", "      pitch: 1.0",
         "  Prize-Message:", "    - " + dq("<gray>Ganaste <white>%reward% <gray>en la " + GACHA_MINI[gid] + "<gray>!"),
         "  Prize-Commands: []",
         "  Settings:", "    Tracking-Crate-Opening: false", "    Knock-Back: false", "    Disabled-Worlds: []",
         "    Border:", "      Glass-Border:", "        Toggle: true", "        Air: true",
         "    CSGO:", "      Finished-Material: " + dq(frame), "      Cycle-Material: " + dq(frame),
         "    Broadcast:", "      Toggle: false", "      Messages: []", "      Permission: " + dq(""),
         "    Rewards:", "      Re-Roll-Spin: false", "      Permission:", "        Toggle: false", "        Persist: false",
         "        Max-Cap: 20",
         "  Item: " + dq(frame), "  Hide-Flags: false", "  Components: []", "  Custom-Model-Data: -1",
         "  Model:", "    Namespace: " + dq(""), "    Id: " + dq(""), "  Glowing: " + dq("add_glow"),
         "  Name: " + dq(GACHA_MINI[gid]), "  Lore:", "    - " + dq("<gray>Tirada: <yellow>" + str(g["cost"]) + "$"),
         "  Preview:", "    Name: " + dq(GACHA_MINI[gid] + "<reset><gray> - premios"), "    Toggle: true", "    Rows: 6",
         "    Glass:", "      Toggle: true", "      Name: " + dq(" "), "      Item: " + dq(glass), "      Custom-Model-Data: -1",
         "      Model:", "        Namespace: " + dq(""), "        Id: " + dq(""),
         "  Animation:", "    Name: " + dq(GACHA_MINI[gid] + "<reset><gray> - girando..."),
         "    Glass-Frame:", "      Toggle: true", "      Items:",
         "        \"1\":", "          name: " + dq(" "), "          lore: []", "          material: " + dq(glass), "          amount: 1",
         "      Random:", "        Toggle: true", "        Items: {}",
         "  PhysicalKey:", "    Name: " + dq(GACHA_MINI[gid] + " - llave"), "    Lore: []", "    Item: " + dq("tripwire_hook"),
         "    Custom-Model-Data: -1", "    Model:", "      Namespace: " + dq(""), "      Id: " + dq(""),
         "    Glowing: " + dq("add_glow"), "    flags:", "      components: []",
         "  Hologram:", "    Toggle: false", "    Height: 1.5", "    Range: 8", "    Update-Interval: -1",
         "    Color: " + dq("transparent"), "    TextShadow: false", "    Message: []",
         "  buttons: {}",
         "  Prizes:"]
    order = ["legendary", "epic", "rare", "uncommon", "common"]      # la vitrina arranca por lo mas raro
    stars = {"legendary": 5, "epic": 4, "rare": 3, "uncommon": 2, "common": 1}
    color = {"legendary": "<gold>", "epic": "<light_purple>", "rare": "<aqua>", "uncommon": "<green>", "common": "<white>"}
    ranked = sorted(rewards, key=lambda r: order.index(r[0]))
    for i, (rar, w, name, cmds) in enumerate(ranked):
        mat, model, amount = icon(cmds)
        weight = round(RARITY_WEIGHT[rar] * w / tot[rar] * scale, 4)
        cm = list(cmds)
        if rar in PITY_RARITIES:
            cm.append(f"scoreboard players set %player% {pity_obj(gid)} 0")
        if rar in ("epic", "legendary"):
            cm.append("broadcast &6&l(!) &e%player% &7saco " + RARITY_AMP[rar] + " &7en la " + GACHA_AMP[gid] + "&7: &f" + name)
        c = color[rar]
        st = c + "★" * stars[rar] + "<dark_gray>" + "★" * (5 - stars[rar])
        # barra de probabilidad (escala logaritmica: 0,1% = 1 cuadradito, 10% o mas = 10)
        import math
        n = max(1, min(10, round(4 + 2 * math.log10(max(weight, 0.01)) * 1.5)))
        bar = c + "▮" * n + "<dark_gray>" + "▮" * (10 - n)
        L += ["    \"%d\":" % (i + 1), "      DisplayName: " + dq(c + "<bold>" + name),
              "      DisplayItem: " + dq(mat), "      Settings:", "        Custom-Model-Data: -1", "        Model:",
              "          Namespace: " + dq("astral" if model else ""), "          Id: " + dq(model or ""),
              "      DisplayAmount: %d" % max(1, min(64, amount))]
        if rar in ("epic", "legendary"):
            L += ["      DisplayEnchantments:", "        - " + dq("unbreaking:1")]   # brillo
        L += ["      DisplayLore:",
              "        - " + dq("<dark_gray>━━━━━━━━━━━━━━━━━━"),
              "        - " + dq("<gray>Rareza: " + RARITY_MINI[rar]),
              "        - " + dq(st),
              "        - " + dq(""),
              "        - " + dq("<gray>Probabilidad: <yellow><bold>" + ("%.2f" % weight).rstrip("0").rstrip(".") + "%"),
              "        - " + dq(bar),
              "        - " + dq("<dark_gray>━━━━━━━━━━━━━━━━━━"),
              "        - " + dq("<dark_gray>Clic al vendedor para tirar (" + str(g["cost"]) + "$)"),
              "        - " + dq("<dark_purple>Garantia: <light_purple>Epico seguro cada " + str(PITY[gid]) + " tiradas"),
              "      Weight: %s" % weight, "      Commands:"] + ["        - " + dq(c2) for c2 in cm]
    return "\n".join(L) + "\n"


def gacha_skills():
    """MythicMobs cobra la tirada y le pide a CrazyCrates que abra la ruleta (o la vitrina de premios)."""
    L = ["# Gachas del lobby (generado por datapack-src/lobby.py)", ""]
    for gid, g in GACHAS.items():
        G = gid.upper()
        o, n = pity_obj(gid), PITY[gid]
        sc = f"score <trigger.name> {o} matches {n}.."
        L += ["AST_%s:" % G, "  Cooldown: 2", "  Skills:",
              "  - 'currencytake{a=%d} @trigger'" % g["cost"],
              "  - 'sound{s=block.amethyst_block.chime;p=1.2} @trigger'",
              f"  - 'command{{c=\"scoreboard players add <trigger.name> {o} 1\"}} @self'",
              f"  - 'command{{c=\"execute if {sc} run crates forceopen {gid}_garantia <trigger.name>\"}} @self'",
              f"  - 'command{{c=\"execute unless {sc} run crates forceopen {gid} <trigger.name>\"}} @self'",
              f"  - 'message{{m=\"&d&lTirada garantizada! &7(Epico o Legendario seguro)\"}} @trigger ?~score{{o={o};v=>{n - 1}}}'",
              "  - delay 1",
              f"  - 'message{{m=\"&7Garantia: &e<trigger.score.{o}>&7/{n} &8(a las {n} tiradas sin Epico te toca uno seguro)\"}} @trigger'",
              "",
              "AST_%s_INFO:" % G, "  Skills:",
              "  - 'command{c=\"sudo <trigger.name> crates preview %s\"} @self'" % gid,
              f"  - 'message{{m=\"&7Tu garantia en esta gacha: &e<trigger.score.{o}>&7/{n}\"}} @trigger'", ""]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ TAB: panel lateral, tabulador y nombres
# Rango segun el poder total de AuraSkills (suma de niveles de skills)
RANKS = [(1500, "<gradient:#FFD24A:#FF7A2A><bold>Leyenda</bold></gradient>"), (800, "<light_purple><bold>Heroe</bold>"),
         (400, "<aqua>Veterano"), (150, "<green>Aventurero"), (0, "<gray>Novato")]

TAB_SECTIONS = r'''header-footer:
  enabled: true
  designs:
    default:
      header:
        - "<dark_gray><strikethrough>                                                  </strikethrough>"
        - ""
        - "%animation:astral_titulo%"
        - "<gray>Bienvenido, <white><bold>%player%</bold> <dark_gray>| %condition:rango%"
        - ""
      footer:
        - ""
        - "<red>❤ <white>%player_health_rounded%<gray>/%player_max_health_rounded%   <gold>⛃ <yellow>%vault_eco_balance_formatted%   <aqua>⚡ <white>%auraskills_power%"
        - "<gray>Jugadores <white>%online%<dark_gray>/<gray>20   <dark_gray>✦   <gray>Ping <white>%ping%ms   <dark_gray>✦   <gray>TPS %server_tps_1_colored%"
        - "<gray>Estas en <white>%condition:mundo%   <dark_gray>✦   <gray>/spawn <dark_gray>vuelve al lobby"
        - ""
        - "%animation:astral_ip%"
        - "<dark_gray><strikethrough>                                                  </strikethrough>"
playerlist-objective:
  enabled: true
  value: "%player_health_rounded%"
  fancy-value: ""
  title: "Vida"
  render-type: HEARTS
  disable-condition: ''
belowname-objective:
  enabled: true
  value: "%player_health_rounded%"
  fancy-value: "<red>❤ <white>%player_health_rounded% <dark_gray>| <aqua>⚡%auraskills_power%"
  fancy-value-default: ""
  title: "<red>❤"
  disable-condition: '%world%=lobby'
  view-distance: 10
scoreboard:
  enabled: true
  toggle-command: /sb
  remember-toggle-choice: true
  hidden-by-default: false
  delay-on-join-milliseconds: 1500
  scoreboards:
    astral:
      title: "%animation:astral_titulo%"
      lines:
        - "<dark_gray><strikethrough>                    </strikethrough>"
        - "<gray>⚔ <white><bold>%player%</bold>"
        - "<gray>Rango||%condition:rango%"
        - "<gray>Titulo||%condition:titulo%"
        - ""
        - "<red>❤ Vida||<white>%player_health_rounded%<gray>/%player_max_health_rounded%"
        - "<gold>⛃ Oro||<yellow>%vault_eco_balance_formatted%"
        - "<aqua>⚡ Poder||<white>%auraskills_power%"
        - "<green>✦ Nivel||<white>%player_level%"
        - ""
        - "<red>⚒ Forja||<white>%auraskills_forging%"
        - "<light_purple>✧ Hechiceria||<white>%auraskills_sorcery%"
        - "<yellow>➶ Arqueria||<white>%auraskills_archery%"
        - "<gray>☠ Bajas||<white>%statistic_mob_kills%   <gray>⌂ <white>%condition:mundo%"
        - "%animation:astral_ip%"
conditions:
''' + "".join(
    "  rango%d:\n    conditions:\n      - \"%%auraskills_power%%>=%d\"\n    true: \"%s\"\n    false: \"%s\"\n" % (
        i, th, txt, ("%%condition:rango%d%%" % (i + 1)) if i + 1 < len(RANKS) - 1 else RANKS[-1][1])
    for i, (th, txt) in enumerate(RANKS[:-1])).replace("rango0", "rango") + r'''  titulo:
    conditions:
      - "%luckperms_prefix%="
    true: "<dark_gray>ninguno"
    false: "%luckperms_prefix%"
  mundo:
    conditions:
      - "%world%=lobby"
    true: "Lobby"
    false: "%condition:mundo2%"
  mundo2:
    conditions:
      - "%world%=world_nether"
    true: "<red>Nether"
    false: "%condition:mundo3%"
  mundo3:
    conditions:
      - "%world%=world_the_end"
    true: "<light_purple>End"
    false: "<green>Mundo"
'''

TAB_GROUPS = r'''# Nombres en el tabulador y arriba de la cabeza (generado por datapack-src/lobby.py)
_DEFAULT_:
  tabprefix: "%luckperms-prefix% "
  tagprefix: "%luckperms-prefix% "
  customtabname: "<white>%player%"
  tabsuffix: " <dark_gray>[<aqua>⚡%auraskills_power%<dark_gray>]"
  tagsuffix: ""
'''

TAB_ANIMATIONS = r'''# Animaciones del tabulador y del panel (generado por datapack-src/lobby.py)
astral_titulo:
  change-interval: 150
  texts:
''' + "".join("    - \"%s\"\n" % t for t in [
    "<gradient:#B07CFF:#4FD1FF><bold>✦ ASTRAL RPG ✦</bold></gradient>",
    "<gradient:#9A6CFF:#5FD8FF><bold>✦ ASTRAL RPG ✦</bold></gradient>",
    "<gradient:#7EC8FF:#B07CFF><bold>✧ ASTRAL RPG ✧</bold></gradient>",
    "<gradient:#4FD1FF:#B07CFF><bold>✦ ASTRAL RPG ✦</bold></gradient>",
    "<gradient:#FFD24A:#B07CFF><bold>✧ ASTRAL RPG ✧</bold></gradient>",
    "<gradient:#B07CFF:#4FD1FF><bold>✦ ASTRAL RPG ✦</bold></gradient>"]) + r'''astral_ip:
  change-interval: 200
  texts:
''' + "".join("    - \"%s\"\n" % t for t in [
    "<dark_gray>AstralRPG2.aternos.me", "<gray>AstralRPG2.aternos.me", "<white>AstralRPG2.aternos.me",
    "<aqua>AstralRPG2.aternos.me", "<white>AstralRPG2.aternos.me", "<gray>AstralRPG2.aternos.me"])


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
         "papi ecloud download Vault",
         "papi ecloud download Player",
         "papi ecloud download Server",
         "papi ecloud download Statistic",
         "papi reload",
         "# --- contadores de garantia (pity) de las gachas",
         ] + [f"scoreboard objectives add {pity_obj(gid)} dummy" for gid in GACHAS] + [
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
    C.append("# Herrero (mejora +1..+10): no tiene lugar fijo. Parate donde lo quieras, y como jugador (con OP):")
    C.append("#   /mm mobs spawn astral_npc_herrero   (con el mob-spawning allow de arriba todavia puesto)")
    C.append(f"rg flag -w {WORLD} __global__ mob-spawning deny")
    return "\n".join(C) + "\n"


def main():
    os.makedirs(os.path.join(OUT, "Essentials"), exist_ok=True)
    mm = os.path.join(HERE, "..", "build", "mythicmobs", "skills")
    os.makedirs(mm, exist_ok=True)
    with open(os.path.join(mm, "gachas.yml"), "w", encoding="utf-8") as f:
        f.write(gacha_skills())
    tab = os.path.join(OUT, "TAB")
    os.makedirs(tab, exist_ok=True)
    for name, txt in (("secciones-config.yml", TAB_SECTIONS), ("groups.yml", TAB_GROUPS), ("animations.yml", TAB_ANIMATIONS)):
        with open(os.path.join(tab, name), "w", encoding="utf-8") as f:
            f.write(txt)
    cc = os.path.join(OUT, "CrazyCrates", "crates")
    os.makedirs(cc, exist_ok=True)
    for gid, g in GACHAS.items():
        with open(os.path.join(cc, f"{gid}.yml"), "w", encoding="utf-8") as f:
            f.write(crate_yml(gid, g))
        with open(os.path.join(cc, f"{gid}_garantia.yml"), "w", encoding="utf-8") as f:
            f.write(crate_yml(gid, g, garantia=True))
    with open(os.path.join(OUT, "Essentials", "spawn.yml"), "w", encoding="utf-8") as f:
        f.write(spawn_yml())
    with open(os.path.join(OUT, "comandos.txt"), "w", encoding="utf-8") as f:
        f.write(commands())
    n = sum(len(g["rewards"]()) for g in GACHAS.values())
    print(f"lobby: {len(GACHAS)} gachas ({n} premios), {len(NPC_POS)} vendedores -> {os.path.abspath(OUT)}")


if __name__ == "__main__":
    main()
