scoreboard objectives add kill trigger
scoreboard players enable @a kill
execute as @a if score @s kill matches 1 run kill
scoreboard players set @a kill 0