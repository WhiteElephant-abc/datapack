effect give @a minecraft:night_vision infinite
effect give @a minecraft:glowing infinite
execute as @a if score @s glass matches 0 run tag @e[type=falling_block] add kill
execute as @a if score @s glass matches 0 at @s run tag @e[type=falling_block,distance=..10] remove kill
execute as @a if score @s glass matches 0 run kill @e[tag=kill]
execute as @a if score @s glass matches 0 at @s run fill ~30 ~30 ~30 ~-30 -64 ~-30 air replace deepslate
execute as @a if score @s glass matches 0 at @s run fill ~30 ~30 ~30 ~-30 -64 ~-30 air replace stone
execute as @a if score @s glass matches 2 at @s run fill ~30 ~30 ~30 ~-30 -64 ~-30 glass replace deepslate
execute as @a if score @s glass matches 2 at @s run fill ~30 ~30 ~30 ~-30 -64 ~-30 glass replace stone
execute as @a at @s run fill ~30 ~30 ~30 ~-30 0 ~-30 minecraft:glass replace minecraft:netherrack
execute as @a at @s run fill ~30 ~30 ~30 ~-30 0 ~-30 minecraft:glass replace minecraft:end_stone
execute as @a if score @s glass matches 1 run tellraw @a [{"type":"translatable","translate":"things.stone.disappearance.data.pack.message","fallback":"[数据包消息]"},{"text":" "},{"type":"selector","selector":"@s"},{"text":" "},{"type":"translatable","translate":"things.stone.disappearance.message.enable","fallback":"开启了填充玻璃"}]
execute as @a if score @s glass matches 1 run scoreboard players set @a glass 2
execute as @a if score @s glass matches 3 run tellraw @a [{"type":"translatable","translate":"things.stone.disappearance.data.pack.message","fallback":"[数据包消息]"},{"text":" "},{"type":"selector","selector":"@s"},{"text":" "},{"type":"translatable","translate":"things.stone.disappearance.message.disable","fallback":"关闭了填充玻璃"}]
execute as @a if score @s glass matches 3 run scoreboard players set @a glass 0
scoreboard players enable @a glass
