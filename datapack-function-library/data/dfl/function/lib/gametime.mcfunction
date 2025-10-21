## 获取游戏时间
scoreboard objectives add dfl_scoreboard dummy "DFL"
execute store result score gametime dfl_scoreboard run time query gametime
