# 启用trigger
scoreboard players enable @a minecraft.is.too.hard
scoreboard players enable @a no.friendly.fire.and.collision
# 处理trigger值
execute as @a unless score @s minecraft.is.too.hard matches 1 run \
    scoreboard players set @s minecraft.is.too.hard 0
execute as @a unless score @s no.friendly.fire.and.collision matches 1 run \
    scoreboard players set @s no.friendly.fire.and.collision 0
# minecraft is too hard
execute as @a[scores={minecraft.is.too.hard=1}] run \
    function dfl:tick/mith
execute if entity @a[scores={minecraft.is.too.hard=1}] run \
    function lucky_block_island:mith
# no friendly fire and collision
execute if entity @a[scores={no.friendly.fire.and.collision=1}] run \
    function dfl:tick/team

# 放置lucky_block
fill 0 0 0 0 0 0 lucky:lucky_block replace minecraft:air

# 掉落物传送
execute positioned 0 0 0 as @e[distance=..3,type=item] \
    unless data entity @s Thrower run tp 0 1 0

# 防掉虚空
execute as @e store result score @s pos run data get entity @s Pos[1]
execute as @e[scores={pos=..-64},type=!item] run tp @s 0 20 0
