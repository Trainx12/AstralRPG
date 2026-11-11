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
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from explosion_protection import commands as explosion_commands

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
                              skills=["skill{s=PET_GANAR_GOLEM} @trigger ~onDeath 0.15",      # mascota (mascotas.py)
                                      "throw{velocity=7;velocityY=3} @target ~onAttack 0.4",
                                      "skill{s=MINA_ONDA_GOLEM} @self ~onTimer:140"]),
    # Jefe final con geometria propia; conserva ID, fases y balance de la Tanda 2.
    "astral_mina_guardian": dict(type="IRON_GOLEM", name="&2&lColoso Musgoso de las Profundidades", hp=1000, dmg=16, speed=0.24,
                                 boss="PURPLE", hostile=True, model=("astral_coloso_musgoso", 2.0, None), money=1500,
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
         oleadas=[[("astral_mina_guardian", 1, 0)]], extra=["astral_mina_minero"],
         final_npcs={"cofre": (40.5, 24, -225.5)}),  # cofre donde llegan a la sala
]
LOBBY_NPC = "astral_npc_mina"
from mobs.tanda3c import npc_skills  # noqa: E402
PREMIO = [("esencia_elite", 4), ("alma_corrupta", 2), ("gema_luminica", 1), ("cristal_refinado", 1)]
PREMIO_PLATA = 2500

MINA = dict(key="mina", name="Minas Olvidadas", world=WORLD, mobs=MOBS, rooms=SALAS,
            npc=LOBBY_NPC, reward=PREMIO, money=PREMIO_PLATA, cooldown=COOLDOWN,
            event="mina", enabled=True)

from mobs.tanda2 import configure, transform
configure(MINA)


def finish(text, dungeon):
    """Solo cambia los identificadores propios del motor; las Minas conservan sus IDs."""
    if dungeon["key"] == "mina":
        return text
    key = dungeon["key"]
    return (text.replace("MINA_", key.upper() + "_")
            .replace("astral_mina_", f"astral_{key}_")
            .replace("astral.mina.cd", f"astral.{key}.cd")
            .replace("tag=mina.", f"tag={key}.")
            .replace("Minas Olvidadas", dungeon["name"])
            .replace("El Guardian de las Profundidades cayo!", "La prueba termino!")
            .replace("Cofre de la Mina", "Cofre de " + dungeon["name"])
            .replace("cofre de la mina", "cofre de esta mazmorra")
            .replace("[&7Mina&8]", "[&7" + dungeon["name"] + "&8]"))


def tipos_sala(s):
    return ",".join(sorted({m for ol in s["oleadas"] for (m, _, _) in ol} | set(s.get("extra", []))))


