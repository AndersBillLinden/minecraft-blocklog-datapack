# 1 if the ray point is inside the centred column (6/16 wide, 10/16 high) of this cell
execute positioned ~0.3125 ~ ~ unless block ~ ~ ~ #blocklog:center run return 0
execute positioned ~-0.3125 ~ ~ unless block ~ ~ ~ #blocklog:center run return 0
execute positioned ~ ~ ~0.3125 unless block ~ ~ ~ #blocklog:center run return 0
execute positioned ~ ~ ~-0.3125 unless block ~ ~ ~ #blocklog:center run return 0
execute positioned ~ ~-0.625 ~ if block ~ ~ ~ #blocklog:center run return 0
return 1
