from elevation import predictions
from beyond.io.tle import Tle
from beyond.frames import create_station
from beyond.dates import Date
import matplotlib.pyplot as plt
from math import pi, log
import numpy as np

# Creating a list of tles to be able to predict multiple satellite at the same time
tles = {}
# Using Tle function to convert the character chain to usable value (decoding it)
tle = Tle("""STARLINK 1029
1 44734U 19074X   23149.91059346  .00000047  00000-0  22043-4 0  9995
2 44734  53.0556 342.1404 0001119  79.5290 280.5825 15.06389128196896""")
# Adding tle to the list
tles["STARLINK-3069"] = tle
# Create an observation station object using Latitude, Longitude and Altitude parameters
station = create_station('ULB', (50.8134718, 4.3812357, 90))
freq = float(input("Frequency of the signal in Ghz : "))
c = 3e8
wave_length = c / (freq * 1e9)
gain_antenna = 10 ** (30.1 / 10)
gain_station = 10 ** (56.3 / 10)
puissance = 10 ** (43.5 / 10)
EIRP = 30
stoptime = float(input('For how much time you want to predict? (in hours)'))
samplingtime = int(input('What is the desired sampling time? (in second)'))
sat_parameter = predictions(tle, station, stoptime, samplingtime)
deg2rad = pi / 180
v = 0
plot_counter = 0
for i in sat_parameter[4]:
    power_received = np.array([])
    s = i
    i = i - v
    for j in range(i):
        # power_linear = puissance * gain_antenna * gain_station * (wave_length / (4 * pi * sat_parameter[2][v + j] * 1000)) ** 2
        power_linear = pow(10, EIRP / 10) * (wave_length / (4 * pi * sat_parameter[2][v + j]*1000)) ** 2
        power_received = np.append(power_received, 10 * log(power_linear, 10) + 30)
    v = s

    if plot_counter < len(sat_parameter[5]):
        pass_time = sat_parameter[5][plot_counter]
        date_time_pass = pass_time.strftime("%m/%d/%Y,%H:%M:%S")
        plt.plot(power_received, '.', label=date_time_pass)
        plot_counter = 1 + plot_counter

now = Date.now()
hour = now.strftime("%H")
minute = now.strftime("%M")

plt.title('Received power by ULB from the STARLINK 1029 (LEO orbit : 550km) starting at %.3s:%.3s' % (hour, minute))
plt.ylabel("Received power [dBm]")
plt.xlabel("Relative time since pass start [s]")
plt.legend(loc="upper right")
plt.grid()
plt.show()
