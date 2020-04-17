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

metrics_list = ['Daily Cases', 'Daily Deaths', 'Cumulative Cases', 'Cumulative Deaths']

### world total number of cases
confirmed_cases = df[df['Case_Type'] == "Confirmed"]
total_cases = confirmed_cases.Difference.sum()

death_cases = df[df['Case_Type'] =='Deaths']
total_deaths = death_cases.Difference.sum()

##maybe do this part as a callback to prevent too much loading later


########################################################################################################################################
################## DASH PORTION ########################################################################################################
########################################################################################################################################



tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'font-size': '20px',
    'font-family':'bold',
    'margin':'auto'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
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
                style = {'font-family':'Helvetica narrow, sans-serif', 'fontWeight':'lighter'})
        ]),
    dcc.Tabs(id = 'tabs', value = 'country' ,
        children = [
            dcc.Tab(label = 'Global', value = 'global', style = tab_style, selected_style = tab_selected_style),
            dcc.Tab(label = 'By Country', value = 'country', style = tab_style, selected_style = tab_selected_style),
        #    dcc.Tab(label = 'Leading Statistics', value = 'leading', style = tab_style, selected_style = tab_selected_style)
        ],style = {'height':'60px'}),
    html.Div(id = 'render_page')
],# style = {'backgroundColor':'#f7f9f9'}
)

global_layout = html.Div(
        children = [
            html.Div(
                children = [
                    html.Div(
                        children  = [
                            html.P('Metrics'),
                            dcc.Dropdown(
                                id = 'metric_dropdown',
                                options = [{'label':i, 'value':i} for i in metrics_list],
                                value = 'Daily Cases',
                                style = {'width':'150px'}
                            ),
                            dcc.RadioItems(
                                id = 'log_radio',
                                options = [{'label':i, 'value':i} for i in ['Linear', 'Log']],
                                value = 'Linear',
                                labelStyle = {'display':'inline-block'}
                            ),
                        ], style = {'display':'inline-block', 'float':'left', 'padding-left':'50px', 'width':'13%'}
                        ),
### add daily cases here if needed?
                    html.Div(
                        children = [
                            html.P('Cases:', style = {'font-size':'25px'}),
                            html.P(total_cases, style = {'font-size': '25px'})
                    ], style = {'display':'inline', 'float':'left', 'width': '15%', 'textAlign':'center',
                        'backgroundColor':'white', 'box-shadow': '2px 2px 2px lightgray', 'border-radius':'5px', 'margin':'0 5px 5px 5px',
                            'border-color':'lightgreen', 'border-style': 'solid' }
                    ),
                    html.Div(
                        children = [
                            html.P('Deaths:', style = {'font-size':'25px'}),
                            html.P(total_deaths, style = {'font-size': '25px'}
                                    ),
                    ], style = {'display':'inline', 'float':'left', 'width': '15%', 'textAlign':'center',
                        'backgroundColor':'white', 'box-shadow': '2px 2px 2px lightgray', 'border-radius':'5px',
                            'border-color':'crimson', 'border-style': 'solid'}
                                ),
                ],style = { 'float':'left', 'width':'100%', 'margin':'auto'}
            ),
            html.Div(
                children = [
                    dcc.Graph(id = 'world_graph',)
                ],
                style = {'width':'100%','float':'left'}
                )
        ],style = {'backgroundColor':'#f7f9f9'})

####### country Layout

