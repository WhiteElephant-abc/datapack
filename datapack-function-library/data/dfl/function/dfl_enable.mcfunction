## 被调用时修改记分板，便于其他项目检测数据包是否启用

scoreboard objectives add dfl_scoreboard dummy
scoreboard players set dfl_enable dfl_scoreboard 1
