# as the player; args: action, block, id, x, y, z, extra, note
data modify storage blocklog:log args.dim set from entity @s Dimension
data modify storage blocklog:log args.player set value "?"
execute store result score #id bl run data get storage blocklog:log args.id
execute if score #id bl matches 0.. run function blocklog:log/name with storage blocklog:log args
tag @s add bl.logger
execute positioned ~ -400 ~ summon minecraft:bat run function blocklog:log/entity
tag @s remove bl.logger
