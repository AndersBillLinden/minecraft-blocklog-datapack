execute store result storage blocklog:tmp pos.x int 1 run scoreboard players get @s bl.sx
execute store result storage blocklog:tmp pos.y int 1 run scoreboard players get @s bl.sy
execute store result storage blocklog:tmp pos.z int 1 run scoreboard players get @s bl.sz
function blocklog:break/vanished_at with storage blocklog:tmp pos
execute if score #vanished bl matches 1 run function blocklog:ray/use_skip
