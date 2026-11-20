BlockLog - logs every block broken or placed to the server log (logs/latest.log)
Minecraft 26.3, vanilla server. Nothing is shown in chat.

INSTALL
  1. Stop the server (or keep it running and use /reload in step 3).
  2. Put this zip file, unopened, in:  <server folder>/world/datapacks/
     (use your world's folder name if it is not "world")
  3. Start the server, or run  /reload  as an operator.
  Check with  /datapack list enabled  - it should list the zip.

WHAT THE LOG LOOKS LIKE
  Each event is one INFO line in logs/latest.log, for example:
  Named entity Bat['[BlockLog] Steve broke minecraft:stone at 12 64 -30 in minecraft:overworld'/4711, ...] died: ...
  Search for [BlockLog], e.g.  findstr /c:"[BlockLog]" logs\latest.log  (Windows) or  grep -F "[BlockLog]" logs/latest.log
  (A hidden bat named with the text is created far below the world and removed at once - that is how a datapack
  can write to the log without chat. Players never see or hear it.)

IGNORE LIST (players who are never logged; works for offline players too, the name must match exactly)
  /function blocklog:ignore {name:"Steve"}
  /function blocklog:unignore {name:"Steve"}
  /function blocklog:ignored          shows the list

GOOD TO KNOW
  - Survival/adventure breaking uses Minecraft's own mining statistics. Creative mode has none, so there a break
    is detected when the block the player is looking at disappears; a piston or explosion at that moment can
    cause an extra "broke" line for a creative player.
  - Made for 26.3. A newer Minecraft version may need a rebuilt pack.

REMOVE
  /function blocklog:uninstall   then delete the zip from the datapacks folder and run /reload.
