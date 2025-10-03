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
scoreboard players operation gametime dfl_scoreboard %= tick sd.temp
    # 如果余数为0，则执行主函数
execute if score gametime dfl_scoreboard matches 0 as @a at @s run function stone_disappearance:new/main


# tick_fill
execute store result score tick_fill sd.temp run data get storage stone_disappearance:data settings.tick_fill
execute if score tick_fill sd.temp matches 4 as @a at @s run fill ~1 ~-1 ~1 ~-1 ~1 ~-1 air replace stone
execute if score tick_fill sd.temp matches 4 as @a at @s run fill ~1 ~-1 ~1 ~-1 ~1 ~-1 air replace deepslate
execute if score tick_fill sd.temp matches 4 as @a at @s run fill ~1 ~-1 ~1 ~-1 ~1 ~-1 air replace netherrack
execute if score tick_fill sd.temp matches 4 as @a at @s run fill ~1 ~-1 ~1 ~-1 ~1 ~-1 air replace end_stone

# 移除临时记分板
scoreboard objectives remove sd.temp
