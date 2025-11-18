# 添加遍历维度的计数记分板
scoreboard objectives add temp.fill.dimension dummy
scoreboard players set i temp.fill.dimension 0
# 遍历维度
function replace_block:fill/traversal_dimension
# 移除遍历维度的计数记分板
scoreboard objectives remove temp.fill.dimension

# i++
scoreboard players add i temp.fill.list 1
# 判断是否遍历完成
execute if score i temp.fill.list > replace_pairs temp.fill run return 1
# 递归
function replace_block:fill/traversal_list
