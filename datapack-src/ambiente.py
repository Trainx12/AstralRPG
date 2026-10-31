"""Puestos, accesos tematicos y plataformas de prueba. Construcciones propias."""
import json
import math

THEMES = {
    "bosque": ("Bosque Sombrio", "dark_oak_log", "mossy_stone_bricks", "lime_stained_glass", "moss_block", "green"),
    "tumba": ("Tumba del Rey de Arena", "cut_sandstone", "chiseled_sandstone", "orange_stained_glass", "smooth_sandstone", "gold"),
    "mina": ("Minas Olvidadas", "stripped_spruce_log", "deepslate_bricks", "cyan_stained_glass", "cobbled_deepslate", "aqua"),
    "cumbre": ("Cumbre Helada", "quartz_pillar", "packed_ice", "light_blue_stained_glass", "snow_block", "aqua"),
    "forja": ("Corazon de la Forja", "polished_blackstone_bricks", "chiseled_polished_blackstone", "red_stained_glass", "polished_basalt", "red"),
    "santuario": ("Santuario Celestial", "quartz_pillar", "purpur_block", "purple_stained_glass", "smooth_quartz", "light_purple"),
    "arena": ("Arena de jugadores", "polished_andesite", "chiseled_stone_bricks", "red_stained_glass", "stone_bricks", "red"),
    "expediciones": ("Expediciones Astrales", "polished_deepslate", "chiseled_deepslate", "purple_stained_glass", "deepslate_tiles", "light_purple"),
}
SERVICES = {
    "bazar": ("Bazar del Refugio", "stripped_spruce_log", "green_wool", "oak_planks", "emerald_block", "green"),
    "subastas": ("Casa de Subastas", "dark_oak_log", "purple_wool", "dark_oak_planks", "gold_block", "gold"),
    "herrero": ("Herreria Astral - mejoras", "polished_basalt", "polished_blackstone_bricks", "deepslate_tiles", "copper_block", "gold"),
}
HUB = [("bosque",156,278,True),("tumba",180,278,True),("mina",204,278,True),
       ("cumbre",150,298,False),("forja",170,298,False),("santuario",190,298,False),("arena",210,298,False)]


