import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import numpy as np
import pandas as pd


########################################################################################################################################
########################################################################################################################################
################## Acquring Data #######################################################################################################
########################################################################################################################################
########################################################################################################################################



df = pd.read_csv('https://query.data.world/s/ihom5k3szttx7w4w2wwqronax7k5db')
df[['Cases','Difference']].fillna(value = 0, inplace = True)
country_list = df['Country_Region'].unique()

metrics_list = ['Daily Cases', 'Cumulative Cases', 'Daily Deaths', 'Cumulative Deaths']

### world total number of cases
confirmed_cases = df[df['Case_Type'] == "Confirmed"]
total_cases = confirmed_cases.Difference.sum()



########################################################################################################################################
########################################################################################################################################
################## DASH PORTION ########################################################################################################
########################################################################################################################################
########################################################################################################################################



app = dash.Dash(__name__)
#app.config.suppress_callback_exceptions = True
server = app.server #uncomment this for deployment





app.layout = html.Div([
    html.Div(
        className = 'header',
        children = [
            html.H1('My Coronavirus Dashboard',
            )
        ]
    ),
    html.Div(
        className = 'left-block',
        children = [
            html.H2('Totals'),
            html.Div([
                html.H3('World total'),
                html.P(total_cases)

            ])
        ]
    ),

    html.Div(
        className = 'middle-block',
        children = [
            html.H2('Daily Cases'),
            dcc.Dropdown(
                id = 'country_dropdown',
                options =  [{'label':i, 'value':i} for i in country_list],
                value = "Canada",
            ),
            dcc.Dropdown(
                id = 'country_dropdown2',
                options =  [{'label':i, 'value':i} for i in country_list],
                value = "US",
            ),
            dcc.Dropdown(
                id = 'metric_dropdown',
                options = [{'label':i, 'value':i} for i in metrics_list],
                value = 'Daily Cases'
            ),
            html.Div(
                className = 'graph1-options',
                children = [
                    html.P('Country Comparison'),
                    dcc.Graph(
                        id = 'virus_graph'
                    ),
            ]),
            html.Div(
                className = 'graph2-options',
                children = [
                    html.P('Global Behavour'),
                    dcc.Graph(
                        id = 'world_graph'
                    )
                ]
            )
])



])




#### Country graph

@app.callback(
    Output('virus_graph', 'figure'),
    [Input('country_dropdown', 'value'),
    Input('country_dropdown2', 'value'),
    Input('metric_dropdown', 'value' )]
)

