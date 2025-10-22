## 实体过多时清除非玩家实体

# TODO
# 创建计分板目标，用于统计实体数量
scoreboard objectives add dfl_scoreboard dummy "DFL"
# 统计非玩家且无need标签的实体数量
execute store result score entitynum dfl_scoreboard \
    if entity @e[type=!minecraft:player,tag=!need]
# 实体数量超限时发送清除通知
$execute if score entitynum dfl_scoreboard matches $(num).. run tellraw @a [
    {
        "text": "[DFL] ",
        "color": "gray",
        "italic": true
    },
    {
        "type": "translatable",
        "translate": "tick.kill.dfl.too.many",
        "fallback": "实体过多，已清除",
        "color": "gray",
        "italic": true
    },
    {
        "text": " "
    },
    {
        "score": {
            "name": "entitynum",
            "objective": "dfl_scoreboard"
        },
        "color": "red"
    },
    {
        "text": " "
    },
    {
        "type": "translatable",
        "translate": "tick.kill.dfl.entity.num",
        "fallback": "个实体",
        "color": "gray",
        "italic": true
    }
]
# 发送如何保护实体的提示信息
$execute if score entitynum dfl_scoreboard matches $(num).. run tellraw @a [
    {
        "type": "translatable",
        "translate": "tick.kill.dfl.need.tag",
        "fallback": "想要防止实体被清除可以为实体",
        "color": "gray",
        "italic": true
    },
    {
        "text": " "
    },
    {
        "type": "translatable",
        "translate": "tick.kill.dfl.add",
        "fallback": "添加",
        "color": "blue",
        "underlined": true,
        "italic": true,
        "clickEvent": {
            "action": "suggest_command",
            "value": "/tag @s add need"
        },
        "click_event": {
            "action": "suggest_command",
            "command": "/tag @s add need"
        }
    },
    {
        "text": " ",
        "color": "blue",
        "underlined": true,
        "italic": true,
        "clickEvent": {
            "action": "suggest_command",
            "value": "/tag @s add need"
        },
        "click_event": {
            "action": "suggest_command",
            "command": "/tag @s add need"
        }
    },
    {
        "text": "'need'",
        "color": "blue",
        "underlined": true,
        "italic": true,
        "clickEvent": {
            "action": "suggest_command",
            "value": "/tag @s add need"
        },
        "click_event": {
            "action": "suggest_command",
            "command": "/tag @s add need"
        }
    },
    {
        "text": " ",
        "color": "blue",
        "underlined": true,
        "italic": true,
        "clickEvent": {
            "action": "suggest_command",
            "value": "/tag @s add need"
        },
        "click_event": {
            "action": "suggest_command",
            "command": "/tag @s add need"
        }
    },
    {
        "type": "translatable",
        "translate": "tick.kill.dfl.tag",
        "fallback": "标签",
        "color": "blue",
        "underlined": true,
        "italic": true,
        "clickEvent": {
            "action": "suggest_command",
            "value": "/tag @s add need"
        },
        "click_event": {
            "action": "suggest_command",
            "command": "/tag @s add need"
        }
    }
]
# 清除非玩家且无need标签的实体
$execute if score entitynum dfl_scoreboard matches $(num).. \
    run kill @e[type=!minecraft:player,tag=!need]
