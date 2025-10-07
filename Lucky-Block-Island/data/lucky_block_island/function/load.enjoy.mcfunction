#include("banner.enjoy.mcfunction")
#@datapack_banner(  "Lucky Block Island",  "white_elephant_",  "https://modrinth.com/user/white_elephant",  "GNU GPL",  "https://www.gnu.org/licenses/gpl-3.0.txt",  "https://github.com/WhiteElephant-abc/datapack")
#include("l10n.enjoy.mcfunction")

execute unless biome 0 10 0 minecraft:the_void run \
    title @a title \
        {\
            "translate":"title.lucky_block_island.lbi",\
            "bold":true,\
            "color":"yellow",\
            "fallback":"[LBI]幸运方块空岛"\
        }
execute unless biome 0 10 0 minecraft:the_void run \
    title @a subtitle \
        {\
            "translate":"title.lucky_block_island.error.subtitle",\
            "bold":true,\
            "color":"red",\
            "fallback":"维度设置验证失败，请在创建世界时加载数据包"\
        }
execute unless biome 0 10 0 minecraft:the_void run \
    return 0
# 定时清方块
function lucky_block_island:redstone
# 重置出生点
setworldspawn 0 1 0
gamerule spawnRadius 0
# 添加记分板
scoreboard objectives add minecraft.is.too.hard trigger
scoreboard objectives add no.friendly.fire.and.collision trigger
scoreboard objectives add clear.offhand trigger

scoreboard objectives add pos dummy
