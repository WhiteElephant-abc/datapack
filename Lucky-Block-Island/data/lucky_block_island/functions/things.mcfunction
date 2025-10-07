effect give @a minecraft:night_vision 30
effect give @a minecraft:glowing 30
fill 0 0 0 0 0 0 lucky:lucky_block replace minecraft:air
time set day
weather clear
execute positioned 0 0 0 run tp @e[distance=..3,type=item] 0 1 0
execute as @e[type=!item] at @s run tp @s[y=-64,dy=-100] ~ 20 ~