# Extract_Crossings.py
#
# By: Paul Clark (PaulZC), October 20th 2024
#
# Licence: MIT
#
# This code will open the pickle file created by Collate.py and
# calculate the time of any Arctic Circle crossings

from datetime import datetime, timedelta
import pickle
import pytz
import math
from haversine import haversine, Unit

class ExtractCrossings():
    def __init__(self):
        self.pickleFile = 'Track_Vessel.pkl'
        self.ArcticCircleLatitude = 66. + (33. / 60.) # Historical value: 66 degrees 33 minutes
        self.timezone = 'UTC'

    def setPickleFilename(self, filename):
        self.pickleFile = filename

    def setArcticCircleLatitude(self, lat):
        self.ArcticCircleLatitude = lat

    def setTimeZone(self, tz):
        self.timezone = tz

    def greatCircleDistance(self, lat1, lon1, lat2, lon2):
        # https://en.wikipedia.org/wiki/Great-circle_distance
        lat1_radians = math.radians(lat1)
        lon1_radians = math.radians(lon1)
        lat2_radians = math.radians(lat2)
        lon2_radians = math.radians(lon2)
        delta_lon = lon1_radians - lon2_radians
        cos_delta_lon = math.cos(delta_lon)
        sin_lat1 = math.sin(lat1_radians)
        cos_lat1 = math.cos(lat1_radians)
        sin_lat2 = math.sin(lat2_radians)
        cos_lat2 = math.cos(lat2_radians)
        central_angle = math.acos((sin_lat1 * sin_lat2) + (cos_lat1 * cos_lat2 * cos_delta_lon))
        earth_radius = 3443.9308 # nautical miles
        distance = earth_radius * central_angle
        return distance

    def greatCircleDistanceHaversine(self, lat1, lon1, lat2, lon2):
        return haversine((lat1, lon1), (lat2, lon2), unit=Unit.NAUTICAL_MILES)

    def extractCrossings(self):
        # Load the pickle file
        pkl = None
        with open(self.pickleFile, 'rb') as f:
            pkl = pickle.load(f)

        # Search for all vessels
        vessels = {}
        for entry in pkl:
            if str(entry['IMO']) not in vessels.keys():
                vessels[str(entry['IMO'])] = entry['NAME']

        print()
        print("Found vessels:")
        for vessel in vessels.keys():
            print(vessel + " : " + vessels[vessel])

        # For each vessel, find entries either side of the Arctic Circle latitude
        for vessel in vessels.keys():
            latSouthOfCircle = -90.
            entrySouthOfCircle = None
            for entry in pkl:
                if str(entry['IMO']) == vessel: # Match the vessel
                    # Set latSouthOfCircle to the highest latitude which is <= the Circle
                    if entry['LATITUDE'] >= latSouthOfCircle and entry['LATITUDE'] <= self.ArcticCircleLatitude:
                        latSouthOfCircle = entry['LATITUDE']
                        entrySouthOfCircle = entry
                    # Check latSouthOfCircle and been set and the latitude of this entry is > the Circle
                    if latSouthOfCircle > -90. and entry['LATITUDE'] > self.ArcticCircleLatitude:

                        # Gather the data we need to calculate the crossing
                        southLat = entrySouthOfCircle['LATITUDE']
                        southLon = entrySouthOfCircle['LONGITUDE']
                        southSpeed = entrySouthOfCircle['SPEED']
                        southDT = pytz.timezone('UTC').localize(datetime.strptime(entrySouthOfCircle['TIMESTAMP'], "%Y-%m-%d %H:%M:%S UTC"))
                        northLat = entry['LATITUDE']
                        northLon = entry['LONGITUDE']
                        northSpeed = entry['SPEED']
                        northDT = pytz.timezone('UTC').localize(datetime.strptime(entry['TIMESTAMP'], "%Y-%m-%d %H:%M:%S UTC"))

                        # Calculate the fractional distance to the Circle - by Latitude alone
                        deltaLat = northLat - southLat
                        deltaCircle = self.ArcticCircleLatitude - southLat
                        fraction = deltaCircle / deltaLat

                        # Calculate the time of the crossing - by Latitude alone
                        timeOfCrossingByLat = southDT + ((northDT - southDT) * fraction)

                        # Calculate the Longitude of the crossing - by Latitude alone
                        crossingLon = southLon + ((northLon - southLon) * fraction)
                        crossingDeg = math.floor(crossingLon)
                        crossingMin = math.floor((crossingLon - crossingDeg) * 60.)
                        crossingSec = (((crossingLon - crossingDeg) * 60.) - crossingMin) * 60.

                        # Calculate the Great Circle Distance between the two points
                        distance = self.greatCircleDistanceHaversine(southLat, southLon, northLat, northLon)

                        # Calculate the time of the crossing - by speed
                        timeDelta = northDT - southDT
                        deltaSpeedPerSecond = (northSpeed - southSpeed)  / timeDelta.total_seconds()
                        fractionalDistance = fraction * distance

                        distanceTravelled = 0.0
                        speedNow = southSpeed
                        timeOfCrossingBySpeed = southDT
                        
                        while distanceTravelled < fractionalDistance:
                            distanceTravelled += speedNow / 3600. # Knots -> Nautical Miles per second
                            timeOfCrossingBySpeed += timedelta(0,1) # Add 1 second
                            speedNow += deltaSpeedPerSecond

                        print("-----------------------------------------------------------------")
                        print("Vessel                    : " + str(vessel))
                        print("Arctic Circle             : {:.5f}".format(self.ArcticCircleLatitude))
                        print("Latitude (South)          : {:.5f} at {}".format(southLat, southDT.isoformat()))
                        print("Latitude (North)          : {:.5f} at {}".format(northLat, northDT.isoformat()))
                        print("Longitude of crossing     : {:.5f} ({:02.0f}° {:02.0f}\' {:02.1f}\")".format(crossingLon, crossingDeg, crossingMin, crossingSec))
                        print("Crossing time by Latitude : " + timeOfCrossingByLat.replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone(self.timezone)).isoformat())
                        print("Crossing time by speed    : " + timeOfCrossingBySpeed.replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone(self.timezone)).isoformat())

                        latSouthOfCircle = -90. # Reset

            print("-----------------------------------------------------------------")
            
if __name__ == '__main__':

    crossings = ExtractCrossings()

    crossings.setTimeZone('Europe/Oslo')

    crossings.extractCrossings()

    # https://en.wikipedia.org/wiki/Arctic_Circle
    crossings.setArcticCircleLatitude(66. + (33. / 60.) + (50.2 / 3600.))

    crossings.extractCrossings()