def mob_yml(dungeon=None):
    dungeon = dungeon or MINA
    MOBS, SALAS, LOBBY_NPC = dungeon["mobs"], dungeon["rooms"], dungeon["npc"]
    L = ["# Mazmorra Minas Olvidadas (generado por datapack-src/mobs/mazmorra.py)", ""]
    for mid, d in MOBS.items():
        L += [f"{mid}:", f"  Type: {d['type']}", f"  Display: {q(d['name'])}", f"  Health: {d['hp']}", f"  Damage: {d['dmg']}",
              "  Options:", f"    MovementSpeed: {d['speed']}", "    PreventOtherDrops: true", "    PreventSunburn: true", "    PreventRandomEquipment: true",
              "    Despawn: false", "    FollowRange: 32", "    Glowing: true"]
        if d.get("boss"):
            if not d.get('model'):
                L.append('    Scale: 2.0')
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
        sk.append(f'command{{c="eco give <trigger.name> {d["money"]}"}} @trigger ~onDeath ?~isplayer')
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
        # Sala de jefe: alcanza con que muera el jefe. Sus ayudantes (y los husks del
        # desierto) no deben trabar el final; se limpian en LIMPIA.
        fin_cond = ("?hastag{tag=mina.jefe.derrotado}" if s.get("require_boss_death")
                    else f"?mobsinradius{{types={tipos};a=0;r={r + 8}}}")
        sk.append(f"skill{{s=MINA_{S}_LIMPIA}} @self ~onTimer:20 ?hastag{{tag=mina.ola{n}}} ?!hastag{{tag=mina.fin}} ?!hastag{{tag=mina.espera}} "
                  + fin_cond)
        sk.append(f"skill{{s=MINA_{S}_RESET}} @self ~onTimer:200 ?hastag{{tag=mina.on}} ?!playerwithin{{d={r + 8}}}")
        L += [f"astral_mina_control_{s['id']}:", "  Type: ARMOR_STAND", f"  Display: {q('Control ' + s['name'])}", "  Health: 100",
              "  Options:", "    Invisible: true", "    Marker: true", "    Invincible: true", "    Silent: true", "    NoGravity: true",
              "    Despawn: false", "    Persistent: true", "    Collidable: false", "  Skills:"] + ["  - " + q(x) for x in sk] + [""]
    # cofre y guia que aparecen al ganar (solo si la sala final los pide)
    if SALAS[-1].get("final_npcs"):
        quieto = ["    NoAI: true", "    Invincible: true", "    Silent: true", "    Despawn: false", "    Persistent: true",
                  "    Collidable: false", "    PreventItemPickup: true", "    PreventOtherDrops: true", "    AlwaysShowName: true"]
        L += ["astral_mina_cofre:", "  Type: SHEEP", f"  Display: {q('&6&lCofre de Minas Olvidadas &7(clic)')}", "  Health: 100",
              "  Options:"] + quieto + ["  Skills:", "  - cancelevent @self ~onInteract",
              "  - model{m=astral_cofre_rpg} @self ~onSpawn", "  - model{m=astral_cofre_rpg} @self ~onLoad",
              "  - state{s=open} @self ~onInteract",
              # El botin se ve y se cobra en la ventana del cofre (cofre_mazmorra.py).
              "  - " + q(f'command{{c="dm open cofre_{dungeon['key']} <trigger.name>"}} @self ~onInteract'), ""]
        L += ["astral_mina_guia:", "  Type: VILLAGER", f"  Display: {q('&b&lExpediciones Astrales &7- elegir destino')}",
              "  Health: 100", "  Options:"] + quieto + ["    Profession: CARTOGRAPHER", "    VillagerType: PLAINS",
              "  Skills:", "  - cancelevent @self ~onInteract"] + ["  - " + s for s in npc_skills('guia', dungeon['key'])] + [
              "  - " + q('command{c="dm open expediciones <trigger.name>"} @self ~onInteract'), ""]
    # Entradas escondidas en salas secretas: no mostrar el nombre tras paredes.
    # vendedor del lobby
    L += [f"{LOBBY_NPC}:", "  Type: VILLAGER", f"  Display: {q('&8&lMazmorra: &7Minas Olvidadas')}", "  Health: 100", "  Options:",
          "    NoAI: true", "    Invincible: true", "    Silent: true", "    Despawn: false", "    Persistent: true",
          "    Collidable: false", "    PreventItemPickup: true", "    PreventOtherDrops: true", "    AlwaysShowName: false",
          "    Profession: MASON", "    VillagerType: PLAINS", "  Skills:", "  - cancelevent @self ~onInteract"] + [
          "  - " + s for s in npc_skills('entrada', dungeon['key'])] + [
          "  - " + q(f'command{{c="lp user <trigger.name> permission set astral.descubierto.{dungeon["key"]} true"}} @self ~onInteract ?~!haspermission{{p=astral.descubierto.{dungeon["key"]}}}'),
          "  - " + q('message{m="&aDestino descubierto. &7Ya puedes encontrarlo en &e/mazmorras&7."} @trigger ~onInteract'),
          "  - " + q("skill{s=MINA_ENTRAR} @trigger ~onInteract"), ""]
    return transform(finish("\n".join(L) + "\n", dungeon) + dungeon.get("mob_blocks", ""), dungeon, 'mobs')


def tp(x, y, z, who="<target.name>", world=WORLD):
    return f'command{{c="execute in minecraft:{world} run minecraft:tp {who} {x} {y} {z}"}}'


def located_summon(mob, point):
    x, y, z = point
    return f"summon{{type={mob};amount=1;radius=0}} @Location{{x={x};y={y};z={z}}}"


