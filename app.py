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
no_world.fillna(0, inplace = True)
most_recent_date = no_world.date.iloc[-1]
## needed sometimes since positivity rates are not updated quickly enough within the first couple days
recent_date = no_world.date.iloc[-3]

def one_week_trends():
    sorted_df = no_world.sort_values(by = 'date', ascending = True)
    last_week = no_world[(no_world['date'] >= no_world.date.iloc[-7])]
    grouped_week = last_week.groupby('location').sum()
    return grouped_week
x =one_week_trends()

global_map_metric = ['One Week Trend: Cases', 'One Week Trend: Deaths', 'Total Cases (In Thousands)', 'Total Deaths']
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
app.title='Just Another COVID-19 Dashboard'
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
    html.Div([
        html.P("Further details about the author and the data sources can be found ", style = {
            'color':'white', 'display':'inline', 'padding-left':'5px'}),
        html.A("here", href = "https://therealmaplejordan.com/", style = {'display':'inline', 'color':'#cf082f', 'padding-right':'15px'})
        ], style = {'display':'inline','float':'right'}
    )
])

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
            style = {'font-size':'25px', 'color':'white', 'width':'95%', 'margin':'auto', 'padding-top':'10px'}
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
            html.Div(id='sidebar', style={'width':'25%', 'float':'left', 'padding-left':'10px'}),
            dcc.Graph(id = 'bar_graph', style={'width':'70%', 'float':'left'})
        ], style = {'display':'inline-block', 'width':'100%', 'verticalAlign':'top'}
        ),
    ]),
        html.Div(id='reproduction_rate_vs_total_cases', style={'width':'37%', 'float':'left', 'padding-left':'15px'}),
        html.Div([
            html.Button('Vs Countries with Most Deaths', id = 'btn-nclicks-1', n_clicks=0, style={'padding':'2%', 'font-weight':'bold', 'backgroundColor':'white'}),
            html.Button('Age Demographic', id = 'btn-nclicks-2', n_clicks=0, style={'padding':'2%', 'font-weight':'bold', 'backgroundColor':'white'}),
            html.Div(id ='country_pie_bar_graph',
                #style = {'width':'70%', 'display':'inline-block', 'float':'left'}
                ),
        ], style = {'width':'60%', 'display':'inline-block', 'float':'left'}
        ),


], style = {'vertical-align':'top', 'backgroundColor':'#333333'})


