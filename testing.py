import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import csv
import pandas as pd
import requests
import plotly.express as px
import numpy as np


### Import Data
url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
url_data = requests.get(url)
decoded_content = url_data.content.decode('utf-8')
full_data = list(csv.reader(decoded_content.splitlines(), delimiter=','))
columns = [full_data[0][0], full_data[0][1], full_data[0][2], full_data[0][3], full_data[0][4], full_data[0][5]]
full_data = pd.DataFrame(full_data[1:])
full_data.columns = columns

#Type conversion
full_data = full_data.astype({'cases': int})
full_data['deaths'] = full_data['deaths'].apply(pd.to_numeric)



##### Functions 
#Filter Data by State, County
def filter_data(df, county, state):
    county = str(county).title()
    state = str(state).title()
    filtered_county = df['county'] == county
    filtered_state = df['state'] == state
    filtered_data = full_data[filtered_county]
    filtered_data = filtered_data[filtered_state]
    return filtered_data

#Adds new columns: Percentage Change, New Cases, New Deaths, Week Number

df = filter_data(full_data, 'jefferson','kentucky')


#Calculate new deaths field
def add_columns(df):
    #New Cases
    df['new_cases'] = df.cases-df.cases.shift(1)
    df['new_cases'].iloc[0] = df.cases.iloc[0]

    #New Cases Percentage Change
    df['new_cases_pct'] = None
    df['new_cases_pct'] = round(df.new_cases.pct_change(),2)
    df['new_cases_pct'].iloc[0] = 0

    #New Deaths
    df['new_deaths'] = df.deaths-df.deaths.shift(1)
    df['new_deaths'].iloc[0] = df.deaths.iloc[0]

    #New Deaths Percentage Change
    x = df.new_deaths
    df['new_deaths_pct'] = round(x.pct_change(),2)
    df['new_deaths_pct'].iloc[0] = 0

    #Calculate Week Number Field
    df['week_num']=None 
    week_num = 0
    for i in range(len(df['date'])):
        if i in range(0,6):
            df['week_num'].iloc[i]=1
        df['week_num'].iloc[i]=(week_num//7)+1
        week_num+=1

    return df
    
### Creating dataframe
df = filter_data(full_data, 'erie','ohio')
df = add_columns(df)

counties = np.sort(full_data['county'].unique())
states = full_data['state'].unique()
#states = states.astype('object')

###Dash
#Styling
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Graphs
fig1 = px.line(df, x='date',y='cases') #Figure for testing
fig2 = px.line(df, x='date',y='new_cases') #Figure for testing
fig3 = px.line(df, x='date',y='new_cases_pct') #Figure for testing

#New cases by week number graph
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

fig4 = dict(data=data, layout=layout)




#Layout
states = full_data['state']
states = states.unique()
states = list(states)

all_options = {
    'States': ['New York City', 'San Francisco', 'Cincinnati'],
    'Canada': [u'Montréal', 'Toronto', 'Ottawa']
}
app.layout = html.Div([
    dcc.Dropdown(
        id='countries-radio',
        options=[{'label': s, 'value': s} for s in full_data['state'].unique()],
        value='America'
    ),

    html.Hr(),

    dcc.Dropdown(id='cities-radio'),

    html.Hr(),

    html.Div(id='display-selected-values')
])


@app.callback(
    Output('cities-radio', 'options'),
    Input('countries-radio', 'value'))
def set_cities_options(selected_country):
    return [{'label': i, 'value': i} for i in all_options[selected_country]]


@app.callback(
    Output('cities-radio', 'value'),
    Input('cities-radio', 'options'))
def set_cities_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('display-selected-values', 'children'),
    Input('countries-radio', 'value'),
    Input('cities-radio', 'value'))
def set_display_children(selected_country, selected_city):
    return u'{} is a city in {}'.format(
        selected_city, selected_country,
    )

def show_hide_element(visibility_state):
    if visibility_state == 'on':
        return {'display': 'block'}
    if visibility_state == 'off':
        return {'display': 'none'}

if __name__ == '__main__':
    app.run_server(debug=True, port=8052)