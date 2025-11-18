# 读取当前维度序号
execute store result storage replace_block:data temp.fill_chunk.dimensions int 1 run \
    scoreboard players get i temp.fill.dimension
# 读取当前方块对序号
execute store result storage replace_block:data temp.fill_chunk.replace_pairs int 1 run \
    scoreboard players get i temp.fill.list
# 调用call_fill并传入序号
function replace_block:fill/call_fill with storage replace_block:data temp.fill_chunk

# i++
scoreboard players add i temp.fill.dimension 1
# 判断是否遍历完成
execute if score i temp.fill.dimension > dimensions temp.fill run return 1
# 递归
function replace_block:fill/traversal_dimension
