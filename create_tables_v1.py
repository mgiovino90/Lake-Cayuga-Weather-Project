from google.cloud import bigquery
from dotenv import load_dotenv
import os

# load account credentials
load_dotenv()

# make table names
cities= ['Aurora', 'Ithaca', 'Cayuga', 'Seneca_Falls', 'Union_Springs', 'Interlaken', 'Lansing']
tables= [f"{i}_table" for i in cities]

# bigquery client
client= bigquery.Client(os.getenv("proj_id"))

# make schema
cols= ['Date', 'Temp_F', 'Humidity_percent', 'Wind_speed_mph', 'Rain_mm_per_hr', 'Snow_mm_per_hr']
schema1= []
for i, j in enumerate(cols):
    if i==0:
        a1= "DATETIME"
    else:
        a1= "FLOAT"
    entry1= bigquery.SchemaField(name= j, field_type= a1, mode= "REQUIRED")
    schema1.append(entry1)


# create tables
for i in tables:
    try:
        table_id= os.getenv('dataset_id') + f".{i}"
        table_ref= bigquery.Table(table_ref= table_id, schema= schema1)
        client.create_table(table= table_ref)
        print(f"Table {i} created!")
    except Exception as error1:
        print(f"Error {error1} occurred")
