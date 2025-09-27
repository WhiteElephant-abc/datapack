scoreboard objectives add tpa trigger
scoreboard objectives add tpa_enable trigger
scoreboard objectives setdisplay list dfl_playerid
scoreboard players enable @a tpa
execute as @a unless score @s tpa_enable matches 1 run scoreboard players enable @s tpa_enable
tag @r[scores={tpa_enable=1}] add tpa_temp
execute as @a[scores={tpa=1..}] if score @s tpa = @r[tag=tpa_temp] dfl_playerid run tp @s @r[tag=tpa_temp]
execute as @a[scores={tpa=1..}] if score @s tpa = @r[tag=tpa_temp] dfl_playerid run scoreboard players set @s tpa 0
tag @a remove tpa_temp