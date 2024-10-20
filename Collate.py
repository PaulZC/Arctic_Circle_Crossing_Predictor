# Collate.py
#
# By: Paul Clark (PaulZC), October 20th 2024
#
# Licence: MIT
#
# This code will collate all Track_Vessel_UTC_*.json files into a single pickle file
# containing a list of dicts. It will collate all files in the current directory and
# sub-directories.

from datetime import datetime
import pytz # pip install pytz
import os
import json
import pickle

class Collate():
    def __init__(self):
        self.vesselData = []
        self.filename = 'Track_Vessel.pkl'

    def setFilename(self, filename):
        self.filename = filename

    def collate(self):
        # Find all Track_Vessel_UTC_*.json files in the current directory
        filePrefix = 'Track_Vessel_UTC_'
        prefixLen = len(filePrefix)
        fileSuffix = '.json'
        suffixLen = len(fileSuffix)
        foundFiles = []
        for root, dirs, files in os.walk("."):
            if len(files) > 0:
                for afile in files:
                    if afile[-suffixLen:] == fileSuffix and afile[:prefixLen] == filePrefix:
                        fileInfo = {
                            'datetime': None,
                            'filename': ''
                        }
                        fileInfo['datetime'] = datetime.strptime(afile, filePrefix + "%Y-%m-%d_%H-%M-%S" + fileSuffix)
                        fileInfo['filename'] = os.path.join(root, afile)
                        foundFiles.append(fileInfo)

        # Now sort the list into ascending time order
        sortedFiles = sorted(foundFiles, key=lambda d: d['datetime'])

        # Now open each file, convert the contents from JSON to dict, and add to the list
        self.vesselData = []
        for file in sortedFiles:
            with open(file['filename'], 'r') as f:
                jsonData = json.loads(f.read())
                for ais in jsonData: # Each file could contain multiple AIS entries
                    #print(ais)
                    self.vesselData.append(ais['AIS'])

        # Now write the list to a pickle file
        with open(self.filename, 'wb') as f:
            pickle.dump(self.vesselData, f)
            
if __name__ == '__main__':

    collate = Collate()

    collate.collate()