gdp_vs_total_testing = no_world[no_world['date']==recent_date][['total_tests_per_thousand', 'gdp_per_capita','location','continent','positive_rate']]
gdp_vs_total_testing.fillna(0,inplace=True)
gdp_testing_scatter = px.scatter(gdp_vs_total_testing, x='gdp_per_capita', y='total_tests_per_thousand', size='positive_rate', color='continent',hover_data=['location'], trendline='ols', trendline_color_override='#d46161')
gdp_testing_scatter.update_layout(
    plot_bgcolor='#333333',
    paper_bgcolor='#333333',
    font=dict(
        color='white'
    ),
    xaxis=dict(
        title='GDP per Capita'
    ),
    yaxis=dict(
        title='Total Test per Thousand'
    ),
    title='Total Test per Thousands vs GDP per Capita'
)


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
        dcc.Graph(id='global_map',
            config={"scrollZoom": False },
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
        dcc.Graph(figure=gdp_testing_scatter, style={'width':'38%','float':'left', 'padding-top':'20px', 'padding-left':'15px'}),
        dcc.Graph(id = 'global_bar_graph', style={'width':'60%', 'float':'left'})
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


##sidebar
### shows gdp, positivity rate, tests per cases,
@app.callback(
    Output('sidebar', 'children'),
    [Input('country_dropdown', 'value')]
)
def sidebar(country_dropdown):
    # delay by 5 days due to lag between ocurrance of event and time it takes to update data
    country = no_world[no_world['location'] == country_dropdown]
    total_test_per_thousand = country['total_tests_per_thousand'].iloc[-5]
    positivity_rate = country['positive_rate'].iloc[-5]
    tests_per_case = country['tests_per_case'].iloc[-5]

    return html.Div(
        children=[
            html.P('Testing Statistics in {}' .format(country_dropdown), style={'padding-left':'20px', 'padding-top':'10px', 'font-size':'20px'}),
            html.P('Total Test per Thousand:', style={ 'border-top':'1px', 'border-left':'1px',
                'border-right':'1px', 'border-bottom':'0','borderColor':'lightgray',
                'margin':'30px 10px 0 10px', 'border-style':'solid', 'padding':'20px 20px 15px 20px'}),
            html.P('{}'.format(round(total_test_per_thousand,2)), style={'border-top':'0',
                'border-left':'1px', 'border-right':'1px', 'border-bottom':'1px','borderColor':'lightgray',
                'margin':'0 10px 0 10px', 'border-style':'solid', 'padding':'0 10px 10px 30px'}),
            html.P('Positivity Rate:', style={ 'border-top':'0', 'border-left':'1px',
                'border-right':'1px', 'border-bottom':'0','borderColor':'lightgray',
                'margin':'0 10px 0px 10px', 'border-style':'solid', 'padding':'20px 20px 15px 20px'}),
            html.P(positivity_rate, style={'border-top':'0',
                'border-left':'1px', 'border-right':'1px', 'border-bottom':'1px','borderColor':'lightgray',
                'border-style':'solid','margin':'0 10px 0 10px',
                'padding':'0 10px 10px 30px'}),
            html.P('Tests per Cases:', style={ 'border-top':'0', 'border-left':'1px',
                'border-right':'1px', 'border-bottom':'0','borderColor':'lightgray',
                'margin':'0 10px 0 10px', 'border-style':'solid', 'padding':'20px 20px 15px 20px'}),
            html.P(tests_per_case, style={'border-top':'0',
                'border-left':'1px', 'border-right':'1px', 'border-bottom':'1px','borderColor':'lightgray',
                'border-style':'solid', 'margin':'0 10px 0 10px',
                'padding':'0 10px 10px 30px',})
        ], style={'color':'white', 'font-size':'20px',}
    )

#style = { 'width': '12%', 'textAlign':'center',
 #'box-shadow': '2px 2px 2px lightgray', 'display':'table-cell'}



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


### reproduction rate
@app.callback(
    Output('reproduction_rate_vs_total_cases', 'children'),
    [Input('country_dropdown', 'value')]
)
def reproduction_graph(country_dropdown):
    country = no_world[no_world['location'] == country_dropdown]
    fig = go.Figure(
                go.Scatter(
                x=country.total_cases_per_million,
                y=country.reproduction_rate
            )
        )
    fig.update_layout(
        title='Reproduction Rate vs Total Cases per Million',
        xaxis=dict(
            title='Total Cases per Million',
            gridcolor='#b3b3b3'
        ),
        yaxis=dict(
            title='Reproduction Rate',
            gridcolor='#b3b3b3'
        ),
        paper_bgcolor='#333333',
        plot_bgcolor='#333333',
        font=dict(
            color='white'
        )
    )

    return html.Div(
                dcc.Graph(figure=fig)
    )

############# bargraphs comparison between selected country and the top countries for most cases and most deaths
@app.callback(
    Output("country_pie_bar_graph", "children"),
    [Input("country_dropdown", "value"),
    Input('btn-nclicks-1', 'n_clicks'),
    Input('btn-nclicks-2', 'n_clicks')]
)
def button_output(country_dropdown, btn1, btn2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    all_countries = no_world[no_world['date']==recent_date][['location','total_cases', 'total_deaths','gdp_per_capita', 'population', 'life_expectancy', 'median_age','aged_70_older']]
    all_countries['Death per Case'] = (all_countries.total_deaths/all_countries.total_cases)
    all_countries['Deaths per Population'] = (all_countries.total_deaths/all_countries.population)
    all_countries['Cases per Population'] = (all_countries.total_cases/all_countries.population)
    one_country = all_countries[all_countries['location']==country_dropdown]
    #one_country = all_countries.query('location=={}' .format(country_dropdown))
    top_death_rates = all_countries.sort_values(by='total_deaths', ascending=False).head()
    append_selected_country = top_death_rates.append(one_country)
    final_df = append_selected_country
    final_df.drop_duplicates(inplace=True)

    # vs global av
    if 'btn-nclicks-2' in changed_id:
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Aged 70 or Older (Percentage)',x=final_df['location'], y=final_df['aged_70_older'],
            marker=dict(color='#2a5b9c')))
        fig.add_trace(go.Bar(name='Life Expectancy (Years)', x=final_df['location'], y=final_df['life_expectancy'],
            marker=dict(color='#228a2e')))
        fig.add_trace(go.Bar(name='Median Age (Years)', x=final_df['location'], y=final_df['median_age'],
            marker=dict(color='#ab983a')))
        fig.update_layout(
            title='Age Demographic',
            plot_bgcolor='#333333',
            paper_bgcolor='#333333',
            font=dict(
                color='white'
            ),
        )
    elif 'btn-nclicks-1' in changed_id:
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Death per Case', y=final_df['location'], x=final_df['Death per Case']*100, orientation='h',
            marker=dict(color='#9c2a2a')))
        fig.add_trace(go.Bar(name='Deaths per Population', y=final_df['location'], x=final_df['Deaths per Population']*100, orientation='h',
            marker=dict(color='#9c472a')))
        fig.add_trace(go.Bar(name='Cases Per Population', y=final_df['location'], x=final_df['Cases per Population']*100, orientation='h',
            marker=dict(color='#742a9c')))
        fig.update_layout(
            title='Deaths and Cases in Percentage',
            plot_bgcolor='#333333',
            paper_bgcolor='#333333',
            font=dict(
                color='white'
            )
        )
    # vs top countries for total deaths
    else:
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Death per Case', y=final_df['location'], x=final_df['Death per Case']*100, orientation='h',
            marker=dict(color='#9c2a2a')))
        fig.add_trace(go.Bar(name='Deaths per Population', y=final_df['location'], x=final_df['Deaths per Population']*100, orientation='h',
            marker=dict(color='#9c472a')))
        fig.add_trace(go.Bar(name='Cases Per Population', y=final_df['location'], x=final_df['Cases per Population']*100, orientation='h',
            marker=dict(color='#742a9c')))
        fig.update_layout(
            title='Deaths and Cases in Percentage',
            plot_bgcolor='#333333',
            paper_bgcolor='#333333',
            font=dict(
                color='white'
            )
        )
    return html.Div(
        dcc.Graph(figure = fig)
    )




