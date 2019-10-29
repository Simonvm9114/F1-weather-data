# ---------------------SUMMARY---------------------
# This script downloads weather data during Formula 1 races.
# To be able to run this script, we need Formula 1 calendar data.
# This data is collected in the 'getcircuits' script. 
# By running this script, the 'getcircuits' script will automatically be triggered as well.
# Therefore the right data is always in place.
# This script will then find the race that will take place the nearest in the future.
# It will retrieve information about the time and date of the race
# It then will start retrieving weather data from 2 hours before until 2 hours after the race every 10 minutes.

# ---------------------PREPARE---------------------
import getcircuits
import urllib.request, urllib.parse, urllib.error
import sqlite3
import json
import time
import calendar
import ssl
import getpass
# -------------------------------------------------
print(' ')
print(' ')
print('---------------------------------')
print('START SCRIPT EXECUTION FOR F1 WEATHER DATA')

# Define advanced rounding functions
def ceil(fl, step):
    half    = step / 2
    result  = (fl + half) / step 
    result  = round(result)
    result  = result * step
    return result
    
def floor(fl, step):
    half    = step / 2
    result  = (fl - half) / step 
    result  = round(result)
    result  = result * step
    return result
# -------------------------------------------------
# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
# Prepare weather API
api_key = input('Insert your app id: ')
testappid = 'http://api.openweathermap.org/data/2.5/weather?q=London,uk&appid=' + api_key
serviceurl = "http://api.openweathermap.org/data/2.5/weather?"

#Connect to weather API.
appidTry = 1

while True :
    try:
        uh = urllib.request.urlopen(testappid, context=ctx)

    except :
        print('Failed to connect to url.')
        appidTry += 1
        
        if appidTry <= 3:
            print('Possibly there is a typo in your appid')
            api_key = input('Please try again: ')
            testappid = 'http://api.openweathermap.org/data/2.5/weather?q=London,uk&appid=' + api_key
            continue
        else :
            print('Quitting the program after 3 tries to connect')
            quit()
    
    print('')
    print('CONNECTION SUCCESSFULL')
    time.sleep(1)
    break

# Connect to database
season = str(time.strftime('%Y'))
conn = sqlite3.connect('F1'+ season +'.sqlite')
cur = conn.cursor()

#Create weather table if it doesn't already exists
cur.execute('''CREATE TABLE IF NOT EXISTS Weather (
            
            Round                       INTEGER NOT NULL,
            Timestamp_W                 INTEGER NOT NULL,
            Temperature                 REAL,
            Wind_speed                  REAL,
            Wind_direction              REAL,
            Weather_type_id             INTEGER,
            Cloudiness                  INTEGER,
            Humidity                    INTEGER,
            Air_pressure                INTEGER,
            Rain_last_hour_in_mm        INTEGER,
            Rain_last_3_hours_in_mm     INTEGER,
            Snow_last_hour_in_mm        INTEGER,
            Snow_last_3_hours_in_mm     INTEGER,
            
            PRIMARY KEY(Round, Timestamp_W))''')

# Get nearest race and define some time offsets
now             = round(time.time())
twohours        = 60 * 60 * 2
fourhours       = twohours * 2
tenminutes      = 10 * 60
reftime         = now - twohours
cur.execute('''SELECT min("Round"), GP_Title, Latitude, Longitude, Timestamp_C FROM Calendar WHERE Timestamp_C > ? ''', (reftime, ))
row = cur.fetchone()
# Store race info in variables
round_id = row[0]
gptitle = row[1]
racestart = row[4]
formattedracestart = time.asctime(time.localtime(racestart))

#Assign variables for api call URL
appid = 'appid=' + api_key
appid_show = 'appid=' + api_key[0:3] + '{...}' + api_key[-3:]
unit = 'units=metric&'
lat = 'lat=' + str(row[2]) + '&'
lng = 'lon=' + str(row[3]) + '&'

#Create full URL
url = serviceurl + unit + lat + lng + appid
url_show = serviceurl + unit + lat + lng + appid_show

# ---------------------GET DATA--------------------
print(' ')
print(' ')
print('----------------', gptitle.upper(), '----------------')
print('Starting time of the race in you local time zone:')
print('--->', formattedracestart)
time.sleep(1)
print(' ')
print('Weather data will be retrieved from:')
print('--->', url_show)
time.sleep(1)

weatherretrievedcount = 0

restartsec = ceil(time.time(), tenminutes)
restart = time.strftime('%H:%Mu' , time.localtime(restartsec))
print(' ')
print('Data will update every 10 minutes. First update:')
print('----------->', restart)
print(' ')

