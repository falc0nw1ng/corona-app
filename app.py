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
df.sort_values('Country_Region', inplace = True)
country_list = df['Country_Region'].unique()

metrics_list = ['Daily Cases', 'Cumulative Cases', 'Daily Deaths', 'Cumulative Deaths']

### world total number of cases
confirmed_cases = df[df['Case_Type'] == "Confirmed"]
total_cases = confirmed_cases.Difference.sum()

death_cases = df[df['Case_Type'] =='Deaths']
total_deaths = death_cases.Difference.sum()
print(total_deaths)

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
            html.H1('Just Another Coronavirus Dashboard',
                style = {
                    'font-family':'arial'
                }
            )
        ], style = {

        }
    ),
    html.Div(
        className = 'left-block',
        children = [
                    html.H2('Global Totals'),
                    html.Div(
                        className = 'first-box',
                        children = [
                            html.P('Cases',
                                style = {
                                    'font-size': '20px',
                                }),
                            html.P(total_cases,
                                style = {
                                    'padding-bottom':'7px'
                                })
                    ], style = {
                        'backgroundColor':'white',
                        'box-shadow': '2px 2px lightgray',
                        'border-radius':'5px',
                        'margin':'auto',
                        'width': '70%',
                    }),
                    html.Div(
                        className = 'second-box',
                        children = [
                            html.P('Deaths',
                                style = {
                                    'font-size':'20px'
                                }),
                            html.P(total_deaths,
                                style = {
                                    'padding-bottom':'7px'

                                }),
                    ], style = {
                        'backgroundColor':'white',
                        'box-shadow': '2px 2px lightgray',
                        'border-radius':'5px',
                        'margin':'auto',
                        'width': '70%',

                    }),


        ], style = {'display':'inline-block','width':'28%', 'textAlign':'center'}
    ),
    html.Div(
        className = 'middle-block',
        children = [
            html.H2('Daily Cases', style = {'textAlign':'center'}),
            html.Div([
                html.Div([
                    html.P('Choose the first country here'),
                    dcc.Dropdown(
                        id = 'country_dropdown',
                        options =  [{'label':i, 'value':i} for i in country_list],
                        value = "Canada",
                    )
                ], style={'width': '150px','display':'inline-block'}
                ),

                html.Div([
                    html.P('Choose the second country here'),
                    dcc.Dropdown(
                        id = 'country_dropdown2',
                        options =  [{'label':i, 'value':i} for i in country_list],
                        value = "US",
                    )
                ], style={'width': '150px','display':'inline-block','padding-left':'50px'}
                ),
            ]),
            html.P('Metrics'),
            dcc.Dropdown(
                id = 'metric_dropdown',
                options = [{'label':i, 'value':i} for i in metrics_list],
                value = 'Daily Cases',
                style = {
                    'width':'150px'
                }
            ),
            dcc.RadioItems(
                id = 'log_radio',
                options = [{'label':i, 'value':i} for i in ['Linear', 'Log']],
                value = 'Linear',
                labelStyle = {'display':'inline-block'}
            ),
            html.Div(
                className = 'graph1-options',
                children = [
                    html.P('Country Comparison',
                        style = {
                            'textAlign':'center',
                            'font-size':'25px'
                        }),
                    dcc.Graph(
                        id = 'virus_graph',
                    ),
            ],
                style = {
                    'width':'45%',
                    'float':'left'
                }
            ),
            html.Div(
                className = 'graph2-options',
                children = [
                    html.P('Global Behavour',
                        style = {
                            'textAlign':'center',
                            'font-size':'25px',
                            'padding-left':'30px'
                        }),
                    dcc.Graph(
                        id = 'world_graph',
                    )
                ],
                style = {
                    'width':'45%',
                    'float':'left'
                }
            )
    ], style = {
        'width':'68%', 'display':'inline-block', 'padding-left':'10px', 'vertical-align':'top'
    })

], style = {
    'backgroundColor':'#f7f9f9'
})




#### Country graph

@app.callback(
    Output('virus_graph', 'figure'),
    [Input('country_dropdown', 'value'),
    Input('country_dropdown2', 'value'),
    Input('metric_dropdown', 'value' ),
    Input('log_radio', 'value')]
)

def the_virus_graph(country_dropdown_value, country_dropdown_value2, metric_dropdown_value, log_radio_value):
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
            ]),
            'layout':{
                'title':{
                    'text': "Daily Cases in {} and {} vs Date".format(country_dropdown_value , country_dropdown_value2)
                },
                'yaxis':{
                    'type':'linear' if log_radio_value == 'Linear' else 'log'
                }
            }
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
            ]),
            'layout':{
                'title':{
                    'text': "Cumulative Cases in {} and {} vs Date".format(country_dropdown_value , country_dropdown_value2)
                },
                'yaxis':{
                    'type':'linear' if log_radio_value == 'Linear' else 'log'
                }
            }
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
            ]),
            'layout':{
                'title':{
                    'text': "Daily Deaths in {} and {} vs Date".format(country_dropdown_value , country_dropdown_value2)
                },
                'yaxis':{
                    'type':'linear' if log_radio_value == 'Linear' else 'log'
                }
            }
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
            'layout':{
                'title':{
                    'text': "Cumulative Deaths in {} and {} vs Date".format(country_dropdown_value , country_dropdown_value2)
                },
                'yaxis':{
                    'type':'linear' if log_radio_value == 'Linear' else 'log'
                }
            }
        }


#### World graph

@app.callback(
    Output('world_graph', 'figure'),
    [Input('metric_dropdown', 'value'),
    Input('log_radio', 'value')]
)


####
def the_world_graph(metric_dropdown_value, log_radio_value):
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
                    'x': x, 'y': y, 'type':'line','marker':{'color':'red'}
                }
            ]),
            'layout':{
                'title':{
                    'text':'Global Daily Cases vs Date'
                },
                'yaxis':{
                    'type':'linear' if log_radio_value == 'Linear' else 'log'
                }
            }

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
                    'x': x, 'y': y, 'type':'line','marker':{'color':'red'}
                }
            ]),
            'layout':{
                'title':{
                    'text':'Global Cumulative Cases vs Date'
                },
                'yaxis':{
                    'type':'linear' if log_radio_value == 'Linear' else 'log'
                }
            }
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
                    'x': x, 'y': y, 'type':'line','marker':{'color':'red'}
                }
            ]),
            'layout':{
                'title':{
                    'text':'Global Daily Deaths vs Date'
                },
                'yaxis':{
                    'type':'linear' if log_radio_value == 'Linear' else 'log'
                }
            }
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
                    'x': x, 'y': y, 'type':'line','marker':{'color':'red'}
                }
            ]),
            'layout':{
                'title':{
                    'text':'Global Cumulative Deaths vs Date'
                },
                'yaxis':{
                    'type':'linear' if log_radio_value == 'Linear' else 'log'
                }
            }
        }




if __name__ == '__main__':
    app.run_server(debug = True)

####
