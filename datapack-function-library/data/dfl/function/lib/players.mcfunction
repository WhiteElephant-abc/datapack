## 获取玩家数
scoreboard objectives add dfl_scoreboard dummy "DFL"
execute store result score players dfl_scoreboard if entity @a
