"""Historia y 14 diarias, sin plugins nuevos. Lo invoca build.py.

El datapack guarda progreso; MythicMobs aporta la fecha real, dinero y permisos.
Los fragmentos son recuerdos: la victoria personal es la prueba, no un item
intercambiable. Asi perderlos al morir no bloquea la historia.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NS = "astral"
CHAPTERS = [
    "Llegar al Refugio: habla con el Herrero y forja una pieza de tier I.",
    "Los campos: mata 10 Espantapajaros, 10 Abejorros y 1 elite; entrega 3 Esencias al Viajero.",
    "La marea: derrota al Cangrejo en las playas y volve con el Viajero.",
    "El bosque: mata 15 Caras Voladoras y derrota al Chaman.",
    "Arena con memoria: derrota a la Momia.",
    "Minas Olvidadas: completa las cuatro salas.",
    "El silencio blanco: derrota al Yeti.",
    "El corazon de la forja: forja una pieza tier V y derrota al Golem de Forja.",
    "Encender la estrella: habla con el Viajero para reunir los fragmentos.",
]
# id, dificultad, nombre, objetivo, meta, descripcion
DAILIES = [
    (1, 0, "Ronda nocturna", "hostil", 15, "Mata 15 hostiles de AstralRPG"),
    (2, 0, "Provisiones", None, 0, "Entrega 32 panes o 32 carnes cocidas del mismo tipo a la Tienda"),
    (3, 0, "Madera para el Refugio", None, 0, "Entrega 64 troncos al Cronista"),
    (4, 0, "Piedra y hierro", None, 0, "Entrega 64 piedras y 16 lingotes de hierro al Herrero"),
    (5, 0, "Plaga de aranas", "spider", 10, "Mata 10 Aranas Amatista"),
    (6, 1, "Caza de elites", "elite", 3, "Mata 3 elites vanilla o de MythicMobs"),
    (7, 1, "Encargo del Bazar", None, 0, "Entrega 5 Esencias de Elite al Bazar"),
    (8, 1, "Explorador", "biomes", 3, "Visita 3 zonas distintas: desierto, nieve, pantano, bosque, llanura, Nether"),
    (9, 1, "Mascota entrenada", "pet", 25, "Mata 25 mobs con una mascota seleccionada, fuera del lobby"),
    (10, 1, "Jinete", "ride", 100000, "Recorre 1000 bloques en una montura terrestre"),
    (11, 2, "Expedicion a las Minas", "mine", 1, "Completa las Minas Olvidadas"),
    (12, 2, "Cazador de jefes", "boss", 1, "Derrota a un jefe"),
    (13, 2, "Pesadilla", "nightmare", 1, "Mata un elite vanilla de tier IV o V"),
    (14, 2, "Mejora arriesgada", "upgrade", 1, "Intenta una mejora +5 o mayor en el Herrero"),
]
COUNTERS = ["hostil", "spider", "elite", "biomes", "pet", "ride", "mine", "boss", "nightmare", "upgrade"]
STORY = {"cangrejo": (3, 1, "fragmento_marea"), "chaman": (4, 2, "fragmento_pantano"),
         "momia": (5, 3, "fragmento_arena"), "mina": (6, 4, "lampara_minero"),
         "yeti": (7, 5, "fragmento_hielo"), "golem_forja": (8, 6, "fragmento_fuego")}


def generate(files, items):
    def fn(name, lines):
        files[f"data/{NS}/function/quest/{name}.mcfunction"] = "\n".join(lines) + "\n"

    def msg(text, color="gray"):
        return "tellraw @s " + json.dumps({"text": text, "color": color}, ensure_ascii=False)

    def call(name):
        return f"function {NS}:quest/{name}"

    def obj(name):
        # Los placeholders de MythicMobs separan campos por puntos. El objetivo
        # de dinero necesita un nombre simple para <target.score.aqmoney>.
        return "aqmoney" if name == "money" else f"aq.{name}"

    def money(amount):
        return f"scoreboard players add @s aqmoney {amount}"

    def inc(counter, amount=1):
        command = f"scoreboard players add @s aq.{counter} {amount}"
        daily = next((d for d in DAILIES if d[3] == counter), None)
        if counter in ("scare", "bee", "face", "helite"):
            return f"execute if score @s aq.accepted matches 1 run {command}"
        return f"execute if score @s aq.active{daily[1]} matches 1 run {command}" if daily else command

    objectives = COUNTERS + ["state", "money", "herrero", "forge1", "forge5", "scare", "bee", "face", "helite",
                             "day", "streak", "last", "mask", "horse", "hbase", "tmp", "clock", "reward"]
    objectives += [f"f{i}" for i in range(1, 7)]
    objectives += ["accepted", "page"] + [f"active{i}" for i in range(3)]
    objectives += [f"d{i}" for i in range(3)] + [f"done{i}" for i in range(3)]
    load = [f"scoreboard objectives add {obj(o)} dummy" for o in objectives if o not in ("horse", "reward")]
    load += ["scoreboard objectives add aq.journal trigger",
             "scoreboard objectives add aq.horse minecraft.custom:minecraft.horse_one_cm",
             "scoreboard objectives add aq.reward trigger",
             "scoreboard players set #seconds aq.clock 86400",
             "scoreboard players set #offset aq.clock -10800",  # medianoche Argentina (UTC-3)
             "scoreboard players set #two aq.clock 2",
             "scoreboard players set #five aq.clock 5",
             "scoreboard players set #four aq.clock 4"]
    fn("load", load)
    # La fecha real llega de MythicMobs, no del tiempo acelerado de Minecraft.
    fn("clock", [
        "scoreboard players operation #today aq.clock = #epoch aq.clock",
        "scoreboard players operation #today aq.clock += #offset aq.clock",
        "scoreboard players operation #today aq.clock /= #seconds aq.clock",
        "execute unless score #today aq.clock = #rolled aq.clock run " + call("roll"),
    ])
    fn("roll", [
        "scoreboard players operation #rolled aq.clock = #today aq.clock",
        "execute store result score #easy aq.clock run random value 1..5",
        "execute store result score #medium aq.clock run random value 6..10",
        "execute store result score #hard aq.clock run random value 11..14",
    ])
    init = [f"scoreboard players add @s {obj(o)} 0" for o in objectives if o not in ("horse", "reward", "day")]
    fn("init", init + ["tag @s add aq.ready", "tag @s add aq.gui", "scoreboard players add @s aq.horse 0"])
    fn("gui/migrate", [
        "scoreboard players set @s aq.page 0",
        "scoreboard players set @s aq.accepted 0",
        "execute if score @s aq.state matches 1..9 run scoreboard players set @s aq.accepted 1",
        *[f"scoreboard players set @s aq.active{i} 1" for i in range(3)],
        "tag @s add aq.gui",
    ])
    fn("sync", [
        "execute unless entity @s[tag=aq.ready] run " + call("init"),
        "execute unless entity @s[tag=aq.gui] run " + call("gui/migrate"),
        "execute if score #today aq.clock matches 1.. unless score @s aq.day = #today aq.clock run " + call("new_day"),
    ])
    fn("new_day", [
        "scoreboard players operation @s aq.day = #today aq.clock",
        "scoreboard players operation @s aq.d0 = #easy aq.clock",
        "scoreboard players operation @s aq.d1 = #medium aq.clock",
        "scoreboard players operation @s aq.d2 = #hard aq.clock",
        "scoreboard players operation @s aq.hbase = @s aq.horse",
        "scoreboard players set @s aq.mask 0",
    ] + [f"scoreboard players set @s aq.done{i} 0" for i in range(3)]
      + [f"scoreboard players set @s aq.active{i} 0" for i in range(3)]
      + [f"scoreboard players set @s aq.{c} 0" for c in COUNTERS])
    fn("tick", [
        "execute as @a at @s run " + call("sync"),
        "execute as @a[scores={aq.d1=8,aq.done1=0,aq.active1=1}] at @s unless dimension minecraft:arena unless dimension minecraft:lobby run " + call("explore"),
        "execute as @a[scores={aq.d1=10,aq.done1=0,aq.active1=1}] at @s run " + call("ride"),
        "scoreboard players enable @a aq.reward",
        "scoreboard players enable @a aq.journal",
        "execute as @a[scores={aq.journal=1..}] at @s run " + call("journal"),
        "execute as @a[scores={aq.reward=1..}] run " + call("choice"),
    ])
    fn("ride", ["scoreboard players operation #delta aq.tmp = @s aq.horse",
                "scoreboard players operation #delta aq.tmp -= @s aq.hbase",
                "execute unless dimension minecraft:arena unless dimension minecraft:lobby if score #delta aq.tmp matches 1.. run scoreboard players operation @s aq.ride += #delta aq.tmp",
                "scoreboard players operation @s aq.hbase = @s aq.horse"])
    zones = {"desert": ["desert", "badlands"], "snow": ["snowy_plains", "frozen_peaks", "jagged_peaks", "ice_spikes"],
             "swamp": ["swamp", "mangrove_swamp"], "forest": ["forest", "dark_forest", "birch_forest"],
             "plains": ["plains", "sunflower_plains"]}
    explore = []
    for i, (zone, biomes) in enumerate(zones.items()):
        files[f"data/astral/tags/worldgen/biome/quest/{zone}.json"] = json.dumps({"values": [f"minecraft:{b}" for b in biomes]})
        explore.append(f"execute if biome ~ ~ ~ #astral:quest/{zone} run " + call(f"zone/{i}"))
    explore.append("execute if dimension minecraft:the_nether run " + call("zone/5"))
    fn("explore", explore)
    for i in range(6):
        # Un score por bit evita depender de tags que sobreviven al cambio de diaria.
        fn(f"zone/{i}", ["scoreboard players operation #bit aq.tmp = @s aq.mask",
                         f"scoreboard players set #div aq.tmp {2 ** i}",
                         "scoreboard players operation #bit aq.tmp /= #div aq.tmp",
                         "scoreboard players operation #bit aq.tmp %= #two aq.clock",
                         "execute if score #bit aq.tmp matches 1 run return 0",
                         inc("mask", 2 ** i), inc("biomes")])

    # Eventos: solo se ejecutan como un jugador. La arena queda excluida tambien
    # en los hooks, no solamente al cobrar.
    def event(name, lines):
        fn("event/" + name, ["execute if dimension minecraft:arena run return 0",
                             "execute if entity @s[gamemode=spectator] run return 0", call("sync")] + lines)

    event("hostil", [inc("hostil")])
    event("espantapajaros", [call("event/hostil"), "execute if score @s aq.state matches 2 run " + inc("scare")])
    event("abejorro", [call("event/hostil"), "execute if score @s aq.state matches 2 run " + inc("bee")])
    event("cara", [call("event/hostil"), "execute if score @s aq.state matches 4 run " + inc("face")])
    event("arana", [call("event/hostil"), inc("spider")])
    event("elite", [inc("elite"), "execute if score @s aq.state matches 2 run " + inc("helite")])
    event("nightmare", [inc("nightmare")])
    event("pet", ["execute unless dimension minecraft:lobby if score @s petsel matches 1..6 run " + inc("pet")])
    event("upgrade", [inc("upgrade")])
    event("forge1", ["execute if score @s aq.accepted matches 1 if score @s aq.state matches 1 run scoreboard players set @s aq.forge1 1"])
    event("forge5", ["execute if score @s aq.accepted matches 1 if score @s aq.state matches 8 run scoreboard players set @s aq.forge5 1"])
    for boss, (state, flag, item) in STORY.items():
        event(boss, [inc("mine" if boss == "mina" else "boss"),
                     f"execute if score @s aq.accepted matches 1 if score @s aq.state matches {state} if score @s aq.f{flag} matches 0 run " + call(f"fragment/{flag}")])
        fn(f"fragment/{flag}", [f"scoreboard players set @s aq.f{flag} 1",
                               f"loot give @s loot astral:item/{item}",
                               msg("Una parte de la estrella te reconoce. Volve con el Viajero.", "aqua")])

    # Solo cuenta mobs (nunca jugadores). Se revoca para volver a dispararse.
    files["data/astral/advancement/quest/pet.json"] = json.dumps({
        "criteria": {"kill": {"trigger": "minecraft:player_killed_entity", "conditions": {"entity": [
            {"condition": "minecraft:inverted", "term": {"condition": "minecraft:entity_properties", "entity": "this",
             "predicate": {"type": "minecraft:player"}}}]}}}, "rewards": {"function": "astral:quest/pet_kill"}})
    fn("pet_kill", ["advancement revoke @s only astral:quest/pet", call("event/pet")])

    # Click normal conversa; agacharse conserva el viaje al mundo.
    fn("gui/accept", [call("sync"),
        "execute if score @s aq.state matches 0 run " + call("start"),
        "execute if score @s aq.state matches 1..9 run scoreboard players set @s aq.accepted 1",
        msg("Mision aceptada. Consulta el objetivo y el premio en el objeto central del menu.", "green")])
    fn("gui/reject", [call("sync"), "scoreboard players set @s aq.accepted 0",
        msg("Mision rechazada o pausada. Conservas tus avances y podes aceptarla mas tarde.", "yellow")])
    for state in range(10):
        chapter = max(1, state)
        amount = [300, 500, 1000, 1500, 2000, 2500, 3000, 5000, 10000][chapter - 1]
        fn(f"gui/details/story/{state}", [msg(CHAPTERS[chapter - 1], "aqua"),
            msg(f"Premio: {amount}$. Acepta la mision, completa el objetivo y usa Comprobar y cobrar.", "gold")])
    for page in range(5):
        fn(f"gui/page/{page}", [call("sync"), f"scoreboard players set @s aq.page {page}"])
    fn("viajero", [call("sync"),
        "execute unless score @s aq.accepted matches 1 run return run " + msg("Primero acepta la mision con el boton verde de /misiones.", "yellow")]
       + [f"execute if score @s aq.state matches {i} run return run " + call(f"chapter/{i}") for i in range(1, 10)]
       + [msg("La estrella vuelve a brillar. El Santuario Celestial guarda sus ecos Ancestrales.", "gold")])
    fn("start", ["scoreboard players set @s aq.state 1", msg("Viajero: la Estrella Astral se partio. Sus fragmentos corrompieron a las criaturas.", "aqua"),
                 msg("El Refugio es lo que quedo del cielo. Habla con el Herrero, forja tu primer equipo y volve.")])
    fn("herrero", [call("sync"), "execute if score @s aq.accepted matches 1 if score @s aq.state matches 1 run scoreboard players set @s aq.herrero 1",
                    "execute if score @s aq.state matches 1 run " + msg("Herrero: acercate a una mesa de herreria y forja equipo de tier I desde la Guia AstralRPG.", "gold"),
                    "execute if score @s aq.state matches 8 run " + msg("Herrero: el ultimo fragmento esta en mi antiguo golem. Forja tier V y vence al Golem de Forja.", "gold"),
                    call("deliver/herrero")])
    def complete(state, amount, extra=()):
        fn(f"complete/{state}", [f"scoreboard players set @s aq.state {state + 1}", "scoreboard players set @s aq.accepted 0", money(amount)] + list(extra)
           + [msg(f"Capitulo terminado. Recompensa: {amount}$.", "green")]
           + ([msg(CHAPTERS[state], "aqua")] if state < 9 else []))
    complete(1, 300)
    complete(2, 500, ["tag @s add aq.choice", msg("Podes elegir una armadura tier I: /trigger aq.reward set N (1-4 Berserker, 5-8 Mago, 9-12 Arquero; casco, pechera, grebas, botas).", "gold")])
    complete(3, 1000)
    complete(4, 1500)
    complete(5, 2000, ["loot give @s loot astral:item/alma_corrupta"])
    complete(6, 2500)
    complete(7, 3000, ["loot give @s loot astral:item/chispa_astral"])
    complete(8, 5000)
    complete(9, 10000, ["tag @s add aq.title", "particle minecraft:firework ~ ~4 ~ 2 3 2 0.1 100", "playsound minecraft:ui.toast.challenge_complete player @s ~ ~ ~ 1 1",
                         msg("La Estrella Astral vuelve a brillar. Sos Portador de la Estrella. El Santuario Celestial esta abierto.", "gold")])
    fn("chapter/1", ["execute if score @s aq.herrero matches 1 if score @s aq.forge1 matches 1 run return run " + call("complete/1"), msg(CHAPTERS[0])])
    pred = '*[minecraft:custom_data~{astral:{id:"esencia_elite"}}]'
    fn("chapter/2", [f"execute store result score #have aq.tmp run clear @s {pred} 0",
                     "execute if score @s aq.scare matches 10.. if score @s aq.bee matches 10.. if score @s aq.helite matches 1.. if score #have aq.tmp matches 3.. run return run " + call("fields_done"),
                     msg(CHAPTERS[1]),
                     'tellraw @s [{"text":"Espantapajaros: "},{"score":{"name":"@s","objective":"aq.scare"}},{"text":"/10 | Abejorros: "},{"score":{"name":"@s","objective":"aq.bee"}},{"text":"/10 | Elites: "},{"score":{"name":"@s","objective":"aq.helite"}},{"text":"/1"}]'])
    fn("fields_done", [f"clear @s {pred} 3", call("complete/2")])
    for boss, (state, flag, _) in STORY.items():
        cond = f"if score @s aq.f{flag} matches 1"
        if boss == "chaman": cond += " if score @s aq.face matches 15.."
        if boss == "golem_forja": cond += " if score @s aq.forge5 matches 1"
        fn(f"chapter/{state}", [f"execute {cond} run return run " + call(f"complete/{state}"), msg(CHAPTERS[state - 1])])
    fn("chapter/9", [msg("Viajero: guarde el eco de cada fragmento que trajiste. Juntos vuelven a encender la estrella.", "aqua"), call("complete/9")])
    # Los recuerdos no se consumen: no son llaves transferibles, ni ingredientes.
    # Evitar premiar tier I mas de una vez, aun repitiendo el trigger.
    choice = ["execute unless entity @s[tag=aq.choice] run return run scoreboard players set @s aq.reward 0"]
    for n, (cls, piece) in enumerate(((c, p) for c in ("berserker", "mago", "arquero") for p in ("helmet", "chestplate", "leggings", "boots")), 1):
        iid = f"{cls}_1_{piece}"
        if iid not in items:
            raise ValueError(f"Premio inexistente: {iid}")
        choice.append(f"execute if score @s aq.reward matches {n} run return run " + call(f"choice/{n}"))
        fn(f"choice/{n}", ["tag @s remove aq.choice", "scoreboard players set @s aq.reward 0", f"loot give @s loot astral:item/{iid}"])
    fn("choice", choice + ["scoreboard players set @s aq.reward 0", msg("Elegi un numero entre 1 y 12.", "red")])

    # Entregas: primero comprobar TODO y despues quitarlo, sin consumir parcialmente.
    def delivery(name, daily, variants):
        d = next(x for x in DAILIES if x[0] == daily)
        tier = d[1]
        dispatch = [call("sync"), f"execute unless score @s aq.d{tier} matches {daily} run return 0",
                    f"execute unless score @s aq.active{tier} matches 1 run return 0",
                    f"execute if score @s aq.done{tier} matches 1 run return 0"]
        for k, ingredients in enumerate(variants):
            checks = []
            for j, (item, count) in enumerate(ingredients):
                dispatch.append(f"execute store result score #ing{j} aq.tmp run clear @s {item} 0")
                checks.append(f"if score #ing{j} aq.tmp matches {count}..")
            dispatch.append("execute " + " ".join(checks) + " run return run " + call(f"delivery/{daily}/{k}"))
            fn(f"delivery/{daily}/{k}", [f"clear @s {item} {count}" for item, count in ingredients] + [call(f"daily/claim/{daily}")])
        fn(f"deliver/{name}", dispatch + [msg(d[5] + ". Todavia faltan materiales.", "yellow")])
    delivery("tienda", 2, [[(f"minecraft:{food}[!minecraft:custom_data]", 32)] for food in
                             ("bread", "cooked_beef", "cooked_porkchop", "cooked_chicken", "cooked_mutton", "cooked_rabbit")])
    delivery("cronista", 3, [[("#minecraft:logs[!minecraft:custom_data]", 64)]])
    delivery("herrero", 4, [[("minecraft:stone[!minecraft:custom_data]", 64), ("minecraft:iron_ingot[!minecraft:custom_data]", 16)]])
    delivery("bazar", 7, [[(pred, 5)]])
    show = [call("sync"), "execute unless score #today aq.clock matches 1.. run return run " + msg("El reloj de diarias no esta conectado. Avisa al administrador.", "yellow")]
    for did, tier, name, counter, goal, desc in DAILIES:
        if counter:
            show.append(f"execute if score @s aq.d{tier} matches {did} if score @s aq.done{tier} matches 0 if score @s aq.{counter} matches {goal}.. run " + call(f"daily/claim/{did}"))
        show.append(f"execute if score @s aq.d{tier} matches {did} run " + msg(f"[{tier + 1}] {name}: {desc}. Premio: {[300,750,1500][tier]}$.", "aqua"))
        show.append(f'execute if score @s aq.d{tier} matches {did} run tellraw @s [{{"text":"Cobrada (0=no, 1=si): "}},{{"score":{{"name":"@s","objective":"aq.done{tier}"}}}}]')
        claim = [f"execute unless score @s aq.d{tier} matches {did} run return 0",
                 f"execute unless score @s aq.active{tier} matches 1 run return 0",
                 f"execute if score @s aq.done{tier} matches 1 run return 0",
                 f"scoreboard players set @s aq.done{tier} 1", money([300,750,1500][tier]), msg(f"Diaria completada: {name}.", "green")]
        if did in (11,12): claim.append("loot give @s loot astral:item/alma_corrupta")
        if did == 13:
            files["data/astral/predicate/quest/chispa.json"] = json.dumps({"condition":"minecraft:random_chance", "chance":0.25})
            claim.append("execute if predicate astral:quest/chispa run loot give @s loot astral:item/chispa_astral")
        if did == 14: claim += ["loot give @s loot astral:item/esencia_elite"] * 2
        fn(f"daily/claim/{did}", claim + [call("streak")])
    fn("cronista", show + [call("deliver/cronista")])
    from lobby import NPC_POS
    delivery_npc = {2: "tienda", 3: "cronista", 4: "herrero", 7: "bazar"}
    for tier in range(3):
        fn(f"gui/daily/accept/{tier}", [call("sync"),
            "execute unless score #today aq.clock matches 1.. run return run " + msg("El reloj de diarias no esta conectado. Avisa al administrador.", "yellow"),
            f"execute if score @s aq.done{tier} matches 1 run return 0",
            "scoreboard players operation @s aq.hbase = @s aq.horse" if tier == 1 else "# Sin desplazamiento pendiente",
            f"scoreboard players set @s aq.active{tier} 1",
            msg("Diaria aceptada. Los objetivos ya cuentan; consulta los detalles en el objeto central.", "green")])
        fn(f"gui/daily/reject/{tier}", [call("sync"),
            f"execute if score @s aq.done{tier} matches 1 run return 0",
            f"scoreboard players set @s aq.active{tier} 0",
            msg("Diaria rechazada o pausada. Conservas tus avances hasta las 00:00 de Argentina.", "yellow")])
        fn(f"gui/details/daily/{tier}", [call("sync")] + [
            f"execute if score @s aq.d{tier} matches {did} run " + msg(f"{name}: {desc}. Premio: {[300,750,1500][tier]}$. Consulta los premios extra y el progreso en el menu.", "aqua")
            for did, dtier, name, counter, goal, desc in DAILIES if dtier == tier])
        claim_button = [call("sync"),
            f"execute unless score @s aq.active{tier} matches 1 run return 0"]
        for did, dtier, name, counter, goal, desc in DAILIES:
            if dtier != tier:
                continue
            if counter:
                claim_button.append(f"execute if score @s aq.d{tier} matches {did} if score @s aq.{counter} matches {goal}.. run return run " + call(f"daily/claim/{did}"))
            else:
                npc = delivery_npc[did]
                x, y, z, _ = NPC_POS["astral_npc_" + npc]
                claim_button.append(f"execute if score @s aq.d{tier} matches {did} if dimension minecraft:lobby positioned {x} {y} {z} if entity @s[distance=..6] run return run " + call(f"deliver/{npc}"))
        fn(f"gui/daily/claim/{tier}", claim_button + [msg("Todavia faltan objetivos. Para entregas, acercate al vendedor indicado y usa este boton.", "yellow")])
    for n in range(1, 13):
        fn(f"gui/choice/{n}", [
            "execute unless entity @s[tag=aq.choice] run return run " + msg("No tenes una armadura pendiente. Este premio se obtiene al cobrar el capitulo 2.", "yellow"),
            f"scoreboard players set @s aq.reward {n}", call("choice")])
    journal = ["scoreboard players set @s aq.journal 0", call("sync")]
    journal += [f"execute if score @s aq.state matches {i} run " + msg(text, "gold") for i,text in enumerate(CHAPTERS,1)]
    journal += ["execute if score @s aq.state matches 0 run " + msg("Habla con el Viajero para empezar la historia.", "gold"),
                "execute if score @s aq.state matches 10.. run " + msg("Historia completada. El Santuario Celestial te espera.", "gold")]
    for did,tier,name,counter,goal,desc in DAILIES:
        journal.append(f"execute if score @s aq.d{tier} matches {did} run " + msg(name + ": " + desc, "aqua"))
        if counter:
            journal.append(f'execute if score @s aq.d{tier} matches {did} run tellraw @s [{{"text":"Progreso: "}},{{"score":{{"name":"@s","objective":"aq.{counter}"}}}},{{"text":"/{goal}"}}]')
    fn("journal", journal + [msg("Cobra las diarias hablando con el Cronista; las entregas se hacen en el NPC indicado.")])
    event("santuario", [msg("Superaste los cinco ecos de la Estrella Astral.", "gold")])
    fn("streak", ["execute unless score @s aq.done0 matches 1 run return 0", "execute unless score @s aq.done1 matches 1 run return 0",
                  "execute unless score @s aq.done2 matches 1 run return 0", "execute if score @s aq.last = #today aq.clock run return 0",
                  "scoreboard players operation #yesterday aq.tmp = #today aq.clock", "scoreboard players remove #yesterday aq.tmp 1",
                  "execute unless score @s aq.last = #yesterday aq.tmp run scoreboard players set @s aq.streak 0",
                  inc("streak"), "scoreboard players operation @s aq.last = #today aq.clock",
                  "execute if score @s aq.streak matches 7.. run " + call("streak_reward")])
    fn("streak_reward", ["scoreboard players set @s aq.streak 0", "tag @s add aq.gacha", msg("Siete dias completos: ganaste una tirada de Gacha de Armas.", "gold")])

    # Integracion en las funciones que ya existen: sin perder sus comandos.
    for name, line in [("load", call("load")), ("loop/t20", call("tick"))]:
        key = f"data/astral/function/{name}.mcfunction"
        files[key] += line + "\n"
    # Solo elites vanilla usan estos avances; MythicMobs notifica por su hook.
    for t in range(1, 6):
        key = f"data/astral/function/drop/elite{t}.mcfunction"
        files[key] += call("event/elite") + "\n"
        if t >= 4: files[key] += call("event/nightmare") + "\n"
    write_bridge()


def write_bridge():
    def q(s): return "'" + s.replace("'", "''") + "'"
    def cmd(s): return f'command{{c="{s}"}}'
    skills = []
    for npc in ("viajero", "herrero", "cronista", "tienda", "bazar"):
        target = npc if npc in ("viajero", "herrero", "cronista") else "deliver/" + npc
        if npc in ("viajero", "cronista"):
            page = 0 if npc == "viajero" else 1
            menu_id = "misiones" if page == 0 else f"misiones_{page}"
            actions = [cmd(f"execute as <target.name> at @s run function astral:quest/gui/page/{page}"), cmd(f"dm open {menu_id} <target.name>")]
        else:
            actions = [cmd(f"execute as <target.name> at @s run function astral:quest/{target}")]
        skills += [f"AQ_{npc.upper()}:", "  Skills:", *["  - " + q(action) for action in actions], ""]
    skills += ["AQ_CLOCK:", "  Skills:", "  - " + q(cmd("scoreboard players set #epoch aq.clock <utils.epoch>")),
               "  - " + q(cmd("function astral:quest/clock")), "",
               "AQ_PAY:", "  TargetConditions:", "  - score{o=aqmoney;v=>0} true", "  Skills:",
               "  - " + q(cmd("eco give <target.name> <target.score.aqmoney>")),
               "  - " + q(cmd("scoreboard players set <target.name> aqmoney 0")), ""]
    for name, tag, command in [("TITLE", "aq.title", "lp user <target.name> meta setprefix 110 <&dq>&b&l«Portador de la Estrella»<&dq>"),
                               ("GACHA", "aq.gacha", "crates forceopen gacha_rpg <target.name>")]:
        skills += [f"AQ_{name}:", "  TargetConditions:", f"  - hastag{{t={tag}}} true", "  Skills:",
                   "  - " + q(cmd(f"tag <target.name> remove {tag}")), "  - " + q(cmd(command)), ""]
    # El Cronista mantiene el reloj incluso cuando los jugadores estan lejos,
    # siempre que se cargue su chunk con los comandos de instalacion.
    for sub in ("skills",):
        path = ROOT / "build" / "mythicmobs" / sub / "misiones.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Generado por misiones.py\n" + "\n".join(skills), encoding="utf-8")
    folder = ROOT / "build" / "misiones"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "comandos.txt").write_text("\n".join([
        "# Misiones: despues de subir el datapack (servidor apagado) y las configs MythicMobs.",
        "# Subir TODOS los misiones*.yml y registrar sus entradas de config-gui_menus.yml en DeluxeMenus.",
        "papi ecloud download ScoreboardObjectives",
        "papi reload",
        "dm reload",
        "# Comprobar como jugador: /papi parse me %objective_score_{aq.state}% (debe ser un numero).",
        "# Cargar/reiniciar el servidor. Para configs solamente: mm reload.",
        "# El Cronista usa el chunk del lobby x=181 z=225. No duplicar el NPC si ya existe.",
        "execute in minecraft:lobby run forceload add 181 225",
        "rg flag -w lobby __global__ mob-spawning allow",
        "mm mobs spawn astral_npc_cronista 1 lobby,181.636,100,225.735",
        "rg flag -w lobby __global__ mob-spawning allow",
        "# Esperar 1 segundo y comprobar el reloj:",
        "scoreboard players get #today aq.clock",
        "# Tiene que ser un numero positivo (dias reales desde 1970, en UTC-3).",
        "# Los NPC existentes necesitan las configs de astral.yml actualizadas.",
        "# Si el cambio de skills no aparece en NPC persistentes, volver a crearlos de uno en uno.",
        "# El Viajero: clic = historia; shift+clic = mundo. El Herrero conserva las mejoras.",
        "# El dinero pendiente queda en aqmoney hasta que el Cronista lo paga con Essentials.",
        "# Revisar que EssentialsX, Vault, LuckPerms y CrazyCrates esten activos ANTES de habilitar misiones.",
    ]) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import subprocess
    import sys
    subprocess.run([sys.executable, str(Path(__file__).with_name("build.py"))], check=True)
