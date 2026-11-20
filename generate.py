"""Generates the BlockLog datapack for a given Minecraft version.

Writes one server-log line per block broken or placed, without anything in chat. A datapack can only reach
the log through chat or through vanilla's "Named entity ... died" line, so each event names a silent bat
below the world and kills it:

  Named entity Bat['[BlockLog] Steve broke minecraft:stone at 12 64 -30 in minecraft:overworld'/4711, ...] died: ...

Block/item registries and the data pack format are read from misode/mcmeta
(an automated mirror of Mojang's data generator output).

    python generate.py                 # 26.3 (default)
    python generate.py --version 26.4-snapshot-10

Output: datapack/ (the pack as a folder, committed) and dist/blocklog-<version>.zip (ignored)
"""
import argparse
import json
import shutil
import urllib.request
from pathlib import Path

NS = "blocklog"
LEAF_SIZE = 8          # blocks per leaf function in the block-id search tree
RAY_STEPS = 60         # 0.1 block per step -> ~6 blocks of reach from the eyes
SWEEP_TICKS = 20       # full statistics sweep interval for survival players

# Blocks that never need a "mined" statistic objective.
UNMINEABLE = {"air", "cave_air", "void_air", "water", "lava", "bubble_column",
              "moving_piston", "end_portal", "end_gateway", "nether_portal"}
# Blocks the look-ray passes through (a broken block turns into one of these).
RAY_PASS = ["air", "cave_air", "void_air", "water", "lava", "bubble_column",
            "light", "structure_void"]
RAY_PASS_FLUID = ["air", "cave_air", "void_air", "light", "structure_void"]
# Blocks only a few pixels high: the ray passes over them unless it is in their bottom quarter.
THIN_FLOOR = ["#minecraft:wool_carpets", "#minecraft:rails", "#minecraft:pressure_plates", "wildflowers",
              "pink_petals", "leaf_litter", "moss_carpet", "pale_moss_carpet", "redstone_wire", "repeater",
              "comparator", "lily_pad", "frogspawn"]
# Narrow blocks in the middle of their cell: the ray passes them unless it is near the centre.
CENTER = ["#minecraft:small_flowers", "oak_sapling", "spruce_sapling", "birch_sapling", "jungle_sapling",
          "acacia_sapling", "dark_oak_sapling", "pale_oak_sapling", "cherry_sapling", "poplar_sapling",
          "mangrove_propagule", "brown_mushroom", "red_mushroom", "crimson_fungus", "warped_fungus",
          "crimson_roots", "warped_roots", "dead_bush", "torch", "soul_torch", "copper_torch", "redstone_torch"]


