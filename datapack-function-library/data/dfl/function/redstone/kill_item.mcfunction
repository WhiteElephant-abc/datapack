## TODO
scoreboard objectives add dfl_scoreboard dummy "DFL"
execute store result score item_number dfl_scoreboard run kill @e[type=item,tag=!need]
tellraw @a [{"text":"[DFL] ","color":"gray","italic":true},{"type":"translatable","translate":"redstone.kill.item.dfl.entity.clear","fallback":"清除了","color":"gray","italic":true},{"text":" "},{"score":{"name":"item_number","objective":"dfl_scoreboard"},"color":"gray","italic":true},{"text":" "},{"type":"translatable","translate":"redstone.kill.item.dfl.entity.item","fallback":"个掉落物","color":"gray","italic":true}]
