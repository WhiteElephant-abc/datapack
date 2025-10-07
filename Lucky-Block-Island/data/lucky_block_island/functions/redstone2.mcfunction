kill @e[type=!player]
tellraw @a [{"type":"translatable","translate":"redstone.lucky.block.island.kill.entity","fallback":"[数据包消息] 已清理实体"}]
schedule function lucky_block_island:redstone2 60s