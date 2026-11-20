# /function blocklog:unignore {name:"Steve"}
$scoreboard players reset $(name) bl.ignore
$data remove storage blocklog:config ignored[{name:"$(name)"}]
$tellraw @s {"text":"BlockLog: $(name) is logged again","color":"gray"}
