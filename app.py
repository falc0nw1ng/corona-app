import os
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import Flask

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
df.Date = pd.to_datetime(df.Date)
country_list = df['Country_Region'].unique()

metrics_list = ['Daily Cases', 'Daily Deaths', 'Cumulative Cases', 'Cumulative Deaths']

#### this is the OWID data set which contains some testing data as well
OWID_df = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv")
OWID_df[['total_cases', 'new_cases',
       'total_deaths', 'new_deaths', 'total_cases_per_million',
       'new_cases_per_million', 'total_deaths_per_million',
       'new_deaths_per_million', 'total_tests', 'new_tests',
       'total_tests_per_thousand', 'new_tests_per_thousand', 'tests_units']] = OWID_df[['total_cases', 'new_cases',
       'total_deaths', 'new_deaths', 'total_cases_per_million',
       'new_cases_per_million', 'total_deaths_per_million',
       'new_deaths_per_million', 'total_tests', 'new_tests',
       'total_tests_per_thousand', 'new_tests_per_thousand', 'tests_units']].fillna(0)

have_test_data = OWID_df[OWID_df['total_tests_per_thousand']>0]
second_country_list = have_test_data.sort_values(by = 'location')


### loads the data for the data boxes
confirmed_cases = df[df['Case_Type'] == "Confirmed"]
total_cases = confirmed_cases.Difference.sum()

death_cases = df[df['Case_Type'] =='Deaths']
total_deaths = death_cases.Difference.sum()

### daily deaths and cases
canada_df = df[df['Country_Region'] == 'Canada']
most_recent_date = canada_df.Date.max()

recent_df = df[df['Date'] == most_recent_date]
recent_cases = recent_df[recent_df['Case_Type'] == 'Confirmed']
recent_deaths = recent_df[recent_df['Case_Type'] == 'Deaths']

daily_global_cases = recent_cases.Difference.sum()
daily_global_deaths = recent_deaths.Difference.sum()


#### generate map ####
confirmed_df = confirmed_cases[['Difference','Lat', 'Long']]
coord = confirmed_df.groupby(['Lat', 'Long']).sum()
coord = coord.sort_values(by = 'Difference', ascending = False)

limits = [(0,5), (6,100), (101, 1000)]
colors = ["crimson", "royalblue","lightseagreen"]
scale = 200

fig = go.Figure()


########################################################################################################################################
################## DASH PORTION ########################################################################################################
########################################################################################################################################

tab_style = {
    'border-top': '1px solid white',
    'border-bottom': '1px solid white',
    'border-right': '1px solid white',
    'border-left': '1px solid white',
    'padding': '6px',
    'font-size': '20px',
    'font-family':'bold',
    'margin':'auto',
    'border':'1px solid white',
    'backgroundColor':'#333333',
    'color':'white'
}

tab_selected_style = {
    'borderTop': '1px solid white',
    'borderBottom': '1px solid white',
    'border':'1px solid white',
    'backgroundColor': '#cf082f',
    'color': 'white',
    'padding': '6px',
    'font-size': '20px',
    'font-family':'bold',
    'margin': 'auto'
}

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
server = app.server #uncomment this for deployment



app.layout = html.Div([
    html.Div(
        children = [
            html.H1('Just Another Coronavirus Dashboard',
                style = {'font-family':'Helvetica narrow, sans-serif', 'fontWeight':'lighter', 'color':'white', 'margin':'auto', 'padding-top':'5px', 'padding-left':'5px'})
        ]),
    dcc.Tabs(id = 'tabs', value = 'country',
        children = [
            dcc.Tab(label = 'By Country', value = 'country', style = tab_style, selected_style = tab_selected_style),
            dcc.Tab(label = 'Around the World', value = 'global', style = tab_style, selected_style = tab_selected_style),
        #    dcc.Tab(label = 'Leading Statistics', value = 'leading', style = tab_style, selected_style = tab_selected_style)
        ],style = {'height': '50px'}),
    html.Div(id = 'render_page')
],style = {'width':'80%', 'margin':'auto', 'backgroundColor':'#333333', 'height':'100%'}
)

