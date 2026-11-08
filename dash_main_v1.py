
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
#import plotly.io as 
from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc


two_weeks= datetime.datetime.today() - datetime.timedelta(days= 14)
two_weeks= two_weeks.replace(hour= 0, minute= 0, second= 0, microsecond= 0)


# format the figure title
def format_title(title):
    dict1= {"text": title, "font": {"size" : 32}, 'automargin': True, "yref":"paper", 
            "x": 0.5, "xanchor":"center", "pad": {"t": 20, "b": 10}}
    return dict1

# format the axis title and tick labels
def format_axis(axis):
    axis_dict= {"title": {"text":axis, "font": {"size": 24}}, 
            "tickfont": {"size": 20}}
    return axis_dict

# format the legend
def format_legend(legend):
    leg_dict= {"font": {"size": 16}, "title": {"text":legend, "font": {"size": 18}}}
    return leg_dict


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


# empty dict to store weather data and aggregated weather data
df_dict= {}
daily_dict= {}
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
    # aggregate the data daily (only makes sense for precipitation)
    day_df= sort_df.resample(rule= "D", on= 'Date').sum()
    day_df= day_df.rename(columns= {"Rain_mm_per_hr":"Rain_mm_per_day", "Snow_mm_per_hr":"Snow_mm_per_day"})
    daily_dict[cities[i]]= day_df
    


# load figure theme
load_figure_template("cyborg")


# initialize dash app
theme1= dbc.themes.CYBORG
app= Dash(__name__, external_stylesheets= [theme1])


city0= 'Ithaca'
precip_list= ['Rain', 'Snow']

# initial temp figure
fig0= px.line(df_dict[city0], x= 'Date', y= 'Temp_F', markers= True, labels= {'Temp_F':'Temperature (F)'}, 
                                      title= city0)
fig0.update_layout(title= format_title(title= city0), margin= {"l":20, "t":20, "r":20, "b":20}, 
                   yaxis= format_axis(axis= "Temperature (F)"), 
                   xaxis= format_axis(axis= "Date"))

# bar chart for precipitation
fig1= px.bar(daily_dict[city0], x= daily_dict[city0].index, y= ["Rain_mm_per_day", "Snow_mm_per_day"], 
             color_discrete_sequence= ['mediumblue', 'white'])
fig1.update_layout(yaxis= format_axis(axis= "Precipitation (mm/day)"), 
                   xaxis= format_axis(axis= "Date"), 
                   legend= format_legend(legend= "Legend"))
for i, j in enumerate(fig1.data):
    j.name= precip_list[i]


# make the layout
app.layout= dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Lake Cayuga Weather', className= "text-center")
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(options= cities, value= city0, id= 'city_name')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure= fig0, id= 'temp_fig')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure= fig1, id= "precip_fig")
        ])
    ])
])

# update the figures based on the dropdown selection
@callback(
    [Output(component_id= 'temp_fig', component_property= 'figure'),
     Output(component_id= 'precip_fig', component_property= 'figure')],
    Input(component_id= 'city_name', component_property= 'value')
)
def update_fig(city_sel):
    # update the temp figure for different cities
    fig= px.line(df_dict[city_sel], x= 'Date', y= 'Temp_F', markers= True, labels= {'Temp_F':'Temperature (F)'}, 
                 title= city_sel)
    fig.update_layout(title= format_title(title= city_sel), margin= {"l":20, "t":20, "r":20, "b":20}, 
                   yaxis= format_axis(axis= "Temperature (F)"), 
                   xaxis= format_axis(axis= "Date"))
    # update the precipitation figure for different cities
    fig2= px.bar(daily_dict[city_sel], x= daily_dict[city_sel].index, y= ["Rain_mm_per_day", "Snow_mm_per_day"], 
                 color_discrete_sequence= ['mediumblue', 'white'])
    fig2.update_layout(yaxis= format_axis(axis= "Precipitation (mm/day)"), 
                   xaxis= format_axis(axis= "Date"), 
                   legend= format_legend(legend= "Legend"))
    for i, j in enumerate(fig2.data):
        j.name= precip_list[i]
    return fig, fig2

# main script
if __name__=="__main__":
    app.run(debug= True)