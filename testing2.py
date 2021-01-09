import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import csv
import json
import pandas as pd
import requests
import plotly.express as px
from covid19 import filter_data, add_columns

## Import Data
url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
url_data = requests.get(url)
decoded_content = url_data.content.decode('utf-8')
full_data = list(csv.reader(decoded_content.splitlines(), delimiter=','))
columns = [full_data[0][0], full_data[0][1], full_data[0][2], full_data[0][3], full_data[0][4], full_data[0][5]]
full_data = pd.DataFrame(full_data[1:])
full_data.columns = columns

##Styles
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

## Layout

#Dropdowns
app.layout = html.Div(
    children = [
        dcc.Dropdown(id='state-dropdown', #State
        options=[{'label': s, 'value':s} for s in sorted(full_data.state.unique())],
        value='Ohio'),

    html.Br(),
    
    dcc.Dropdown(id='county-dropdown', value='Erie'), #County

    #Graphs
    dcc.Graph(id='graph-total-cases'), 
    dcc.Graph(id='graph-total-week'), 
    dcc.Graph(id='graph-new-cases'),
    dcc.Graph(id='covid-new-pct'), 

    #Intermediate Values
    html.Div(id='int-val-1', style={'display':'none'}),
    html.Div(id='int-val-2', style={'display':'none'}),
    html.Div(id='int-val-3', style={'display':'none'})
])

##Callbacks

#Populate county dropdown
@app.callback(
    Output(component_id='county-dropdown', component_property='options'),
    Input(component_id='state-dropdown', component_property='value')
)
def update_output_div(input_value):
    if len(input_value)>0 or input_value != None:
        dff = full_data['state'] == input_value
        df = full_data[dff]
        county = sorted(df.county.unique())
        return [{'label':c,'value':c} for c in county]

#Store state dropdown value
@app.callback(
    Output('int-val-1', 'value'),
    Input('state-dropdown', 'value')
)
def return_intermediate_value(state):
    if state != None:
        return state

#Store county dropdown value
@app.callback(
    Output('int-val-2', 'value'),
    Input('county-dropdown', 'value')
)
def return_intermediate_value2(county):
    if county != None:
        return county

#Create DateFrame from State, County
@app.callback(
    Output('int-val-3', 'value'),
    Input('int-val-1', 'value'),
    Input('int-val-2', 'value')
)
def return_filtered_data(state, county):
    if state != None and county != None:
        df = filter_data(full_data, county, state)
        df = add_columns(df)
        df_json = df.to_json()
        return df_json

#Create figures from DataFrame
@app.callback(
    Output('graph-total-cases', 'figure'),
    Output('graph-total-week', 'figure'),
    Output('graph-new-cases', 'figure'),
    Output('covid-new-pct', 'figure'),
    Input('int-val-3', 'value')
)
def create_graphs(df_json):
    if df_json != None:
        df = pd.read_json(df_json)
        #Figures
        totalCases = px.line(df, x='date', y='cases')
        data = [dict(
            type = 'line',
            x = df.week_num,
            y = df.new_cases,
            transforms = [dict(
                type = 'aggregate',
                groups = df.week_num,
                aggregations = [dict(
                    target = 'y', func = 'sum',enabled = True),
                        ]
                )]
            )]
        layout = dict(
                    title = '<b>New Cases by Week Number</b>',
                    xaxis = dict(title = 'Week Number'),
                    yaxis = dict(title = 'New Cases (count)'),
                    )
        totalWeekNum = dict(data=data, layout=layout)
        newCases = px.line(df, x='date', y='new_cases')
        newCasesPct = px.line(df, x='date', y='new_cases_pct')
        return totalCases, totalWeekNum, newCases, newCasesPct

##Run
if __name__ == '__main__':
    app.run_server(debug=True)