def generate(files):
    def fn(name,lines):
        files[f"data/astral/function/ambiente/{name}.mcfunction"]="\n".join(lines)+"\n"

    def title(label,color,tag,y=5.8,z=2.5):
        text=json.dumps([{"text":label,"color":color,"bold":True},
                         {"text":"\nHabla con el guardian","color":"gray","bold":False}],ensure_ascii=False)
        return (f'summon minecraft:text_display ~0.5 ~{y} ~{z} '
                f'{{Tags:["astral.amb.rotulo","{tag}"],billboard:"center",background:1073741824,'
                f'view_range:0.8f,line_width:240,text:{text}}}')

    def module(key,theme,service=False,reverse=False):
        label,pillar,trim,glass,floor,color=theme
        if service:floor=theme[3]
        name=key+("_sur" if reverse else "");tag=f"astral.amb.{key}";sign=-1 if reverse else 1
        lines=[f'execute if entity @e[type=minecraft:marker,tag={tag},distance=..1] run return 0']
        for x in range(-3,4):
            for z in range(5):
                for y in range(6):
                    lines.append(f'execute unless block ~{x*sign} ~{y} ~{z*sign} minecraft:air run return run function astral:ambiente/ocupado')
        z0,z1=sorted((0,4*sign))
        lines += [f'fill ~-3 ~-1 ~{z0} ~3 ~-1 ~{z1} minecraft:{floor}',
                  f'summon minecraft:marker ~0.5 ~ ~0.5 {{Tags:["{tag}","astral.amb.modulo"]}}']
        blocks={}
        def put(x,y,z,b):blocks[(x,y,z)]=b
        if service:
            for x in (-3,3):
                for z in (1,4):
                    for y in range(4):put(x,y,z,pillar)
            for x in range(-3,4):
                for z in range(1,5):put(x,4,z,trim if (x+z)%2 else floor)
            for x in range(-2,3):put(x,0,2,"barrel[facing=north]")
            for x in (-2,2):put(x,2,1,"lantern[hanging=true]")
            if key=="herrero":
                put(-1,1,2,"anvil[facing=north]");put(1,1,2,"smithing_table")
                put(0,0,4,"blast_furnace[facing=north]");put(0,1,4,"shroomlight");put(0,2,4,"orange_stained_glass")
                put(-2,1,3,"copper_block");put(2,1,3,"iron_chain")
            elif key=="subastas":
                put(0,1,2,"lectern[facing=north]");put(-2,1,3,"gold_block");put(2,1,3,"amethyst_block")
            else:
                put(-2,1,3,"melon");put(2,1,3,"hay_block");put(0,1,4,"emerald_block")
        else:
            for x in (-2,2):
                for y in range(4):put(x,y,3,pillar)
                put(x,4,3,trim)
            for x in range(-1,2):
                put(x,4,3,trim)
                for y in range(1,4):put(x,y,3,glass)
            for x in (-3,3):
                put(x,0,3,trim);put(x,1,3,"soul_lantern" if key in ("mina","cumbre","santuario") else "lantern")
            put(0,5,3,"amethyst_block" if key in ("santuario","expediciones") else trim)
            if key=="bosque":
                for x in (-3,-2,2,3):put(x,4,3,"azalea_leaves[persistent=true]")
                put(-3,0,1,"moss_block");put(3,0,1,"moss_block")
            if key=="tumba":put(0,5,3,"gold_block")
            if key=="mina":put(-2,0,2,"deepslate_diamond_ore");put(2,0,2,"deepslate_iron_ore")
            if key=="cumbre":put(-3,0,1,"blue_ice");put(3,0,1,"blue_ice")
            if key=="forja":put(-3,0,1,"shroomlight");put(3,0,1,"shroomlight")
            if key=="arena":put(-3,0,1,"red_concrete");put(3,0,1,"red_concrete")
        for (x,y,z),b in blocks.items():
            if reverse:b=b.replace("facing=north","facing=south")
            lines.append(f'setblock ~{x*sign} ~{y} ~{z*sign} minecraft:{b} keep')
        for x in (-1,0,1):
            facing="north" if reverse else "south"
            lines += [f'setblock ~{x} ~-2 ~{-2*sign} minecraft:stone_brick_stairs[facing={facing}] keep',
                      f'setblock ~{x} ~-1 ~{-sign} minecraft:stone_brick_stairs[facing={facing}] keep']
        lines += [title(label,color,tag,z=2.5*sign),"return 1"]
        fn(name,[f'execute align xyz run function astral:ambiente/{name}/build']);fn(name+"/build",lines)

    for key,theme in THEMES.items():module(key,theme);module(key,theme,reverse=True)
    for key,theme in SERVICES.items():module(key,theme,service=True)
    fn("ocupado",['tellraw @s {"text":"No hay espacio libre: hace falta una zona de 7 de ancho, 5 de fondo y 6 de alto. El frente mira al norte.","color":"yellow"}',"return 0"])
    terrace=["execute if entity @e[type=minecraft:marker,tag=astral.amb.terraza,distance=..1] run return 0",
             "fill ~-36 ~-1 ~-18 ~36 ~-1 ~18 minecraft:polished_deepslate keep",
             "fill ~-34 ~-2 ~-16 ~34 ~-2 ~16 minecraft:deepslate_bricks keep",
             "fill ~-30 ~-3 ~-12 ~30 ~-3 ~12 minecraft:deepslate_tiles keep",
             "fill ~-22 ~-4 ~-6 ~22 ~-4 ~6 minecraft:deepslate_bricks keep",
             "summon minecraft:marker ~ ~ ~ {Tags:[\"astral.amb.terraza\"]}"]
    for x in range(-36,37):
        for z in (-18,18):terrace.append(f"setblock ~{x} ~ ~{z} minecraft:dark_oak_fence keep")
    for z in range(-17,18):
        for x in (-36,36):terrace.append(f"setblock ~{x} ~ ~{z} minecraft:dark_oak_fence keep")
    for x in (-34,-12,12,34):
        for z in (-16,16):
            terrace += [f"setblock ~{x} ~ ~{z} minecraft:chiseled_deepslate keep",f"setblock ~{x} ~1 ~{z} minecraft:lantern keep"]
    terrace.append(title("Galeria de Expediciones","light_purple","astral.amb.rotulo_hub",y=5,z=0.5));fn("terraza",terrace)
    setup=["execute in minecraft:lobby positioned 180 100 288 run function astral:ambiente/terraza"]
    for key,x,z,reverse in HUB:setup.append(f'execute in minecraft:lobby positioned {x} 100 {z} run function astral:ambiente/{key}{"_sur" if reverse else ""}')
    for key,x,z in [("expediciones",172,214),("bazar",166,187),("subastas",190,187),("herrero",180,202)]:
        setup.append(f"execute in minecraft:lobby positioned {x} 100 {z} run function astral:ambiente/{key}")
    fn("lobby",setup)

    from mobs.mazmorras_data import DEFINITIONS,ARENA
    for dungeon in DEFINITIONS:
        key=dungeon["key"];lines=[]
        for i,point in enumerate(dungeon["points"]):
            x,y,z=map(math.floor,point);r=34 if i==len(dungeon["points"])-1 else 22
            floor={"bosque":"mossy_stone_bricks","tumba":"smooth_sandstone","cumbre":"packed_ice","forja":"polished_blackstone_bricks","santuario":"smooth_quartz"}[key]
            # Dividir en capas para respetar el limite de 32768 bloques por fill.
            lines += [f"execute in minecraft:{key} run fill {x-r} {y+dy} {z-r} {x+r} {y+min(dy+3,13)} {z+r} minecraft:air" for dy in range(0,14,4)]
            lines.append(f"execute in minecraft:{key} run fill {x-r} {y-2} {z-r} {x+r} {y-1} {z+r} minecraft:{floor}")
            for a,b,c,d in [(x-r,z-r,x+r,z-r),(x-r,z+r,x+r,z+r),(x-r,z-r,x-r,z+r),(x+r,z-r,x+r,z+r)]:
                lines.append(f"execute in minecraft:{key} run fill {a} {y} {b} {c} {y} {d} minecraft:stone_brick_wall")
            for dx,dz in ((-r+1,-r+1),(-r+1,r-1),(r-1,-r+1),(r-1,r-1)):
                lines.append(f"execute in minecraft:{key} run setblock {x+dx} {y} {z+dz} minecraft:lantern")
        fn("prueba/"+key,lines)
    x,y,z=map(math.floor,ARENA["arrival"]);r=24
    fn("prueba/arena",[f"execute in minecraft:arena run fill {x-r} {y+dy} {z-r} {x+r} {y+min(dy+3,13)} {z+r} minecraft:air" for dy in range(0,14,4)]
       +[f"execute in minecraft:arena run fill {x-r} {y-1} {z-r} {x+r} {y-1} {z+r} minecraft:stone_bricks"]
       +[f"execute in minecraft:arena run fill {a} {y} {b} {c} {y+1} {d} minecraft:polished_andesite" for a,b,c,d in [(x-r,z-r,x+r,z-r),(x-r,z+r,x+r,z+r),(x-r,z-r,x-r,z+r),(x+r,z-r,x+r,z+r)]])
