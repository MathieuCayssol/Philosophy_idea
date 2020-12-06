import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

from apps import firststep



app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


index_page = html.Div(
    id="index_page_div",
    children=[
    dbc.Row(style={
                    'background': 'url("assets/bg.png")',
                    'background-repeat': 'no-repeat',
                    'background-position': 'center',
                    'background-attachment': 'fixed',
                    '-webkit-background-size': 'cover',
                    '-moz-background-size': 'cover',
                    '-o-background-size': 'cover',
                    'background-size': 'cover',
                    'height': '800px',
                }, children=[
                dbc.Col(html.Div(), md=2, xs=0),
                dbc.Col(html.Div(children=[
                    html.H1("Philosoph", id='title_proj'),
                    html.P(["PhilosophAI is a tool for visualizing the chronology of philosophical ideas.",html.Br() ,"It uses machine learning techniques (NLP, RNN-LSTM...) on databases from Wikipedia."], id='pres_p'),
                    html.Img(src="assets/pipeline.png", style={'width':'80%'}, id='img_pipeline'),
                    html.Div(children=[
                        dbc.NavLink("Try it now !", href="/apps/firststep", id="link_app")
                    ])
                    ]), md=8, xs=12),
                dbc.Col(html.Div(), md=2, xs=0)
        ]                               
    )
])



@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if (pathname == '/apps/firststep'):
        return firststep.layout
    if (pathname == ''):
        return index_page
    else:
        #return index_page
        return "Error"



if __name__ == '__main__':
    app.run_server(debug=True)
