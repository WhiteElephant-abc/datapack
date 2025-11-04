## 设置初始化

# 重置设置
$data modify storage $(storage) replace_block set value \
    {\
        selector:"@e[type=player]",\
        replace_pairs:[\
            {\
                target_block:"stone",\
                replace_with:"glass"\
            },\
            {\
                target_block:"dirt",\
                replace_with:"air"\
            }\
        ],\
        dimensions:[\
            {\
                dimension:"minecraft:overworld",\
                min_y:-64,\
                max_y:319\
            },\
            {\
                dimension:"minecraft:the_nether",\
                min_y:0,\
                max_y:255\
            },\
                {\
                dimension:"minecraft:the_end",\
                min_y:0,\
                max_y:255\
            }\
        ],\
        falling_blocks:{\
            enabled:true,\
            replace_with:"glass",\
            targets:["sand","red_sand","gravel"]\
        },\
        search_range:3,\
        success_threshold:50\
    }
