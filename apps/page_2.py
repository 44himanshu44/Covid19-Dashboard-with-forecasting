import pickle
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import json
import scipy.optimize as optim
from fbprophet import Prophet
from app import app

def func_logistic(t, a, b, c):
    return c / (1 + a * np.exp(-b*t))


# load data and geojson
df = pd.read_csv('apps/data/covid_19_india.csv')

px.set_mapbox_access_token(
    "pk.eyJ1IjoiNDRoaW1hbnNodTQ0NCIsImEiOiJjazh5azlnNGgwMnJwM2xxcDJyNzFhMG05In0.srzRed7pv2bC2PSGEuRaNg")

path = "apps/states2.json"
f = open(path, "r")
state_geo = json.loads(f.read())

states_list = [{'label': i, 'value': i} for i in df['states'].unique()]
duration_list = [{'label':'Tomorrow', 'value':1},
                  {'label': 'Next week', 'value': 7},
                  {'label': 'Next month', 'value': 30}]



total_confirmed = int(df[df['states']=='India']['Confirmed'].to_list()[-1])
total_deaths = int(df[df['states']=='India']['Deaths'].to_list()[-1])
total_cured = int(df[df['states']=='India']['Cured'].to_list()[-1])


layout = html.Div(
    [
        
        html.Div(id="output-clientside"),
        dcc.Link('Go to App 2', href='/apps/page_3'),
        html.Div(
            [
                
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "INDIA CORONA STATUS",
                                    style={"margin-left": "-300px"},
                                ),
                                html.H5(
                                    "Detailed Report", style={"margin-left": "-450px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Mahrashtra govt site", id="learn-more-button", style = {'color': '#006eff'}),
                            href="https://www.mygov.in/covid-19/",
                        )
                    ],
                    className="one-half column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P("Select States", className="control_label"),
                        dcc.Dropdown(
                            id='state-picker', 
                            options=states_list, 
                            value='India',
                            className="dcc_control",
            
                        ),
                        html.P("Predict number of cases", className="control_label"),
                        dcc.RadioItems(
                            id="forecast",
                            options=[
                                {"label": "Yes ", "value": "yes"},
                                {"label": "No", "value": "no"},
                            ],
                            value="No",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="period",
                            options=duration_list,
                            value= 1,
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="well_text"), html.H4("Confirmed",style = {'textAlign': 'center'}),
                                    html.Br(),
                                    html.H1('{}'.format(total_confirmed), 
                                    style={'textAlign': 'center','color': '#BF0000'})],
                                    id="wells",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="gasText"), html.H4("Deaths",style = {'textAlign': 'center'}),
                                    html.Br(),
                                    html.H1('{}'.format(total_deaths),
                                    style={'textAlign': 'center','color': '#BF0000'})],
                                    id="gas",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="oilText"), html.H4("Recovered",style = {'textAlign': 'center'}),
                                    html.Br(),
                                    html.H1('{}'.format(total_cured),
                                    style={'textAlign': 'center','color': '#BF0000'})],
                                    id="oil",
                                    className="mini_container",
                                )
                        
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="choropleth",config={
                                                                'displayModeBar': False
                                                            })], ##### choropleth graph
                            id="countGraphContainer",
                            className="pretty_2_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [
                     dcc.Loading(
                                id="loading",
                                type="default",
                                children=html.Div(dcc.Graph(id="line_graph",config={
                                                        'displayModeBar': False
                                                    }))
        )                               ], ####### line graph
                    className="pretty_container five columns",
                ),
                html.Div(
                    [
                    dcc.Loading(
                                id="loading2",
                                type="default",
                                children=html.Div(dcc.Graph(id="bar_confirmed",config={
                                                            'displayModeBar': False   ###### bar confirmed
                                                        })))
                                        ],  
                    className="pretty_container seven columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="bar_deaths",config={
                                                'displayModeBar': False
                                                                 })],    ##### bar deaths
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="bar_recovered",config={
                                                'displayModeBar': False  ####### bar recovered
                                                                 })],
                    className="pretty_container seven columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="pie_chart_ac",config={
                                                'displayModeBar': False   #### pie chart for active/closed
                                                                 })],    
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="bar_graph",config={
                                                'displayModeBar': False    ##### bar rate
                                                                 })],
                    className="pretty_container seven columns",
                ),
            ],
            className="row flex-display",
        )
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
    
)



