# advancement reward, runs as the player in the same tick the block was placed
advancement revoke @s only blocklog:place_block
execute if score @s bl.ignore matches 1.. run return 0
tag @a remove bl.self
tag @s add bl.self
scoreboard players operation #ph bl = @s bl.hit
scoreboard players operation #px bl = @s bl.tx
scoreboard players operation #py bl = @s bl.ty
scoreboard players operation #pz bl = @s bl.tz
scoreboard players set #fluid bl 0
execute at @s run function blocklog:ray/start
execute if score @s bl.shit matches 1 if score #ph bl matches 1 if score @s bl.tx = #px bl if score @s bl.ty = #py bl if score @s bl.tz = #pz bl run function blocklog:ray/use_skip
scoreboard players set #fluid bl 0
data modify storage blocklog:log args set value {action:"placed",block:"unknown",id:-1,extra:"",note:""}
execute if score @s bl.hit matches 1 store result storage blocklog:log args.id int 1 run scoreboard players get @s bl.tid
execute if score @s bl.hit matches 1 run function blocklog:log/at_target
execute if score @s bl.hit matches 0 run function blocklog:log/at_player
function blocklog:log/emit
tag @s remove bl.self