country_layout = html.Div(
    children = [
        html.Div([
            html.Div([
                html.P('Pick a country here!'),
                dcc.Dropdown(
                    id = 'country_dropdown',
                    options =  [{'label':i, 'value':i} for i in country_list],
                    value = "Canada",
                    style = {'width':'80%'}
                )
            ], style = {'display':'inline', 'float':'left', 'padding-left':'10px', 'width':'9%'}
            ),
            html.Div([
                html.P('Metrics'),
                dcc.Dropdown(
                    id = 'metric_dropdown',
                    options = [{'label':i, 'value':i} for i in metrics_list],
                    value = 'Daily Cases',
                    style = {'width':'80%'}
                ),
                dcc.RadioItems(
                    id = 'log_radio',
                    options = [{'label':i, 'value':i} for i in ['Linear', 'Log']],
                    value = 'Linear',
                    labelStyle = {'display':'inline',}
                    ),
            ], style = {'display':'inline-block', 'float':'left', 'width':'9%'}),
            html.Div([
                html.Div(id = 'daily_country_cases', style = {'display':'inline', 'float':'left', 'width': '15%', 'textAlign':'center',
                    'backgroundColor':'white', 'box-shadow': '2px 2px 2px lightgray', 'border-radius':'5px', 'margin':'0 5px 5px 5px',
                    'border-color':'lightgreen', 'border-style': 'solid'}),
                html.Div(id = 'daily_country_deaths', style = {'display':'inline', 'float':'left', 'width': '15%', 'textAlign':'center',
                    'backgroundColor':'white', 'box-shadow': '2px 2px 2px lightgray', 'border-radius':'5px', 'margin':'0 5px 5px 5px',
                    'border-color':'lightblue', 'border-style': 'solid'}),
                html.Div(id = 'total_country_cases', style = {'display':'inline', 'float':'left', 'width': '15%', 'textAlign':'center',
                    'backgroundColor':'white', 'box-shadow': '2px 2px 2px lightgray', 'border-radius':'5px', 'margin':'0 5px 5px 5px',
                    'border-color':'lightorange', 'border-style': 'solid'}),
                html.Div(id = 'total_country_deaths', style = {'display':'inline', 'float':'left', 'width': '15%', 'textAlign':'center',
                    'backgroundColor':'white', 'box-shadow': '2px 2px 2px lightgray', 'border-radius':'5px', 'margin':'0 5px 5px 5px',
                    'border-color':'crimson', 'border-style': 'solid'})
            ],style = {'display':'inline', 'width': '90%', 'vertical-align':'top', 'padding-left':'10%'}),
        ],style = {'vertical-align':'top', 'width':'100%'}
        ),
        html.Div(
            children = [
                html.Div([
                    dcc.Graph(id = 'virus_graph',)
                ], style = {'display':'inline-block', 'width':'60%'}),
                html.Div([
                    dcc.Graph(id = 'pie_graph')
                ], style = {'display':'inline-block', 'width':'25%', 'padding-right':'10px'})

        ],
            style = {
             'display':'inline-block', 'width':'100%'}
        ),
###'''    html.Div([
###        dcc.Graph(id = 'pie_graph')
###    ], style = {'float':'left', 'wdith': '25%','display':'inline'}
###    )'''

], style = {'vertical-align':'top'}
)

####### Leading Layout
'''
leading_layout = html.Div(
    children = [
    ]
)
'''

##### update case and deaths for country
## daily cases
@app.callback(
    Output('daily_country_cases', 'children'),
    [Input('country_dropdown', 'value')]
)

def daily_country_cases_update(country_dropdown_value):
    country_df = df[df['Country_Region']==country_dropdown_value]
    confirmed_df = country_df[country_df['Case_Type'] == 'Confirmed']
    confirmed_df.Date = pd.to_datetime(confirmed_df.Date)
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
    confirmed_df.Date = pd.to_datetime(confirmed_df.Date)
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
            html.P('Total cases in {}:' .format(country_dropdown_value),
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


############################################################################################################################################
############################ Pie Graph #####################################################################################################
############################################################################################################################################

@app.callback(
    Output('pie_graph', 'figure'),
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
        }}}

#### Country graph
@app.callback(
    Output('virus_graph', 'figure'),
    [Input('country_dropdown', 'value'),
    Input('metric_dropdown', 'value' ),
    Input('log_radio', 'value')]
)

