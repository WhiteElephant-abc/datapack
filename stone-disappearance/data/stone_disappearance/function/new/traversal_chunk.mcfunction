execute if score n temp.chunk >= n sd.settings run \
    function #unif.logger:logger/v1/debug \
    {"msg":'n到达设定上限',"namespace":"Stone-Disappearance"}
execute if score n temp.chunk >= n sd.settings run return run scoreboard players get n temp.chunk

scoreboard players add n temp.chunk 1
scoreboard players operation 2n temp.chunk = n temp.chunk 
scoreboard players operation 2n temp.chunk += n temp.chunk 

scoreboard players set n temp.chunk.child 1
function stone_disappearance:new/child_traversal_chunk/x
execute if score success temp.chunk matches 1 run return run scoreboard players get n temp.chunk

scoreboard players operation n temp.chunk.child = 2n temp.chunk
scoreboard players remove n temp.chunk.child 1
function stone_disappearance:new/child_traversal_chunk/z-
execute if score success temp.chunk matches 1 run return run scoreboard players get n temp.chunk

scoreboard players operation n temp.chunk.child = 2n temp.chunk
function stone_disappearance:new/child_traversal_chunk/x-
execute if score success temp.chunk matches 1 run return run scoreboard players get n temp.chunk

scoreboard players operation n temp.chunk.child = 2n temp.chunk
function stone_disappearance:new/child_traversal_chunk/z
execute if score success temp.chunk matches 1 run return run scoreboard players get n temp.chunk

scoreboard players operation n temp.chunk.child = 2n temp.chunk
function stone_disappearance:new/child_traversal_chunk/x
execute if score success temp.chunk matches 1 run return run scoreboard players get n temp.chunk

return run function stone_disappearance:new/traversal_chunk