global_layout = html.Div([
    html.Div([
        html.Div([
            html.P('Daily Cases:'),
            html.P(daily_global_cases)
        ], style = {'textAlign':'center', 'box-shadow': '2px 2px 2px lightgray', 'font-size':'25px', 'width':'25%', 'float':'left'}
        ),
        html.Div([
            html.P('Daily Deaths'),
            html.P(daily_global_deaths)
        ],style = {'textAlign':'center','box-shadow': '2px 2px 2px lightgray', 'font-size':'25px', 'width':'25%', 'float':'left'}
        ),
        html.Div([
            html.P('Total Cases:'),
            html.P(total_cases)
        ], style = {'textAlign':'center', 'box-shadow': '2px 2px 2px lightgray', 'font-size':'25px', 'width':'25%', 'float':'left'}
        ),
        html.Div([
            html.P('Total Deaths:'),
            html.P(total_deaths),
        ], style = {'textAlign':'center','box-shadow': '2px 2px 2px lightgray', 'font-size':'25px', 'width':'25%', 'float':'left', 'padding-top':'none'}
        ),
    ],style = {'vertical-align':'top', 'width':'100%', 'color':'white', 'backgroundColor':'#333333'}
        ),
    html.Div([
        dcc.Graph(figure = fig, style = {'height':800})
        ], style = {'width':'100%', 'float':'left' }
        ),
    html.Div([
        html.P('Select a metric',
        style = {'color':'white', 'font-size':'20px'}
        ),
        dcc.Dropdown(
            id = 'metric_dropdown',
            options = [{'label':i, 'value':i} for i in metrics_list],
            value = 'Daily Cases',
            style = {'width':'35%'}
        ),
        dcc.RadioItems(
            id = 'log_radio',
            options = [{'label':i, 'value':i} for i in ['Linear', 'Log']],
            value = 'Linear',
            style = {'color':'white'}
        ),
        ], style = {'width':'95%','margin':'auto'}),
    html.Div([
        dcc.Graph(id = 'world_graph')
        ],
        style = {'width':'100%'}
        ),
    ],style = {'backgroundColor':'#333333'})

####### country Layout
country_layout = html.Div([
    html.Div([
        html.Div(id = 'daily_country_cases', style = { 'width': '12%', 'textAlign':'center',
         'box-shadow': '2px 2px 2px lightgray', 'display':'table-cell'}),
        html.Div(id = 'daily_country_deaths', style = {'width': '12%', 'textAlign':'center',
         'box-shadow': '2px 2px 2px lightgray', 'display':'table-cell'}),
        html.Div(id = 'total_country_cases', style = {'width': '12%', 'textAlign':'center',
         'box-shadow': '2px 2px 2px lightgray', 'display':'table-cell'}),
        html.Div(id = 'total_country_deaths', style = {'width': '12%','textAlign':'center',
         'box-shadow': '2px 2px 2px lightgray', 'display':'table-cell'})
    ],style = {'vertical-align':'top', 'width':'100%', 'color':'white', 'backgroundColor':'#333333'}
    ),
    html.Div([
        html.Div([
            html.P('Select a country and the displayed data you want here:',
            style = {'font-size':'25px', 'color':'white', 'width':'95%', 'margin':'auto'}
            ),
            html.Br(),
            html.Div([
                    dcc.Dropdown(
                        id = 'country_dropdown',
                        options =  [{'label':i, 'value':i} for i in country_list],
                        value = "Canada",
                        style = {'width':'35%'}
                    ),
                    dcc.Dropdown(
                        id = 'metric_dropdown',
                        options = [{'label':i, 'value':i} for i in metrics_list],
                        value = 'Daily Cases',
                        style = {'width':'35%', 'padding-left':'10%'}
                    ),
            ],style = {'display':'flex', 'font-size':'20px', 'width':'95%', 'margin':'auto'}
            ),
            dcc.RadioItems(
                id = 'log_radio',
                options = [{'label':i, 'value':i} for i in ['Linear', 'Log']],
                value = 'Linear',
                style = {'color':'white', 'width':'95%', 'margin':'auto'}
                ),
        ], style = {'width':'100%', 'display':'inline-block', 'margin':'auto'}
        ),

        html.Div([
            dcc.Graph(id = 'virus_graph',)
        ], style = {'display':'inline-block', 'width':'100%'}
        ),
    ],
    ),
    html.Div([
        dcc.Graph(id = 'pie_graph_country',
            style = {'width':'75%'}
            ),
        html.Div(id = 'death_info',
            style = {
                'color':'white', 'font-size':'18px', 'textAlign':'center', 'width':'20%', 'margin':'auto'}
                )
    ], style = {'display':'flex', 'width':'80%'}
    ),

    html.Div([
        html.H2('What is the scaled case?',
            style = {'fontWeight':'bold', 'font-size':'35px', 'color':'white', 'textAlign':'center'}),
        html.P('The scaled case is a simple metric to tell you how a country is doing against the spread of the virus. It acomplishes this by scaling cases by the number of tests. Often times when the media is announcing new cases or deaths, it does not take into account the testing done. By scaling the cases with the number of tests, we can get a more accurate portrayal of how much the virus has spread in each country relative to each other. The same rule applies here as for most other Coronavirus graphs, bigger number = bad!', style = {'color':'white', 'font-size':'25px'})
    ], style = {'color':'white', 'width':'95%', 'margin':'auto'}),
    html.Div([
        dcc.Dropdown(
            id = 'scaled_dropdown',
            options = [{'label':i, 'value':i} for i in second_country_list['location'].unique()],
            value = 'Canada',
            style = {'width':'35%'}
        ),
        dcc.Dropdown(
            id = 'scaled_dropdown2',
            options = [{'label':i, 'value':i} for i in second_country_list['location'].unique()],
            value = 'United States',
            style = {'width':'35%', 'padding-left':'10%'}
        ),
    ],style = {'display':'flex', 'width':'95%', 'margin':'auto'}),
    html.Div([
        dcc.Graph(id = 'scaled_cases'),
    ]),
    html.Div([
        html.P(['Data source from Johns Hopkins and OWID. Further details about the data source and information about me can be found ',
            html.A('here',href = 'https://therealmaplejordan.com/', style = {'color':'orange'})],
                style = {'color':'white'}),
], style = {'vertical-align':'top', 'backgroundColor':'#333333'}
)
], style = {'vertical-align':'top', 'backgroundColor':'#333333'})



