# as a temporary marker at the block's corner: copy its block coordinates to the player
execute store result score @a[tag=bl.self,limit=1] bl.tx run data get entity @s Pos[0]
execute store result score @a[tag=bl.self,limit=1] bl.ty run data get entity @s Pos[1]
execute store result score @a[tag=bl.self,limit=1] bl.tz run data get entity @s Pos[2]
kill @s
