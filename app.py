import os
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import Flask
import plotly.express as px

import numpy as np
import pandas as pd

df = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv")
country_list = df.location.unique()

no_world = df.query("location != 'World'")
no_world = no_world.query("location != 'International'")
no_world = no_world.query("location !='Hong Kong'")
no_world = no_world.query("location != 'Spain'")
no_world.fillna(0, inplace = True)
most_recent_date = no_world.date.iloc[-1]

def one_week_trends():
    sorted_df = no_world.sort_values(by = 'date', ascending = True)
    last_week = no_world[(no_world['date'] >= no_world.date.iloc[-7])]
    grouped_week = last_week.groupby('location').sum()
    return grouped_week

x =one_week_trends()

global_map_metric = ['One Week Trend: Cases', 'One Week Trend: Deaths', 'Total Cases', 'Total Deaths']
metrics_dict = {
    "Daily Cases":'new_cases',
    "Daily Deaths": "new_deaths",
    "Cumulative Cases": "total_cases",
    "Cumulative Deaths": "total_deaths"
     }

def convert_column(column_name):
    if column_name == "new_cases":
        return "Daily Cases"
    elif column_name == "new_deaths":
        return "Daily Deaths"
    elif column_name == "total_cases":
        return "Cumulative Cases"
    elif column_name == "total_deaths":
        return "Cumulative Deaths"

##global boxes, world data
no_world = df.query("location != 'World'")

global_daily_cases = no_world[no_world['date'] == most_recent_date].new_cases.sum()
global_daily_deaths = no_world[no_world['date'] == most_recent_date].new_deaths.sum()
global_total_cases = no_world.new_cases.sum()
global_total_deaths = no_world.new_deaths.sum()

tab_style = {
    'border-top': '1px solid lightgray',
    'border-bottom': '1px solid lightgray',
    'border-right': '1px solid lightgray',
    'border-left': '1px solid lightgray',
    'padding': '6px',
    'font-size': '20px',
    'font-family':'bold',
    'margin':'auto',
    'border':'1px solid lightgray',
    'backgroundColor':'#333333',
    'color':'white',
    'box-shadow':'1px 1px 1px lightgray'
}

tab_selected_style = {
    'borderTop': '1px solid lightgray',
    'borderBottom': '1px solid lightgray',
    'border':'1px solid lightgray',
    'backgroundColor': '#cf082f',
    'color': 'white',
    'padding': '6px',
    'font-size': '20px',
    'font-family':'bold',
    'margin': 'auto',
    'box-shadow':'1px 1px 1px lightgray'
}

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
server = app.server #uncomment this for deployment

app.layout = html.Div([
    html.Div(
        children = [
            html.H1('Just Another COVID - 19 Dashboard',
                style = {'font-family':'Helvetica narrow, sans-serif', 'fontWeight':'lighter', 'color':'white', 'margin':'auto', 'padding-top':'5px', 'padding-left':'5px'})
        ]),
    dcc.Tabs(id = 'tabs', value = 'country',
        children = [
            dcc.Tab(label = 'By Country', value = 'country', style = tab_style, selected_style = tab_selected_style),
            dcc.Tab(label = 'Around the World', value = 'global', style = tab_style, selected_style = tab_selected_style),
        ],style = {'height': '50px'}),
    html.Div(id = 'render_page'),

],style = {'width':'80%', 'margin':'auto', 'backgroundColor':'#333333', 'height':'100%'}
)

