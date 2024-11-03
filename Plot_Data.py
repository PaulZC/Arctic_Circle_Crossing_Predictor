# Plot_Data.py
#
# By: Paul Clark (PaulZC), November 1st 2024
#
# Licence: MIT
#
# This code will open the pickle file created by Collate.py and
# plot the data using MatPlotLib.

from datetime import datetime, timedelta
import pickle
import pytz
import matplotlib.pyplot as plt
from haversine import haversine, Unit
import copy

class PlotData():
    def __init__(self):
        self.pickleFile = 'Track_Vessel.pkl'
        self.plotTZ = 'UTC'
        self.pickleJar = {}
        self.vessel = 0
        self.TZ = ''
        self.start = ''
        self.end = ''

    def setPickleFilename(self, filename):
        self.pickleFile = filename

    def setPlotTimeZone(self, tz):
        self.plotTZ = tz

    def setVessel(self, IMO):
        self.vessel = IMO

    def setWindow(self, tz, start, end):
        self.TZ = tz
        self.start = start
        self.end = end

    def greatCircleDistanceHaversine(self, lat1, lon1, lat2, lon2):
        return haversine((lat1, lon1), (lat2, lon2), unit=Unit.NAUTICAL_MILES)

    def extractDataForVessel(self):
        # Load the pickle file
        pkl = None
        with open(self.pickleFile, 'rb') as f:
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
                    DTlocal = DT.replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone(self.plotTZ))

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

    def plotAgainstDT(self, yData):
        xVals = []
        yVals = []
        for DT in self.pickleJar.keys():
            xVals.append(DT)
            yVals.append(self.pickleJar[DT][yData])
        
        plt.plot(xVals, yVals)
        plt.ylabel(yData)
        plt.tick_params(axis='x', labelrotation=90)
        plt.show()        

if __name__ == '__main__':

    plotData = PlotData()

    plotData.setPlotTimeZone('Europe/Oslo')

    plotData.setVessel(9107796) # MS Polarlys

    # Set the time window: timezone, start, end
    # timezone is in pytz format. See pytz.all_timezones
    # start and end are in YYYY-MM-DD HH:MM:SS format
    plotData.setWindow('Europe/Oslo', '2024-10-21 07:00:00', '2024-10-21 10:00:00')

    plotData.extractDataForVessel()

    plotData.plotAgainstDT('SPEED')

