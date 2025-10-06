dialog show @s {\
    type: "confirmation",\
    title: {\
        translate: "dialog.stone_disappearance.advanced_common.title",\
        fallback: "石头消失高级设置：通用设置"\
    },\
    no: {\
        label: {\
            translate: "dialog.white.elephant.common.cancel",\
            fallback: "取消"\
        },\
        tooltip: {\
            translate: "dialog.white.elephant.common.cancel_tooltip",\
            fallback: "放弃当前更改"\
        }\
    },\
    yes: {\
        label: {\
            translate: "dialog.white.elephant.common.save_and_exit",\
            fallback: "保存并退出"\
        },\
        tooltip: {\
            translate: "dialog.white.elephant.common.save_tooltip",\
            fallback: "保存当前设置"\
        },\
        action: {\
            type: "dynamic/run_command",\
            template: "data modify storage stone_disappearance:data settings merge value {success_num:$(success_num),fill_falling_block_with:'$(fill_falling_block_with)',tick_fill:'$(tick_fill)'}"\
        }\
    },\
    inputs: [\
        {\
            type: "number_range",\
            label: {\
                translate: "dialog.stone_disappearance.advanced_common.success_num",\
                fallback: "一次区块清除被视为成功的清除方块数量"\
            },\
            key: "success_num",\
            initial: 50,\
            start: 1,\
            end: 500,\
            step: 1\
        },\
        {\
            type: "minecraft:text",\
            key: "fill_falling_block_with",\
            label: {\
                translate: "dialog.stone_disappearance.advanced_common.fill_falling_block_with",\
                fallback: "用于替换可下落方块的方块"\
            },\
            initial: "glass"\
        },\
        {\
            type: "boolean",\
            key: "tick_fill",\
            label: {\
                translate: "dialog.stone_disappearance.advanced_common.tick_fill",\
                fallback: "实时清除玩家附近3*3*3区域内的石头"\
            },\
            initial: true\
        }\
    ]\
}