# country_page
country_layout = html.Div([
    html.Div([
        html.Div(id = 'daily_country_cases', style = { 'width': '12%', 'textAlign':'center',
         'box-shadow': '2px 2px 2px lightgray', 'display':'table-cell'}),
        html.Div(id = 'daily_country_deaths', style = { 'width': '12%', 'textAlign':'center',
         'box-shadow': '2px 2px 2px lightgray', 'display':'table-cell'}),
        html.Div(id = 'total_country_cases', style = { 'width': '12%', 'textAlign':'center',
          'box-shadow': '2px 2px 2px lightgray', 'display':'table-cell'}),
        html.Div(id = 'total_country_deaths', style = { 'width': '12%', 'textAlign':'center',
           'box-shadow': '2px 2px 2px lightgray', 'display':'table-cell'}),
    ],style = {'vertical-align':'top', 'width':'100%', 'color':'white', 'backgroundColor':'#333333'}),
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
                        options = [{'label':key, 'value':value} for key,value in metrics_dict.items()],
                        value = 'new_cases',
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
            dcc.Graph(id = 'bar_graph',)
        ], style = {'display':'inline-block', 'width':'100%'}
        ),
    ]),
        html.Div([
            dcc.Graph(id = 'country_pie_graph',
                style = {'width':'70%', 'display':'inline-block', 'float':'left'}
                ),
            html.Div(id = 'death_rate',
                style = {
                    'color':'white', 'font-size':'18px', 'width':'18%', 'display':'inline-block', 'float':'left', 'padding-top':'10%'}
                    )
        ], style = {'width':'90%', 'display':'inline-block'}
        ),


], style = {'vertical-align':'top', 'backgroundColor':'#333333'})

global_layout = html.Div([
    html.Div([
        html.Div([
            html.P('Daily Cases:', style = {'font-size':'25px'}),
            html.P(global_daily_cases, style = {'font-size':'25px'})
        ], style = {'textAlign':'center', 'box-shadow': '2px 2px 2px lightgray', 'display':'table-cell', "width": "8%"}
        ),
        html.Div([
            html.P('Daily Deaths:', style = {'font-size':'25px'}),
            html.P(global_daily_deaths, style = {'font-size':'25px'})
        ],style = {'textAlign':'center','box-shadow': '2px 2px 2px lightgray', 'display':'table-cell', "width": "8%"}
        ),
        html.Div([
            html.P('Total Cases:', style = {'font-size':'25px'}),
            html.P(global_total_cases, style = {'font-size':'25px'})
        ], style = {'textAlign':'center', 'box-shadow': '2px 2px 2px lightgray', 'display':'table-cell', "width": "8%"}
        ),
        html.Div([
            html.P('Total Deaths:', style = {'font-size':'25px'}),
            html.P(global_total_deaths, style = {'font-size':'25px'}),
        ], style = {'textAlign':'center', 'box-shadow': '2px 2px 2px lightgray', 'display':'table-cell', "width": "8%" }
        ),
    ],style = {'vertical-align':'top', 'color':'white', 'backgroundColor':'#333333'}
        ),
    html.Div([
        html.Div(
            dcc.RadioItems(
                id = "radio_map",
                options = [{'label':i, 'value':i} for i in global_map_metric],
                value = 'One Week Trend: Cases',
                style = {'color':'white'}
            ),
            style = {'margin-right':'20px'}
        ),
        dcc.Graph('global_map',
            style = {
                'height':800,
                'width':'100%', 'float':'left'
            })
        ],style = {'margin-right':'20px'}),

    html.Div([
        html.P('Select a metric',
        style = {'color':'white', 'font-size':'20px'}
        ),
        dcc.Dropdown(
            id = 'metric_dropdown2',
            options = [{'label':key, 'value':value} for key,value in metrics_dict.items()],
            value = 'new_cases',
            style = {'width':'35%'}
        ),
        dcc.RadioItems(
            id = 'log_radio2',
            options = [{'label':i, 'value':i} for i in ['Linear', 'Log']],
            value = 'Linear',
            style = {'color':'white'}
        ),
        ], style = {'width':'95%','margin':'auto'}),
    html.Div([
        dcc.Graph(id = 'global_bar_graph')
        ],
        style = {'width':'100%'}
        ),
],style = {'backgroundColor':'#333333'})

#### country boxes

# daily cases
@app.callback(
    Output("daily_country_cases", "children"),
    [Input('country_dropdown', 'value')]
)

def daily_country_cases(country_dropdown):
    country = no_world[no_world['location'] == country_dropdown]
    daily_cases = country.new_cases.iloc[-1]
    return [
        html.Div([
            html.P('Daily cases in {}:' .format(country_dropdown),
                style = {'font-size':'25px'}
                ),
            html.P(daily_cases,
                style = {'font-size':'25px'}
                )
        ])
    ]

