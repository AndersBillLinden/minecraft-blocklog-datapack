execute store result storage blocklog:log args.x int 1 run data get entity @s Pos[0]
execute store result storage blocklog:log args.y int 1 run data get entity @s Pos[1]
execute store result storage blocklog:log args.z int 1 run data get entity @s Pos[2]
data modify storage blocklog:log args.note set value " (player position; exact block not found)"
