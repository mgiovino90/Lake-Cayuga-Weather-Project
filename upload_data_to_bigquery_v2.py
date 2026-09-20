# import packages
from dotenv import load_dotenv
import logging
from logging.handlers import TimedRotatingFileHandler
from google.cloud import bigquery
import os
import datetime
import time
import json
import requests
import pandas as pd
import sys

# setup the child logger
logger= logging.getLogger("lake_cayuga")
logger.setLevel(logging.INFO)

# load the env file------------------------------------------------------------------------------------------------------
# meipass is temp dir for exe
def load_env_file():
    if getattr(sys, 'frozen', False):
        proj_dir= os.path.dirname(sys.executable)
    else:
        proj_dir= os.path.dirname(os.path.abspath(__file__))
    env_path= os.path.join(proj_dir, ".env")
    load_dotenv(dotenv_path= env_path)



# setup the logger--------------------------------------------------------------------------------------------------------
def make_logger():
    logfile= os.path.join(os.getenv("log_dir"), f"cayuga_lake_log.log")
    # parent logger
    root_logger= logging.getLogger()
    root_logger.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)
    format1= logging.Formatter("%(asctime)s-%(levelname)s-%(message)s")
    handler= TimedRotatingFileHandler(filename= logfile, when= 'midnight', interval= 1, backupCount= 60)
    handler.setLevel(logging.INFO)
    handler.setFormatter(format1)
    root_logger.addHandler(handler)



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
    now= datetime.datetime.today()
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
        results= [now, temp, humid, wind, rain, snow]
        df1= pd.DataFrame(data= [results], columns= cols)
        job1= client.load_table_from_dataframe(dataframe= df1, destination= table_ref, job_config= job_config)
        logger.info(f"{table} data uploaded successfully")
    except Exception as error1:
        logger.error(f"Error {error1} occurred.")

if __name__=="__main__":

    # load the env file and api key
    load_env_file()
    api= os.getenv("weather_api")

    # setup the logger
    make_logger()

    # make the bigquery client and job config
    try:
        client= bigquery.Client(project= os.getenv("proj_id"))
        job_config= bigquery.LoadJobConfig(write_disposition= "WRITE_APPEND")
        #logger.info(f"Credentials loaded successfully")
    except Exception as error1:
        logger.critical(f"Error {error1} occurred.  Couldn't load credentials.")
        sys.exit()

    # get the coordinates
    lat_list, long_list= read_coords(file= os.getenv(key="coord_json"))

    # upload the data every hour
    while True:
        for i, j in enumerate(tables):
            upload_data(lat= lat_list[i], long= long_list[i], api= api, table= j)

        time.sleep(3600)