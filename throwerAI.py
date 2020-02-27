from numpy import *

dist = array([94, 157, 191, 370, 135, 130, 303, 380, 348, 380, 103, 173, 265, 145, 191, 249, 330, 410, 496, 251])
speed = array([200, 300, 350, 600, 300, 350, 450, 600, 550, 600, 200, 300, 450, 300, 350, 450, 550, 650, 700, 400])

dist_bounce = array([203, 278, 321, 370, 504, 622, 174, 235, 329, 420, 536, 670])
speed_bounce = array([150, 250, 300, 350, 500, 600, 150, 250, 300, 400, 500, 650])

from scipy.interpolate import *

fit = polyfit(dist, speed, 1)
fit_bounce = polyfit(dist_bounce, speed_bounce, 1)

print(fit)
#print(fit_bounce)

from matplotlib.pyplot import *
%matplotlib inline

plot(dist, speed, 'o')
plot(dist, polyval(fit, dist), 'r-')

#plot(dist_bounce, speed_bounce, 'o')
#plot(dist_bounce, polyval(fit_bounce, dist_bounce), 'r-')

