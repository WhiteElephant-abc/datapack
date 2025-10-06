dialog show @s {\
    type: "confirmation",\
    title: {\
        translate: "dialog.stone_disappearance.advanced_nether.title",\
        fallback: "石头消失高级设置：下界设置"\
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
            template: "data modify storage stone_disappearance:data settings merge value {nether_block:'$(nether_block)',nether_min:$(nether_min),nether_max:$(nether_max)}"\
        }\
    },\
    inputs: [\
        {\
            type: "minecraft:text",\
            key: "nether_block",\
            label: {\
                translate: "dialog.stone_disappearance.advanced.replace_stone_with",\
                fallback: "将石头替换为："\
            },\
            initial: "glass"\
        },\
        {\
            type: "number_range",\
            key: "nether_min",\
            label: {\
                translate: "dialog.stone_disappearance.advanced_nether.min",\
                fallback: "下界下限"\
            },\
            start: -100,\
            end: 500,\
            step: 1,\
            initial: 0\
        },\
        {\
            type: "number_range",\
            key: "nether_max",\
            label: {\
                translate: "dialog.stone_disappearance.advanced_nether.max",\
                fallback: "下界上限"\
            },\
            start: -100,\
            end: 500,\
            step: 1,\
            initial: 255\
        }\
    ]\
}