############################# choropleth ###############################

@app.callback(Output('choropleth', 'figure'),
              [Input('state-picker', 'value')])
def update_choropleth(state):
    if state == 'India':
        fig = px.choropleth_mapbox(df, geojson=state_geo, locations='states', color='Confirmed',
                                    color_continuous_scale="reds",
                                    #range_color=(0, 30000),
                                    mapbox_style="light",
                                    zoom=3.5, center={"lat": 22, "lon": 78.9629},
                                    opacity=0.7,
                                    hover_data=['Deaths'],
                                    width=800,
                                    height=450,
                                    title='india corona cases'
                                    )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    else:
        df_state = df[df['states'] == state]
        fig = px.choropleth_mapbox(df_state, geojson=state_geo, locations='states', color='Confirmed',
                                color_continuous_scale="reds",
                                #range_color=(0, 30000),
                                mapbox_style="light",
                                zoom=3.5, center={"lat": 22, "lon": 78.9629},
                                opacity=0.7,
                                hover_data=['Deaths'],
                                width=800,
                                height=450,
                                title='india corona cases'
                                )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

############################# line chart ###############################

@app.callback(Output("line_graph", "figure"),
              [Input("state-picker", "value"),
              Input('forecast','value'),
              Input('period','value')])
def update_line(state,forecast,window):

    if forecast == 'yes':
        df_state = df[df['states'] == state]
        df_state_30 = df_state.iloc[-30:,:]
        

        data = pd.DataFrame()
        data['ds'] = df_state_30['Date']
        data['y'] = df_state_30['Confirmed']


        timesteps = [i for i in range(data.shape[0])]
        data['timesteps'] = timesteps

        p0 = np.random.exponential(size=3)
        bounds = (0, [100000., 1000., 1000000000.])
        x = np.array(data['timesteps']) + 1
        y = np.array(data['y'])

        (a,b,c),cov = optim.curve_fit(func_logistic, x, y, bounds=bounds, p0=p0, maxfev=1000000)

        t_fastest = np.log(a) / b
        i_fastest = func_logistic(t_fastest, a, b, c)

        if t_fastest <= x[-1]:
            data['cap'] = func_logistic(x[-1] + 10, a, b, c)
        else:
            data['cap'] = func_logistic(i_fastest + 10, a, b, c)

        data = data[['ds', 'y','cap']]    
        m = Prophet(growth="logistic",interval_width=0.95)
        m.fit(data)
        future = m.make_future_dataframe(periods=window)
        future['cap'] = data['cap'].iloc[0]
        forecast = m.predict(future)
        forecast = forecast.iloc[-window:,:]


        trace1 = go.Scatter(
        x = forecast['ds'],
        y = forecast['yhat'],
        mode = 'lines+markers',
        name = 'Prediction',
        marker=dict(color='#ffbf00'),

        )
        trace0 = go.Scatter(
        x = df_state_30['Date'],
        y = df_state_30['Confirmed'],
        mode = 'lines+markers',
        name = 'confirmed'
        )
        data2 = [trace0, trace1]  # assign traces to data
        layout = go.Layout(
        title = 'Cases for {}'.format(state),
        plot_bgcolor= '#e3e3e3',
        paper_bgcolor = '#e3e3e3',
        font = { 'color':'darkslategray'},
        xaxis = {
            'showgrid': True
        }
        )
        fig = go.Figure(data=data2,layout = layout)
        #fig.update_xaxes(rangeslider_visible=True, title = 'select date range')


    else :


        df_state = df[df['states'] == state]
        df_state_30 = df_state.iloc[-30:,:]
        # Create traces
        trace0 = go.Scatter(
            x=df_state_30['Date'],
            y=df_state_30['Confirmed'],
            mode='lines+markers',
            name='Confirmed'
        )
        trace1 = go.Scatter(
            x=df_state_30['Date'],
            y=df_state_30['Deaths'],
            mode='lines+markers',
            name='Deaths'
        )
        trace2 = go.Scatter(
            x=df_state_30['Date'],
            y=df_state_30['Cured'],
            mode='lines+markers',
            name='Recovered'
        )
        data = [trace0, trace1, trace2]  # assign traces to data
        layout = go.Layout(
        title = 'Cases for {}'.format(state),
        plot_bgcolor= 'whitesmoke',
        paper_bgcolor = 'whitesmoke',
        font = { 'color':'darkslategray'},
        xaxis = {
            'showgrid': True
        }
        )
        fig = go.Figure(data=data,layout = layout)
        #fig.update_xaxes(rangeslider_visible=True, title = 'select date range')

    return fig


