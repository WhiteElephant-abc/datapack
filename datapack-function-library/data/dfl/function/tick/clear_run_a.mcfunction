## 清除单个物品并执行命令
$function dfl:lib/things_count {name:"$(name)"}

$execute as @a if score @s dfl_$(name)_num matches 1.. run $(run)
$execute as @a if score @s dfl_$(name)_num matches 1.. run clear @s $(name) 1
