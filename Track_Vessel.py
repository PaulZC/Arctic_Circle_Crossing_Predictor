# Track_Vessel.py
#
# By: Paul Clark (PaulZC), October 19th 2024
#
# Licence: MIT
#
# This code will track a single vessel, or multiple vessels, for the time windows defined in the code.
# Each url request is written to a separate file.

from datetime import datetime
import pytz # pip install pytz
import urllib.request
from time import sleep

class Tracker():
    def __init__(self):
        self.vessels = {}
        self.windows = []
        self.userkey = ''

    def addVessel(self, name, IMO):
        self.vessels[name] = IMO

    def addWindow(self, tz, start, end):
        window = {
            'tz': tz,
            'start': start,
            'end': end
        }
        self.windows.append(window)

    def setUserKey(self, key):
        self.userkey = key

    def track(self):
        while True:

            inWindow = False
            futureWindow = False

            for window in self.windows:
                now = datetime.now(pytz.timezone(window['tz'])) # now in the window timezone
                print("Now :          " + now.isoformat())
                start = pytz.timezone(window['tz']).localize(datetime.strptime(window['start'], "%Y-%m-%d %H:%M:%S"))
                print("Window start : " + start.isoformat())
                end = pytz.timezone(window['tz']).localize(datetime.strptime(window['end'], "%Y-%m-%d %H:%M:%S"))
                print("Window end :   " + end.isoformat())

                if now >= start and now <= end:
                    inWindow = True
                    print("In window")
                
                if now <= end:
                    futureWindow = True

            if not futureWindow:
                print("All time windows have expired")
                break
            
            if inWindow:
                # Construct the URL for the VESSELS API request
                request = "https://api.vesselfinder.com/vessels?userkey="
                request += self.userkey
                request += "&imo="
                for vessel in self.vessels.keys():
                    request += str(self.vessels[vessel]) # Add each IMO
                    if vessel != list(self.vessels.keys())[-1]:
                        request += ","
                print("Request : " + request)

                result = urllib.request.urlopen(request).read().decode("utf-8")

                # Write result to file
                dt = datetime.now(pytz.UTC) # Use UTC for the file name
                filename = dt.strftime("Track_Vessel_UTC_%Y-%m-%d_%H-%M-%S.json")
                with open(filename, 'w') as f:
                    f.write(result)
                print("Wrote JSON to " + filename + " :")
                print(result)

            # Repeat every 60 seconds until all windows have expired
            sleep(60)
            
if __name__ == '__main__':

    tracker = Tracker()

    # Set the user key
    tracker.setUserKey('<ADD YOUR KEY HERE>')

    # Add a vessel: name, IMO
    tracker.addVessel('MS Polarlys', 9107796)

    # Add a time window: timezone, start, end
    # timezone is in pytz format. See pytz.all_timezones
    # start and end are in YYYY-MM-DD HH:MM:SS format
    tracker.addWindow('Europe/Oslo', '2024-10-21 07:00:00', '2024-10-21 10:00:00')

    tracker.track()
