# -*- coding: utf-8 -*-
"""
Mazmorra "Minas Olvidadas" (MythicMobs). Mundo 'mina' de Multiverse con el mapa dungeon1-endlessxl.schem pegado
con WorldEdit (//schem load + //paste -o: la esquina queda en -73 -55 -290). El mapa NO va al repo (es de terceros).

Como funciona:
  - Cada sala tiene un controlador invisible (armor stand de MythicMobs) en su centro.
  - Cuando llega un jugador, el controlador larga la oleada 1; cuando no queda ningun mob vivo, la 2; y cuando
    se limpia la ultima, avisa y a los 5 segundos teletransporta a todos a la sala siguiente.
  - Con 2 o mas jugadores en la sala aparecen mobs extra.
  - Si la sala se queda sin jugadores, se reinicia sola (borra sus mobs).
  - La ultima sala es la del Guardian de las Profundidades. Al matarlo, cada jugador cerca cobra el cofre final
    si no lo cobro en los ultimos 30 minutos (permiso temporal de LuckPerms astral.mina.cd) y vuelve al lobby.
  - Se entra con el vendedor 'astral_npc_mina' del lobby.

Salida: ../../build/mythicmobs/{mobs,skills}/mazmorra.yml y ../../build/mazmorra/comandos.txt
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "build")
WORLD = "mina"
COOLDOWN = "30m"


def q(s):
    return "'" + str(s).replace("'", "''") + "'"


def drop(item, chance, n=1):
    return [f'command{{c="execute at <caster.uuid> run loot spawn ~ ~0.5 ~ loot astral:item/{item}"}} @self ~onDeath {chance}'] * n


# ------------------------------------------------------------------ mobs de la mina
# equipo: lista de "item SLOT" (HAND, OFFHAND, HEAD, CHEST, LEGS, FEET)
MOBS = {
    "astral_mina_minero": dict(type="ZOMBIE", name="&7Minero Corrupto", hp=45, dmg=7, speed=0.24,
                               equip=["iron_pickaxe HAND", "leather_helmet HEAD"], money=20,
                               drops=drop("esencia_elite", 0.10) + drop("fragmento_umbrio", 0.15)),
    "astral_mina_esqueleto": dict(type="SKELETON", name="&fEsqueleto Minero", hp=32, dmg=5, speed=0.25,
                                  equip=["bow HAND", "chainmail_helmet HEAD"], money=20,
                                  drops=drop("esencia_elite", 0.10)),
    "astral_mina_ahogado": dict(type="DROWNED", name="&3Minero Ahogado", hp=42, dmg=8, speed=0.25,
                                equip=["trident HAND"], money=20,
                                drops=drop("esencia_elite", 0.12) + drop("fragmento_cristal", 0.20)),
    "astral_mina_arana": dict(type="CAVE_SPIDER", name="&8Arana de la Mina", hp=24, dmg=5, speed=0.32, money=15,
                              drops=drop("fragmento_cristal", 0.15)),
    # mini jefes
    "astral_mina_capataz": dict(type="DROWNED", name="&3&lCapataz Ahogado", hp=380, dmg=11, speed=0.27, boss="BLUE",
                                equip=["trident HAND", "iron_helmet HEAD"], money=400,
                                drops=drop("alma_corrupta", 1.0) + drop("esencia_elite", 1.0, 2) + drop("gema_luminica", 0.4),
                                skills=["summon{type=astral_mina_ahogado;amount=2;radius=3} @self ~onTimer:300",
                                        "potion{type=SLOWNESS;duration=60;level=1} @PlayersInRadius{r=6} ~onTimer:160",
                                        "particles{p=bubble_pop;amount=60;hS=5;vS=0.5} @self ~onTimer:160"]),
    "astral_mina_golem": dict(type="IRON_GOLEM", name="&7&lGolem de Piedra Antiguo", hp=480, dmg=14, speed=0.22, boss="WHITE",
                              hostile=True, money=500,
                              drops=drop("alma_corrupta", 1.0) + drop("esencia_elite", 1.0, 2) + drop("netherita_fundida", 0.5),
                              skills=["throw{velocity=7;velocityY=3} @target ~onAttack 0.4",
                                      "skill{s=MINA_ONDA_GOLEM} @self ~onTimer:140"]),
    # jefe final (modelo del Golem de la Forja, mas grande y gris piedra)
    "astral_mina_guardian": dict(type="IRON_GOLEM", name="&8&lGuardian de las Profundidades", hp=1000, dmg=16, speed=0.24,
                                 boss="PURPLE", hostile=True, model=("astral_golem_forja", 1.5, "8A93A6"), money=1500,
                                 drops=drop("chispa_astral", 1.0, 2) + drop("alma_corrupta", 1.0, 2) + drop("nucleo_furia", 0.5),
                                 skills=["potion{type=RESISTANCE;duration=240;level=0;hasParticles=false} @self ~onTimer:200",
                                         "throw{velocity=8;velocityY=3} @target ~onAttack 0.35",
                                         "skill{s=MINA_ONDA_GUARDIAN} @self ~onTimer:160",
                                         # fase 2 (60%): llama mineros. fase 3 (25%): se enfurece
                                         "skill{s=MINA_GUARDIAN_F2} @self ~onDamaged ?healthpercent{p=<0.6} ?!hastag{tag=mina.f2}",
                                         "skill{s=MINA_GUARDIAN_F3} @self ~onDamaged ?healthpercent{p=<0.25} ?!hastag{tag=mina.f3}",
                                         "summon{type=astral_mina_minero;amount=2;radius=5} @self ~onTimer:400 ?hastag{tag=mina.f2}"]),
}

# ------------------------------------------------------------------ salas
# centro: donde va el controlador. llegada: donde aparecen los jugadores. r: radio de la sala.
# oleadas: [(mob, cantidad base, extra con 2+ jugadores)]
SALAS = [
    dict(id="sala1", name="Campamento Minero", centro=(10.5, -45, -124.5), llegada=(10.5, -45, -124.5), r=16,
         oleadas=[[("astral_mina_minero", 4, 2)],
                  [("astral_mina_minero", 3, 1), ("astral_mina_esqueleto", 3, 1)]]),
    dict(id="sala2", name="Lago Subterraneo", centro=(19.5, -39, -158.5), llegada=(19.5, -39, -158.5), r=22,
         oleadas=[[("astral_mina_ahogado", 5, 2)],
                  [("astral_mina_capataz", 1, 0), ("astral_mina_ahogado", 2, 1)]]),
    dict(id="sala3", name="Tuneles de Soporte", centro=(43.5, -24, -201.5), llegada=(43.5, -24, -201.5), r=16,
         oleadas=[[("astral_mina_arana", 6, 2), ("astral_mina_esqueleto", 2, 1)],
                  [("astral_mina_golem", 1, 0)]]),
    dict(id="sala4", name="Salon del Guardian", centro=(36.5, 24, -248.5), llegada=(40.5, 24, -225.5), r=35,
         oleadas=[[("astral_mina_guardian", 1, 0)]], extra=["astral_mina_minero"]),
]
LOBBY_NPC = "astral_npc_mina"
PREMIO = [("esencia_elite", 4), ("alma_corrupta", 2), ("gema_luminica", 1), ("cristal_refinado", 1)]
PREMIO_PLATA = 2500


def tipos_sala(s):
    return ",".join(sorted({m for ol in s["oleadas"] for (m, _, _) in ol} | set(s.get("extra", []))))


def mob_yml():
    L = ["# Mazmorra Minas Olvidadas (generado por datapack-src/mobs/mazmorra.py)", ""]
    for mid, d in MOBS.items():
        L += [f"{mid}:", f"  Type: {d['type']}", f"  Display: {q(d['name'])}", f"  Health: {d['hp']}", f"  Damage: {d['dmg']}",
              "  Options:", f"    MovementSpeed: {d['speed']}", "    PreventOtherDrops: true", "    PreventSunburn: true", "    PreventRandomEquipment: true",
              "    Despawn: false", "    FollowRange: 32"]
        if d.get("boss"):
            L += ["    KnockbackResistance: 0.8", "  BossBar:", "    Enabled: true", f"    Title: {q(d['name'])}", "    Range: 48",
                  f"    Color: {d['boss']}", "    Style: SEGMENTED_10"]
        if d.get("hostile"):
            L += ["  AIGoalSelectors:", "  - clear", "  - meleeattack", "  - randomstroll", "  - lookatplayers",
                  "  AITargetSelectors:", "  - clear", "  - attacker", "  - players"]
        if d.get("equip"):
            L += ["  Equipment:"] + [f"  - {e}" for e in d["equip"]]
        L += ["  Drops:", "  - exp 15"]
        sk = list(d.get("skills", [])) + list(d.get("drops", []))
        if d.get("model"):
            m, sc, col = d["model"]
            sk = [f"skill{{s=MINA_MODELO_{mid}}} @self ~onSpawn", f"skill{{s=MINA_MODELO_{mid}}} @self ~onLoad",
                  "state{s=attack} @self ~onAttack"] + sk
        sk.append(f'command{{c="eco give <trigger.name> {d["money"]}"}} @trigger ~onDeath ?isplayer')
        L += ["  Skills:"] + ["  - " + q(s) for s in sk] + [""]
    # controladores de sala: armor stand invisible y quieto
    for i, s in enumerate(SALAS):
        tipos = tipos_sala(s)
        r = s["r"]
        S = s["id"].upper()
        sk = [f"skill{{s=MINA_{S}_INICIO}} @self ~onTimer:20 ?playerwithin{{d={r}}} ?!hastag{{tag=mina.on}}"]
        n = len(s["oleadas"])
        for k in range(2, n + 1):
            sk.append(f"skill{{s=MINA_{S}_OLA{k}}} @self ~onTimer:20 ?hastag{{tag=mina.ola{k - 1}}} ?!hastag{{tag=mina.ola{k}}} "
                      f"?!hastag{{tag=mina.espera}} ?mobsinradius{{types={tipos};a=0;r={r + 8}}}")
        sk.append(f"skill{{s=MINA_{S}_LIMPIA}} @self ~onTimer:20 ?hastag{{tag=mina.ola{n}}} ?!hastag{{tag=mina.fin}} ?!hastag{{tag=mina.espera}} "
                  f"?mobsinradius{{types={tipos};a=0;r={r + 8}}}")
        sk.append(f"skill{{s=MINA_{S}_RESET}} @self ~onTimer:200 ?hastag{{tag=mina.on}} ?!playerwithin{{d={r + 8}}}")
        L += [f"astral_mina_control_{s['id']}:", "  Type: ARMOR_STAND", f"  Display: {q('Control ' + s['name'])}", "  Health: 100",
              "  Options:", "    Invisible: true", "    Marker: true", "    Invincible: true", "    Silent: true", "    NoGravity: true",
              "    Despawn: false", "    Persistent: true", "    Collidable: false", "  Skills:"] + ["  - " + q(x) for x in sk] + [""]
    # vendedor del lobby
    L += [f"{LOBBY_NPC}:", "  Type: VILLAGER", f"  Display: {q('&8&lMazmorra: &7Minas Olvidadas')}", "  Health: 100", "  Options:",
          "    NoAI: true", "    Invincible: true", "    Silent: true", "    Despawn: false", "    Persistent: true",
          "    Collidable: false", "    PreventItemPickup: true", "    PreventOtherDrops: true", "    AlwaysShowName: true",
          "    Profession: MASON", "    VillagerType: PLAINS", "  Skills:", "  - cancelevent @self ~onInteract",
          "  - " + q("skill{s=MINA_ENTRAR} @trigger ~onInteract"), ""]
    return "\n".join(L) + "\n"


def tp(x, y, z, who="<target.name>"):
    return f'command{{c="execute in minecraft:{WORLD} run minecraft:tp {who} {x} {y} {z}"}}'


def skill_yml():
    L = ["# Mazmorra Minas Olvidadas (generado por datapack-src/mobs/mazmorra.py)", ""]
    for mid, d in MOBS.items():
        if d.get("model"):
            m, sc, col = d["model"]
            L += [f"MINA_MODELO_{mid}:", "  Skills:", "  - addtag{tag=astral.seen} @self", f"  - model{{m={m};s={sc}}} @self",
                  "  - delay 2", f"  - tint{{c={col}}} @self", ""]
    # ondas con aviso (1 segundo para alejarse)
    for nombre, dano, radio in (("GOLEM", 7, 5), ("GUARDIAN", 9, 6)):
        L += [f"MINA_ONDA_{nombre}:", "  Skills:",
              "  - " + q(f"particles{{p=cloud;amount=60;hS={radio};vS=0.2;speed=0}} @self"),
              "  - " + q("sound{s=entity.ravager.roar;v=1.5;p=0.7} @self"), "  - delay 20",
              "  - " + q(f"particles{{p=explosion;amount=12;hS={radio};vS=0.3}} @self"),
              "  - " + q(f"damage{{a={dano}}} @PlayersInRadius{{r={radio}}}"),
              "  - " + q(f"throw{{velocity=4;velocityY=2}} @PlayersInRadius{{r={radio}}}"), ""]
    L += ["MINA_GUARDIAN_F2:", "  Skills:", "  - addtag{tag=mina.f2} @self",
          "  - " + q('message{m="&8&lEl Guardian golpea la roca: los mineros corruptos despiertan!"} @PlayersInRadius{r=48}'),
          "  - summon{type=astral_mina_minero;amount=3;radius=5} @self", "",
          "MINA_GUARDIAN_F3:", "  Skills:", "  - addtag{tag=mina.f3} @self",
          "  - " + q('message{m="&4&lEl Guardian se enfurece! Su piel de piedra se agrieta..."} @PlayersInRadius{r=48}'),
          "  - potion{type=STRENGTH;duration=999999;level=0} @self", "  - potion{type=SPEED;duration=999999;level=0} @self", ""]
    # salas
    for i, s in enumerate(SALAS):
        S = s["id"].upper()
        r = s["r"]
        sig = SALAS[i + 1] if i + 1 < len(SALAS) else None

        def ola(k):
            out = []
            for (m, base, extra) in s["oleadas"][k - 1]:
                out.append(q(f"summon{{type={m};amount={base};radius=4}} @self"))
                if extra:
                    out.append(q(f"summon{{type={m};amount={extra};radius=4}} @self ?playersinradius{{r={r};a=>1}}"))
            return ["  - " + x for x in out]
        n = len(s["oleadas"])
        L += [f"MINA_{S}_INICIO:", "  Skills:", "  - addtag{tag=mina.on} @self", "  - addtag{tag=mina.ola1} @self",
              "  - " + q(f'message{{m="&8[&7Mina&8] &f{s["name"]} &7- sala {i + 1}/{len(SALAS)}. &cAhi vienen!"}} @PlayersInRadius{{r={r + 8}}}'),
              "  - " + q("sound{s=entity.warden.emerge;v=0.6;p=1.4} @PlayersInRadius{r=" + str(r + 8) + "}")] + ola(1) + [""]
        for k in range(2, n + 1):
            L += [f"MINA_{S}_OLA{k}:", "  Skills:", f"  - addtag{{tag=mina.ola{k}}} @self", "  - addtag{tag=mina.espera} @self",
                  "  - " + q(f'message{{m="&8[&7Mina&8] &7Oleada {k}/{n}..."}} @PlayersInRadius{{r={r + 8}}}'),
                  "  - delay 40"] + ola(k) + ["  - delay 10", "  - removetag{tag=mina.espera} @self", ""]
        if sig:
            L += [f"MINA_{S}_LIMPIA:", "  Skills:", "  - addtag{tag=mina.fin} @self",
                  "  - " + q(f'message{{m="&a&lSala limpia! &7En 5 segundos pasan a: &f{sig["name"]}"}} @PlayersInRadius{{r={r + 8}}}'),
                  "  - " + q("sound{s=ui.toast.challenge_complete} @PlayersInRadius{r=" + str(r + 8) + "}"),
                  "  - delay 100",
                  "  - " + q(f"skill{{s=MINA_IR_{sig['id'].upper()}}} @PlayersInRadius{{r={r + 8}}}"),
                  "  - delay 20",
                  "  - removetag{tag=mina.on} @self", "  - removetag{tag=mina.fin} @self"] + \
                 [f"  - removetag{{tag=mina.ola{k}}} @self" for k in range(1, n + 1)] + [""]
            L += [f"MINA_IR_{sig['id'].upper()}:", "  Skills:", "  - " + q(tp(*sig["llegada"])),
                  "  - " + q("sound{s=entity.enderman.teleport}"), ""]
        else:
            # sala final: premio y vuelta al lobby
            L += [f"MINA_{S}_LIMPIA:", "  Skills:", "  - addtag{tag=mina.fin} @self",
                  "  - " + q(f'message{{m="&6&lEl Guardian de las Profundidades cayo! &7Abran el cofre..."}} @PlayersInRadius{{r={r + 8}}}'),
                  "  - " + q("sound{s=ui.toast.challenge_complete} @PlayersInRadius{r=" + str(r + 8) + "}"),
                  "  - delay 40",
                  "  - " + q(f"skill{{s=MINA_PREMIO}} @PlayersInRadius{{r={r + 8}}}"),
                  "  - " + q(f"skill{{s=MINA_PREMIO_YA}} @PlayersInRadius{{r={r + 8}}}"),
                  "  - " + q(f'message{{m="&7En 15 segundos vuelven al lobby."}} @PlayersInRadius{{r={r + 8}}}'),
                  "  - delay 300",
                  "  - " + q(f'command{{c="spawn <target.name>"}} @PlayersInRadius{{r={r + 8}}}'),
                  "  - delay 20",
                  "  - removetag{tag=mina.on} @self", "  - removetag{tag=mina.fin} @self"] + \
                 [f"  - removetag{{tag=mina.ola{k}}} @self" for k in range(1, n + 1)] + [""]
        tipos = tipos_sala(s)
        L += [f"MINA_{S}_RESET:", "  Skills:", "  - " + q(f"remove @MobsInRadius{{r={r + 8};types={tipos}}}"),
              "  - removetag{tag=mina.on} @self", "  - removetag{tag=mina.fin} @self", "  - removetag{tag=mina.espera} @self"] + \
             [f"  - removetag{{tag=mina.ola{k}}} @self" for k in range(1, len(s["oleadas"]) + 1)] + [""]
    # premio final (una vez cada 30 minutos por jugador)
    L += ["MINA_PREMIO:", "  TargetConditions:", "  - haspermission{p=astral.mina.cd} false", "  Skills:"]
    for it, n in PREMIO:
        L += ["  - " + q(f'command{{c="loot give <target.name> loot astral:item/{it}"}}')] * n
    L += ["  - " + q('command{c="loot give <target.name> loot astral:item/chispa_astral"} 0.25'),
          "  - " + q(f'command{{c="eco give <target.name> {PREMIO_PLATA}"}}'),
          "  - " + q(f'command{{c="lp user <target.name> permission settemp astral.mina.cd true {COOLDOWN}"}}'),
          "  - " + q(f'message{{m="&6Cofre de la Mina: &fmateriales de elite y &e{PREMIO_PLATA}$&f. &7(el proximo cofre en 30 minutos)"}}'),
          "",
          "MINA_PREMIO_YA:", "  TargetConditions:", "  - haspermission{p=astral.mina.cd} true", "  Skills:",
          "  - " + q('message{m="&7Ya cobraste el cofre de la mina hace poco. &8(se puede cobrar cada 30 minutos)"}'), ""]
    # entrada desde el lobby
    s1 = SALAS[0]
    L += ["MINA_ENTRAR:", "  Skills:",
          "  - " + q('message{m="&8[&7Mina&8] &7Bajando a las &fMinas Olvidadas&7... &8(4 salas. Para salir: /spawn)"}'),
          "  - " + q(tp(*s1["llegada"], who="<trigger.name>")), ""]
    return "\n".join(L) + "\n"


def commands():
    C = ["# Mazmorra Minas Olvidadas: comandos de consola (sin /). Generado por datapack-src/mobs/mazmorra.py",
         "# --- 1) mundo vacio (una sola vez)",
         f'mv create {WORLD} normal --world-type FLAT --no-structures --no-adjust-spawn '
         '--generator-settings {"layers":[{"block":"minecraft:air","height":1}],"biome":"minecraft:the_void"}',
         f"mv modify {WORLD} set difficulty hard",
         f"mv modify {WORLD} set gamemode survival",
         f"mv modify {WORLD} set pvp false",
         f"mv modify {WORLD} set allow-weather false",
         f"mv gamerule set minecraft:spawn_mobs false {WORLD}",
         f"mv gamerule set minecraft:keep_inventory true {WORLD}",
         f"mv gamerule set minecraft:advance_time false {WORLD}",
         f"execute in minecraft:{WORLD} run time set midnight",
         f"rg flag -w {WORLD} __global__ build deny",
         f"rg flag -w {WORLD} __global__ chest-access deny",
         f"rg flag -w {WORLD} __global__ mob-spawning allow",
         f"rg flag -w {WORLD} __global__ pvp deny",
         "# --- 2) pegar el mapa (lo hace un jugador con OP, en el juego):",
         "#   subir dungeon1-endlessxl.schem a plugins/WorldEdit/schematics/",
         f"#   /mvtp {WORLD}    /gamemode creative    //schem load dungeon1-endlessxl    //paste -o",
         "#   (con -o el mapa cae siempre en el mismo lugar: esquina -73 -55 -290)",
         "# --- 3) controladores de las salas (una sola vez, despues de pegar el mapa)",
         f"execute in minecraft:{WORLD} run forceload add -80 -300 160 -60"]
    for s in SALAS:
        x, y, z = s["centro"]
        C.append(f"mm mobs spawn astral_mina_control_{s['id']} 1 {WORLD},{x},{y},{z}")
    C += [f"execute in minecraft:{WORLD} run forceload remove -80 -300 160 -60",
          "# --- 4) vendedor de la entrada: parate en el lobby donde lo quieras y (con mob-spawning allow en el lobby):",
          f"#   /mm mobs spawn {LOBBY_NPC}",
          "# --- para reiniciar una sala trabada: mm mobs kill astral_mina_control_salaN y volver a spawnearla"]
    return "\n".join(C) + "\n"


def main():
    for sub in ("mobs", "skills"):
        os.makedirs(os.path.join(OUT, "mythicmobs", sub), exist_ok=True)
    os.makedirs(os.path.join(OUT, "mazmorra"), exist_ok=True)
    open(os.path.join(OUT, "mythicmobs", "mobs", "mazmorra.yml"), "w", encoding="utf-8").write(mob_yml())
    open(os.path.join(OUT, "mythicmobs", "skills", "mazmorra.yml"), "w", encoding="utf-8").write(skill_yml())
    open(os.path.join(OUT, "mazmorra", "comandos.txt"), "w", encoding="utf-8").write(commands())
    print(f"mazmorra: {len(MOBS)} mobs, {len(SALAS)} salas")


if __name__ == "__main__":
    main()
