# BlockLog

A vanilla Minecraft datapack that writes **every block broken or placed** to the server log
(`logs/latest.log`). **Nothing is shown in chat.** It needs no mods or plugins, and players install nothing.

```
[Server thread/INFO]: Named entity Bat['[BlockLog] Steve broke minecraft:stone at 12 64 -30 in minecraft:overworld'/4711, l='ServerLevel[world]', x=12.50, y=-400.00, z=-30.50] died: [BlockLog] Steve broke minecraft:stone at 12 64 -30 in minecraft:overworld was killed
[Server thread/INFO]: Named entity Bat['[BlockLog] Steve placed minecraft:oak_planks at 13 65 -30 in minecraft:overworld'/4712, ...] died: ...
```

Each line gives the player, the action, the block ID, the exact block coordinates and the dimension.
Search for `[BlockLog]` to find them all.

Targets **Minecraft 26.3** (data pack format 121). It was tested on a real 26.3 server.

## Installation

1. Get the pack in one of these ways:
   - download `blocklog-<version>.zip` from the Releases page;
   - copy the [`datapack/`](datapack) folder (rename it, e.g. to `blocklog`);
   - build it yourself (see [Building](#building)).
2. Put the zip (unopened) or the folder into `<server>/world/datapacks/`.
3. Restart the server, or run `/reload` as an operator.
4. Check that it loaded: `/datapack list enabled` should list the zip.

## Ignore list

Players on the ignore list are never logged. Names work for offline players too, but they must match the
player name exactly.

| Command | Effect |
|---|---|
| `/function blocklog:ignore {name:"Steve"}` | stop logging Steve |
| `/function blocklog:unignore {name:"Steve"}` | log Steve again |
| `/function blocklog:ignored` | show the list |

## Searching the log

```sh
grep -F "[BlockLog]" logs/latest.log                  # Linux / macOS
findstr /c:"[BlockLog]" logs\latest.log               # Windows
zgrep -F "[BlockLog]" logs/*.log.gz                   # older, compressed logs
```

## How it works

A datapack has only two ways to get text into the server log. Chat commands such as `say` reach the log,
but every player sees them. The other way is vanilla's `Named entity … died` line, which goes to the log
only. BlockLog uses the second one: for each event it summons a silent bat 400 blocks below the world,
names it with the log text, and kills it straight away. Players never see or hear it.

**Placing.** A hidden `placed_block` advancement fires in the same tick a block is placed. A ray cast from the
player's eyes finds the new block, and a binary search over generated block tags (about 11 checks) gives
its exact ID. Thin blocks (carpets, petals, rails…) and narrow centred blocks (flowers, saplings,
torches) are handled by their shape, so you can look past them and still place onto the block behind.

**Breaking in survival and adventure.** Breaks come from Minecraft's own `minecraft.mined` statistics, one
objective per block, so the counts are exact. The position is the block the player was looking at.

**Breaking in creative.** Creative mode keeps no mining statistics, so a break is detected when the block the
player was looking at disappears.

## Limitations

- **Creative breaks are a best guess.** A piston, an explosion or another player removing the block a
  creative player is looking at can produce an extra "broke" line.
- **The log lines are wordy.** The `Named entity Bat[…] died:` wrapper is the cost of keeping the
  messages out of chat.
- **Version-specific.** The block list and JSON formats are tied to one Minecraft version. Rebuild for a new
  version, and test it: a datapack with invalid JSON stops the server from starting.
- Blocks broken indirectly are not attributed to a player: explosions, pistons, fluids, and the upper half
  of a door.

## Building

Requires Python 3.10+ and an internet connection. The block and item registries and the data pack format come
from [misode/mcmeta](https://github.com/misode/mcmeta), an automated mirror of Mojang's data generator
output.

```sh
python generate.py                              # Minecraft 26.3 (default)
python generate.py --version 26.4-snapshot-10   # another version
```

Output:

- `datapack/` – the pack as a folder (committed, so the repository always contains the current pack)
- `dist/blocklog-<version>.zip` – the pack as a zip, ready to install (not committed; attach it to a release)

Don't edit the files in `datapack/` by hand. They are generated, so change `generate.py` and rebuild instead.

## Repository layout

| Path | Contents |
|---|---|
| `generate.py` | the generator: all pack logic lives here |
| `datapack/pack.mcmeta` | pack metadata (format 121 = Minecraft 26.3) |
| `datapack/data/blocklog/function/` | the functions: `tick`, `player`, `ray/*`, `break/*`, `place/*`, `log/*`, `id/*` (block-ID search tree) |
| `datapack/data/blocklog/advancement/` | hidden `placed_block` triggers |
| `datapack/data/blocklog/tags/block/` | ray pass-through tags and the block-ID search tags |
| `datapack/README.txt` | short install note shipped inside the zip |

## Uninstalling

Run `/function blocklog:uninstall`, which removes the pack's scoreboards and storage. Then delete the zip from
the `datapacks` folder and run `/reload`.

## Performance

For each online player, every tick, the pack casts one short ray (at most 60 steps) and runs a few
score checks. The full per-block statistics scan runs only when a looked-at block disappears, plus
once per second as a sweep. Logging an event costs one temporary entity.
