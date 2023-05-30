# importing SPG4 libraries
import numpy as np
from beyond.dates import Date, timedelta
from math import cos, sin, pi, log


# Creating a function that allows predictions : it takes as argument a tle, the observation station (in the station
# object format), the duration of prediction (in hours) and the sampling time (in seconds).
# For each time delta (defined by the sampling time), it will compute the azimuth, elevation and radius of the
# satellite in reference of the observation station. The computation is done using the beyond libraries that contains
# the SGP4 model. The function returns lists of azimuths, elevations, radius and time ; computed from the current
# instant till the desired time with the desired sampling time.
def predictions(tle, station, hours, samplingtime):
    # creating list
    t, azims, elevs, radiuses, time = [], [], [], [], []
    nbrpass = []
    # setting the satellite in orbit
    orbit = tle.orbit()
    # initializing the orbit
    start = None
    end = None
    max_alt = None
    t0 = 0
    # Calculate several parameters for each orbits
    for orb in station.visibility(orbit, start=Date.now(), stop=timedelta(hours=hours),
                                  step=timedelta(seconds=samplingtime),
                                  events=True):
        # Calculating and appending in the lists the different parameters
        t.append(t0 * samplingtime)
        elev = orb.phi * 180 / pi
        azim = (360 - (180 / pi * orb).theta) % 360
        r = orb.r / 1000
        azims.append(azim)
        elevs.append(elev)
        radiuses.append(r)
        # Checking if the satellite is moving
        if orb.event is not None:

            # Checking if the satellite is visible for the observation station
            if orb.event.info == 'AOS':  # Acquisition of signal
                start = orb.date
                time.append(start)

            # If the satellite is at the maximum elevation, store useful parameters that will be printed after
            if orb.event.info == 'MAX':
                max_alt = elev
                max_azim = azim
                date_of_max = orb.date

            # Check when the satellite is not visible for the observation satellite anymore and print useful info
            if orb.event.info == 'LOS':  # loss of signal
                end = orb.date
                nbrpass.append(t0)
                if max_alt and max_alt >= 40 : # Considers the satellite visible only if the elevation bigger than 10°
                    print("Pass (start time; max elevation; end time): %s %s %s" % (start, max_alt, end))
                    print("Max elevation at (UTC) with elevation and azimuth:", date_of_max)
                    print("Max elevation in degrees :", max_alt)
                    print("Max azimuth in degrees", max_azim)
                    start = None
                    end = None
                    max_alt = None

        t0 += 1  # Actualise the time list

    return [azims, elevs, radiuses, t, nbrpass, time]


# Creating a function that allows predictions : it takes as argument a tle, the observation station (in the station
# object format), the duration of prediction (in hours) and the sampling time (in seconds).
# For each time delta (defined by the sampling time), it will compute the latitude, longitude and altitude of the
# satellite. The computation is done using the beyond libraries that contains
# the SGP4 model. The function returns lists of latitude, longitude, altitude and time (UTC) ; computed from the current
# instant till the desired time with the desired sampling time.
def latitudeandlongitude(tle, hours, samplingtime):
    # Initializing several parameters
    longitudes, latitudes, altitudes, t = [], [], [], []
    t0 = 0
    # Setting the satellite in orbit
    orb = tle.orbit()
    # For each point of the satellite trajectory, compute different parameters
    for point in orb.ephemeris(start=Date.now(), stop=timedelta(hours=hours), step=timedelta(seconds=samplingtime),
                               events=True):
        # Updating the time list
        t.append(t0 * samplingtime)
        # Conversion to earth rotating frame
        point.frame = 'ITRF'
        # Conversion from cartesian to spherical coordinates (range, latitude, longitude
        point.form = 'spherical'
        # Computing different parameters and adding them to the lists
        lon, lat = np.degrees(point[1:3])
        alt = point[0] / 1000 - 6378.137
        longitudes.append(lon)
        latitudes.append(lat)
        altitudes.append(alt)
        # Updating time
        t0 += 1
    return [t, longitudes, latitudes, altitudes]


