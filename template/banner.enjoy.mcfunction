#define datapack_banner(name, author, author_url, license_name, license_url)
tellraw @a "--------------------"
tellraw @a [{"text": "| #(name) "},{"type":"translatable","translate":"license.white.elephant.enable","fallback":"数据包加载成功","color":"green","bold":true}]
tellraw @a [{"text": "| "},{"text":"by #(author)","color":"blue","underlined":true,"italic":true,"clickEvent":{"action":"open_url","value":"#(author_url)"},"click_event":{"action":"open_url","url":"#(author_url)"}}]
tellraw @a "| "
tellraw @a [{"text": "| "},{"type":"translatable","translate":"license.white.elephant.use","fallback":"本数据包使用","bold": true},{"text": " "},{"text":"#(license_name)","color":"blue","underlined":true,"italic":true,"clickEvent":{"action":"open_url","value":"#(license_url)"},"click_event":{"action":"open_url","url":"#(license_url)"}},{"text": " "},{"type":"translatable","translate":"license.white.elephant.open.source","fallback":"协议开源","bold": true}]
tellraw @a {"type":"translatable","translate":"no.resource.pack.white.elephant.a","fallback":"| "}
#end