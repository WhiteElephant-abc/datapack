## 保持拥有指定数量的物品
$function dfl:lib/things_count {name:"$(name)"}
$execute unless score @s dfl_$(name)_num matches $(num).. run give @s $(name) 1
$execute unless score @s dfl_$(name)_num matches ..$(num) run clear @s $(name) 1
$execute if score @s dfl_$(name)_num matches $(num) run return fail
$function dfl:tick/keep_have_things {name:"$(name)",num:"$(num)"}