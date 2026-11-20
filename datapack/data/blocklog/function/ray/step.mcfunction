execute if score #fluid bl matches 0 if block ~ ~ ~ #blocklog:thin_floor if function blocklog:ray/above_thin run return run function blocklog:ray/skip
execute if score #fluid bl matches 0 if block ~ ~ ~ #blocklog:center unless function blocklog:ray/in_center run return run function blocklog:ray/skip
execute if score #fluid bl matches 0 unless block ~ ~ ~ #blocklog:ray_pass run return run function blocklog:ray/hit
execute if score #fluid bl matches 1 unless block ~ ~ ~ #blocklog:ray_pass_fluid run return run function blocklog:ray/hit
function blocklog:ray/next
