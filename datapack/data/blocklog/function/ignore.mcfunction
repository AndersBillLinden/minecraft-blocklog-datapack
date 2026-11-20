# /function blocklog:ignore {name:"Steve"}
$scoreboard players set $(name) bl.ignore 1
$data remove storage blocklog:config ignored[{name:"$(name)"}]
$data modify storage blocklog:config ignored append value {name:"$(name)"}
$tellraw @s {"text":"BlockLog: $(name) is no longer logged","color":"gray"}
