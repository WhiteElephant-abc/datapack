dialog show @s {\
    type: "confirmation",\
    title: {\
        translate: "dialog.stone_disappearance.advanced_overworld.title",\
        fallback: "石头消失高级设置：主世界设置"\
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
            template: "data modify storage stone_disappearance:data settings merge value {overworld_block:'$(overworld_block)',overworld_min:$(overworld_min),overworld_max:$(overworld_max)}"\
        }\
    },\
    inputs: [\
        {\
            type: "minecraft:text",\
            key: "overworld_block",\
            label: {\
                translate: "dialog.stone_disappearance.advanced.replace_stone_with",\
                fallback: "将石头替换为："\
            },\
            initial: "glass"\
        },\
        {\
            type: "number_range",\
            key: "overworld_min",\
            label: {\
                translate: "dialog.stone_disappearance.advanced_overworld.min",\
                fallback: "主世界下限"\
            },\
            start: -100,\
            end: 500,\
            step: 1,\
            initial: -64\
        },\
        {\
            type: "number_range",\
            key: "overworld_max",\
            label: {\
                translate: "dialog.stone_disappearance.advanced_overworld.max",\
                fallback: "主世界上限"\
            },\
            start: -100,\
            end: 500,\
            step: 1,\
            initial: 319\
        }\
    ]\
}