def fetch(version: str, path: str):
    url = f"https://raw.githubusercontent.com/misode/mcmeta/{version}-summary/{path}"
    with urllib.request.urlopen(url) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="26.3")
    here = Path(__file__).parent
    ap.add_argument("--pack-dir", default=str(here / "datapack"), help="where the pack folder is written")
    ap.add_argument("--dist-dir", default=str(here / "dist"), help="where the zip is written")
    args = ap.parse_args()

    meta = fetch(args.version, "version.json")
    regs = fetch(args.version, "registries/data.min.json")
    blocks = sorted(regs["block"])
    items = regs["item"]
    water_buckets = sorted(i for i in items if i.endswith("_bucket")
                           and i not in {"bucket", "milk_bucket", "lava_bucket", "powder_snow_bucket"})
    fmt = meta["data_pack_version"]

    root = Path(args.pack_dir)
    out = Path(args.dist_dir)
    out.mkdir(parents=True, exist_ok=True)
    if root.exists():  # clear contents (keeps the folder itself, which may be open elsewhere)
        for child in root.iterdir():
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    files: dict[str, str] = {}

    def fn(name, lines):
        files[f"data/{NS}/function/{name}.mcfunction"] = "\n".join(lines) + "\n"

    def js(path, obj):
        files[path] = json.dumps(obj, indent=2) + "\n"

    mc = lambda b: f"minecraft:{b}"
    idx = {b: i for i, b in enumerate(blocks)}
    mined = [b for b in blocks if b not in UNMINEABLE]

    # ---------------------------------------------------------------- pack
    js("pack.mcmeta", {"pack": {
        "description": f"BlockLog: logs block breaking/placing to the server log (MC {args.version})",
        "min_format": fmt, "max_format": fmt}})
    js("data/minecraft/tags/function/load.json", {"values": [f"{NS}:load"]})
    js("data/minecraft/tags/function/tick.json", {"values": [f"{NS}:tick"]})
    js(f"data/{NS}/tags/block/ray_pass.json", {"values": [mc(b) for b in RAY_PASS]})
    js(f"data/{NS}/tags/block/ray_pass_fluid.json", {"values": [mc(b) for b in RAY_PASS_FLUID]})
    tagv = lambda lst: [b if b.startswith("#") else mc(b) for b in lst if b.startswith("#") or b in idx]
    js(f"data/{NS}/tags/block/thin_floor.json", {"values": tagv(THIN_FLOOR)})
    js(f"data/{NS}/tags/block/center.json", {"values": tagv(CENTER)})

    # ---------------------------------------------------------------- load / uninstall
    dummies = ["bl", "bl.tx", "bl.ty", "bl.tz", "bl.tid", "bl.hit", "bl.dim", "bl.ignore",
               "bl.sx", "bl.sy", "bl.sz", "bl.sid", "bl.shit"]
    fn("load", [
        "# BlockLog: set up scoreboards and the block name table",
        *[f"scoreboard objectives add {o} dummy" for o in dummies],
        *[f"scoreboard objectives add bl.m.{idx[b]} minecraft.mined:minecraft.{b}" for b in mined],
        "data modify storage blocklog:data blocks set value " + json.dumps([mc(b) for b in blocks]),
        "execute unless data storage blocklog:config ignored run data modify storage blocklog:config ignored set value []",
        "scoreboard players set #fluid bl 0",
    ])

    # ---------------------------------------------------------------- ignore list
    # Players on the list are never logged. Names work offline but must match the player's name exactly.
    fn("ignore", [
        "# /function blocklog:ignore {name:\"Steve\"}",
        "$scoreboard players set $(name) bl.ignore 1",
        "$data remove storage blocklog:config ignored[{name:\"$(name)\"}]",
        "$data modify storage blocklog:config ignored append value {name:\"$(name)\"}",
        "$tellraw @s {\"text\":\"BlockLog: $(name) is no longer logged\",\"color\":\"gray\"}",
    ])
    fn("unignore", [
        "# /function blocklog:unignore {name:\"Steve\"}",
        "$scoreboard players reset $(name) bl.ignore",
        "$data remove storage blocklog:config ignored[{name:\"$(name)\"}]",
        "$tellraw @s {\"text\":\"BlockLog: $(name) is logged again\",\"color\":\"gray\"}",
    ])
    fn("ignored", [
        "# /function blocklog:ignored  - shows the ignore list",
        'execute unless data storage blocklog:config ignored[0] run return run tellraw @s {"text":"BlockLog: nobody is ignored","color":"gray"}',
        'tellraw @s [{"text":"BlockLog ignores: ","color":"gray"},{"nbt":"ignored[].name","storage":"blocklog:config","separator":", ","color":"white"}]',
    ])
    fn("discard", ["# ignored player: throw away mining statistics so nothing is logged later",
                   *[f"scoreboard players set @s bl.m.{idx[b]} 0" for b in mined],
                   "scoreboard players set @s bl.hit 0"])
    fn("uninstall", [
        "# Removes all BlockLog scoreboards and storage. Then disable the pack with /datapack disable",
        *[f"scoreboard objectives remove {o}" for o in dummies],
        *[f"scoreboard objectives remove bl.m.{idx[b]}" for b in mined],
        "data remove storage blocklog:data blocks",
        "data remove storage blocklog:log args",
        "data remove storage blocklog:tmp pos",
        "advancement revoke @a from blocklog:place_block",
        "advancement revoke @a from blocklog:place_water",
        "advancement revoke @a from blocklog:place_lava",
        "data remove storage blocklog:config ignored",
    ])

    # ---------------------------------------------------------------- tick
    fn("tick", [
        "scoreboard players add #tick bl 1",
        f"execute if score #tick bl matches {SWEEP_TICKS}.. run scoreboard players set #tick bl 0",
        "scoreboard players set #fluid bl 0",
        "scoreboard players set @a[gamemode=spectator] bl.hit 0",
        f"execute as @a[gamemode=!spectator] unless score @s bl.ignore matches 1.. at @s run function {NS}:player",
        f"execute if score #tick bl matches 0 as @a if score @s bl.ignore matches 1.. run function {NS}:discard",
    ])
    fn("player", [
        "# as/at each non-spectator player, once per tick",
        "tag @s add bl.self",
        f"function {NS}:util/dim",
        "# Did the block this player was looking at last tick disappear?",
        "scoreboard players set #vanished bl 0",
        f"execute if score @s bl.hit matches 1 if score @s bl.dim = #dim bl run function {NS}:break/check_vanished",
        f"execute if score #vanished bl matches 0 if score @s bl.shit matches 1 if score @s bl.dim = #dim bl run function {NS}:break/check_vanished_skip",
        "# Survival/adventure: mining statistics are authoritative (checked when the target vanished, plus a periodic sweep)",
        f"execute if entity @s[gamemode=!creative] if score #vanished bl matches 1 run function {NS}:break/scan",
        f"execute if entity @s[gamemode=!creative] if score #vanished bl matches 0 if score #tick bl matches 0 run function {NS}:break/scan",
        "# Creative: no mining statistics exist, so a vanished target counts as broken",
        f"execute if entity @s[gamemode=creative] if score #vanished bl matches 1 run function {NS}:break/creative",
        "# Remember what the player is looking at now",
        f"function {NS}:ray/start",
        "tag @s remove bl.self",
    ])
    fn("util/dim", [
        "scoreboard players set #dim bl 0",
        "execute if dimension minecraft:overworld run scoreboard players set #dim bl 1",
        "execute if dimension minecraft:the_nether run scoreboard players set #dim bl 2",
        "execute if dimension minecraft:the_end run scoreboard players set #dim bl 3",
    ])

    # ---------------------------------------------------------------- ray cast
    fn("ray/start", [
        "# as/at the player (tagged bl.self); finds the first solid block along the view",
        "scoreboard players set @s bl.hit 0",
        "scoreboard players set @s bl.shit 0",
        "scoreboard players set #steps bl 0",
        f"function {NS}:util/dim",
        f"execute anchored eyes positioned ^ ^ ^ anchored feet run function {NS}:ray/step",
    ])
    fn("ray/step", [
        f"execute if score #fluid bl matches 0 if block ~ ~ ~ #{NS}:thin_floor if function {NS}:ray/above_thin run return run function {NS}:ray/skip",
        f"execute if score #fluid bl matches 0 if block ~ ~ ~ #{NS}:center unless function {NS}:ray/in_center run return run function {NS}:ray/skip",
        f"execute if score #fluid bl matches 0 unless block ~ ~ ~ #{NS}:ray_pass run return run function {NS}:ray/hit",
        f"execute if score #fluid bl matches 1 unless block ~ ~ ~ #{NS}:ray_pass_fluid run return run function {NS}:ray/hit",
        f"function {NS}:ray/next",
    ])
    fn("ray/next", [
        "scoreboard players add #steps bl 1",
        f"execute if score #steps bl matches ..{RAY_STEPS} positioned ^ ^ ^0.1 run function {NS}:ray/step",
    ])
    fn("ray/above_thin", [
        "# 1 if the ray point is above the bottom quarter of this thin block's cell",
        f"execute positioned ~ ~-0.25 ~ if block ~ ~ ~ #{NS}:thin_floor run return 1",
        "return 0",
    ])
    fn("ray/in_center", [
        "# 1 if the ray point is inside the centred column (6/16 wide, 10/16 high) of this cell",
        f"execute positioned ~0.3125 ~ ~ unless block ~ ~ ~ #{NS}:center run return 0",
        f"execute positioned ~-0.3125 ~ ~ unless block ~ ~ ~ #{NS}:center run return 0",
        f"execute positioned ~ ~ ~0.3125 unless block ~ ~ ~ #{NS}:center run return 0",
        f"execute positioned ~ ~ ~-0.3125 unless block ~ ~ ~ #{NS}:center run return 0",
        f"execute positioned ~ ~-0.625 ~ if block ~ ~ ~ #{NS}:center run return 0",
        "return 1",
    ])
    fn("ray/skip", [
        "# looked past a thin/centred block: remember it (it may be what was just placed or broken)",
        "scoreboard players set @s bl.shit 1",
        f"execute store result score @s bl.sid run function {NS}:id/n0",
        f"execute align xyz summon minecraft:marker run function {NS}:ray/mark_skip",
        f"function {NS}:ray/next",
    ])
    fn("ray/mark_skip", [
        "execute store result score @a[tag=bl.self,limit=1] bl.sx run data get entity @s Pos[0]",
        "execute store result score @a[tag=bl.self,limit=1] bl.sy run data get entity @s Pos[1]",
        "execute store result score @a[tag=bl.self,limit=1] bl.sz run data get entity @s Pos[2]",
        "kill @s",
    ])
    fn("ray/use_skip", [
        "scoreboard players operation @s bl.tx = @s bl.sx",
        "scoreboard players operation @s bl.ty = @s bl.sy",
        "scoreboard players operation @s bl.tz = @s bl.sz",
        "scoreboard players operation @s bl.tid = @s bl.sid",
        "scoreboard players set @s bl.hit 1",
    ])
    fn("ray/hit", [
        "scoreboard players set @s bl.hit 1",
        "scoreboard players operation @s bl.dim = #dim bl",
        f"execute store result score @s bl.tid run function {NS}:id/n0",
        f"execute align xyz summon minecraft:marker run function {NS}:ray/mark",
    ])
    fn("ray/mark", [
        "# as a temporary marker at the block's corner: copy its block coordinates to the player",
        "execute store result score @a[tag=bl.self,limit=1] bl.tx run data get entity @s Pos[0]",
        "execute store result score @a[tag=bl.self,limit=1] bl.ty run data get entity @s Pos[1]",
        "execute store result score @a[tag=bl.self,limit=1] bl.tz run data get entity @s Pos[2]",
        "kill @s",
    ])

    # ---------------------------------------------------------------- block id search tree
    counter = [0]

    def build(group):
        node = f"n{counter[0]}"
        counter[0] += 1
        if len(group) <= LEAF_SIZE:
            fn(f"id/{node}", [f"execute if block ~ ~ ~ {mc(b)} run return {idx[b]}" for b in group]
               + ["return -1"])
            return node
        mid = len(group) // 2
        left, right = group[:mid], group[mid:]
        ln = build(left)
        rn = build(right)
        js(f"data/{NS}/tags/block/id/{ln}.json", {"values": [mc(b) for b in left]})
        fn(f"id/{node}", [
            f"execute if block ~ ~ ~ #{NS}:id/{ln} run return run function {NS}:id/{ln}",
            f"return run function {NS}:id/{rn}",
        ])
        return node

    build(blocks)  # n0 is the root; tags exist only for left children

    # ---------------------------------------------------------------- breaking
    fn("break/check_vanished", [
        "execute store result storage blocklog:tmp pos.x int 1 run scoreboard players get @s bl.tx",
        "execute store result storage blocklog:tmp pos.y int 1 run scoreboard players get @s bl.ty",
        "execute store result storage blocklog:tmp pos.z int 1 run scoreboard players get @s bl.tz",
        f"function {NS}:break/vanished_at with storage blocklog:tmp pos",
    ])
    fn("break/check_vanished_skip", [
        "execute store result storage blocklog:tmp pos.x int 1 run scoreboard players get @s bl.sx",
        "execute store result storage blocklog:tmp pos.y int 1 run scoreboard players get @s bl.sy",
        "execute store result storage blocklog:tmp pos.z int 1 run scoreboard players get @s bl.sz",
        f"function {NS}:break/vanished_at with storage blocklog:tmp pos",
        f"execute if score #vanished bl matches 1 run function {NS}:ray/use_skip",
    ])
    fn("break/vanished_at", [
        f"$execute positioned $(x) $(y) $(z) if block ~ ~ ~ #{NS}:ray_pass run scoreboard players set #vanished bl 1",
    ])
    fn("break/scan", [f"execute if score @s bl.m.{idx[b]} matches 1.. run function {NS}:break/mined {{i:{idx[b]}}}"
                      for b in mined])
    fn("break/mined", [
        "$scoreboard players operation #count bl = @s bl.m.$(i)",
        "$scoreboard players set @s bl.m.$(i) 0",
        'data modify storage blocklog:log args set value {action:"broke",block:"unknown",extra:"",note:""}',
        "$data modify storage blocklog:log args.id set value $(i)",
        f"execute if score #count bl matches 2.. run function {NS}:log/count",
        f"execute if score #vanished bl matches 1 run function {NS}:log/at_target",
        f"execute if score #vanished bl matches 0 run function {NS}:log/at_player",
        f"function {NS}:log/emit",
    ])
    fn("break/creative", [
        'data modify storage blocklog:log args set value {action:"broke",block:"unknown",extra:"",note:""}',
        "execute store result storage blocklog:log args.id int 1 run scoreboard players get @s bl.tid",
        f"function {NS}:log/at_target",
        f"function {NS}:log/emit",
    ])

    # ---------------------------------------------------------------- placing
    def place(name, fluid, init):
        fn(f"place/{name}", [
            "# advancement reward, runs as the player in the same tick the block was placed",
            f"advancement revoke @s only {NS}:place_{name}",
            "execute if score @s bl.ignore matches 1.. run return 0",
            "tag @a remove bl.self",
            "tag @s add bl.self",
            "scoreboard players operation #ph bl = @s bl.hit",
            "scoreboard players operation #px bl = @s bl.tx",
            "scoreboard players operation #py bl = @s bl.ty",
            "scoreboard players operation #pz bl = @s bl.tz",
            f"scoreboard players set #fluid bl {fluid}",
            f"execute at @s run function {NS}:ray/start",
            f"execute if score @s bl.shit matches 1 if score #ph bl matches 1 if score @s bl.tx = #px bl if score @s bl.ty = #py bl if score @s bl.tz = #pz bl run function {NS}:ray/use_skip",
            "scoreboard players set #fluid bl 0",
            f"data modify storage blocklog:log args set value {init}",
            *([] if fluid else ["execute if score @s bl.hit matches 1 store result storage blocklog:log args.id int 1 run scoreboard players get @s bl.tid"]),
            f"execute if score @s bl.hit matches 1 run function {NS}:log/at_target",
            f"execute if score @s bl.hit matches 0 run function {NS}:log/at_player",
            f"function {NS}:log/emit",
            *(["# a fluid is see-through, so it must not become the 'looked-at' block (it would look broken next tick)",
               "scoreboard players set @s bl.hit 0", "scoreboard players set @s bl.shit 0"] if fluid else []),
            "tag @s remove bl.self",
        ])

    place("block", 0, '{action:"placed",block:"unknown",id:-1,extra:"",note:""}')
    place("water", 1, '{action:"placed",block:"minecraft:water",id:-1,extra:" (bucket)",note:""}')
    place("lava", 1, '{action:"placed",block:"minecraft:lava",id:-1,extra:" (bucket)",note:""}')

    def adv(name, condition):
        js(f"data/{NS}/advancement/place_{name}.json", {
            "criteria": {"placed": {"trigger": "minecraft:placed_block",
                                    "conditions": {"location": condition}}},
            "rewards": {"function": f"{NS}:place/{name}"}})

    water_tool = {"type": "minecraft:match_tool", "predicate": {"items": [mc(i) for i in water_buckets]}}
    lava_tool = {"type": "minecraft:match_tool", "predicate": {"items": "minecraft:lava_bucket"}}
    adv("water", water_tool)
    adv("lava", lava_tool)
    adv("block", {"type": "minecraft:all_of", "terms": [
        {"type": "minecraft:inverted", "term": water_tool},
        {"type": "minecraft:inverted", "term": lava_tool}]})

    # ---------------------------------------------------------------- logging
    fn("log/count", [
        "execute store result storage blocklog:log args.count int 1 run scoreboard players get #count bl",
        f"function {NS}:log/count_text with storage blocklog:log args",
    ])
    fn("log/count_text", ['$data modify storage blocklog:log args.extra set value " (x$(count))"'])
    fn("log/at_target", [
        "execute store result storage blocklog:log args.x int 1 run scoreboard players get @s bl.tx",
        "execute store result storage blocklog:log args.y int 1 run scoreboard players get @s bl.ty",
        "execute store result storage blocklog:log args.z int 1 run scoreboard players get @s bl.tz",
    ])
    fn("log/at_player", [
        "execute store result storage blocklog:log args.x int 1 run data get entity @s Pos[0]",
        "execute store result storage blocklog:log args.y int 1 run data get entity @s Pos[1]",
        "execute store result storage blocklog:log args.z int 1 run data get entity @s Pos[2]",
        'data modify storage blocklog:log args.note set value " (player position; exact block not found)"',
    ])
    # The server log line comes from vanilla's "Named entity ... died" message: a silent bat, named
    # with the log text, is summoned below the world and killed at once. Nothing is sent to chat.
    fn("log/emit", [
        "# as the player; args: action, block, id, x, y, z, extra, note",
        "data modify storage blocklog:log args.dim set from entity @s Dimension",
        'data modify storage blocklog:log args.player set value "?"',
        "execute store result score #id bl run data get storage blocklog:log args.id",
        f"execute if score #id bl matches 0.. run function {NS}:log/name with storage blocklog:log args",
        "tag @s add bl.logger",
        f"execute positioned ~ -400 ~ summon minecraft:bat run function {NS}:log/entity",
        "tag @s remove bl.logger",
    ])
    fn("log/name", ["$data modify storage blocklog:log args.block set from storage blocklog:data blocks[$(id)]"])
    fn("log/entity", [
        "# as the freshly summoned bat",
        "data merge entity @s {Silent:1b,NoAI:1b,PersistenceRequired:0b}",
        "tag @s add bl.logent",
        "# player name: a player head filled from the logging player",
        f"execute as @a[tag=bl.logger,limit=1] run loot replace entity @e[type=minecraft:bat,tag=bl.logent,limit=1] weapon.mainhand loot {NS}:player_head",
        'data modify storage blocklog:log args.player set from entity @s equipment.mainhand.components."minecraft:profile".name',
        "item replace entity @s weapon.mainhand with minecraft:air",
        f"function {NS}:log/name_entity with storage blocklog:log args",
        "kill @s",
    ])
    fn("log/name_entity", [
        '$data modify entity @s CustomName set value "[BlockLog] $(player) $(action) $(block) at $(x) $(y) $(z) in $(dim)$(extra)$(note)"',
    ])
    js(f"data/{NS}/loot_table/player_head.json", {"pools": [{"rolls": 1, "entries": [{
        "type": "minecraft:item", "name": "minecraft:player_head",
        "modifier": {"type": "minecraft:fill_player_head", "entity": "this"}}]}]})

    files["README.txt"] = f"""BlockLog - logs every block broken or placed to the server log (logs/latest.log)
Minecraft {args.version}, vanilla server. Nothing is shown in chat.

INSTALL
  1. Stop the server (or keep it running and use /reload in step 3).
  2. Put this zip file, unopened, in:  <server folder>/world/datapacks/
     (use your world's folder name if it is not "world")
  3. Start the server, or run  /reload  as an operator.
  Check with  /datapack list enabled  - it should list the zip.

WHAT THE LOG LOOKS LIKE
  Each event is one INFO line in logs/latest.log, for example:
  Named entity Bat['[BlockLog] Steve broke minecraft:stone at 12 64 -30 in minecraft:overworld'/4711, ...] died: ...
  Search for [BlockLog], e.g.  findstr /c:"[BlockLog]" logs\\latest.log  (Windows) or  grep -F "[BlockLog]" logs/latest.log
  (A hidden bat named with the text is created far below the world and removed at once - that is how a datapack
  can write to the log without chat. Players never see or hear it.)

IGNORE LIST (players who are never logged; works for offline players too, the name must match exactly)
  /function blocklog:ignore {{name:"Steve"}}
  /function blocklog:unignore {{name:"Steve"}}
  /function blocklog:ignored          shows the list

GOOD TO KNOW
  - Survival/adventure breaking uses Minecraft's own mining statistics. Creative mode has none, so there a break
    is detected when the block the player is looking at disappears; a piston or explosion at that moment can
    cause an extra "broke" line for a creative player.
  - Made for {args.version}. A newer Minecraft version may need a rebuilt pack.

REMOVE
  /function blocklog:uninstall   then delete the zip from the datapacks folder and run /reload.
"""

    # ---------------------------------------------------------------- write
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
    for old in out.glob("blocklog-*.zip"):
        old.unlink()
    zip_base = out / f"blocklog-{args.version}"
    shutil.make_archive(str(zip_base), "zip", root)
    print(f"MC {args.version}, pack format {fmt}: {len(blocks)} blocks, {len(mined)} mined objectives, "
          f"{len(files)} files -> {root} and {zip_base}.zip")


if __name__ == "__main__":
    main()
