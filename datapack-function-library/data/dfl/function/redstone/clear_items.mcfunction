## 清理掉落物

# 初始化计分板
scoreboard objectives add dfl_scoreboard dummy "DFL"

# 清理非必要掉落物并记录数量
execute store result score item_number dfl_scoreboard \
    run kill @e[type=item,tag=!need]

# 向玩家显示清理结果
tellraw @a [ \
    {"text": "[DFL] ", "color": "gray", "italic": true}, \
    {"type": "translatable", "translate": "redstone.kill.item.dfl.entity.clear", \
        "fallback": "清除了", "color": "gray", "italic": true}, \
    {"text": " "}, \
    {"score": {"name": "item_number", "objective": "dfl_scoreboard"}, \
        "color": "gray", "italic": true}, \
    {"text": " "}, \
    {"type": "translatable", "translate": "redstone.kill.item.dfl.entity.item", \
        "fallback": "个掉落物", "color": "gray", "italic": true} \
]
