# Plot_Data.py
#
# By: Paul Clark (PaulZC), November 1st 2024
#
# Licence: MIT
#
# This code will open the pickle file created by
# Extract_Data.py and plot the data using MatPlotLib.

from datetime import datetime, timedelta
import pickle
import pytz
import matplotlib.pyplot as plt

class PlotData():
    def __init__(self):
        self.pickleFile = None
        self.plotTZ = 'UTC'
        self.pickleJar = {}

    def setPickleFilename(self, filename):
        self.pickleFile = filename

    def setPlotTimeZone(self, tz):
        self.plotTZ = tz

    def loadPickleFile(self):
        if self.pickleFile is None:
            return
        
        # Load the pickle file
        self.pickleJar = None
        with open(self.pickleFile, 'rb') as f:
            self.pickleJar = pickle.load(f)

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

    def plotYAgainstX(self, yData, xData):
        xVals = []
        yVals = []
        for DT in self.pickleJar.keys():
            xVals.append(self.pickleJar[DT][xData])
            yVals.append(self.pickleJar[DT][yData])
        
        plt.plot(xVals, yVals)
        plt.xlabel(xData)
        plt.ylabel(yData)
        plt.tick_params(axis='x', labelrotation=90)
        plt.show()        

if __name__ == '__main__':

    plotData = PlotData()

    plotData.setPickleFilename('Track_Vessel_9107796.pkl')

    plotData.setPlotTimeZone('Europe/Oslo')

    plotData.loadPickleFile()

    plotData.plotAgainstDT('SPEED')

    plotData.plotAgainstDT('LATITUDE')

    plotData.plotYAgainstX('REMAINING_NM', 'LATITUDE')

    plotData.plotYAgainstX('CIRCLE_NM', 'LATITUDE')

