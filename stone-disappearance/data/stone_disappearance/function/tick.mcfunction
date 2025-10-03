## tick函数

# 初始化设置
execute unless score loaded sd.settings matches 1 run function stone_disappearance:new/reset_settings

# 执行主函数
    # 获取游戏时间
function dfl:lib/gametime
    # 读取设置项值
scoreboard objectives add sd.temp dummy
execute store result score tick sd.temp run data get storage stone_disappearance:data settings.tick
    # 计算游戏时间与tick的余数
scoreboard players operation tick sd.temp %= gametime dfl_scoreboard
    # 如果余数为0，则执行主函数
execute if score tick sd.temp matches 0 run function stone_disappearance:new/main
