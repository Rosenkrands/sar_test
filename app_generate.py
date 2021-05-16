import dash
import matplotlib
matplotlib.use('Agg')
from logging import debug, error
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from matplotlib import pyplot as plt

from io import BytesIO
import base64
import os

from sar_moe8.map import MapGenerator
from sar_moe8.map import WORK_DIR
from sar_moe8.map import MAP_DIR

# source: https://github.com/4QuantOSS/DashIntro/blob/master/notebooks/Tutorial.ipynb
def fig_to_uri(fig, close_all=True):
    """
    Convert a matplotlib figure into something that can be passed into html.Img.
    """
    out_img = BytesIO()
    fig.savefig(out_img, format = 'png', bbox_inches='tight')
    if close_all:
        fig.clf()
        plt.close('all')
    out_img.seek(0)
    encoded = base64.b64encode(out_img.read()).decode('ascii').replace("\n", "")
    return "data:image/png;base64,{}".format(encoded)

# Find the available map instances from the 'map-instance' dropdown
instances = [{'label': map_id, 'value': os.path.join(MAP_DIR, map_id)} for map_id in os.listdir(MAP_DIR)]

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],suppress_callback_exceptions=True)

header = dbc.Col(html.H1("Instance Generator", style={'text-align': 'center', 'padding-top': 20}), width={'size': 12})

parameters = dbc.Card([
                    dbc.CardBody([
                        html.H4("Parameters", className='card-title'),
                        html.P("The Image below shows a heatmap of the generated instance.", className='card-text'),
                        html.H6("Difficulty"),
                        dcc.Slider(id='difficulty', min=.5, max=3, step=.5, marks={i: str(i) for i in [0.5,1,1.5,2,2.5,3]},value=1),
                        html.H6("Centers"),
                        dcc.Slider(id='centers', min=2, max=5, step=1, marks={i: str(i) for i in range(2,6)},value=3),
                        html.H6("Dimension"),
                        dcc.Slider(id='dimension', min=50, max=200, step=50, marks={i: str(i) for i in [50,100,150,200]},value=100),
                    ])
            ])

# for i in np.linspace(1,5,5):
#     print(str(int(i)))

score_map = dbc.Card([
                    dbc.CardBody([
                        html.P("The Image below shows a heatmap of the generated instance.", className='card-text'),
                        dbc.Row([
                            dbc.Col(html.P("Pressing the button will generate a new instance.", className='card-text'),width={'size': 7}),
                            dbc.Col(dbc.Button(id='generate', n_clicks=0, children="Generate", color="primary", className="mr-1", block=True),width={'size': 5}) 
                        ])
                    ]),
                dbc.CardImg(id = 'score-plot', src = '', style={'width':'100%'}, bottom=True)
            ])

FOOTER_STYLE = {
    "bottom": 0,
    "left": 0,
    "right": 0,
    "height": "10rem",
    "padding": "1rem 1rem",
    "background-color": "white",
}

app.layout = dbc.Container(
    [
        dbc.Row(header),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                parameters
            ], width={'size': 4}),
            dbc.Col([
                score_map,
            ], width={'size': 8})
        ]),
        html.Div(style=FOOTER_STYLE)       
    ]
)

@app.callback(
    Output('score-plot', 'src'),
    Input('generate', 'n_clicks'),
    State('difficulty', 'value'),
    State('centers', 'value'),
    State('dimension', 'value')
)
def map_plot(n_clicks, difficulty, centers,dim):
    try:
        inst = MapGenerator(centers=centers, difficulty=difficulty, map_dim=(dim,dim))
        fig = inst.plot(add_targets=True)
        text = fig_to_uri(fig)
        return text
    except:
        return('https://via.placeholder.com/600')

if __name__ == '__main__':
    app.run_server(debug=True)