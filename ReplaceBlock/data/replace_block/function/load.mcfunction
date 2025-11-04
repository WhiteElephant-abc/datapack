function dfl:lib/datapack_banner {\
    name:"ReplaceBlock",\
    author:"white_elephant_",\
    author_url:"https://modrinth.com/user/white_elephant",\
    license_name:"GNU GPL",\
    license_url:"https://www.gnu.org/licenses/gpl-3.0.txt",\
    official_url:"https://github.com/WhiteElephant-abc/datapack"}

gamerule commandModificationBlockLimit 2147483647

scoreboard objectives add rb.debug dummy
scoreboard objectives add rb.settings dummy

execute as @a run \
    function #unif.logger:logger/v1/tips \
    {"msg":'初始化成功',"namespace":"ReplaceBlock"}
