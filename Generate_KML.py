# Generate_KML.py
#
# By: Paul Clark (PaulZC), October 20th 2024
#
# Licence: MIT
#
# This code will open the pickle file created by Collate.py and convert the vessel
# position data into a KML file for Google Earth

from datetime import datetime
import pickle
import simplekml # pip install simplekml
import pytz

class GenerateKML():
    def __init__(self):
        self.pickleFile = 'Track_Vessel.pkl'
        self.vessel = 0
        self.tz = ''
        self.start = ''
        self.end = ''

    def setPickleFilename(self, filename):
        self.pickleFile = filename

    def setVessel(self, IMO):
        self.vessel = IMO

    def setWindow(self, tz, start, end):
        self.tz = tz
        self.start = start
        self.end = end

    def generate(self):
        # Load the pickle file
        pkl = None
        with open(self.pickleFile, 'rb') as f:
            pkl = pickle.load(f)

        # Search for entries which match the vessel and time window
        kml = simplekml.Kml()
        coords = [] # Store all the coords for the Line String
        start = pytz.timezone(self.tz).localize(datetime.strptime(self.start, "%Y-%m-%d %H:%M:%S"))
        end = pytz.timezone(self.tz).localize(datetime.strptime(self.end, "%Y-%m-%d %H:%M:%S"))
        for entry in pkl:
            if entry['IMO'] == self.vessel:
                entryTime = pytz.timezone('UTC').localize(datetime.strptime(entry['TIMESTAMP'], "%Y-%m-%d %H:%M:%S UTC"))
                if entryTime >= start and entryTime <= end:
                    kml.newpoint(name=entry['TIMESTAMP'], coords=[(entry['LONGITUDE'], entry['LATITUDE'])])
                    coords.append((entry['LONGITUDE'], entry['LATITUDE']))

        # Save the Points KML file
        filename = str(self.vessel) + "_Points.kml"
        kml.save(filename)

        # Create the LineString KML file
        kml = simplekml.Kml()
        name = "IMO " + str(self.vessel) + " " + self.tz + " " + self.start + " " + self.end
        kml.newlinestring(name=name , coords=coords)
        filename = str(self.vessel) + "_LineString.kml"
        kml.save(filename)
            
if __name__ == '__main__':

    generate = GenerateKML()

    # Set the vessel: IMO
    generate.setVessel(9107796) # MS Polarlys

    # Set the time window: timezone, start, end
    # timezone is in pytz format. See pytz.all_timezones
    # start and end are in YYYY-MM-DD HH:MM:SS format
    #generate.setWindow('Europe/Oslo', '2024-10-21 07:00:00', '2024-10-21 10:00:00')
    #generate.setWindow('Europe/Oslo', '2024-11-01 06:00:00', '2024-11-01 10:10:00')
    #generate.setWindow('Europe/Oslo', '2024-11-12 06:00:00', '2024-11-12 10:10:00')
    generate.setWindow('Europe/Oslo', '2024-11-23 06:00:00', '2024-11-23 10:10:00')

    generate.generate()