# 初始化设置
execute unless score loaded alb.settings matches 1 run scoreboard players set countdown alb.settings 30
execute unless score loaded alb.settings matches 1 run scoreboard players set loaded alb.settings 1

scoreboard objectives add alb.temp dummy
scoreboard players set 20 alb.temp 20
    # 获取游戏时间
function dfl:lib/gametime
    # 写入临时记分板
scoreboard players operation gametime alb.temp = gametime dfl_scoreboard
    # 转换为秒
scoreboard players operation gametime alb.temp /= 20 alb.temp
    # 计算游戏时间与countdown的余数
scoreboard players operation gametime alb.temp %= countdown alb.settings

# 计算剩余时间
scoreboard players operation countdown alb.temp = gametime alb.temp
scoreboard players operation countdown alb.temp -= 20 alb.temp
# 倒计时
title @a actionbar [{"text":"lucky block : ","color":"yellow"},{"score":{"name":"countdown","objective":"alb.temp"},"color":"red"},{"text":"s","color":"yellow"}]
# 移除临时记分板
scoreboard objectives remove alb.temp

# 如果余数为0，则执行主函数
execute if score gametime alb.temp matches 0 as @a at @s run function auto_lucky_block:setblock

# 定时调用
schedule function auto_lucky_block:main 1s
