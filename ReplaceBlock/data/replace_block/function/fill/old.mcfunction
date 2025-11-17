## 执行fill并返回成败

# fill计数
scoreboard objectives add temp.fill dummy

# 处理数据
data modify storage replace_block:data temp.run_fill set from storage replace_block:data settings
$data modify storage replace_block:data temp.run_fill merge value {a_x:$(a_x),a_z:$(a_z),b_x:$(b_x),b_z:$(b_z)}

# 获取维度数量
execute store result score dimensions rb.temp run data get storage replace_block:data dimensions
# 执行fill
function replace_block:fill/fill

# 读取settings.success_threshold
execute store result score success_num temp.fill run data get storage replace_block:data settings.success_threshold
# 如果fill失败，则令return失败，则整个函数返回值失败
execute if score 1 temp.fill <= success_num temp.fill run scoreboard objectives remove temp.fill
return run scoreboard objectives remove temp.fill
