# import packages
from google.cloud import bigquery
from dotenv import load_dotenv
import pandas as pd
import os
import sys


# load the env file------------------------------------------------------------------------------------------------------
# meipass is temp dir for exe
def load_env_file():
    if getattr(sys, 'frozen', False):
        proj_dir= os.path.dirname(sys.executable)
    else:
        proj_dir= os.path.dirname(os.path.abspath(__file__))
    env_path= os.path.join(proj_dir, ".env")
    load_dotenv(dotenv_path= env_path)

# make bigquery client, load apis
load_env_file()
api_key= os.getenv('weather_api')
client= bigquery.Client(project= os.getenv('proj_id'))


table_list= sorted(['aurora_table', 'cayuga_table', 'ithaca_table', 'interlaken_table', 'lansing_table', 'seneca_falls_table', 'union_springs_table'])

cols= ['Date', 'Temp_F', 'Humidity_percent', 'Wind_speed_mph', 'Rain_mm_per_hr', 'Snow_mm_per_hr']

for i, j in enumerate(table_list):
    q1= """SELECT *
            FROM @table1;"""

    config1= bigquery.QueryJobConfig(query_parameters= [bigquery.ScalarQueryParameter("table1", 'STRING', j)])