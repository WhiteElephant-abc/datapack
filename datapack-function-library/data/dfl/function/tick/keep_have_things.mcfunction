## 保持拥有指定数量的物品

# 统计玩家当前拥有的物品数量
$function dfl:lib/things_count {name:"$(name)"}
# 如果物品数量不足目标数量，则给予物品
$execute unless score @s dfl_$(name)_num matches $(num).. \
    run give @s $(name) 1
# 如果物品数量超过目标数量，则清除多余物品
$execute unless score @s dfl_$(name)_num matches ..$(num) \
    run clear @s $(name) 1
# 如果物品数量已达到目标数量，则结束函数
$execute if score @s dfl_$(name)_num matches $(num) \
    run return fail
# 递归调用以持续保持物品数量
$function dfl:tick/keep_have_things {name:"$(name)",num:"$(num)"}
