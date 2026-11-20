# looked past a thin/centred block: remember it (it may be what was just placed or broken)
scoreboard players set @s bl.shit 1
execute store result score @s bl.sid run function blocklog:id/n0
execute align xyz summon minecraft:marker run function blocklog:ray/mark_skip
function blocklog:ray/next
