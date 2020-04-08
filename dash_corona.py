import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import os


########################################################################################################################################
########################################################################################################################################
################## Acquring Data #######################################################################################################
########################################################################################################################################
########################################################################################################################################

de = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')
available_indicators = de['Indicator Name'].unique()

df = pd.read_csv('https://query.data.world/s/ihom5k3szttx7w4w2wwqronax7k5db')
df[['Cases','Difference']].fillna(value = 0, inplace = True)
country_list = df['Country_Region'].unique()

metrics_list = ['Daily Cases', 'Cumulative Cases', 'Daily Deaths', 'Cumulative Deaths']


#### function that takes country input, and returns the number of daily confirmed cases in the form of a dataframe/series
#### which has date as the index
def country(country_name):
    country_df = df[df['Country_Region'] == country_name]
    confirmed_df = country_df[country_df['Case_Type'] == 'Confirmed']
    sorted_df = confirmed_df.sort_values('Date', ascending = True)
    sum_df = sorted_df.groupby('Date').sum()['Difference']
    return sum_df


########################################################################################################################################
########################################################################################################################################
################## DASH PORTION ########################################################################################################
########################################################################################################################################
########################################################################################################################################


app = dash.Dash(name = __name__, server = server)
server = app.server
app.config.supress_callback_exceptions = True




app.layout = html.Div([
    html.Div(
        id = 'header',
        children = [
            html.H1('My Coronavirus Dashboard')
        ]
    ),
    html.H2('Daily Cases'),
    dcc.Dropdown(
        id = 'country_dropdown',
        options =  [{'label':i, 'value':i} for i in country_list],
        value = country_list[0]
    ),
    dcc.Dropdown(
        id = 'metric_dropdown',
        options = [{'label':i, 'value':i} for i in metrics_list],
        value = 'Daily Cases'
    ),
    dcc.Graph(
        id = 'virus_graph'
    ),
])




####

@app.callback(
    Output('virus_graph', 'figure'),
    [Input('country_dropdown', 'value'),
    Input('metric_dropdown', 'value' )]
)

def the_virus_graph(country_dropdown_value, metric_dropdown_value):
    ### Daily Cases
    if metric_dropdown_value == 'Daily Cases':
        country_df = df[df['Country_Region'] == country_dropdown_value]
        confirmed_df = country_df[country_df['Case_Type'] == 'Confirmed']
        confirmed_df['Date'] = pd.to_datetime(confirmed_df['Date']);
        sorted_df = confirmed_df.sort_values('Date', ascending = True)
        sum_df = sorted_df.groupby('Date').sum()['Difference']
        x = sum_df.index
        y = sum_df

        return {
            'data':([
                {
                    'x': x, 'y': y, 'type':'bar'
                }
            ])
        }
    ### Cumulative Cases
    elif metric_dropdown_value == 'Cumulative Cases':
        country_df = df[df['Country_Region'] == country_dropdown_value]
        confirmed_df = country_df[country_df['Case_Type'] == 'Confirmed']
        confirmed_df['Date'] = pd.to_datetime(confirmed_df['Date']);
        sorted_df = confirmed_df.sort_values('Date', ascending = True)
        sum_df = sorted_df.groupby('Date').sum()['Cases']
        x = sum_df.index
        y = sum_df

        return {
            'data':([
                {
                    'x': x, 'y': y, 'type':'bar'
                }
            ])
        }
    ### Daily Deaths
    elif metric_dropdown_value == 'Daily Deaths':
        country_df = df[df['Country_Region'] == country_dropdown_value]
        confirmed_df = country_df[country_df['Case_Type'] == 'Deaths']
        confirmed_df['Date'] = pd.to_datetime(confirmed_df['Date']);
        sorted_df = confirmed_df.sort_values('Date', ascending = True)
        sum_df = sorted_df.groupby('Date').sum()['Difference']
        x = sum_df.index
        y = sum_df

        return {
            'data':([
                {
                    'x': x, 'y': y, 'type':'bar'
                }
            ])
        }
    ### Daily Deaths
    elif metric_dropdown_value == 'Cumulative Deaths':
        country_df = df[df['Country_Region'] == country_dropdown_value]
        confirmed_df = country_df[country_df['Case_Type'] == 'Deaths']
        confirmed_df['Date'] = pd.to_datetime(confirmed_df['Date']);
        sorted_df = confirmed_df.sort_values('Date', ascending = True)
        sum_df = sorted_df.groupby('Date').sum()['Cases']
        x = sum_df.index
        y = sum_df

        return {
            'data':([
                {
                    'x': x, 'y': y, 'type':'bar', 'color': 'r'
                }
            ]),
        }


if __name__ =='__main__':
    app.run_server(debug = True)

####