##### update case and deaths for country
#### this is the four boxes at the top of the country tab

## daily cases
@app.callback(
    Output('daily_country_cases', 'children'),
    [Input('country_dropdown', 'value')]
)

def daily_country_cases_update(country_dropdown_value):
    country_df = df[df['Country_Region']==country_dropdown_value]
    confirmed_df = country_df[country_df['Case_Type'] == 'Confirmed']
#    confirmed_df.Date = pd.to_datetime(confirmed_df.Date)
    grouped_df = confirmed_df.groupby('Date').sum()[['Cases','Difference']]
    sorted_df = grouped_df.sort_values(by = 'Date', ascending = False).Difference
    daily_cases = sorted_df.iloc[0]
    return [
        html.Div([
            html.P('Daily cases in {}:' .format(country_dropdown_value),
                style = {'font-size':'25px'}
                ),
            html.P(daily_cases,
                style = {'font-size':'25px'}
                )
        ])
    ]

@app.callback(
    Output('daily_country_deaths', 'children'),
    [Input('country_dropdown', 'value')]
)

### Daily deaths
def daily_country_cases_update(country_dropdown_value):
    country_df = df[df['Country_Region']==country_dropdown_value]
    confirmed_df = country_df[country_df['Case_Type'] == 'Deaths']
#    confirmed_df.Date = pd.to_datetime(confirmed_df.Date)
    grouped_df = confirmed_df.groupby('Date').sum()[['Cases','Difference']]
    sorted_df = grouped_df.sort_values(by = 'Date', ascending = False).Difference
    daily_deaths = sorted_df.iloc[0]
    return [
        html.Div([
            html.P('Daily deaths in {}:' .format(country_dropdown_value),
                style = {'font-size':'25px'}
                ),
            html.P(daily_deaths,
                style = {'font-size':'25px'}
                )
        ])
    ]

@app.callback(
    Output('total_country_cases', 'children'),
    [Input('country_dropdown', 'value')]
)

def total_country_cases_update(country_dropdown_value):
    country_df = df[df['Country_Region'] == country_dropdown_value]
    confirmed_df = country_df[country_df['Case_Type']=='Confirmed']
    return [
        html.Div([
            html.P('Total cases in \n{}:' .format(country_dropdown_value),
                style = {'font-size':'25px'}
                ),
            html.P(confirmed_df.Difference.sum(),
                style = {'font-size':'25px'}
                )
        ])
    ]

