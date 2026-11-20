$scoreboard players operation #count bl = @s bl.m.$(i)
$scoreboard players set @s bl.m.$(i) 0
data modify storage blocklog:log args set value {action:"broke",block:"unknown",extra:"",note:""}
$data modify storage blocklog:log args.id set value $(i)
execute if score #count bl matches 2.. run function blocklog:log/count
execute if score #vanished bl matches 1 run function blocklog:log/at_target
execute if score #vanished bl matches 0 run function blocklog:log/at_player
function blocklog:log/emit
