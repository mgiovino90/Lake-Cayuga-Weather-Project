
#%%
# import packages
from google.cloud import bigquery
from dotenv import load_dotenv
import pandas as pd
import os
import sys
import datetime
from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import plotly.express as px
import dash_bootstrap_components as dbc


two_weeks= datetime.datetime.today() - datetime.timedelta(days= 14)
two_weeks= two_weeks.replace(hour= 0, minute= 0, second= 0, microsecond= 0)

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


# list of tables
table_list= sorted(['aurora_table', 'cayuga_table', 'ithaca_table', 'interlaken_table', 'lansing_table', 'seneca_falls_table', 'union_springs_table'])
#cols= ['Date', 'Temp_F', 'Humidity_percent', 'Wind_speed_mph', 'Rain_mm_per_hr', 'Snow_mm_per_hr']

# city names for the dictionary
cities= ['Aurora', 'Cayuga', 'Ithaca', 'Interlaken', 'Lansing', 'Seneca Falls', 'Union Springs']

# empty dict to store weather data
df_dict= {}
# loop to store weather data from last 2 weeks
for i, j in enumerate(table_list):
    table1= os.getenv(j)
    # need the backticks to insert the table name
    q1= f"""SELECT *
            FROM `{table1}`
            WHERE Date >= ?;""".format(j)

    config1= bigquery.QueryJobConfig(query_parameters= [bigquery.ScalarQueryParameter(None, 'DATETIME', two_weeks)])
    results_df= client.query_and_wait(query= q1, job_config= config1).to_dataframe()
    sort_df= results_df.sort_values(by= ['Date'])
    df_dict[cities[i]]= sort_df






# initialize dash app
theme1= dbc.themes.CYBORG
app= Dash(__name__, external_stylesheets= [theme1])






# make the layout
app.layout= dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Lake Cayuga Weather', className= "text-center")
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(options= cities, value= 'Ithaca', id= 'city_name')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure= px.line(df_dict['Ithaca'], x= 'Date', y= 'Temp_F', markers= True, labels= {'Temp_F':'Temperature (F)'}),
                      id= 'temp_fig')
        ])
    ])
])

# update the figure based on the dropdown selection
@callback(
    Output(component_id= 'temp_fig', component_property= 'figure'),
    Input(component_id= 'city_name', component_property= 'value')
)
def update_fig(city_sel):
    fig= px.line(df_dict[city_sel], x= 'Date', y= 'Temp_F', markers= True, labels= {'Temp_F':'Temperature (F)'})
    return fig

# main script
if __name__=="__main__":
    app.run(debug= True)