@app.callback(
    Output('total_country_deaths', 'children'),
    [Input('country_dropdown', 'value')]
)

def total_country_deaths_update(country_dropdown_value):
    country_df = df[df['Country_Region'] == country_dropdown_value]
    deaths_df = country_df[country_df['Case_Type']=='Deaths']
    return [
        html.Div([
            html.P('Total deaths in {}:' .format(country_dropdown_value),
                style = {'font-size':'25px'}
                ),
            html.P(deaths_df.Difference.sum(),
                style = {'font-size':'25px'}
                )
        ])
    ]

##########################################################################################
########## multi date dropdown graph #####################################################
##########################################################################################

@app.callback(
    Output('virus_graph', 'figure'),
    [Input('country_dropdown', 'value'),
    Input('metric_dropdown', 'value' ),
    Input('log_radio', 'value')]
)


def the_virus_graph(country_dropdown_value, metric_dropdown_value, log_radio_value):
    if metric_dropdown_value == 'Daily Cases':
        country_df = df[df['Country_Region'] == country_dropdown_value]
        confirmed_df = country_df[country_df['Case_Type'] == 'Confirmed']
#        confirmed_df['Date'] = pd.to_datetime(confirmed_df['Date']);
        sorted_df = confirmed_df.sort_values('Date', ascending = True)
        sum_df = sorted_df.groupby('Date').sum()['Difference']
        x = sum_df.index
        y = sum_df
        z = moving_average = sum_df.rolling(5).mean()

        return {
                'data':([
                    {'x':x, 'y':y, 'type':'bar', 'name':'Daily Cases for {}'.format(country_dropdown_value), 'mode':'lines+markers', 'markers':{
                    }, 'marker':{
                            'color':'orange'
                    }},
                    {'x':x, 'y': z, 'type':'line', 'name': 'Moving Average (window = 5 Days)', 'marker':{
                        'color':'red'
                    }}
                ]),
            'layout':{
                'title':{
                    'text': "Daily Cases in {} vs Date".format(country_dropdown_value)
                },
                'yaxis':{
                    'title':{
                        'text':metric_dropdown_value
                    },
                    'type':'linear' if log_radio_value == 'Linear' else 'log',
                    'gridcolor':'#b3b3b3'
                },
                'xaxis':{
                    'title':{
                        'text': 'Date'
                    }},
                'plot_bgcolor':'#333333',
                'paper_bgcolor':'#333333',
                'font':{
                    'color':'white'
                },
                }
            }


    ### Cumulative Cases
    elif metric_dropdown_value == 'Cumulative Cases':
        country_df = df[df['Country_Region'] == country_dropdown_value]
        confirmed_df = country_df[country_df['Case_Type'] == 'Confirmed']
    #    confirmed_df['Date'] = pd.to_datetime(confirmed_df['Date']);
        sorted_df = confirmed_df.sort_values('Date', ascending = True)
        sum_df = sorted_df.groupby('Date').sum()['Cases']
        x = sum_df.index
        y = sum_df

        z = moving_average = sum_df.rolling(5).mean()

        return {
                'data':([
                    {'x':x, 'y':y, 'type':'bar', 'name':'Cumulative Cases for {}' .format(country_dropdown_value), 'mode':'lines+markers','markers':{
                    }, 'marker':{
                            'color':'orange'
                    }},
                    {'x':x, 'y': z, 'type':'line', 'name': 'Moving Average (window = 5 Days)', 'marker':{
                        'color':'red'
                    }}

                ]),
            'layout':{
                'title':{
                    'text': "Daily Cases in {} vs Date".format(country_dropdown_value)
                },
                'yaxis':{
                    'title':{
                        'text':metric_dropdown_value
                    },
                    'type':'linear' if log_radio_value == 'Linear' else 'log',
                    'gridcolor':'#b3b3b3'
                },
                'xaxis':{
                    'title':{
                        'text': 'Date'
                    }},
                'plot_bgcolor':'#333333',
                'paper_bgcolor':'#333333',
                'font':{
                    'color':'white'
                },
                }
        }
    ### Daily Deaths
    elif metric_dropdown_value == 'Daily Deaths':
        country_df = df[df['Country_Region'] == country_dropdown_value]
        confirmed_df = country_df[country_df['Case_Type'] == 'Deaths']
    #    confirmed_df['Date'] = pd.to_datetime(confirmed_df['Date']);
        sorted_df = confirmed_df.sort_values('Date', ascending = True)
        sum_df = sorted_df.groupby('Date').sum()['Difference']
        x = sum_df.index
        y = sum_df

        z = moving_average = sum_df.rolling(5).mean()

        return {
                'data':([
                    {'x':x, 'y':y, 'type':'bar', 'name':'Daily Deaths for {}' .format(country_dropdown_value), 'mode':'lines+markers','markers':{
                    }, 'marker':{
                            'color':'orange'
                    }},
                    {'x':x, 'y': z, 'type':'line', 'name': 'Moving Average (window = 5 Days)', 'marker':{
                        'color':'red'
                    }}

                ]),
            'layout':{
                'title':{
                    'text': "Daily Cases in {} vs Date".format(country_dropdown_value)
                },
                'yaxis':{
                    'title':{
                        'text':metric_dropdown_value
                    },
                    'type':'linear' if log_radio_value == 'Linear' else 'log',
                    'gridcolor':'#b3b3b3'
                },
                'xaxis':{
                    'title':{
                        'text': 'Date'
                    }},
                'plot_bgcolor':'#333333',
                'paper_bgcolor':'#333333',
                'font':{
                    'color':'white'
                },
                }
        }
    ### Daily Deaths
    elif metric_dropdown_value == 'Cumulative Deaths':
        country_df = df[df['Country_Region'] == country_dropdown_value]
        confirmed_df = country_df[country_df['Case_Type'] == 'Deaths']