while True : 
    #Loop until 10 minute mark
    while True :
        if round(time.time()) % tenminutes == 0 : break
        else : continue
    
    #Test if next race starts within 2 hours from now/is not over yet.
    if time.time() > racestart - twohours :
        if time.time() < racestart + fourhours :
            
            #Some guiding printstatements
            if weatherretrievedcount == 0 : 
                if time.time() > racestart : 
                    print('Race has started. Data is being retrieved from now until 4 hours after the start of the race.')
                else :
                    print('Race will start within 2 hours. Data is being retrieved from now until 4 hours after the start of the race.')
            
            #Connect to weather API.
            try: 
                uh = urllib.request.urlopen(url, context=ctx)
                time.sleep(2)
            except:
                print('Failed to connect to url.')
                print('Waiting 30 seconds to try again.')
                time.sleep(30)
                continue
            
            data = uh.read().decode()
        
            #Convert results and pick up the necessary values
            js = json.loads(data)
            temp = js['main']['temp']
            timestamp = js['dt']
            if weatherretrievedcount > 0 :
                if timestamp == latest_timestamp :
                    restartsec = ceil(time.time(), tenminutes)
                    restart = time.strftime('%H:%Mu' , time.localtime(restartsec)) 
                    print('No new weather data. Next update:')          
                    print('----------->', restart)
                    print(' ')
                    while True :
                        if round(time.time()) % tenminutes == 0 : break
                        else : continue
                    continue
            weather_type_id = js['weather'][0]['id']
            wind_speed = js['wind']['speed']
            try : wind_dir = js['wind']['deg']
            except : wind_dir = None
            cloudiness = js['clouds']['all']
            humidity = js['main']['humidity']
            pressure = js['main']['pressure']
            try : rain1h = js['rain']['1h'] 
            except : rain1h = None
            try : rain3h = js['rain']['3h'] 
            except : rain3h = None
            try : snow1h = js['snow']['1h'] 
            except : snow1h = None
            try : snow3h = js['snow']['3h'] 
            except : snow3h = None
            
            #Store data into database.
            cur.execute('''INSERT OR IGNORE INTO Weather (
                        Round, Temperature, Timestamp_W, Wind_speed, 
                        Wind_direction, Weather_type_id, Cloudiness, 
                        Humidity, Air_pressure, Rain_last_hour_in_mm,
                        Rain_last_3_hours_in_mm, Snow_last_hour_in_mm,
                        Snow_last_3_hours_in_mm)
                        
                        VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (round_id, temp, timestamp, wind_speed, wind_dir, 
                        weather_type_id, cloudiness, humidity, pressure, rain1h, 
                        rain3h, snow1h, snow3h))
            
            conn.commit()
            latest_timestamp = timestamp
            weatherretrievedcount = weatherretrievedcount + 1
            
            #Print weather report
            print(' ')
            print(' ')           
            print('---------------------CURRENT WEATHER REPORT---------------------')
            if timestamp - racestart < 0 :
                print('     Race starts in:', abs(round((timestamp - racestart) / 60)), 'minutes')
            else :
                print('     Time underway:', round((timestamp - racestart) / 60), 'minutes')
            print('     Temperature:', temp)
            print('     Wind speed:', wind_speed)
            print('     humidity:', humidity)
            print('     cloudiness:', cloudiness)
            print('----------------------------------------------------------------')
            
            #Pause until next 10 minutes mark
            restartsec = ceil(time.time(), tenminutes)
            restart = time.strftime('%H:%Mu' , time.localtime(restartsec))
            print('script will pause for about 10 minutes. Next update:')
            print('----------->', restart)
            print(' ')
            while True :               
                if round(time.time()) % tenminutes == 0: break
                else : continue
    
    #Else statements for when a race is over or will start more than 2 hours from now.
        else : 
            print('Race is over. Finishing script execution')
            break

    else :
        ctrltime = round(time.time())
        if  ctrltime % tenminutes == 0:
            timetillstart = racestart - ctrltime
            minutesleft = round((timetillstart % 3600) / 60)
            hoursleft = round((timetillstart - minutesleft * 60 ) / 3600)
            print(hoursleft, 'hours and', minutesleft, 'minutes before start of the race')
            restartsec = ceil(ctrltime + 1, tenminutes)
            restart = time.strftime('%H:%Mu' , time.localtime(restartsec))
            print('Next update:')
            print('----------->', restart)
            while True :
                if round(time.time()) == ctrltime : continue
                else : break
        else : continue    
            
print(' ')
print('---------------------------------')
print('WEATHER RETRIEVAL COMPLETED')
print('Collected weather data for', weatherretrievedcount, 'moments in the race')
print('EXECUTION FINISHED')
print('---------------------------------')