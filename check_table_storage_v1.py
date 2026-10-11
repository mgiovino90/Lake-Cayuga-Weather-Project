# import packages
import pandas as pd
from google.cloud import bigquery
import datetime
from dotenv import load_dotenv
import os


# load credentials
load_dotenv()

# make list of tables
table_list= ['aurora_table', 'cayuga_table', 'interlaken_table', 'ithaca_table', 'lansing_table', 'seneca_falls_table', 'union_springs_table']

# make bigquery client
client= bigquery.Client(project= os.getenv("proj_id"))

# query to get table storage in kb
q1= """ SELECT ?, 
ROUND(total_logical_bytes / 1024, 2) AS logical_kb,
ROUND(active_logical_bytes / 1024, 2) AS active_kb,
ROUND(long_term_logical_bytes / 1024, 2) AS long_term_kb,
total_rows
"""