#        confirmed_df['Date'] = pd.to_datetime(confirmed_df['Date']);
        sorted_df = confirmed_df.sort_values('Date', ascending = True)
        sum_df = sorted_df.groupby('Date').sum()['Cases']
        x = sum_df.index
        y = sum_df

        z = moving_average = sum_df.rolling(5).mean()

        return {
                'data':([
                    {'x':x, 'y':y, 'type':'bar', 'name':'Cumulative Deaths for {}' .format(country_dropdown_value), 'mode':'lines+markers','markers':{
                    }, 'marker':{
                            'color':'orange'
                    }},
                    {'x':x, 'y': z, 'type':'line', 'name': 'Moving Average (window = 5 Days)', 'marker':{
                        'color':'red'
                    }}
                ]),
            'layout':{
                'title':{
                    'text': "Daily Cases in {} vs Date".format(country_dropdown_value)
                },
                'yaxis':{
                    'title':{
                        'text':metric_dropdown_value
                    },
                    'type':'linear' if log_radio_value == 'Linear' else 'log',
                    'gridcolor':'#b3b3b3'
                },
                'xaxis':{
                    'title':{
                        'text': 'Date'
                    }},
                'plot_bgcolor':'#333333',
                'paper_bgcolor':'#333333',
                'font':{
                    'color':'white'
                },
                }
        }


############################################################################################################################################
############################ Pie Graph + death_info ###########################################################################################
############################################################################################################################################

### up
@app.callback(
    Output('death_info', 'children'),
    [Input('country_dropdown', 'value')]
)

def the_death_info(country_dropdown_value):
    #global death rate
    global_death = df[df['Case_Type'] == 'Deaths']
    global_cases = df[df['Case_Type'] == 'Confirmed']
    global_death_rate = global_death.Difference.sum()/global_cases.Difference.sum()

    country_df = df[df['Country_Region'] == country_dropdown_value]
    confirmed_df = country_df[country_df['Case_Type'] == 'Confirmed']
    death_df = country_df[country_df['Case_Type'] == 'Deaths']
    confirmed = confirmed_df.Difference.sum()
    deaths = death_df.Difference.sum()
    country_death_rate = deaths/confirmed

    if global_death_rate < country_death_rate:
        return [
            html.Div([
                html.P('The country of {} is doing worst than the global average death rate of {:.3f}%.' .format(country_dropdown_value, global_death_rate*100))
            ])
        ]
    elif global_death_rate > country_death_rate:
        return [
            html.Div([
                html.P('The country of {} is doing better than the global average death rate of {:.3f}%.' .format(country_dropdown_value, global_death_rate*100))
            ])
        ]
    elif global_death_rate == country_death_rate:
        return [
            html.Div([
                html.P('{} is doing exactly(?!?!?!) the global average death rate of {:.3f}%.' .format(country_dropdown_value, global_death_rate*100))
            ])
        ]
    else:
        return [
            html.Div([
                html.P('Select a country please.')
            ])
    ]