def group_wave_skills(room, world):
    """Refuerzos sin limite artificial ni expresiones que requieran Premium.

    El contador pertenece al UUID del controlador y se toma al comenzar cada ola.
    Cada llamada consume uno (o dos) de los jugadores por encima de la base de dos.
    """
    lines = []
    S = room["id"].upper()
    x, y, z = room["centro"]
    for k, (mob, amount, players_per_batch) in room.get("group_scaling", {}).items():
        name = f"MINA_{S}_GRUPO{k}"
        points = room["golem_points"] if mob.endswith("_golem") else room["spawn_points"]
        choices = [f"{name}_P{i}" for i in range(len(points))]
        lines += [name + ":", "  Skills:",
                  "  - " + q(f'command{{c="execute in minecraft:{world} positioned {x} {y} {z} store result score <caster.uuid> ad.party run execute if entity @a[distance=..{room["r"]},gamemode=!spectator]"}} @self'),
                  "  - " + q('command{c="scoreboard players remove <caster.uuid> ad.party 2"} @self'),
                  "  - " + q(f"skill{{s={name}_LOOP}} @self"), "",
                  name + "_LOOP:", "  Conditions:",
                  f"  - score{{o=ad.party;v=>{players_per_batch - 1}}} true", "  Skills:",
                  "  - " + q(f'command{{c="scoreboard players remove <caster.uuid> ad.party {players_per_batch}"}} @self')]
        lines += ["  - " + q("randomskill{skills=" + ",".join(choices) + "} @self")] * amount
        lines += ["  - " + q(f"skill{{s={name}_LOOP}} @self"), ""]
        for name, point in zip(choices, points):
            lines += [name + ":", "  Skills:", "  - " + q(located_summon(mob, point)), ""]
    return lines


