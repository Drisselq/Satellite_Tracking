from elevation import predictions, latitudeandlongitude
from beyond.io.tle import Tle
from beyond.frames import create_station
from beyond.dates import Date
import matplotlib.pyplot as plt
from math import pi,cos,sin,log
# Creating a list of tles to be able to predict multiple satellite at the same time
tles = {}
# Using Tle function to convert the character chain to usable value (decoding it)
tle = Tle("""STARLINK 1029
1 44734U 19074X   23149.91059346  .00000047  00000-0  22043-4 0  9995
2 44734  53.0556 342.1404 0001119  79.5290 280.5825 15.06389128196896""")
# Adding tle to the list
tles["STARLINK-1029"] = tle

# Create an observation station object using Latitude, Longitude and Altitude parameters
station = create_station('ULB', (50.8134718, 4.3812357, 90))

stoptime = float(input('For how much time you want to predict? (in hours)'))
samplingtime = int(input('What is the desired sampling time? (in second)'))
alpha = predictions(tle, station, stoptime, samplingtime)
alpha1 = latitudeandlongitude(tle, stoptime, samplingtime)


now = Date.now()
hour = now.strftime("%H")
minute = now.strftime("%M")

# Ploting different parameters
fig, axs = plt.subplots(2, 2)
axs[0, 0].plot(alpha1[0], alpha1[2])
axs[0, 0].set_title("Latitude [deg] in function of time [s]")
axs[1, 0].plot(alpha1[0],alpha1[1])
axs[1, 0].set_title("Longitude [deg] in function of time [s]")
axs[0, 1].plot(alpha[0], alpha[1], '.')
axs[0, 1].set_title("Latitude and Longitude mapping")
axs[1, 1].plot(alpha1[0], alpha1[3],'.')
axs[1, 1].set_title("Altitude [km] in function of time [s]")
fig.tight_layout()
plt.show()
deg2rad = pi / 180

# Converting azimuth and elevation into cartesian coordinate with the observation station as origin and the
# North Pole as the x-axis and the z-axis as the perpendicular axe in regard of the floor
# And plotting the cartesian coordinate in 3D
ax = plt.axes(projection='3d')
v = 0
plot_counter= 0
#Plotting in different color for each visible pass
for i in alpha[4]:
    zline = []
    xline = []
    yline = []
    eirp = []
    s = i
    i = i - v
    for j in range(i):
        zline.append(alpha[2][v+j] * cos((90 - alpha[1][v+j]) * deg2rad))
        xline.append(alpha[2][v+j] * sin((90 - alpha[1][v+j]) * deg2rad) * cos((alpha[0][v+j]) * deg2rad))
        yline.append(alpha[2][v+j] * sin((90 - alpha[1][v+j]) * deg2rad) * sin((alpha[0][v+j]) * deg2rad))
    v = s
    # Removing the first point which is redundant (except for the first pass)
    del zline[0]
    del yline[0]
    del xline[0]
    pass_time = alpha[5][plot_counter]
    date_time_pass = pass_time.strftime("%m/%d/%Y,%H:%M:%S")
    ax.plot3D(xline,yline,zline,label = date_time_pass)
    plot_counter = 1 + plot_counter
    plt.legend(loc="upper right")

# Adding the observation station
ax.plot3D(0, 0, 0, '*')
ax.set_zlabel("Height above the ULB station [km]")
plt.xlabel("Distance along North Pole [km]")
plt.ylabel("Distance along the West [km]")
plt.title("Trajectory of the STARLINK 1029 in ULB Topocentric coordinates (the red star = origin)")
plt.show()
