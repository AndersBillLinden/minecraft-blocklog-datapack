execute store result storage blocklog:tmp pos.x int 1 run scoreboard players get @s bl.tx
execute store result storage blocklog:tmp pos.y int 1 run scoreboard players get @s bl.ty
execute store result storage blocklog:tmp pos.z int 1 run scoreboard players get @s bl.tz
function blocklog:break/vanished_at with storage blocklog:tmp pos