def skill_yml(dungeon=None):
    dungeon = dungeon or MINA
    MOBS, SALAS, WORLD = dungeon["mobs"], dungeon["rooms"], dungeon["world"]
    PREMIO, PREMIO_PLATA, COOLDOWN = dungeon["reward"], dungeon["money"], dungeon["cooldown"]
    L = ["# Mazmorra Minas Olvidadas (generado por datapack-src/mobs/mazmorra.py)", ""]
    for mid, d in MOBS.items():
        if d.get("model"):
            m, sc, col = d["model"]
            L += [f"MINA_MODELO_{mid}:", "  Skills:", "  - addtag{tag=astral.seen} @self", f"  - model{{m={m};s={sc}}} @self",
                  *(["  - delay 2", f"  - tint{{c={col}}} @self"] if col else []), ""]
            if dungeon.get('tanda2'):
                from mobs.tamanos import skills as size_skills
                L[-1:-1] = ['  - '+x for x in size_skills(m,sc,d['type'],protect_sanctuary=(mid!='astral_mina_guardian'))]
    model_skills = L[:]
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
    if dungeon["key"] != "mina":
        L = ["# Mazmorra " + dungeon["name"] + " (generada por mazmorra.py)"] + model_skills[1:]
    for i, s in enumerate(SALAS):
        S = s["id"].upper()
        r = s["r"]
        sig = SALAS[i + 1] if i + 1 < len(SALAS) else None

        def ola(k):
            if dungeon.get('tanda2'):
                return []  # tanda2.transform agrega la cola vanilla y el jefe exacto
            out = []
            spawn_radius = s.get("spawn_radius", 4)
            index = 0
            for (m, base, extra) in s["oleadas"][k - 1]:
                if "spawn_points" in s:
                    points = s["golem_points"] if m.endswith("_golem") else s["spawn_points"]
                    for _ in range(base):
                        out.append(q(located_summon(m, points[index % len(points)])))
                        index += 1
                    continue
                out.append(q(f"summon{{type={m};amount={base};radius={spawn_radius}}} @self"))
                if extra:
                    out.append(q(f"summon{{type={m};amount={extra};radius={spawn_radius}}} @self ?playersinradius{{r={r};a=>1}}"))
            if k in s.get("group_scaling", {}):
                out.append(q(f"skill{{s=MINA_{S}_GRUPO{k}}} @self"))
            return ["  - " + x for x in out]
        L += group_wave_skills(s, WORLD)
        n = len(s["oleadas"])
        L += [f"MINA_{S}_INICIO:", "  Skills:",
              *(["  - removetag{tag=mina.jefe.derrotado} @self", "  - addtag{tag=mina.espera} @self"] if s.get("require_boss_death") else []),
              "  - addtag{tag=mina.on} @self", "  - addtag{tag=mina.ola1} @self",
              "  - " + q(f'message{{m="&8[&7Mina&8] &f{s["name"]} &7- sala {i + 1}/{len(SALAS)}. &cAhi vienen!"}} @PlayersInRadius{{r={r + 8}}}'),
              "  - " + q("sound{s=entity.warden.emerge;v=0.6;p=1.4} @PlayersInRadius{r=" + str(r + 8) + "}")] + ola(1) + \
             (["  - delay 10", "  - removetag{tag=mina.espera} @self"] if s.get("require_boss_death") else []) + [""]
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
            L += [f"MINA_IR_{sig['id'].upper()}:", "  Skills:", "  - " + q(tp(*sig["llegada"], world=WORLD)),
                  "  - " + q("sound{s=entity.enderman.teleport}"), ""]
        else:
            # sala final: premio y vuelta al lobby
            L += [f"MINA_{S}_LIMPIA:",
                  *(["  Conditions:", "  - hastag{tag=mina.jefe.derrotado} true", "  - hastag{tag=mina.fin} false"] if s.get("require_boss_death") else []),
                  "  Skills:", "  - addtag{tag=mina.fin} @self",
                  *(["  - " + q(f"remove @MobsInRadius{{r={r + 8};types={tipos_sala(s)}}}")] if s.get("require_boss_death") else []),
                  "  - " + q(f'message{{m="&6&lEl Guardian de las Profundidades cayo! &7Abran el cofre..."}} @PlayersInRadius{{r={r + 8}}}'),
                  "  - " + q("sound{s=ui.toast.challenge_complete} @PlayersInRadius{r=" + str(r + 8) + "}"),
                  "  - " + q(f'command{{c="execute as <target.name> at @s run function astral:quest/event/{dungeon["event"]}"}} @PlayersInRadius{{r={r + 8}}}'),
                  # Permanente: abre la expedicion de la mazmorra siguiente (viajes_mazmorras.py).
                  "  - " + q(f'command{{c="lp user <target.name> permission set astral.completada.{dungeon["key"]} true"}} @PlayersInRadius{{r={r + 8}}}')]
            fin = s.get("final_npcs")
            if fin:
                # Sin teletransporte: aparece un cofre (se cobra con clic) y el guia de
                # Expediciones, que los lleva a donde quieran. RESET los quita cuando se van.
                L += ["  - " + q(f"remove @MobsInRadius{{r={r + 8};types=astral_mina_cofre,astral_mina_guia}}"),
                      "  - " + q("summon{type=astral_mina_cofre;amount=1;radius=0} @Location{x=%s;y=%s;z=%s}" % fin["cofre"])]
                if fin.get("guia"):
                    L += ["  - " + q("summon{type=astral_mina_guia;amount=1;radius=0} @Location{x=%s;y=%s;z=%s}" % fin["guia"])]
                if dungeon["key"] == "mina":
                    # La mascota Golem sigue saliendo al 5% al ganar (antes venia con el cofre).
                    L += ["  - " + q(f"skill{{s=MINA_MASCOTA}} @PlayersInRadius{{r={r + 8}}}")]
                guia = "&7El guia de Expediciones los lleva a donde quieran." if fin.get("guia") else "&7Desde el cofre pueden volver al lobby."
                L += ["  - delay 20",
                      "  - " + q(f'message{{m="&eAparecio el cofre del jefe: &fclic para ver el botin&e. {guia}"}} @PlayersInRadius{{r={r + 8}}}'), ""]
            else:
                L += ["  - delay 40",
                      "  - " + q(f"skill{{s=MINA_PREMIO}} @PlayersInRadius{{r={r + 8}}}"),
                      "  - " + q(f"skill{{s=MINA_PREMIO_YA}} @PlayersInRadius{{r={r + 8}}}"),
                      "  - " + q(f'message{{m="&7En 15 segundos vuelven al lobby."}} @PlayersInRadius{{r={r + 8}}}'),
                      "  - delay 300",
                      "  - " + q(f'command{{c="spawn <target.name>"}} @PlayersInRadius{{r={r + 8}}}'),
                      "  - delay 20",
                      "  - removetag{tag=mina.on} @self", "  - removetag{tag=mina.fin} @self"] + \
                     [f"  - removetag{{tag=mina.ola{k}}} @self" for k in range(1, n + 1)] + [""]
        tipos = tipos_sala(s)
        if i == len(SALAS) - 1 and s.get("final_npcs"):
            tipos += ",astral_mina_cofre,astral_mina_guia"
        L += [f"MINA_{S}_RESET:", "  Skills:", "  - " + q(f"remove @MobsInRadius{{r={r + 8};types={tipos}}}"),
              *(["  - removetag{tag=mina.jefe.derrotado} @self"] if s.get("require_boss_death") else []),
              "  - removetag{tag=mina.on} @self", "  - removetag{tag=mina.fin} @self", "  - removetag{tag=mina.espera} @self"] + \
             [f"  - removetag{{tag=mina.ola{k}}} @self" for k in range(1, len(s["oleadas"]) + 1)] + [""]
    # premio final (una vez cada 30 minutos por jugador)
    L += ["MINA_PREMIO:", "  TargetConditions:", "  - haspermission{p=astral.mina.cd} false", "  Skills:"]
    for it, n in PREMIO:
        L += ["  - " + q(f'command{{c="loot give <target.name> loot astral:item/{it}"}}')] * n
    L += ["  - " + q('command{c="loot give <target.name> loot astral:item/chispa_astral"} 0.25'),
          "  - " + q(f'command{{c="eco give <target.name> {PREMIO_PLATA}"}}'),
          *( ["  - " + q("skill{s=PET_GANAR_GOLEM} 0.05")] if dungeon["key"] == "mina" else [] ),
          "  - " + q(f'command{{c="lp user <target.name> permission settemp astral.mina.cd true {COOLDOWN}"}}'),
          "  - " + q(f'message{{m="&6Cofre de la Mina: &fmateriales de elite y &e{PREMIO_PLATA}$&f. &7(el proximo cofre en 30 minutos)"}}'),
          "",
          "MINA_PREMIO_YA:", "  TargetConditions:", "  - haspermission{p=astral.mina.cd} true", "  Skills:",
          "  - " + q('message{m="&7Ya cobraste el cofre de la mina hace poco. &8(se puede cobrar cada 30 minutos)"}'), ""]
    if dungeon["key"] == "mina":
        L += ["MINA_MASCOTA:", "  TargetConditions:", "  - haspermission{p=astral.mina.cd} false", "  Skills:",
              "  - " + q("skill{s=PET_GANAR_GOLEM} 0.05"), ""]
    # entrada desde el lobby
    s1 = SALAS[0]
    if not dungeon.get("enabled", False):
        L += ["MINA_ENTRAR:", "  Skills:", "  - " + q('message{m="&eEsta mazmorra esta en preparacion. Falta revisar las salas en Minecraft."}'), ""]
        return finish("\n".join(L) + "\n", dungeon)
    L += ["MINA_ENTRAR:"]
    L += ["  Skills:",
          "  - " + q(f'message{{m="&8[&7Mina&8] &7Bajando a las &fMinas Olvidadas&7... &8({len(SALAS)} salas. Para salir: /spawn)"}}'),
          "  - " + q(tp(*s1["llegada"], who="<trigger.name>", world=WORLD)), ""]
    return transform(finish("\n".join(L) + "\n", dungeon), dungeon, 'skills')


