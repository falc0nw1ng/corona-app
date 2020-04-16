import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Home Page'),
    dcc.Tabs(id = 'tabs',
        children = [
            dcc.Tab(label='Compare', value='compare'),
            dcc.Tab(label='Global', value='global'),
        ]),
    html.Div(id = 'render_page')
])

compare_layout = html.Div([
    html.P('This is the homepage')
])

global_layout = html.Div([
    html.P('GLOBAL STUFF')
])


@app.callback(
    Output('render_page', 'children'),
    [Input('tabs', 'value')]
)
def display_page(tab_value):
    if tab_value == 'global':
        return global_layout
    else:
        return compare_layout

if __name__ == '__main__':
    app.run_server(debug = True)
