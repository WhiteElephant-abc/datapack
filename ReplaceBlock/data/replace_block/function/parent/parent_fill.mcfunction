## 传参并调用fill函数

# 运行fill，传入pos
data modify storage replace_block:data temp.fill_chunk set from storage replace_block:data temp.find_chunk
function replace_block:fill/main
execute if score success temp.chunk matches 1 run return 1