############################# bar plot daily confirmed ###############################

@app.callback(Output('bar_confirmed', 'figure'),
              [Input('state-picker', 'value'),
              Input('forecast','value'),
              Input('period','value')])
def update_bar_confirmed(state,forecast,window):

    if forecast == 'yes':
        df_state = df[df['states'] == state]
        df_state_30 = df_state.iloc[-30:,:]
        

        data = pd.DataFrame()
        data['ds'] = df_state_30['Date']
        data['y'] = df_state_30['Confirmed']


        timesteps = [i for i in range(data.shape[0])]
        data['timesteps'] = timesteps

        p0 = np.random.exponential(size=3)
        bounds = (0, [100000., 1000., 1000000000.])
        x = np.array(data['timesteps']) + 1
        y = np.array(data['y'])

        (a,b,c),cov = optim.curve_fit(func_logistic, x, y, bounds=bounds, p0=p0, maxfev=1000000)

        t_fastest = np.log(a) / b
        i_fastest = func_logistic(t_fastest, a, b, c)

        if t_fastest <= x[-1]:
            data['cap'] = func_logistic(x[-1] + 10, a, b, c)
        else:
            data['cap'] = func_logistic(i_fastest + 10, a, b, c)

        data = data[['ds', 'y','cap']]    
        m = Prophet(growth="logistic",interval_width=0.95)
        m.fit(data)
        future = m.make_future_dataframe(periods=window)
        future['cap'] = data['cap'].iloc[0]
        forecast = m.predict(future)
        forecast = forecast.iloc[-window:,:]


        
        df_state = df[df['states']==state]
        df_state = df_state.iloc[-30:,:]
        trace1 = go.Bar(
        x=df_state['Date'],
        y = df_state['Confirmed'].diff()[1:].astype(int).to_list()[:],
        name = "Daily Cases",
        text = df_state['Confirmed'].diff()[1:].astype(int).to_list()[:],
        textposition='outside',
        marker=dict(color='#58697a')
        )

        trace2 = go.Bar(
            x=forecast['ds'],
            y = forecast['yhat'].diff()[1:].astype(int).to_list()[1:],
            name = "Prediction",
            text = df_state['Confirmed'].diff()[1:].astype(int).to_list()[:],
            textposition='outside',
            marker=dict(color='#ffbf00')
        ) 



        layout = go.Layout(
            title="Daily cases for {}".format(state),
            barmode = 'group',
            plot_bgcolor = 'whitesmoke',
            paper_bgcolor = 'whitesmoke',
            font = { 'color':'darkslategray'}
        )
        data2 = [trace1, trace2]
        fig = go.Figure(data=data2, layout=layout)
        #fig.update_xaxes(rangeslider_visible=True, title = 'select date range')
        

    else :

        df_state = df[df['states']==state]
        df_state = df_state.iloc[-30:,:]
        trace1 = go.Bar(
        x=df_state['Date'],
        y = df_state['Confirmed'].diff()[1:].astype(int).to_list()[:],
        name = "Daily Cases",
        text = df_state['Confirmed'].diff()[1:].astype(int).to_list()[:],
        textposition='outside',
        marker=dict(color='#58697a')
        )
        layout = go.Layout(
        title="Daily cases for {}".format(state),
        barmode = 'group',
        plot_bgcolor = 'whitesmoke',
        paper_bgcolor = 'whitesmoke',
        font = { 'color':'darkslategray'}
        )
        data3 = [trace1]
        fig = go.Figure(data=data3, layout=layout)
        #fig.update_xaxes(rangeslider_visible=True, title = 'select date range')
    
    return fig


