## 获取实体密度
scoreboard objectives add dfl_density dummy
execute as @e at @s store result score @s dfl_density if entity @e[distance=..10]
