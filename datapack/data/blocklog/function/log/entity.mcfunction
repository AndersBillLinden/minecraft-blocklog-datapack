# as the freshly summoned bat
data merge entity @s {Silent:1b,NoAI:1b,PersistenceRequired:0b}
tag @s add bl.logent
# player name: a player head filled from the logging player
execute as @a[tag=bl.logger,limit=1] run loot replace entity @e[type=minecraft:bat,tag=bl.logent,limit=1] weapon.mainhand loot blocklog:player_head
data modify storage blocklog:log args.player set from entity @s equipment.mainhand.components."minecraft:profile".name
item replace entity @s weapon.mainhand with minecraft:air
function blocklog:log/name_entity with storage blocklog:log args
kill @s
