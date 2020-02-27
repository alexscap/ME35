dist_bounce = array([203, 278, 321, 370, 504, 622, 174, 235, 329, 420, 536, 670])
speed_bounce = array([150, 250, 300, 350, 500, 600, 150, 250, 300, 400, 500, 650])

fit_bounce = polyfit(dist_bounce, speed_bounce, 1)

print(fit_bounce)