def the_virus_graph(country_dropdown_value, metric_dropdown_value, log_radio_value):

    ### Daily Cases
    if metric_dropdown_value == 'Daily Cases':
        country_df = df[df['Country_Region'] == country_dropdown_value]
        confirmed_df = country_df[country_df['Case_Type'] == 'Confirmed']
        confirmed_df['Date'] = pd.to_datetime(confirmed_df['Date']);
        sorted_df = confirmed_df.sort_values('Date', ascending = True)
        sum_df = sorted_df.groupby('Date').sum()['Difference']
        x = sum_df.index
        y = sum_df

        z = moving_average = sum_df.rolling(5).mean()

        return {
                'data':([
                    {'x':x, 'y':y, 'type':'bar', 'name':country_dropdown_value, 'mode':'lines+markers','markers':{
                    }, 'marker':{
                            'color':'orange'
                    }},
                    {'x':x, 'y': z, 'type':'line', 'name': '5 day moving average', 'marker':{
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
                },
                'xaxis':{
                    'title':{
                        'text': 'Date'
                    }
                },

                }}


    ### Cumulative Cases
    elif metric_dropdown_value == 'Cumulative Cases':
        country_df = df[df['Country_Region'] == country_dropdown_value]
        confirmed_df = country_df[country_df['Case_Type'] == 'Confirmed']
        confirmed_df['Date'] = pd.to_datetime(confirmed_df['Date']);
        sorted_df = confirmed_df.sort_values('Date', ascending = True)
        sum_df = sorted_df.groupby('Date').sum()['Cases']
        x = sum_df.index
        y = sum_df

        z = moving_average = sum_df.rolling(5).mean()

        return {
                'data':([
                    {'x':x, 'y':y, 'type':'bar', 'name':country_dropdown_value, 'mode':'lines+markers','markers':{
                    }, 'marker':{
                            'color':'orange'
                    }},
                    {'x':x, 'y': z, 'type':'line', 'name': '5 day moving average', 'marker':{
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
            },
                'xaxis':{
                    'title':{
                        'text': 'Date'
                    }
                },
            }}
    ### Daily Deaths
    elif metric_dropdown_value == 'Daily Deaths':
        country_df = df[df['Country_Region'] == country_dropdown_value]
        confirmed_df = country_df[country_df['Case_Type'] == 'Deaths']
        confirmed_df['Date'] = pd.to_datetime(confirmed_df['Date']);
        sorted_df = confirmed_df.sort_values('Date', ascending = True)
        sum_df = sorted_df.groupby('Date').sum()['Difference']
        x = sum_df.index
        y = sum_df

        z = moving_average = sum_df.rolling(5).mean()

        return {
                'data':([
                    {'x':x, 'y':y, 'type':'bar', 'name':country_dropdown_value, 'mode':'lines+markers','markers':{
                    }, 'marker':{
                            'color':'orange'
                    }},
                    {'x':x, 'y': z, 'type':'line', 'name': '5 day moving average', 'marker':{
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
                },
                'xaxis':{
                    'title':{
                        'text': 'Date'
                    }
                },
                }}
    ### Daily Deaths
    elif metric_dropdown_value == 'Cumulative Deaths':
        country_df = df[df['Country_Region'] == country_dropdown_value]
        confirmed_df = country_df[country_df['Case_Type'] == 'Deaths']
        confirmed_df['Date'] = pd.to_datetime(confirmed_df['Date']);
        sorted_df = confirmed_df.sort_values('Date', ascending = True)
        sum_df = sorted_df.groupby('Date').sum()['Cases']
        x = sum_df.index
        y = sum_df

        z = moving_average = sum_df.rolling(5).mean()

        return {
                'data':([
                    {'x':x, 'y':y, 'type':'bar', 'name':country_dropdown_value, 'mode':'lines+markers','markers':{
                    }, 'marker':{
                            'color':'orange'
                    }},
                    {'x':x, 'y': z, 'type':'line', 'name': '5 day moving average', 'marker':{
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
                },
                'xaxis':{
                    'title':{
                        'text': 'Date'
                    }
                },
                }}

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
                {'x':x, 'y':y.rolling(window = 5).mean(),'name':'5 day moving average', 'type':'line', 'marker':{
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
                    }
                },
                'xaxis':{
                    'title':{
                        'text':('Date')
                    }
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
                {'x':x, 'y':y.rolling(window = 5).mean(),'name':'5 day moving average', 'type':'line', 'marker':{
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
                    }
                },
                'xaxis':{
                    'title':{
                        'text':('Date')
                    }
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
                {'x':x, 'y':y.rolling(window = 5).mean(),'name':'5 day moving average', 'type':'line', 'marker':{
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
                    }
                },
                'xaxis':{
                    'title':{
                        'text':'Date'
                    }
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
                {'x':x, 'y':y.rolling(window = 5).mean(),'name':'5 day moving average', 'marker':{
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
                    }
                },
                'xaxis':{
                    'title':{
                        'text':'Date'
                    }
                }
            }
        }

####################################################################################################################################################
############################ Leading ###########################################################################################################
####################################################################################################################################################








####################################################################################################################################################
############################ Render tabs ###########################################################################################################
####################################################################################################################################################

@app.callback(
    Output('render_page', 'children'),
    [Input('tabs', 'value')]
)
def display_page(tab_value):
    if tab_value == 'global':
        return global_layout
#    elif tab_value == 'leading':
#        return leading_layout
    else:
        return country_layout




if __name__ == '__main__':
    app.run_server(debug = True)

####
