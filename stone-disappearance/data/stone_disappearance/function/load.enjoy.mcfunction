#include("banner.enjoy.mcfunction")
#@datapack_banner(  "Stone Disappearance",  "white_elephant_",  "https://modrinth.com/user/white_elephant",  "GNU GPL",  "https://www.gnu.org/licenses/gpl-3.0.txt",  "https://github.com/WhiteElephant-abc/datapack")
#include("l10n.enjoy.mcfunction")

gamerule commandModificationBlockLimit 2147483647
scoreboard objectives add glass trigger
scoreboard players enable @a glass
#scoreboard players set @a glass 0
scoreboard objectives add sd.debug dummy
scoreboard objectives add sd.settings dummy

execute as @a run \
    function #unif.logger:logger/v1/tips \
    {"msg":'初始化成功',"namespace":"Stone-Disappearance"}