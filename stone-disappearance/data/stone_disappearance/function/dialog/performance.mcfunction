dialog show @s {\
    type: "confirmation",\
    title: {\
        translate: "dialog.stone_disappearance.performance.title",\
        fallback: "石头消失性能设置"\
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
            template: "data modify storage stone_disappearance:data settings merge value {overworld_block:'$(overworld_block)',n:$(n),tick:$(tick),fill_falling_block:'$(fill_falling_block)',fill_falling_block_with:'glass'}"\
        }\
    },\
    body: [\
        {\
            type: "plain_message",\
            width: 1000,\
            contents: {\
                translate: "dialog.white.elephant.common.technical_limitation",\
                fallback: "由于技术限制，此处显示的设置均为默认值",\
                color: "red",\
                bold: true\
            }\
        }\
    ],\
    inputs: [\
        {\
            type: "boolean",\
            label: {\
                translate: "dialog.stone_disappearance.performance.replace_with_glass",\
                fallback: "将石头替换为玻璃而不是直接清除"\
            },\
            key: "overworld_block",\
            initial: true,\
            on_true: "glass",\
            on_false: "air"\
        },\
        {\
            type: "number_range",\
            label: {\
                translate: "dialog.stone_disappearance.performance.clear_distance",\
                fallback: "单位为区块，清除区块的最远距离"\
            },\
            key: "n",\
            initial: 1,\
            start: 1,\
            end: 20,\
            step: 1\
        },\
        {\
            type: "number_range",\
            label: {\
                translate: "dialog.stone_disappearance.performance.wait_ticks",\
                fallback: "每次清除后等待的tick数"\
            },\
            key: "tick",\
            initial: 20,\
            start: 1,\
            end: 100,\
            step: 1\
        },\
        {\
            type: "boolean",\
            label: {\
                translate: "dialog.stone_disappearance.performance.fill_falling_block",\
                fallback: "将可下落的方块替换为玻璃"\
            },\
            key: "fill_falling_block",\
            initial: true\
        }\
    ]\
}
