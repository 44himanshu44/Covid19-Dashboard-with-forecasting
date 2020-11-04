import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px
import json
from app import app

df = pd.read_csv('apps/data/time-series-19-covid-combined.csv')


px.set_mapbox_access_token("pk.eyJ1IjoiNDRoaW1hbnNodTQ0NCIsImEiOiJjazh5azlnNGgwMnJwM2xxcDJyNzFhMG05In0.srzRed7pv2bC2PSGEuRaNg")

path = "apps/countries.geo.json"
f = open (path, "r")
country_geo = json.loads(f.read())



fig = px.choropleth_mapbox(df, geojson=country_geo, locations='country', color='Confirmed',
                    color_continuous_scale="reds",featureidkey="properties.name",
                    range_color=(0, 50000),
                    mapbox_style="outdoors",
                    animation_frame = 'Date',
                    zoom=1.5, center = {"lat": 27.309310, "lon": 1.262070},
                    opacity=0.7,
                    hover_data = ['Recovered'],
                    width = 1500,
                    height = 900,
                    title = 'How corona spread across the Globe'

                    )
                    
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                   
        
layout = html.Div([
     html.H1("How corona spread throughout the world"),
     dcc.Graph(id = 'graph',figure = fig)
])

