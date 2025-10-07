#include("banner.enjoy.mcfunction")
#@datapack_banner(  "Lucky Block Island",  "white_elephant_",  "https://modrinth.com/user/white_elephant",  "GNU GPL",  "https://www.gnu.org/licenses/gpl-3.0.txt",  "https://github.com/WhiteElephant-abc/datapack")
#include("l10n.enjoy.mcfunction")

# 定时清方块
function lucky_block_island:redstone
# 重置出生点
setworldspawn 0 1 0
gamerule spawnRadius 0
# 添加记分板
scoreboard objectives add minecraft.is.too.hard trigger
scoreboard objectives add no.friendly.fire.and.collision trigger

scoreboard objectives add pos dummy