# daily deaths
@app.callback(
    Output("daily_country_deaths", "children"),
    [Input("country_dropdown", "value")]
)

def daily_country_deaths(country_dropdown):
    country = no_world[no_world['location'] == country_dropdown]
    daily_deaths = country.new_deaths.iloc[-1]
    return [
        html.Div([
            html.P('Daily death in {}:' .format(country_dropdown),
                style = {'font-size':'25px'}
                ),
            html.P(daily_deaths,
                style = {'font-size':'25px'}
                )
        ])
    ]

# total country cases
@app.callback(
    Output("total_country_cases", "children"),
    [Input("country_dropdown", 'value')]
)

def total_country_cases(country_dropdown):
    country = no_world[no_world['location'] == country_dropdown]
    total_cases = country.total_cases.iloc[-1]
    return [
        html.Div([
            html.P('Total cases in {}:' .format(country_dropdown),
                style = {'font-size':'25px'}
                ),
            html.P(total_cases,
                style = {'font-size':'25px'}
                )
        ])
    ]

## total country deaths
@app.callback(
    Output("total_country_deaths", "children"),
    [Input("country_dropdown", "value")]
)

def total_country_deaths(country_dropdown):
    country = no_world[no_world['location'] == country_dropdown]
    total_deaths = country.total_deaths.iloc[-1]
    return [
        html.Div([
            html.P('Total deaths in {}:' .format(country_dropdown),
                style = {'font-size':'25px'}
                ),
            html.P(total_deaths,
                style = {'font-size':'25px'})
        ])
    ]

### user adjustable bar graph
@app.callback(
    Output("bar_graph",'figure'),
    [Input('country_dropdown', 'value'),
    Input('metric_dropdown', 'value'),
    Input('log_radio', 'value')]
)

def bar_graph(country_dropdown, metric_dropdown, log_radio):
    country = no_world[no_world['location'] == country_dropdown]
    return {
        'data':([
            {'x':country.date, 'y':country[metric_dropdown], 'type':'bar', 'name':'Daily Cases for {}'.format(country_dropdown), 'mode':'lines+markers', 'markers':{
            }, 'marker':{
                    'color':'orange',
            }},
            {'x':country.date, 'y': country[metric_dropdown].rolling(5).mean(), 'type':'line', 'name': 'Moving Average (window = 5 Days)', 'marker':{
                'color':'red'
            }}
        ]),
        'layout':{
            'title':{
                'text': "Daily Cases in {} vs Date".format(country_dropdown)
            },
            'yaxis':{
                'title':{
                    'text': convert_column(metric_dropdown)
                },
                'type':'linear' if log_radio == 'Linear' else 'log',
                'gridcolor':'#b3b3b3'
            },
            'xaxis':{
                'title':{
                    'text': 'Date'
                },
                'rangeselector':{
                    'buttons':{
                        'step':'all'
                    }
                },
                'rangeslider':{
                    'visibility':True
                },
                'type':'date'},
            'plot_bgcolor':'#333333',
            'paper_bgcolor':'#333333',
            'font':{
                'color':'white'
            },
            }
        }

############# pie graph + death rate

@app.callback(
    Output("country_pie_graph", "figure"),
    [Input("country_dropdown", "value")]
)

def pie_graph(country_dropdown):
    country = no_world[no_world['location'] == country_dropdown]
    return{
        'data':([
            {
                'values':[country.total_cases.iloc[-1], country.total_deaths.iloc[-1]] , 'type':'pie', 'labels':['Confirmed', 'Deaths'], 'marker' : {
                    'colors':['lightgreen','red'],
                    'line':{
                        'color':'black',
                        'width':'2'
            }}}
        ]),
        'layout':{
            'title':{
                'text':'Death rate in {}' .format(country_dropdown)
        },
        'paper_bgcolor':'#333333',
        'font':{
            'color':'white'
        }
        }}

### country vs global death rate comparison

@app.callback(
    Output('death_rate', 'children'),
    [Input('country_dropdown', 'value')]
)

