$function dfl:lib/things_count {name:"$(name)"}

$execute if score @s dfl_$(name)_num matches 1.. run $(run)
$execute if score @s dfl_$(name)_num matches 1.. run clear @s $(name) 1
$execute if score @s dfl_$(name)_num matches 0 run return fail
$function dfl:tick/clear_run_b {name:"$(name)",run:"$(run)"}