############################# bar plot daily deaths ###############################

@app.callback(Output('bar_deaths', 'figure'),
              [Input('state-picker', 'value')])
def update_bar_confirmed(state):
    df_state = df[df['states']==state]
    df_state = df_state.iloc[-30:,:]
    trace2 = go.Bar(
    x=df_state['Date'],
    y = df_state['Deaths'].diff()[1:].astype(int).to_list()[1:],
    name = "Daily Cases",
    text = df_state['Deaths'].diff()[1:].astype(int).to_list()[1:],
    textposition='outside',
    marker=dict(color='#ff0900')
    )
    layout = go.Layout(
    title="Daily deaths for {}".format(state),
    barmode = 'group',
    plot_bgcolor = 'whitesmoke',
    paper_bgcolor = 'whitesmoke',
    font = { 'color':'darkslategray'}
    )
    data = [trace2]
    fig = go.Figure(data=data, layout=layout)
    
    return fig




############################# bar plot daily recovered ###############################

@app.callback(Output('bar_recovered', 'figure'),
              [Input('state-picker', 'value')])
def update_bar_confirmed(state):
    df_state = df[df['states']==state]
    df_state = df_state.iloc[-30:,:]
    trace3 = go.Bar(
    x=df_state['Date'],
    y = df_state['Cured'].diff()[1:].astype(int).to_list()[1:],
    name = "Daily Cases",
    text = df_state['Cured'].diff()[1:].astype(int).to_list()[1:],
    textposition='outside',
    marker=dict(color='#74d600')
    )
    layout = go.Layout(
    title="Daily recovered for {}".format(state),
    barmode = 'group',
    plot_bgcolor = 'whitesmoke',
    paper_bgcolor = 'whitesmoke',
    font = { 'color':'darkslategray'}
    )
    data = [trace3]
    fig = go.Figure(data=data, layout=layout)
    
    return fig



############################# pie chart active closed ###############################

@app.callback(Output('pie_chart_ac', 'figure'),
              [Input('state-picker', 'value')])
def update_pie_ac(state):
    df_state = df[df['states'] == state]
    active = df_state['active_cases'].to_list()[-1]
    closed = df_state['closed_cases'].to_list()[-1]

    labels = ['Active','Closed']
    values = [active, closed]

    layout = go.Layout(
    title = 'Active and Closed cases for {}'.format(state),
    paper_bgcolor = 'whitesmoke',
    font = { 'color':'darkslategray'}
    )
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.45)],layout = layout)

    return fig


############################# bar plot rate ###############################

@app.callback(Output('bar_graph', 'figure'),
              [Input('state-picker', 'value')])
def barplot(state):
    df_state = df[df['states'] == state]
    df_state = df_state.iloc[-30:,:]
    trace2 = go.Bar(
    x=df_state['Date'],
    y = df_state['death_rate'],
    name = "Death rate %",
    marker=dict(color='#ff0900')
    )


    trace1 = go.Bar(
    x=df_state['Date'],
    y = df_state['recovery_rate'],
    name = "Recovery rate %",
    marker=dict(color='#58697a')
    )

    layout = go.Layout(
    title="Death rate vs Recovery rate in {}".format(state),
    barmode = 'stack',
    plot_bgcolor = 'whitesmoke',
    paper_bgcolor = 'whitesmoke',
    font = { 'color':'darkslategray'}
    )
    data = [trace1, trace2]
    #config = {'displayModeBar': False}

    fig = go.Figure(data=data, layout=layout)
    
    return fig
