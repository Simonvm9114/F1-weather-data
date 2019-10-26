import urllib.request, urllib.parse, urllib.error
import sqlite3
import json
import time
import calendar
import ssl

# ---------------------SUMMARY---------------------
# This script downloads F1 calendar details from the current season.
# To do so, it uses the ergast.com F1 API.
# This script has only to be run once a year before the start of the F1 season.
# You can run it more than once though, there is a fail safe build in for this.
print(' ')
print(' ')
print('---------------------------------')
print('START SCRIPT EXECUTION FOR F1 CALENDAR DATA')
# ---------------------PREPARE---------------------
# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
# -------------------------------------------------
# Define URL variables
serviceurl = "http://ergast.com/api/f1/"
format = ".json"
season = str(time.strftime('%Y'))
print('Season to retrieve is', season)
print('---------------------------------')
print(' ')
time.sleep(1)
# Test if season info is available
testurl = serviceurl + season
try : uh = urllib.request.urlopen(testurl, context=ctx)
except : 
    print('No data available for current season yet')
    quit()
print('Data for', season, 'is available')
time.sleep(1)
# -------------------------------------------------
# Connect to database
conn = sqlite3.connect('F1'+ season +'.sqlite')
cur = conn.cursor()
# -------------------------------------------------
# Securing data will not be doubled
cur.execute('''DROP TABLE IF EXISTS Calendar''')
# -------------------------------------------------
# Create table
cur.execute('''CREATE TABLE IF NOT EXISTS Calendar (
            
    Round           INTEGER PRIMARY KEY UNIQUE,
    GP_Title        TEXT, 
    Circuit         TEXT,
    City            TEXT, 
    Country         TEXT, 
    Latitude        REAL, 
    Longitude       REAL, 
    Timestamp_C     INTEGER                          )''')

# ---------------------GET DATA--------------------    
# Create URL and get data
url = serviceurl + season + format
print('Retrieving data from:', url)
uh = urllib.request.urlopen(url, context=ctx)
data_races = uh.read().decode()
js_races = json.loads(data_races)

# -------------------PROCESS DATA------------------
# Get the Grand Prix information
count = 0
for race in js_races['MRData']['RaceTable']['Races'] :
    round = race['round']
    gptitle = race['raceName']
    circuitname = race['Circuit']['circuitName']
    city = race['Circuit']['Location']['locality']
    country = race['Circuit']['Location']['country']
    lat = race['Circuit']['Location']['lat']
    lng = race['Circuit']['Location']['long']
    date = race['date']
    starttime = race['time']
    # ---------------------------------------------
    # Modity date and time to a 'seconds after epoch' timestamp.
    timestamp = date + ' ' + starttime
    struct_timestamp = time.strptime(timestamp, '%Y-%m-%d %H:%M:%SZ')  
    timestamp = calendar.timegm(struct_timestamp)
    # ---------------------------------------------
    # Store data into table
    cur.execute('''INSERT INTO Calendar (
                Round, GP_Title, Circuit, City, Country,
                Latitude, Longitude, Timestamp_C) 
                
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                (round, gptitle, circuitname, city, country,
                 lat, lng, timestamp))
    
    count = count + 1
    conn.commit()

print(' ')
print('---------------------------------')
print('CALENDAR RETRIEVED SUCCESFULLY')
print('Retrieved details for', count, 'Grand Prix')
print('---------------------------------')
time.sleep(1)