###outputs the deathrate of selected country as a piechart
@app.callback(
    Output('pie_graph_country', 'figure'),
    [Input('country_dropdown', 'value')],
)

## death rates
def the_pie_graph(country_dropdown_value):
    country_df = df[df['Country_Region'] == country_dropdown_value]
    confirmed_df = country_df[country_df['Case_Type'] == 'Confirmed']
    death_df = country_df[country_df['Case_Type'] == 'Deaths']
    confirmed = confirmed_df.Difference.sum()
    deaths = death_df.Difference.sum()

    return{
        'data':([
            {
                'values':[confirmed, deaths] , 'type':'pie', 'labels':['Confirmed', 'Deaths'], 'marker' : {
                    'colors':['lightgreen','red'],
                    'line':{
                        'color':'black',
                        'width':'2'
            }}}
        ]),
        'layout':{
            'title':{
                'text':'Death rate in {}' .format(country_dropdown_value)
        },
        'paper_bgcolor':'#333333',
        'font':{
            'color':'white'
        }
        }}



#####################################################################################################################################
####################### Scaled Cases ################################################################################################
#####################################################################################################################################

@app.callback(
    Output('scaled_cases', 'figure'),
    [Input('scaled_dropdown', 'value'),
    Input('scaled_dropdown2', 'value')]
)

def the_scaled_cases(scaled_dropdown_value, scaled_dropdown_value2):
    country_df = OWID_df[OWID_df['location']== scaled_dropdown_value]
    country_df['Scaled Cases'] = country_df['total_cases']/country_df['total_tests']

    country_df2 = OWID_df[OWID_df['location']== scaled_dropdown_value2]
    country_df2['Scaled Cases'] = country_df2['total_cases']/country_df2['total_tests']

    return {
        'data':([
            {'x':country_df.date, 'y':country_df['Scaled Cases'], 'type':'line', 'name':scaled_dropdown_value},
            {'x':country_df2.date, 'y':country_df2['Scaled Cases'], 'type':'line', 'name':scaled_dropdown_value2}
        ]),
        'layout':{
            'yaxis':{
                'title':'Scaled Cases',
                'gridcolor':'#b3b3b3'
            },
            'xaxis':{
                'title':'Date'
            },
            'font':{
                'color':'white'
            },
            'plot_bgcolor':'#333333',
            'paper_bgcolor':'#333333',
            'title': ('Scaled Cases for this {} vs {}' .format(scaled_dropdown_value, scaled_dropdown_value2))
        }
    }


#####################################################################################################################################
####################### WORLD PAGE ##################################################################################################
#####################################################################################################################################

####

