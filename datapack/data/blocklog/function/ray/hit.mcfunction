scoreboard players set @s bl.hit 1
scoreboard players operation @s bl.dim = #dim bl
execute store result score @s bl.tid run function blocklog:id/n0
execute align xyz summon minecraft:marker run function blocklog:ray/mark
