import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import csv
import pandas as pd
import requests
import plotly.express as px
from covid19 import filter_data, add_columns


### Import Data
url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
url_data = requests.get(url)
decoded_content = url_data.content.decode('utf-8')
full_data = list(csv.reader(decoded_content.splitlines(), delimiter=','))
columns = [full_data[0][0], full_data[0][1], full_data[0][2], full_data[0][3], full_data[0][4], full_data[0][5]]
full_data = pd.DataFrame(full_data[1:])
full_data.columns = columns








external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


## Dropdowns
app.layout = html.Div(
    children = [
        dcc.Dropdown(id='dropdown1', #State Dropdown
        options=[{'label': s, 'value':s} for s in sorted(full_data.state.unique())],
        value=''),

    html.Br(),
    
    html.Div(id='my-output', children=[]), #County Dropdown

    html.Div(id='text-test', children=[]),

    html.Div(id='intermediate-value', style={'display':'none'})
])


@app.callback(
    Output(component_id='my-output', component_property='children'),
    Input(component_id='dropdown1', component_property='value')
)

def update_output_div(input_value):
    if len(input_value)>0:
        dff = full_data['state'] == input_value
        df = full_data[dff]
        county = sorted(df.county.unique())
        print('county is ', county)
        print(type(county))
        return html.Div(dcc.Dropdown(id = 'county-dropdown',
        options = [{'label':c,'value':c} for c in county]))

@app.callback(
    Output('text-test', 'children'),
    Input('dropdown1', 'value'),
    Input('my-output', 'value')
)
def return_text(d1, d2):
    print(d1)
    print(d2)
    print(type(d2))
    return 'd1 is {}, d2 is {}'.format(d1, d2)

if __name__ == '__main__':
    app.run_server(debug=True)