def death_rate(country_dropdown):
    country = no_world[no_world['location'] == country_dropdown]
    dead = country.total_deaths.iloc[-1]
    cases = country.total_cases.iloc[-1]
    country_death_rate = dead/cases

    global_cases = no_world.new_cases.sum()
    global_deaths = no_world.new_deaths.sum()
    global_death_rate = (global_deaths/global_cases).round(3)

    if global_death_rate > country_death_rate:
        return [
            html.Div([
                html.P("The country of {} is doing worst than the global average death rate of {}%" .format(country_dropdown, global_death_rate*100))
            ])
        ]
    elif global_death_rate == country_death_rate:
        return [
            html.Div([
                html.P("The country of {} has the same death rate, as the global average of {}%" .format(country_dropdown, global_death_rate*100))
            ])
        ]
    elif global_death_rate < country_death_rate:
        return [
            html.Div([
                html.P("The country of {} is doing better than the global average death rate of {}%" .format(country_dropdown, global_death_rate*100))
            ])
        ]
    else:
        return [
            html.Div([
                html.P("Please select a country at the top")
            ])
        ]

############################ World Page ##################
############################ global bar graph  ####################################

@app.callback(
    Output('global_bar_graph','figure'),
    [Input('metric_dropdown2', 'value'),
    Input('log_radio2', 'value')]
)

def global_bar_graph(metric_dropdown2, log_radio2):
    world = df[df['location'] == 'World']
    return {
        'data':([
            {'x': world.date, 'y': world[metric_dropdown2], 'type':'bar', 'name': convert_column(metric_dropdown2), 'marker':{
                'color':'orange'
            }},
            {'x': world.date, 'y': world[metric_dropdown2].rolling(5).mean(),'name':'Moving Average (window = 5 Days)', 'type':'line', 'marker':{
                'color':'red'
            }}
        ]),
        'layout':{
            'title':{
                'text':'Global Daily Deaths vs Date'
            },
            'yaxis':{
                'type':'linear' if log_radio2 == 'Linear' else 'log',
                'title':{
                    'text':(convert_column(metric_dropdown2))
                },
                'gridcolor':'#b3b3b3'
            },
            'xaxis':{
                'title':{
                    'text':('Date')
                },
                'rangeselector':{
                    'buttons':{
                        'step':'all'
                    }
                },
                'rangeslider':{
                    'visibility':True
                },
                'type':'date'
            },
            'plot_bgcolor':'#333333',
            'paper_bgcolor':'#333333',
            'font':{
                'color':'white'
            }
        }
    }

### Global Map
@app.callback(
    Output('global_map', 'figure'),
    [Input('radio_map', 'value')]
)

def create_map(column_name):
    totals = no_world.groupby(by = 'location').sum()
    d = {'One Week Trend: Cases': x.new_cases,
         'One Week Trend: Deaths': x.new_deaths,
         'Total Cases': totals.new_cases,
         'Total Deaths': totals.new_deaths}
    combined_df = pd.DataFrame(data = d)
    combined_df.fillna(0, inplace = True)

    scale = 100
    trace = go.Scattergeo(
    locationmode = 'country names',
    locations = combined_df.index,
    text = combined_df[column_name],
    marker = dict(
        size = combined_df[column_name]/scale,
        color = 'red',
        line_color='rgb(40,40,40)',
        line_width=1,
        sizemode = 'area'
    ),name = column_name
    )
    return {
        'data': [trace],
        'layout': go.Layout(
            title_text = ('{} Around the World' .format(column_name)),
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
                showland = True,
                landcolor = 'lightgray',
                showcoastlines = False,
                coastlinecolor = "blue",
                showocean = True,
                oceancolor = '#333333',
                showlakes = True,
                lakecolor = 'white',
        ))
    }
#### render tabs
@app.callback(
    Output('render_page', 'children'),
    [Input('tabs', 'value')]
)
def display_page(tab_value):
    if tab_value == 'global':
        return global_layout
    else:
        return country_layout

if __name__ == '__main__':
    app.run_server(debug = True)


#####
