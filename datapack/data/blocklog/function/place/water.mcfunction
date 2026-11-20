# advancement reward, runs as the player in the same tick the block was placed
advancement revoke @s only blocklog:place_water
execute if score @s bl.ignore matches 1.. run return 0
tag @a remove bl.self
tag @s add bl.self
scoreboard players operation #ph bl = @s bl.hit
scoreboard players operation #px bl = @s bl.tx
scoreboard players operation #py bl = @s bl.ty
scoreboard players operation #pz bl = @s bl.tz
scoreboard players set #fluid bl 1
execute at @s run function blocklog:ray/start
execute if score @s bl.shit matches 1 if score #ph bl matches 1 if score @s bl.tx = #px bl if score @s bl.ty = #py bl if score @s bl.tz = #pz bl run function blocklog:ray/use_skip
scoreboard players set #fluid bl 0
data modify storage blocklog:log args set value {action:"placed",block:"minecraft:water",id:-1,extra:" (bucket)",note:""}
execute if score @s bl.hit matches 1 run function blocklog:log/at_target
execute if score @s bl.hit matches 0 run function blocklog:log/at_player
function blocklog:log/emit
# a fluid is see-through, so it must not become the 'looked-at' block (it would look broken next tick)
scoreboard players set @s bl.hit 0
scoreboard players set @s bl.shit 0
tag @s remove bl.self
