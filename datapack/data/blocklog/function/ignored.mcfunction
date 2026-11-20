# /function blocklog:ignored  - shows the ignore list
execute unless data storage blocklog:config ignored[0] run return run tellraw @s {"text":"BlockLog: nobody is ignored","color":"gray"}
tellraw @s [{"text":"BlockLog ignores: ","color":"gray"},{"nbt":"ignored[].name","storage":"blocklog:config","separator":", ","color":"white"}]