def the_virus_graph(country_dropdown_value, country_dropdown_value2, metric_dropdown_value):
    ### Daily Cases
    if metric_dropdown_value == 'Daily Cases':
        country_df = df[df['Country_Region'] == country_dropdown_value]
        confirmed_df = country_df[country_df['Case_Type'] == 'Confirmed']
        confirmed_df['Date'] = pd.to_datetime(confirmed_df['Date']);
        sorted_df = confirmed_df.sort_values('Date', ascending = True)
        sum_df = sorted_df.groupby('Date').sum()['Difference']
        x = sum_df.index
        y = sum_df

        country_df2 = df[df['Country_Region'] == country_dropdown_value2]
        confirmed_df2 = country_df2[country_df2['Case_Type'] == 'Confirmed']
        confirmed_df2['Date'] = pd.to_datetime(confirmed_df2['Date']);
        sorted_df2 = confirmed_df2.sort_values('Date', ascending = True)
        sum_df2 = sorted_df2.groupby('Date').sum()['Difference']
        x2 = sum_df2.index
        z = sum_df2

        return {
            'data':([
                {'x':x, 'y':y, 'type':'line', 'name':country_dropdown_value},
                {'x':x2, 'y':z, 'type':'line', 'name':country_dropdown_value2}
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

        country_df2 = df[df['Country_Region'] == country_dropdown_value2]
        confirmed_df2 = country_df2[country_df2['Case_Type'] == 'Confirmed']
        confirmed_df2['Date'] = pd.to_datetime(confirmed_df2['Date']);
        sorted_df2 = confirmed_df2.sort_values('Date', ascending = True)
        sum_df2 = sorted_df2.groupby('Date').sum()['Cases']
        x2 = sum_df2.index
        z = sum_df2

        return {
            'data':([
                {'x': x, 'y': y, 'type':'line', 'name':country_dropdown_value},
                {'x': x2, 'y': z, 'type':'line', 'name':country_dropdown_value2}
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

        country_df2 = df[df['Country_Region'] == country_dropdown_value2]
        confirmed_df2 = country_df2[country_df2['Case_Type'] == 'Deaths']
        confirmed_df2['Date'] = pd.to_datetime(confirmed_df2['Date']);
        sorted_df2 = confirmed_df2.sort_values('Date', ascending = True)
        sum_df2 = sorted_df2.groupby('Date').sum()['Difference']
        x2 = sum_df2.index
        z = sum_df2


        return {
            'data':([
                {'x': x, 'y': y, 'type':'line', 'name':country_dropdown_value},
                {'x': x2, 'y': z, 'type':'line', 'name':country_dropdown_value2}
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

        country_df2 = df[df['Country_Region'] == country_dropdown_value2]
        confirmed_df2 = country_df2[country_df2['Case_Type'] == 'Deaths']
        confirmed_df2['Date'] = pd.to_datetime(confirmed_df2['Date']);
        sorted_df2 = confirmed_df2.sort_values('Date', ascending = True)
        sum_df2 = sorted_df2.groupby('Date').sum()['Cases']
        x2 = sum_df2.index
        z = sum_df2


        return {
            'data':([
                {'x': x, 'y': y, 'type':'line', 'color': 'r', 'name':country_dropdown_value},
                {'x': x2, 'y': z, 'type':'line', 'name':country_dropdown_value2}
            ]),
        }


#### World graph

@app.callback(
    Output('world_graph', 'figure'),
    [Input('metric_dropdown', 'value')]
)


####
def the_world_graph(metric_dropdown_value):
    grouped_df = df[df['Case_Type'] == 'Confirmed']
    grouped_df = grouped_df.groupby('Date').sum()[['Difference','Cases']]
    grouped_df.index = pd.to_datetime(grouped_df.index)
    grouped_df.sort_index(inplace = True)

    if metric_dropdown_value == 'Daily Cases':
        grouped_df = df[df['Case_Type'] == 'Confirmed']
        grouped_df = grouped_df.groupby('Date').sum()[['Difference','Cases']]
        grouped_df.index = pd.to_datetime(grouped_df.index)
        grouped_df.sort_index(inplace = True)
        x = grouped_df.index
        y = grouped_df['Difference']

        return {
            'data':([
                {
                    'x': x, 'y': y, 'type':'line'
                }
            ])
        }
    ### Cumulative Cases
    elif metric_dropdown_value == 'Cumulative Cases':
        grouped_df = df[df['Case_Type'] == 'Confirmed']
        grouped_df = grouped_df.groupby('Date').sum()[['Difference','Cases']]
        grouped_df.index = pd.to_datetime(grouped_df.index)
        grouped_df.sort_index(inplace = True)
        x = grouped_df.index
        y = grouped_df['Cases']

        return {
            'data':([
                {
                    'x': x, 'y': y, 'type':'line'
                }
            ])
        }
    ### Daily Deaths
    elif metric_dropdown_value == 'Daily Deaths':
        grouped_df = df[df['Case_Type'] == 'Deaths']
        grouped_df = grouped_df.groupby('Date').sum()[['Difference','Cases']]
        grouped_df.index = pd.to_datetime(grouped_df.index)
        grouped_df.sort_index(inplace = True)
        x = grouped_df.index
        y = grouped_df['Difference']

        return {
            'data':([
                {
                    'x': x, 'y': y, 'type':'line'
                }
            ])
        }
    ### Daily Deaths
    elif metric_dropdown_value == 'Cumulative Deaths':
        grouped_df = df[df['Case_Type'] == 'Deaths']
        grouped_df = grouped_df.groupby('Date').sum()[['Difference','Cases']]
        grouped_df.index = pd.to_datetime(grouped_df.index)
        grouped_df.sort_index(inplace = True)
        x = grouped_df.index
        y = grouped_df['Cases']

        return {
            'data':([
                {
                    'x': x, 'y': y, 'type':'line'
                }
            ])
        }




if __name__ == '__main__':
    app.run_server(debug = True)

####
