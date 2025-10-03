## 执行fill并返回成败

# fill计数
scoreboard objectives add temp.fill dummy

# 处理数据
data modify storage stone_disappearance:data temp.run_fill set from storage stone_disappearance:data settings
$data modify storage stone_disappearance:data temp.run_fill set value {a_x:$(a_x),a_z:$(a_z),b_x:$(b_x),b_z:$(b_z)}
# 执行fill
function stone_disappearance:new/child_fill with storage stone_disappearance:data temp.run_fill

# 如果fill失败，则令return失败，则整个函数返回值失败
execute if score 1 temp.fill matches ..50 run scoreboard objectives remove temp.fill
return run scoreboard objectives remove temp.fill
