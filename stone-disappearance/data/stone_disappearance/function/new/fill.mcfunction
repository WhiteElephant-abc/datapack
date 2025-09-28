scoreboard objectives add temp.fill dummy
$function stone_disappearance:new/child_fill {a_x:"$(a_x)",a_z:"$(a_z)",b_x:"$(b_x)",b_z:"$(b_z)"}
execute if score 1 temp.fill matches ..50 run scoreboard objectives remove temp.fill
return run scoreboard objectives remove temp.fill