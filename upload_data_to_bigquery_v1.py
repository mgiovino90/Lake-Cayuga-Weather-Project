# import packages
from dotenv import load_dotenv
import logging
from google.cloud import bigquery
import os
import datetime
import time
import json
import requests
import pandas as pd
import sys


# get todays date
today= datetime.datetime.today()
date_str= today.strftime("%m%d%y")

# setup the logger--------------------------------------------------------------------------------------------------------
logfile= os.path.join(os.getenv("log_dir"), f"weather_log_{date_str}.log")
logger= logging.getLogger("weather")
logger.setLevel(logging.INFO)
format1= logging.Formatter("%(asctime)s-%(levelname)s-%(message)s")
handler= logging.FileHandler(filename= logfile, mode= "a", encoding= 'utf-8')
handler.setLevel(logging.INFO)
handler.setFormatter(format1)
logger.addHandler(handler)


# load the env file------------------------------------------------------------------------------------------------------
# meipass is temp dir for exe
if getattr(sys, 'frozen', False):
    proj_dir= os.path.dirname(sys.executable)
else:
    proj_dir= os.path.dirname(os.path.abspath(__file__))
env_path= os.path.join(proj_dir, ".env")
load_dotenv(dotenv_path= env_path)
api= os.getenv("weather_api")


# make the bigquery client and job config
try:
    client= bigquery.Client(project= os.getenv("proj_id"))
    job_config= bigquery.LoadJobConfig(write_disposition= "WRITE_APPEND")
    #logger.info(f"Credentials loaded successfully")
except Exception as error1:
    logger.critical(f"Error {error1} occurred.  Couldn't load credentials.")
    sys.exit()




# get table ids and make table list
cities= ['aurora', 'cayuga', 'interlaken', 'ithaca', 'lansing', 'seneca_falls', 'union_springs']
tables= [f"{i}_table" for i in cities]

# columns
cols= ['Date', 'Temp_F', 'Humidity_percent', 'Wind_speed_mph', 'Rain_mm_per_hr', 'Snow_mm_per_hr']

# read latitude and longitude-----------------------------------------------------------------------------------
def read_coords(file):
    with open(file, mode= 'r') as f:
        dict1= json.load(f)

    lats= []
    longs= []
    for i in sorted(list(dict1.keys())):
        lat1= dict1[i]['lat']
        lats.append(lat1)
        long1= dict1[i]['long']
        longs.append(long1)
    return lats, longs


# upload data to bigquery
def upload_data(lat, long, api, table):
    url1= f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&units=imperial&appid={api}"
    try:
        table_ref= bigquery.Table(table_ref= os.getenv(table))
        response= requests.get(url= url1)
        data= response.json()
        temp= data['main']['temp']
        humid= data['main']['humidity']
        wind= data['wind']['speed']
        rain= data.get('rain', {}).get('1h', 0.0)
        snow= data.get('snow', {}).get('1h', 0.0)
        results= [today, temp, humid, wind, rain, snow]
        df1= pd.DataFrame(data= [results], columns= cols)
        job1= client.load_table_from_dataframe(dataframe= df1, destination= table_ref, job_config= job_config)
        logger.info(f"{table} data uploaded successfully")
    except Exception as error1:
        logger.error(f"Error {error1} occurred.")

if __name__=="__main__":

    lat_list, long_list= read_coords(file= os.getenv(key="coord_json"))

    while True:
        for i, j in enumerate(tables):
            upload_data(lat= lat_list[i], long= long_list[i], api= api, table= j)

        time.sleep(3600)