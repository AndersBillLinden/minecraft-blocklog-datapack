scoreboard players add #tick bl 1
execute if score #tick bl matches 20.. run scoreboard players set #tick bl 0
scoreboard players set #fluid bl 0
scoreboard players set @a[gamemode=spectator] bl.hit 0
execute as @a[gamemode=!spectator] unless score @s bl.ignore matches 1.. at @s run function blocklog:player
execute if score #tick bl matches 0 as @a if score @s bl.ignore matches 1.. run function blocklog:discard
