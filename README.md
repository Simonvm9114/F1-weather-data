# F1-weather-data
This repository contains code to retrieve weather data during Formula 1 races.


# Resulting table description: 

Round:                    A number that indicates which round in the current Formula 1 World Championship season this race is.
Timestamp_W:              An epoch unix formatted timestamp. Google for unix timestamp for documentation on this type of timestamp.
Temperature:              Temperature in degrees Celcius.
Wind_speed:               Wind speed in meters/second.
Wind_direction:           Wind direction degrees. 0 = North, 90 = East, 180 = South, 270 = West
Weather_type_id:          OpenWeatherMaps weather ID. Matching descriptions can be found in the OpenWeatherMap documentation.
Cloudiness:               In percentages.
Humidity:                 In percentages.
Air_pressure:             Atmospheric pressure in hPa.
Rain_last_hour_in_mm:     Rainfall in millimeters in the last hour.
Rain_last_3_hours_in_mm:  Rainfall in millimeters in the last 3 hours.
Snow_last_hour_in_mm:     Snowfall in millimeters in the last hour.
Snow_last_3_hours_in_mm:  Snowfall in millimeters in the last 3 hours.
