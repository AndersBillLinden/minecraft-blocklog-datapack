# as/at each non-spectator player, once per tick
tag @s add bl.self
function blocklog:util/dim
# Did the block this player was looking at last tick disappear?
scoreboard players set #vanished bl 0
execute if score @s bl.hit matches 1 if score @s bl.dim = #dim bl run function blocklog:break/check_vanished
execute if score #vanished bl matches 0 if score @s bl.shit matches 1 if score @s bl.dim = #dim bl run function blocklog:break/check_vanished_skip
# Survival/adventure: mining statistics are authoritative (checked when the target vanished, plus a periodic sweep)
execute if entity @s[gamemode=!creative] if score #vanished bl matches 1 run function blocklog:break/scan
execute if entity @s[gamemode=!creative] if score #vanished bl matches 0 if score #tick bl matches 0 run function blocklog:break/scan
# Creative: no mining statistics exist, so a vanished target counts as broken
execute if entity @s[gamemode=creative] if score #vanished bl matches 1 run function blocklog:break/creative
# Remember what the player is looking at now
function blocklog:ray/start
tag @s remove bl.self
