# -*- coding: utf-8 -*-
"""
Genera la configuracion de MythicMobs para las criaturas de AstralRPG:
mobs (vida, dano, modelo), monturas, elites, jefes, drops y probabilidad de aparicion.
Salida: ../../build/mythicmobs/{mobs,skills,randomspawns}/astral.yml
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "build", "mythicmobs")


def astral_drop(item, chance, amount=1):
    """Suelta un item de AstralRPG donde muere el mob (usa las loot tables del datapack)."""
    lines = []
    for _ in range(amount):
        lines.append(f"- command{{c=\"execute at <caster.uuid> run loot spawn ~ ~0.5 ~ loot astral:item/{item}\"}} @self ~onDeath {chance}")
    return lines


# --------------------------------------------------------------------------- definicion
# kind: pasivo | hostil | montura | jefe
MOBS = {
    # ---------------- fauna
    "astral_mapache": dict(kind="pasivo", type="FOX", name="&6Mapache", hp=14, speed=0.3,
                           drops=["leather 1-2 0.8", "sweet_berries 1-3 0.5", "exp 3"],
                           astral=[("cuero_tratado", 0.15)],
                           spawn=dict(chance=0.06, biomes=["minecraft:forest", "minecraft:birch_forest", "minecraft:dark_forest",
                                                           "minecraft:old_growth_pine_taiga", "minecraft:taiga"])),
    "astral_pinguino": dict(kind="pasivo", type="CHICKEN", name="&bPinguino de Cristal", hp=12, speed=0.22,
                            drops=["cod 1-2 0.7", "feather 1-2 0.6", "exp 3"],
                            astral=[("fragmento_cristal", 0.12)],
                            spawn=dict(chance=0.08, biomes=["minecraft:snowy_plains", "minecraft:ice_spikes", "minecraft:frozen_ocean",
                                                            "minecraft:snowy_beach", "minecraft:frozen_peaks"])),
    # ---------------- hostiles
    "astral_espantapajaros": dict(kind="hostil", type="VEX", name="&6Espantapajaros Maldito", hp=34, damage=6, speed=0.25,
                                  drops=["pumpkin 1 0.5", "wheat 1-4 0.8", "string 1-2 0.5", "exp 8"],
                                  astral=[("esencia_elite", 0.08), ("fragmento_umbrio", 0.10)],
                                  spawn=dict(chance=0.05, night=True, biomes=["minecraft:plains", "minecraft:sunflower_plains",
                                                                               "minecraft:savanna", "minecraft:meadow"])),
    "astral_abejorro": dict(kind="hostil", type="VEX", name="&8Abejorro Sombrio", hp=20, damage=5, speed=0.3,
                            drops=["honeycomb 1-2 0.4", "string 1 0.4", "exp 8"],
                            astral=[("gema_umbria_fragmentada", 0.08), ("esencia_elite", 0.06)],
                            spawn=dict(chance=0.04, biomes=["minecraft:flower_forest", "minecraft:dark_forest", "minecraft:swamp",
                                                            "minecraft:mangrove_swamp"])),
    "astral_arana": dict(kind="hostil", type="SPIDER", name="&5Arana Amatista", hp=26, damage=5, speed=0.3,
                         drops=["string 1-3 0.9", "spider_eye 1 0.5", "amethyst_shard 1-2 0.5", "exp 8"],
                         astral=[("fragmento_cristal", 0.15), ("cristal_arcano", 0.03)],
                         spawn=dict(chance=0.05, cave=True, biomes=["minecraft:dripstone_caves", "minecraft:lush_caves",
                                                                    "minecraft:deep_dark", "minecraft:dark_forest"])),
    "astral_cara": dict(kind="hostil", type="PHANTOM", name="&cCara Voladora", hp=22, damage=6, speed=0.3,
                        drops=["phantom_membrane 1 0.6", "rotten_flesh 1-2 0.6", "exp 10"],
                        astral=[("gema_umbria", 0.03), ("alma_corrupta", 0.05)],
                        spawn=dict(chance=0.03, night=True, biomes=["minecraft:swamp", "minecraft:mangrove_swamp",
                                                                     "minecraft:dark_forest", "minecraft:badlands"])),
    # ---------------- monturas (sin montura puesta: el jugador le pone la suya)
    "astral_grillo": dict(kind="montura", type="HORSE", name="&aGrillo Saltarin", hp=26, speed=0.24, jump=1.25,
                          drops=["leather 1 0.5", "slime_ball 1 0.3", "exp 5"],
                          spawn=dict(chance=0.025, biomes=["minecraft:plains", "minecraft:meadow", "minecraft:sunflower_plains"])),
    "astral_chocobo": dict(kind="montura", type="HORSE", name="&eAve Corredora", hp=30, speed=0.38, jump=0.7,
                           drops=["feather 2-4 0.9", "exp 5"],
                           spawn=dict(chance=0.02, biomes=["minecraft:savanna", "minecraft:savanna_plateau", "minecraft:plains"])),
    "astral_escarabajo": dict(kind="montura", type="HORSE", name="&9Escarabajo Acorazado", hp=60, speed=0.14, jump=0.45,
                              drops=["turtle_scute 1 0.3", "exp 5"], armor=10,
                              spawn=dict(chance=0.02, biomes=["minecraft:jungle", "minecraft:sparse_jungle", "minecraft:bamboo_jungle"])),
    "astral_lagarto": dict(kind="montura", type="SKELETON_HORSE", name="&aLagarto de Pantano", hp=34, speed=0.22, jump=0.6,
                           drops=["leather 1-2 0.8", "exp 5"],
                           spawn=dict(chance=0.025, biomes=["minecraft:swamp", "minecraft:mangrove_swamp", "minecraft:river"])),
    "astral_ave": dict(kind="montura", type="PARROT", name="&6Gran Ave", hp=40, speed=0.32, fly=True,
                       drops=["feather 3-6 1", "exp 6"],
                       spawn=dict(chance=0.01, biomes=["minecraft:windswept_hills", "minecraft:stony_peaks", "minecraft:jagged_peaks",
                                                       "minecraft:meadow"])),
    "astral_pterodactilo": dict(kind="montura", type="PHANTOM", name="&9Pterodactilo", hp=50, speed=0.36, fly=True,
                                drops=["bone 2-4 0.9", "exp 6"],
                                spawn=dict(chance=0.008, biomes=["minecraft:badlands", "minecraft:eroded_badlands",
                                                                 "minecraft:wooded_badlands", "minecraft:jungle"])),
    # ---------------- jefes
    "astral_momia": dict(kind="jefe", type="HUSK", name="&e&lMomia Ancestral", hp=320, damage=10, speed=0.24,
                         bar="YELLOW", drops=["gold_ingot 3-8 1", "bone 4-8 1", "exp 120"],
                         astral=[("alma_corrupta", 1.0), ("chispa_astral", 0.35), ("gema_luminica", 0.8), ("esencia_elite", 1.0, 3)],
                         skills=["- summon{type=HUSK;amount=2;radius=3} @self ~onTimer:300",
                                 "- potion{type=SLOW;duration=80;level=1} @target ~onAttack 0.4",
                                 "- message{m=\"&eLa Momia Ancestral despierta...\"} @PlayersInRadius{r=30} ~onSpawn"],
                         spawn=dict(chance=0.0015, biomes=["minecraft:desert"])),
    "astral_yeti": dict(kind="jefe", type="RAVAGER", name="&f&lYeti de las Cumbres", hp=450, damage=14, speed=0.28,
                        bar="WHITE", drops=["snow_block 4-10 1", "leather 4-8 1", "exp 150"],
                        astral=[("alma_corrupta", 1.0, 2), ("chispa_astral", 0.45), ("cristal_refinado", 0.8), ("esencia_elite", 1.0, 3)],
                        skills=["- potion{type=SLOW;duration=100;level=2} @PlayersInRadius{r=6} ~onTimer:200",
                                "- leap{velocity=150;noise=0} @target ~onTimer:160 0.5",
                                "- message{m=\"&fUn rugido helado retumba en la montana...\"} @PlayersInRadius{r=40} ~onSpawn"],
                        spawn=dict(chance=0.0012, biomes=["minecraft:frozen_peaks", "minecraft:snowy_slopes", "minecraft:ice_spikes"])),
    "astral_golem_forja": dict(kind="jefe", type="IRON_GOLEM", name="&c&lGolem de la Forja", hp=500, damage=16, speed=0.22,
                               bar="RED", drops=["netherite_scrap 1-2 0.5", "iron_ingot 6-12 1", "blaze_rod 2-4 1", "exp 180"],
                               astral=[("nucleo_furia", 1.0, 2), ("netherita_fundida", 0.6), ("chispa_astral", 0.5),
                                       ("esencia_elite", 1.0, 3)],
                               hostile_ai=True,
                               skills=["- ignite{ticks=80} @PlayersInRadius{r=4} ~onTimer:100",
                                       "- particles{p=flame;amount=40;hS=1;vS=1.5;speed=0.05} @self ~onTimer:40",
                                       "- message{m=\"&cEl suelo arde: el Golem de la Forja se levanta.\"} @PlayersInRadius{r=40} ~onSpawn"],
                               spawn=dict(chance=0.002, world="world_nether", biomes=["minecraft:basalt_deltas", "minecraft:nether_wastes",
                                                                                       "minecraft:crimson_forest"])),
    "astral_cangrejo": dict(kind="jefe", type="SPIDER", name="&6&lCangrejo Ermitano Gigante", hp=260, damage=9, speed=0.26,
                            bar="PINK", drops=["nautilus_shell 1 0.6", "prismarine_shard 2-5 1", "exp 100"],
                            astral=[("alma_corrupta", 0.8), ("corazon_shulker", 0.3), ("esencia_elite", 1.0, 2)],
                            skills=["- throw{velocity=8;velocityY=4} @target ~onAttack 0.35",
                                    "- message{m=\"&6Algo enorme se arrastra por la arena...\"} @PlayersInRadius{r=30} ~onSpawn"],
                            spawn=dict(chance=0.002, biomes=["minecraft:beach", "minecraft:stony_shore", "minecraft:warm_ocean"])),
    "astral_chaman": dict(kind="jefe", type="EVOKER", name="&2&lChaman del Pantano", hp=340, damage=8, speed=0.25,
                          bar="GREEN", drops=["totem_of_undying 1 0.3", "emerald 3-8 1", "slime_ball 2-6 1", "exp 160"],
                          astral=[("alma_corrupta", 1.0, 2), ("chispa_astral", 0.4), ("gema_umbria", 0.8), ("esencia_elite", 1.0, 3)],
                          skills=["- potion{type=POISON;duration=80;level=1} @PlayersInRadius{r=8} ~onTimer:220",
                                  "- summon{type=WITCH;amount=1;radius=3} @self ~onTimer:400",
                                  "- message{m=\"&2Un canto extrano sale del pantano...\"} @PlayersInRadius{r=40} ~onSpawn"],
                          spawn=dict(chance=0.0015, night=True, biomes=["minecraft:swamp", "minecraft:mangrove_swamp"])),
}

# Elites: versiones modificadas (mas grandes, con otro color) que dan mas cosas
ELITES = {
    "astral_espantapajaros": ("FF3A3A", "&4Espantapajaros Infernal"),
    "astral_abejorro": ("FFC020", "&6Abejorro Reina"),
    "astral_arana": ("40FFD0", "&3Arana de Cristal Vivo"),
    "astral_cara": ("A040FF", "&5Cara del Abismo"),
    "astral_cangrejo": ("60A0FF", "&9Cangrejo Abisal"),
}


def mob_block(mid, d, model=None, elite=None):
    model = model or mid
    lines = [f"{mid}:", f"  Type: {d['type']}", f"  Display: '{elite[1] if elite else d['name']}'"]
    hp = d["hp"] * (2.5 if elite else 1)
    lines.append(f"  Health: {int(hp)}")
    if d.get("damage"):
        lines.append(f"  Damage: {round(d['damage'] * (1.6 if elite else 1), 1)}")
    if d.get("armor") or elite:
        lines.append(f"  Armor: {d.get('armor', 0) + (6 if elite else 0)}")
    opts = ["    PreventOtherDrops: true", "    Silent: false", "    PreventSunburn: true", "    Despawn: false"
            if d["kind"] in ("montura", "jefe") else "    Despawn: true"]
    if d.get("speed"):
        opts.append(f"    MovementSpeed: {d['speed']}")
    if d["kind"] == "jefe" or elite:
        opts.append("    KnockbackResistance: 0.8")
        opts.append("    FollowRange: 40")
    opts.append("    PreventRandomEquipment: true")   # el vex no saca su espada encima del modelo
    lines.append("  Options:")
    lines += opts
    if d["kind"] == "montura" and d["type"] == "PHANTOM":
        # pterodactilo: vuela en circulos como un phantom pero no ataca
        lines += ["  AITargetSelectors:", "  - clear"]
    if d.get("hostile_ai"):
        lines += ["  AIGoalSelectors:", "  - clear", "  - meleeattack", "  - randomstroll", "  - lookatplayers",
                  "  AITargetSelectors:", "  - clear", "  - attacker", "  - players"]
    if d["kind"] == "jefe":
        lines += ["  BossBar:", "    Enabled: true", f"    Title: '{d['name']}'", "    Range: 48",
                  f"    Color: {d['bar']}", "    Style: SEGMENTED_10"]
    # drops vanilla
    drops = list(d.get("drops", []))
    if elite:
        drops = [x for x in drops] + ["exp 30", "diamond 1 0.15"]
    lines.append("  Drops:")
    lines += [f"  - {x}" for x in drops]
    # habilidades
    sk = [f"- skill{{s=AST_MODEL_{(elite and mid) or model}}} @self ~onSpawn", f"- skill{{s=AST_MODEL_{(elite and mid) or model}}} @self ~onLoad"]
    if d["kind"] == "montura":
        mode = "flying" if d.get("fly") else "walking"
        sk += [f"- skill{{s=AST_MOUNT_{mid}}} @self ~onSpawn",
               "- skill{s=AST_SILLA_VER} @self ~onLoad",
               # nada de comportamiento vanilla al hacer clic (domar, subirse al caballo invisible, semillas al loro)
               "- cancelevent @self ~onInteract",
               "- skill{s=AST_ENSILLAR} @self ~onInteract ?~holding{m=SADDLE} ?!hastag{tag=astral.ensillado}",
               # subirse con el asiento de BetterModel: el jugador la maneja con WASD (salto/volar con espacio, bajarse con shift)
               f"- mountmodel{{driver=true;mode={mode}}} @trigger ~onInteract ?hastag{{tag=astral.ensillado}} ?~!holding{{m=SADDLE}}",
               "- setAI{ai=false} @self ~onTimer:10 ?modelhaspassenger",
               "- setAI{ai=true} @self ~onTimer:10 ?!modelhaspassenger",
               "- dropitem{items=saddle} @self ~onDeath ?hastag{tag=astral.ensillado}"]
    elif d["kind"] in ("hostil", "jefe") or elite:
        sk.append("- state{s=attack} @self ~onAttack")
    for a in d.get("astral", []):
        item, ch = a[0], a[1]
        amount = a[2] if len(a) > 2 else 1
        if elite:
            ch = min(1.0, ch * 2.5)
            amount += 1
        sk += astral_drop(item, ch, amount)
    if elite:
        sk += astral_drop("esencia_elite", 1.0, 2) + astral_drop("alma_corrupta", 0.3)
    sk += d.get("skills", [])
    lines.append("  Skills:")
    lines += ["  " + s for s in sk]
    return "\n".join(lines) + "\n"


def metaskills():
    out = []
    for mid, d in MOBS.items():
        out += [f"AST_MODEL_{mid}:", "  Skills:", "  - addtag{tag=astral.seen} @self", f"  - model{{m={mid}}} @self"]
        if d["kind"] == "montura":
            # BetterModel mueve la montura con la velocidad de movimiento y salta con jump_strength
            out += [f"AST_MOUNT_{mid}:", "  Skills:", "  - delay 2",
                    f"  - command{{c=\"attribute <caster.uuid> minecraft:movement_speed base set {d['speed']}\"}} @self",
                    f"  - command{{c=\"attribute <caster.uuid> minecraft:max_health base set {d['hp']}\"}} @self",
                    "  - skill{s=AST_SILLA_VER} @self"]
            if d.get("jump"):
                out += [f"  - command{{c=\"attribute <caster.uuid> minecraft:jump_strength base set {d['jump']}\"}} @self"]
    # la silla se ve solo si el jugador le puso una montura
    out += ["AST_SILLA_VER:", "  Skills:", "  - delay 3",
            "  - partvisibility{p=silla;v=false} @self ?!hastag{tag=astral.ensillado}",
            "  - partvisibility{p=silla;v=true} @self ?hastag{tag=astral.ensillado}",
            "AST_ENSILLAR:", "  Skills:",
            "  - command{c=\"clear <trigger.name> minecraft:saddle 1\"} @self",
            "  - addtag{tag=astral.ensillado} @self",
            "  - partvisibility{p=silla;v=true} @self",
            "  - sound{s=entity.horse.saddle} @self"]
    for mid, (color, _) in ELITES.items():
        out += [f"AST_MODEL_{mid}_elite:", "  Skills:", "  - addtag{tag=astral.seen} @self",
                f"  - model{{m={mid};s=1.35}} @self", "  - delay 2",
                f"  - tint{{c={color}}} @self"]
    return "\n".join(out) + "\n"


def spawns():
    out = []
    for mid, d in MOBS.items():
        s = d.get("spawn")
        if not s:
            continue
        out += spawn_entry(mid, mid, s, s["chance"])
        if mid in ELITES:
            out += spawn_entry(f"{mid}_elite", f"{mid}_elite", s, round(s["chance"] * 0.15, 5))
    return "\n".join(out) + "\n"


def spawn_entry(key, mob, s, chance):
    lines = [f"spawn_{key}:", "  Action: ADD", f"  Type: {mob}", f"  Worlds: {s.get('world', 'world')}",
             f"  Chance: {chance}", "  Priority: 1", "  Reason: NATURAL", "  Biomes:"]
    lines += [f"  - {b}" for b in s["biomes"]]
    cond = []
    if s.get("night"):
        cond.append("  - night true")
    if s.get("cave"):
        cond.append("  - outside false")
    if cond:
        lines += ["  Conditions:"] + cond
    return lines


def main():
    for sub in ("mobs", "skills", "randomspawns"):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    mobs = [mob_block(mid, d) for mid, d in MOBS.items()]
    mobs += [mob_block(f"{mid}_elite", MOBS[mid], model=mid, elite=e) for mid, e in ELITES.items()]
    with open(os.path.join(OUT, "mobs", "astral.yml"), "w", encoding="utf-8") as f:
        f.write("# Criaturas de AstralRPG (generado por datapack-src/mobs/mythic.py)\n\n" + "\n".join(mobs))
    with open(os.path.join(OUT, "skills", "astral.yml"), "w", encoding="utf-8") as f:
        f.write(metaskills())
    with open(os.path.join(OUT, "randomspawns", "astral.yml"), "w", encoding="utf-8") as f:
        f.write(spawns())
    print(len(mobs), "mobs de MythicMobs generados")


if __name__ == "__main__":
    main()
