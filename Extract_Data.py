# Extract_Data.py
#
# By: Paul Clark (PaulZC), November 24th 2024
#
# Licence: MIT
#
# This code will open the pickle file created by Collate.py and
# extract the data for the chosen vessel and time window.
# It calculates the total distance travelled (CUMULATIVE_NM)
# and the distance remaining (REMAINING_NM).
# The extracted data is saved to a new pickle file.

from datetime import datetime, timedelta
import pickle
import pytz
from haversine import haversine, Unit
import copy

class ExtractData():
    def __init__(self):
        self.inputPickleFile = 'Track_Vessel.pkl'
        self.outputPickleFile = None
        self.setArcticCircleDegMinSec(66., 33., 0.) # Historical value: 66 degrees 33 minutes
        self.pickleJar = {}
        self.vessel = 0
        self.TZ = ''
        self.start = ''
        self.end = ''
        self.circleDistance = 0.0

    def setInputPickleFilename(self, filename):
        self.inputPickleFile = filename

    def setOutputPickleFilename(self, filename):
        self.outputPickleFile = filename

    def setVessel(self, IMO):
        self.vessel = IMO

    def setWindow(self, tz, start, end):
        self.TZ = tz
        self.start = start
        self.end = end

    # Convert degrees to deg/min/sec
    # This version only works correctly for positive dd
    # Based on https://stackoverflow.com/a/2580236
    def decdeg2dms(self, dd):
        mnt,sec = divmod(dd*3600, 60)
        deg,mnt = divmod(mnt, 60)
        return deg, mnt, sec

    def setArcticCircleLatitude(self, lat):
        self.ArcticCircleLatitude = lat
        self.ArcticCircleDeg, self.ArcticCircleMin, self.ArcticCircleSec = self.decdeg2dms(self.ArcticCircleLatitude)

    def setArcticCircleDegMinSec(self, deg, min, sec):
        self.ArcticCircleDeg = deg
        self.ArcticCircleMin = min
        self.ArcticCircleSec = sec
        self.ArcticCircleLatitude = self.ArcticCircleDeg + (self.ArcticCircleMin / 60.) + (self.ArcticCircleSec / 3600.)

    def greatCircleDistanceHaversine(self, lat1, lon1, lat2, lon2):
        return haversine((lat1, lon1), (lat2, lon2), unit=Unit.NAUTICAL_MILES)

    def findCrossing(self):
        # Find entries either side of the Arctic Circle latitude
        latSouthOfCircle = -90.
        entrySouthOfCircle = None
        for DT in self.pickleJar.keys():
            # Set latSouthOfCircle to the highest latitude which is <= the Circle
            if self.pickleJar[DT]['LATITUDE'] >= latSouthOfCircle and self.pickleJar[DT]['LATITUDE'] <= self.ArcticCircleLatitude:
                latSouthOfCircle = self.pickleJar[DT]['LATITUDE']
                entrySouthOfCircle = self.pickleJar[DT]
                DTSouthOfCircle = DT
            # Check latSouthOfCircle and been set and the latitude of this entry is > the Circle
            if latSouthOfCircle > -90. and self.pickleJar[DT]['LATITUDE'] > self.ArcticCircleLatitude:

                # Gather the data we need to calculate the crossing
                southLat = entrySouthOfCircle['LATITUDE']
                southLon = entrySouthOfCircle['LONGITUDE']
                northLat = self.pickleJar[DT]['LATITUDE']
                northLon = self.pickleJar[DT]['LONGITUDE']

                # Calculate the fractional distance to the Circle - by Latitude alone
                deltaLat = northLat - southLat
                deltaCircle = self.ArcticCircleLatitude - southLat
                fraction = deltaCircle / deltaLat

                # Calculate the Great Circle Distance
                distance = self.greatCircleDistanceHaversine(southLat, southLon, northLat, northLon)

                self.circleDistance = (distance * fraction) + self.pickleJar[DTSouthOfCircle]['CUMULATIVE_NM']

                return

    def extractDataForVessel(self):
        # Load the pickle file
        pkl = None
        with open(self.inputPickleFile, 'rb') as f:
            pkl = pickle.load(f)

        self.pickleJar = {}

        previousEntry = None
        cumulativeNM = 0.0

        start = pytz.timezone(self.TZ).localize(datetime.strptime(self.start, "%Y-%m-%d %H:%M:%S"))
        end = pytz.timezone(self.TZ).localize(datetime.strptime(self.end, "%Y-%m-%d %H:%M:%S"))

        for entry in pkl:
            if entry['IMO'] == self.vessel: # Match the vessel

                if previousEntry is not None and entry['TIMESTAMP'] != previousEntry['TIMESTAMP']: # Remove duplicates

                    DT = pytz.timezone('UTC').localize(datetime.strptime(entry['TIMESTAMP'], "%Y-%m-%d %H:%M:%S UTC"))
                    DTlocal = DT.replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone(self.TZ))

                    if DTlocal >= start and DTlocal <= end: # If in window

                        modifiedEntry = copy.deepcopy(entry)

                        if previousEntry is not None:
                            # Calculate the Great Circle Distance between the two points
                            distance = self.greatCircleDistanceHaversine( \
                                previousEntry['LATITUDE'], previousEntry['LONGITUDE'], \
                                entry['LATITUDE'], entry['LONGITUDE'])
                            cumulativeNM += distance
                            modifiedEntry['CUMULATIVE_NM'] = cumulativeNM
                            # Calculate the speed based on distance travelled
                            previousDT = pytz.timezone('UTC').localize(datetime.strptime(previousEntry['TIMESTAMP'], "%Y-%m-%d %H:%M:%S UTC"))
                            timeDelta = DT - previousDT
                            interval = timeDelta.total_seconds()
                            if interval > 0.0:
                                modifiedEntry['SPEED_BY_DISTANCE'] = 3600. * distance / interval
                            else:
                                modifiedEntry['SPEED_BY_DISTANCE'] = None

                        else:
                            modifiedEntry['CUMULATIVE_NM'] = 0.0
                            modifiedEntry['SPEED_BY_DISTANCE'] = None

                        self.pickleJar[DTlocal] = modifiedEntry

                previousEntry = copy.deepcopy(entry)

        print("Total distance travelled (NM): {:.1f}".format(cumulativeNM))

        pickleJarCopy = copy.deepcopy(self.pickleJar)
        self.pickleJar = {}

        for DTlocal in pickleJarCopy.keys():
            modifiedEntry = copy.deepcopy(pickleJarCopy[DTlocal])

            modifiedEntry['REMAINING_NM'] = cumulativeNM - pickleJarCopy[DTlocal]['CUMULATIVE_NM']

            self.pickleJar[DTlocal] = modifiedEntry

        self.findCrossing() 

        pickleJarCopy = copy.deepcopy(self.pickleJar)
        self.pickleJar = {}

        for DTlocal in pickleJarCopy.keys():
            modifiedEntry = copy.deepcopy(pickleJarCopy[DTlocal])

            modifiedEntry['REMAINING_NM'] = cumulativeNM - pickleJarCopy[DTlocal]['CUMULATIVE_NM']

            modifiedEntry['CIRCLE_NM'] = self.circleDistance - pickleJarCopy[DTlocal]['CUMULATIVE_NM']

            self.pickleJar[DTlocal] = modifiedEntry

        # Now write the list to a pickle file
        if self.outputPickleFile is None:
            self.outputPickleFile = self.inputPickleFile.split('.')[0] + '_' + str(self.vessel) + '.' + self.inputPickleFile.split('.')[1]
        with open(self.outputPickleFile, 'wb') as f:
            pickle.dump(self.pickleJar, f)
            

if __name__ == '__main__':

    extractData = ExtractData()

    extractData.setVessel(9107796) # MS Polarlys

    # Polar Circle Globe on Vikingen Island
    extractData.setArcticCircleLatitude(66.533540)

    # Set the time window: timezone, start, end
    # timezone is in pytz format. See pytz.all_timezones
    # start and end are in YYYY-MM-DD HH:MM:SS format
    extractData.setWindow('Europe/Oslo', '2024-11-23 06:05:00', '2024-11-23 10:10:00')

    extractData.extractDataForVessel()

