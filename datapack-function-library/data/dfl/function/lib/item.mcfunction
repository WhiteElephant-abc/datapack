## 获取掉落物数
scoreboard objectives add dfl_scoreboard dummy "DFL"
execute store result score item dfl_scoreboard if entity @e[type=item]
