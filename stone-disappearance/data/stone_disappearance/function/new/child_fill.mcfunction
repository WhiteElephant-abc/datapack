$execute if dimension minecraft:overworld \
    store result score 1 temp.fill run \
    fill $(a_x) -64 $(a_z) $(b_x) 319 $(b_z) glass replace deepslate
$execute if dimension minecraft:overworld \
    store result score 2 temp.fill run \
    fill $(a_x) -64 $(a_z) $(b_x) 319 $(b_z) glass replace stone
execute if dimension minecraft:overworld run \
    scoreboard players operation 1 temp.fill += 2 temp.fill

$execute if dimension minecraft:the_nether \
    store result score 1 temp.fill run \
    fill $(a_x) 0 $(a_z) $(b_x) 255 $(b_z) glass replace netherrack
$execute if dimension minecraft:the_nether \
    store result score 2 temp.fill run \
    fill $(a_x) 0 $(a_z) $(b_x) 255 $(b_z) glass replace basalt
execute if dimension minecraft:the_nether run \
    scoreboard players operation 1 temp.fill += 2 temp.fill

$execute if dimension minecraft:the_end \
    store result score 1 temp.fill run \
    fill $(a_x) 0 $(a_z) $(b_x) 255 $(b_z) glass replace end_stone