def espera_cofre(key):
    # Un OP tiene todo permiso que nadie definio, asi que el cofre le decia "ya cobraste".
    # El false del grupo default le gana al OP; el settemp de 30 min del jugador le gana al false.
    return ["# espera del cofre: false para todos (sin esto el cofre no le paga a los OP)",
            f"lp group default permission set astral.{key}.cd false"]


def commands(dungeon=None):
    dungeon = dungeon or MINA
    if dungeon.get('tanda2'):
        from mobs.entrega_tanda2 import upgrade_commands
        return upgrade_commands(dungeon) + '\n' + '\n'.join(espera_cofre(dungeon['key'])) + '\n' + ('\n'.join(__import__('cofre_mazmorra').lp_defaults())+'\n' if dungeon['key']=='mina' else '')
    if dungeon["key"] != "mina":
        return new_commands(dungeon)
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
         f"mv gamerule set minecraft:random_tick_speed 0 {WORLD}",
         f"mv gamerule set minecraft:advance_time false {WORLD}",
         f"execute in minecraft:{WORLD} run time set midnight",
         f"rg flag -w {WORLD} __global__ build deny",
         *explosion_commands(WORLD),
         f"rg flag -w {WORLD} __global__ chest-access deny",
         # clic en cofres y aldeanos de MythicMobs (build deny los bloquea); puertas y botones siguen bloqueados
         f"rg flag -w {WORLD} __global__ interact allow",
         f"rg flag -w {WORLD} __global__ use deny",
         f"rg flag -w {WORLD} __global__ mob-spawning allow",
         f"rg flag -w {WORLD} __global__ pvp deny",
         *espera_cofre("mina"),
         "# coleccion de Fragmentos Astrales (/fragmentos): false para todos, igual que la espera",
         *__import__("cofre_mazmorra").lp_defaults(),
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
    from arena import generate as generate_arena
    from mazmorras_data import catalog
    MAZMORRAS = [MINA] + catalog()
    for sub in ("mobs", "skills"):
        os.makedirs(os.path.join(OUT, "mythicmobs", sub), exist_ok=True)
    os.makedirs(os.path.join(OUT, "mazmorra"), exist_ok=True)
    open(os.path.join(OUT, "mythicmobs", "mobs", "mazmorra.yml"), "w", encoding="utf-8").write(mob_yml())
    open(os.path.join(OUT, "mythicmobs", "skills", "mazmorra.yml"), "w", encoding="utf-8").write(skill_yml())
    open(os.path.join(OUT, "mazmorra", "comandos.txt"), "w", encoding="utf-8").write(commands())
    for dungeon in MAZMORRAS[1:]:
        filename = dungeon["key"] + ".yml"
        for sub, content in (("mobs", mob_yml(dungeon)), ("skills", skill_yml(dungeon))):
            open(os.path.join(OUT, "mythicmobs", sub, filename), "w", encoding="utf-8").write(content)
        folder = os.path.join(OUT, "mazmorras", dungeon["key"])
        os.makedirs(folder, exist_ok=True)
        open(os.path.join(folder, "comandos.txt"), "w", encoding="utf-8").write(commands(dungeon))
    print(f"mazmorra: {len(MOBS)} mobs, {len(SALAS)} salas")
    generate_arena()


