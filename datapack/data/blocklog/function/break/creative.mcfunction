data modify storage blocklog:log args set value {action:"broke",block:"unknown",extra:"",note:""}
execute store result storage blocklog:log args.id int 1 run scoreboard players get @s bl.tid
function blocklog:log/at_target
function blocklog:log/emit
