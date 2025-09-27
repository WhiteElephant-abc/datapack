scoreboard objectives add dfl_scoreboard dummy "DFL"
scoreboard objectives add dfl_playerid dummy
execute as @a unless score @s dfl_playerid matches 1.. run scoreboard players set @s dfl_playerid 0
execute as @r[scores={dfl_playerid=0}] run scoreboard players add playerid_temp dfl_scoreboard 1
execute as @r[scores={dfl_playerid=0}] run scoreboard players operation @s dfl_playerid = playerid_temp dfl_scoreboard