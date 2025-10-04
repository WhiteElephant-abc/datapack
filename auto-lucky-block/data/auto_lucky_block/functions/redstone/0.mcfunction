title @a actionbar {"text":"lucky block !","color":"yellow"}
execute at @a run fill ~ ~1 ~ ~ ~1 ~ lucky:lucky_block
execute at @a run fill ~ ~ ~ ~ ~ ~ minecraft:redstone_block
execute at @a run fill ~ ~ ~ ~ ~ ~ air
schedule function auto_lucky_block:redstone/15 1s