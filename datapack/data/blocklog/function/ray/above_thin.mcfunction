# 1 if the ray point is above the bottom quarter of this thin block's cell
execute positioned ~ ~-0.25 ~ if block ~ ~ ~ #blocklog:thin_floor run return 1
return 0
