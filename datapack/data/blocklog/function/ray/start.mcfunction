# as/at the player (tagged bl.self); finds the first solid block along the view
scoreboard players set @s bl.hit 0
scoreboard players set @s bl.shit 0
scoreboard players set #steps bl 0
function blocklog:util/dim
execute anchored eyes positioned ^ ^ ^ anchored feet run function blocklog:ray/step
