dialog show @s {\
    type: "confirmation",\
    title: {\
        translate: "dialog.stone_disappearance.advanced_end.title",\
        fallback: "石头消失高级设置：末地设置"\
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
            template: "data modify storage stone_disappearance:data settings merge value {end_block:'$(end_block)',end_min:$(end_min),end_max:$(end_max)}"\
        }\
    },\
    inputs: [\
        {\
            type: "minecraft:text",\
            key: "end_block",\
            label: {\
                translate: "dialog.stone_disappearance.advanced.replace_stone_with",\
                fallback: "将石头替换为："\
            },\
            initial: "glass"\
        },\
        {\
            type: "number_range",\
            key: "end_min",\
            label: {\
                translate: "dialog.stone_disappearance.advanced_end.min",\
                fallback: "末地下限"\
            },\
            start: -100,\
            end: 500,\
            step: 1,\
            initial: 0\
        },\
        {\
            type: "number_range",\
            key: "end_max",\
            label: {\
                translate: "dialog.stone_disappearance.advanced_end.max",\
                fallback: "末地上限"\
            },\
            start: -100,\
            end: 500,\
            step: 1,\
            initial: 255\
        }\
    ]\
}