### country vs global death rate comparison
#### UNUSED
@app.callback(
    Output('death_rate', 'children'),
    [Input('country_dropdown', 'value')]
)
def death_rate(country_dropdown):
    country = no_world[no_world['location'] == country_dropdown]
    dead = country.total_deaths.iloc[-1]
    cases = country.total_cases.iloc[-1]
    country_death_rate = (dead/cases).round(3)

    global_cases = no_world.new_cases.sum()
    global_deaths = no_world.new_deaths.sum()
    global_death_rate = (global_deaths/global_cases).round(3)
    global_rate = (global_death_rate*100).round(3)

    if global_death_rate > country_death_rate:
        return [
            html.Div([
                html.P("The country of {} is doing better than the global average death rate of {}%" .format(country_dropdown, global_rate))
            ])
        ]
    elif global_death_rate == country_death_rate:
        return [
            html.Div([
                html.P("The country of {} has the same death rate, as the global average of {}%" .format(country_dropdown, global_rate))
            ])
        ]
    elif global_death_rate < country_death_rate:
        return [
            html.Div([
                html.P("The country of {} is doing worse than the global average death rate of {}%" .format(country_dropdown, global_rate))
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

#global bar graph
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
                'text':('Global {} vs Date' .format(convert_column(metric_dropdown2)))
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
    scaled_total_case = (totals.new_cases)/1000
    d = {'One Week Trend: Cases': x.new_cases,
         'One Week Trend: Deaths': x.new_deaths,
         'Total Cases (In Thousands)': (scaled_total_case),
         'Total Deaths': totals.new_deaths}
    combined_df = pd.DataFrame(data = d)
    combined_df.fillna(0, inplace = True)
    combined_df = combined_df.abs()
    scale = 100
    trace = go.Scattergeo(
    locationmode = 'country names',
    locations = combined_df.index,
    text = combined_df[column_name],
    marker = dict(
        size = (combined_df[column_name]/scale),
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
        )),
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