@app.callback(
    Output('world_graph', 'figure'),
    [Input('metric_dropdown', 'value'),
    Input('log_radio', 'value')]
)

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
                {'x': x, 'y': y, 'type':'bar', 'name': metric_dropdown_value,'marker':{
                    'color':'orange'
                }},
                {'x':x, 'y':y.rolling(window = 5).mean(),'name':'Moving Average (window = 5 Days)', 'type':'line', 'marker':{
                    'color':'red'
                }}
            ]),
            'layout':{
                'title':{
                    'text':'Global Daily Cases vs Date'
                },
                'yaxis':{
                    'type':'linear' if log_radio_value == 'Linear' else 'log',
                    'title':{
                        'text':(metric_dropdown_value)
                    },
                    'gridcolor':'#b3b3b3'
                },
                'xaxis':{
                    'title':{
                        'text':('Date')
                    }
                },
                'plot_bgcolor':'#333333',
                'paper_bgcolor':'#333333',
                'font':{
                    'color':'white'
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
                {'x': x, 'y': y, 'type':'bar', 'name': metric_dropdown_value, 'marker':{
                    'color':'lightgreen'
                }},
                {'x':x, 'y':y.rolling(window = 5).mean(),'name':'Moving Average (window = 5 Days)', 'type':'line', 'marker':{
                    'color':'red'
                }}
            ]),
            'layout':{
                'title':{
                    'text':'Global Cumulative Cases vs Date'
                },
                'yaxis':{
                    'type':'linear' if log_radio_value == 'Linear' else 'log',
                    'title':{
                        'text':(metric_dropdown_value)
                    },
                    'gridcolor':'#b3b3b3'
                },
                'xaxis':{
                    'title':{
                        'text':('Date')
                    }
                },
                'plot_bgcolor':'#333333',
                'paper_bgcolor':'#333333',
                'font':{
                    'color':'white'
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
                {'x': x, 'y': y, 'type':'bar', 'name': metric_dropdown_value, 'marker':{
                    'color':'mediumpurple'
                }},
                {'x':x, 'y':y.rolling(window = 5).mean(),'name':'Moving Average (window = 5 Days)', 'type':'line', 'marker':{
                    'color':'red'
                }}
            ]),
            'layout':{
                'title':{
                    'text':'Global Daily Deaths vs Date'
                },
                'yaxis':{
                    'type':'linear' if log_radio_value == 'Linear' else 'log',
                    'title':{
                        'text':(metric_dropdown_value)
                    },
                    'gridcolor':'#b3b3b3'
                },
                'xaxis':{
                    'title':{
                        'text':('Date')
                    }
                },
                'plot_bgcolor':'#333333',
                'paper_bgcolor':'#333333',
                'font':{
                    'color':'white'
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
                {'x': x, 'y': y, 'type':'bar', 'name': metric_dropdown_value,'mode':'lines+markers', 'marker':{
                    'color':'slategray'
                }},
                {'x':x, 'y':y.rolling(window = 5).mean(),'name':'Moving Average (window = 5 Days)', 'marker':{
                    'color':'red'
                }}
            ]),
            'layout':{
                'title':{
                    'text':'Global Cumulative Deaths vs Date'
                },
                'yaxis':{
                    'type':'linear' if log_radio_value == 'Linear' else 'log',
                    'title':{
                        'text':(metric_dropdown_value)
                    },
                    'gridcolor':'#b3b3b3'
                },
                'xaxis':{
                    'title':{
                        'text':('Date')
                    }
                },
                'plot_bgcolor':'#333333',
                'paper_bgcolor':'#333333',
                'font':{
                    'color':'white'
                }
            }
        }



####################################################################################################################################################
############################ Render tabs ###########################################################################################################
####################################################################################################################################################

@app.callback(
    Output('render_page', 'children'),
    [Input('tabs', 'value')]
)
def display_page(tab_value):
    if tab_value == 'global':
        for i in range(len(limits)):
            lim = limits[i]
            df_sub = coord[lim[0]:lim[1]]
            fig.add_trace(go.Scattergeo(
                locationmode = 'ISO-3',
                lat = df_sub.index.get_level_values(level = 0),
                lon = df_sub.index.get_level_values(level = 1),
                text = df_sub.Difference,
                marker = dict(
                    size = df_sub.Difference/scale,
                    color = colors[i],
                    line_color='rgb(40,40,40)',
                    line_width=1,
                    sizemode = 'area'
                ),
                name = '{0} - {1}'.format(lim[0], lim[1])
                    )),
        fig.update_layout(
            title_text = "Largest 1000 Coronavirus Epicenters Around the World (note: top right handside of graph to reset)",
            title_x = 0.5,
            showlegend = True,
            plot_bgcolor = '#333333',
            paper_bgcolor = '#333333',
            xaxis = dict(fixedrange = True),
            yaxis = dict(fixedrange = True),
            font = dict(
                color = 'white',
            ),
            geo = go.layout.Geo(
                resolution = 50,
                scope = 'world',
                showframe = False,
                showcoastlines = True,
                landcolor = 'rgb(217,217,217)',
                showocean = True,
                oceancolor = '#333333',
                countrycolor = "white" ,
                coastlinecolor = "white",
        ),
        )
        return global_layout
    else:
        return country_layout



if __name__ == '__main__':
    app.run_server(debug = True)












####
