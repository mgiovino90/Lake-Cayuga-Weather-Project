# import packages
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import datetime
from dotenv import load_dotenv
import os


# load credentials
load_dotenv()
cred= os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
cred1= service_account.Credentials.from_service_account_file(cred)

# make list of tables
table_list= ['aurora_table', 'cayuga_table', 'interlaken_table', 'ithaca_table', 'lansing_table', 'seneca_falls_table', 'union_springs_table']


# make bigquery client
proj_id= os.getenv("proj_id")
info_table= os.getenv("dataset_id") + ".region-us.INFORMATION_SCHEMA.TABLE_STORAGE"
info_check= f"`{proj_id}`.`region-us`.INFORMATION_SCHEMA.PROJECT_OPTIONS"
client= bigquery.Client(project= proj_id, credentials= cred1)
storage_df= pd.DataFrame()


# check if info schema enabled
q0= """ SELECT *
        FROM {};
""".format(info_check)

result_df= client.query(query= q0).to_dataframe()
print(result_df.head(20))

    # query to get table storage in kb
q1= """ SELECT table_name,
ROUND(total_logical_bytes / 1024, 2) AS logical_kb,
ROUND(active_logical_bytes / 1024, 2) AS active_kb,
ROUND(long_term_logical_bytes / 1024, 2) AS long_term_kb,
total_rows
FROM region-us.INFORMATION_SCHEMA.TABLE_STORAGE;
"""

job1= client.query(q1)
storage_df= job1.result().to_dataframe()
#storage_df= result1
#config1= bigquery.QueryJobConfig(query_parameters= [bigquery.ScalarQueryParameter(None, "STRING", os.getenv(j))])


if storage_df.shape[0] > 0:
    storage_df.columns= ['Table', 'total_logical_KB', 'active_logical_KB', 'long_term_logical_KB', 'num_rows']
    print(storage_df.head(10))