def new_commands(dungeon):
    w = dungeon["world"]
    lines = [f'# {dungeon["name"]} - ubicaciones propuestas, revisar en creativo antes de habilitar.',
             '# Editar enabled y coordenadas en datapack-src/mobs/mazmorras_data.py y regenerar.',
             '# Crear un mundo NUEVO. Nunca subir nada sobre world ni sobre mina.',
             f'mv create {w} normal --world-type FLAT --no-structures --no-adjust-spawn '
             '--generator-settings {"layers":[{"block":"minecraft:air","height":1}],"biome":"minecraft:the_void"}',
             f'# Apagar el servidor y copiar SOLO las regiones recortadas a world/dimensions/minecraft/{w}/region.',
             '# Ver docs/MAZMORRAS.md para preparar los recortes sin datapacks ni entidades del mapa original.',
             f'mv modify {w} set difficulty hard', f'mv modify {w} set gamemode survival',
             f'mv modify {w} set pvp false', f'mv modify {w} set allow-weather false',
             f'mv gamerule set minecraft:spawn_mobs false {w}', f'mv gamerule set minecraft:keep_inventory true {w}',
             f'mv gamerule set minecraft:random_tick_speed 0 {w}',
             f'rg flag -w {w} __global__ build deny', f'rg flag -w {w} __global__ chest-access deny',
             f'rg flag -w {w} __global__ pvp deny', f'rg flag -w {w} __global__ mob-spawning allow',
             f'rg flag -w {w} __global__ interact allow', f'rg flag -w {w} __global__ use deny',
             *(explosion_commands(w) if dungeon['key'] != 'santuario' else []),
             *espera_cofre(dungeon["key"]),
             '# RECORRIDO DE REVISION (OP en creativo; el mapa tiene que estar cargado):']
    if any(s.get("group_scaling") for s in dungeon["rooms"]):
        lines += ['# Contador de jugadores para los refuerzos (una vez; si ya existe, conservarlo).',
                  'scoreboard objectives add ad.party dummy']
    for room in dungeon["rooms"]:
        x,y,z = room["llegada"]
        lines += [f'# {room["name"]}: execute in minecraft:{w} run minecraft:tp <jugador> {x} {y} {z}',
                  '# Confirmar piso, techo, recorrido y espacio para el jefe. Son sugerencias, no puntos probados.']
    lines += ['# DESPUES de revisar las coordenadas y cambiar enabled=True:']
    for room in dungeon["rooms"]:
        x,y,z=room["centro"]
        lines += [f'# execute in minecraft:{w} run forceload add {int(x)} {int(z)}',
                  f'# mm mobs spawn astral_{dungeon["key"]}_control_{room["id"]} 1 {w},{x},{y},{z}',
                  f'# execute in minecraft:{w} run forceload remove {int(x)} {int(z)}']
    lines += [f'# NPC de entrada (en el lobby): mm mobs spawn {dungeon["npc"]}',
              '# Los jefes y mobs del mundo normal conservan sus apariciones.']
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
