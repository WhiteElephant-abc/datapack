scoreboard objectives add dfl_tntdensity dummy
execute as @e at @s store result score @s dfl_tntdensity if entity @e[distance=..5,type=minecraft:tnt]
$execute as @e at @s if score @s dfl_tntdensity matches $(num).. run kill @e[distance=..5,type=minecraft:tnt]