function stone_disappearance:new/find_chunk

execute unless function stone_disappearance:new/if_loaded run \
    function #unif.logger:logger/v1/error \
    {"msg":'find_chunk输出坐标在if_loaded检测失败',"namespace":"Stone-Disappearance"}
execute unless function stone_disappearance:new/if_loaded run \
    return fail

execute if function stone_disappearance:new/parent_fill run return run \
    function #unif.logger:logger/v1/info \
    {"msg":'fill在原位置成功',"namespace":"Stone-Disappearance"}

scoreboard objectives add temp.chunk dummy
scoreboard objectives add temp.chunk.child dummy
scoreboard players set n temp.chunk 0
execute store result score x.a temp.chunk run data get storage stone_disappearance:find_chunk pos.a_x
execute store result score z.a temp.chunk run data get storage stone_disappearance:find_chunk pos.a_z
execute store result score x.b temp.chunk run data get storage stone_disappearance:find_chunk pos.b_x
execute store result score z.b temp.chunk run data get storage stone_disappearance:find_chunk pos.b_z
execute store result score n sd.debug run function stone_disappearance:new/traversal_chunk
scoreboard objectives remove temp.chunk
scoreboard objectives remove temp.chunk.child
