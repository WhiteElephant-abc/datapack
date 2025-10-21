## 使用三种煤冶炼物品
## TODO 可变燃料

# 计数
    # 输入物品数量
$function dfl:lib/things_count {name:"$(input)"}
    # 煤炭数量
function dfl:lib/things_count {name:"coal_block"}
# 数量足够则添加标签
$execute \
    if score @s dfl_$(input)_num matches 9.. \
    if score @s dfl_coal_block_num matches 1.. \
    if score @s xp matches 9.. run \
    tag @s add $(input)_coal_block
# 处理拥有标签的玩家
    # 给予输出物
$give @s[tag=$(input)_coal_block] $(output) 9
    # 清除输入物
$clear @s[tag=$(input)_coal_block] $(input) 9
    # 清除燃料
$clear @s[tag=$(input)_coal_block] coal_block 1
    # 扣除经验
$xp add @s[tag=$(input)_coal_block] -9
    # 移除标签
$tag @s remove $(input)_coal_block


$function dfl:lib/things_count {name:"$(input)"}
function dfl:lib/things_count {name:"coal"}
$execute \
    if score @s dfl_$(input)_num matches 1.. \
    if score @s dfl_coal_num matches 1.. \
    if score @s xp matches 1.. run \
    tag @s add $(input)_coal
$give @s[tag=$(input)_coal] $(output)
$clear @s[tag=$(input)_coal] $(input) 1
$clear @s[tag=$(input)_coal] coal 1
$xp add @s[tag=$(input)_coal] -1
$tag @s remove $(input)_coal


$function dfl:lib/things_count {name:"$(input)"}
function dfl:lib/things_count {name:"charcoal"}
$execute \
    if score @s dfl_$(input)_num matches 1.. \
    if score @s dfl_charcoal_num matches 1.. \
    if score @s xp matches 1.. run \
    tag @s add $(input)_charcoal
$give @s[tag=$(input)_charcoal] $(output)
$clear @s[tag=$(input)_charcoal] $(input) 1
$clear @s[tag=$(input)_charcoal] charcoal 1
$xp add @s[tag=$(input)_charcoal] -1
$tag @s remove $(input)_charcoal
