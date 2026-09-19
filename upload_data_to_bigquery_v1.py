# import packages
from dotenv import load_dotenv
import logging
from google.cloud import bigquery
import os
import datetime
import time
import json
import requests


# make the bigquery client and job config
client= bigquery.Client(project= os.getenv("proj_id"))
job_config= bigquery.LoadJobConfig(write_disposition= "WRITE_APPEND")

# load the env file------------------------------------------------------------------------------------------------------
load_dotenv()

# get todays date
today= datetime.datetime.today()
date_str= today.strftime("%m%d%y")

# setup the logger--------------------------------------------------------------------------------------------------------
logfile= os.path.join(os.getenv("log_dir"), f"weather_log_{date_str}.log")
logger= logging.getLogger("weather")
logger.setLevel(logging.INFO)
format1= logging.Formatter("%(asctime)s-%(level)s-%(message)s")
handler= logging.FileHandler(filename= logfile, mode= "a", encoding= 'utf-8')
handler.setLevel(logging.INFO)
handler.setFormatter(format1)
logger.addHandler(handler)

# get table ids and make table list
cities= ['aurora', 'cayuga', 'interlaken', 'ithaca', 'lansing', 'seneca_falls', 'union_springs']
tables= [f"{i}_table" for i in cities]


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
        response= requests.get(url= url1)
        data= response.json()
        temp= data['main']['temp']
        humid= data['main']['humidity']
        wind= data['wind']['speed']
    except Exception as error1:
        logger.error(f"Error {error1} occurred.")

if __name__=="__main__":

    lat_list, long_list= read_coords(file= os.getenv(key="coord_json"))
