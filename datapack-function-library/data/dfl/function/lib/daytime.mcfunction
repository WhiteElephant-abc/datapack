## 获取当日时间
scoreboard objectives add dfl_scoreboard dummy "DFL"
execute store result score daytime dfl_scoreboard run time query daytime
