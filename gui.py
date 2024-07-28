import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np
from main_multi import *

# Initialize the Dash app
app = dash.Dash(__name__)


chemo_lookup = {0: "2 day", 1: "CYVE-2", 2: "M1", 3: "End"} # idx, name

# Function to translate solutions to human-readable form
def translate_solution(sol):
    res = ""
    for cycle in sol:
        res += f"{chemo_lookup[CHEMO_DAYS.index(cycle)]}, " 
    return res[:-2]


# Function to create the bar chart based on infection cost
def create_figure(infection_cost, placement_cost, er_no_picc_cost, infection_chance_per_1000):
    # just pass arguments along
    data = find_optimal_solution(infection_cost=infection_cost, 
                                 placement_cost=placement_cost, 
                                 er_no_picc_cost=er_no_picc_cost, 
                                 infection_chance_per_1000=infection_chance_per_1000)
    data.sort(key=lambda x: x[1])
    annotation = [x[0] for x in data]  # Annotations for each bar
    annotation = list(map(translate_solution, annotation))
    y_axis = [x[1] for x in data]  # y-axis values (avg cost)
    x_axis = np.arange(0, len(y_axis), 1)  # x-axis positions

    fig = go.Figure(data=[
        go.Bar(
            name='Test',
            x=x_axis,
            y=y_axis,
            text=annotation,  # Add annotations
            textposition='auto'  # Automatically place text on bars
        )
    ])

    # Update layout with title and axis labels
    fig.update_layout(
        title=f'Cost of Different PICC Removal Times',
        xaxis_title='',
        yaxis_title='Cost (arbitrary)',
        xaxis=dict(tickvals=x_axis, ticktext=[str(i) for i in x_axis])
    )
    return fig


# Define the layout of the Dash app
app.layout = html.Div([
    dcc.Loading(
        id="loading",
        type="circle",  # Options are 'default', 'dot', 'circle'
        children=[
            dcc.Graph(id='bar-chart'),
        ]
    ),
    html.Div([
        html.Div(id='slider-output-container',
                             style={'marginTop': '20px'}),
        dcc.Slider(
            id='infection-cost-slider',
            min=int(PICC_PLACEMENT_COST * 100 / 10),
            max=PICC_PLACEMENT_COST * 100 * 5,
            step=PICC_PLACEMENT_COST * 2,
            value=PICC_PLACEMENT_COST * 100,  # Default value       \
            marks={i: str(i) for i in range(1000, 50000, 5000 )},
            dots=False,
            )
    ]),

    html.Div([
        html.Div(id='er-no-picc-slider-output-container',
                             style={'marginTop': '20px'}),
        dcc.Slider(
            id='er-no-picc-slider',
            min=1,
            max=10000,
            step=50,
            value=1000,
            marks={i: str(i) for i in range(0, 10001, 1000)},
            dots=False,
            )
    ]),

    html.Div([
        html.Div(id='picc-placement-cost-slider-output-container',
                             style={'marginTop': '20px'}),
        dcc.Slider(
            id='picc-placement-cost-slider',
            min=1,
            max=1000,
            step=20,
            value=100,
            marks={i: str(i) for i in range(0, 1001, 100)},
            dots=False,
            )
    ]),

    html.Div([
        html.Div(id='chance-slider-output-container',
                             style={'marginTop': '20px'}),
        dcc.Slider(
            id='infection-chance-slider',
            min=1,
            max=10,
            step=0.5,
            value=4,
            marks={i: str(i) for i in range(1, 11, 1 )},
            dots=False,
            )
    ])
])

# Callback to update the figure based on the slider value
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('infection-cost-slider', 'value'),
     Input('infection-chance-slider', 'value'),
     Input('er-no-picc-slider', 'value'),
     Input('picc-placement-cost-slider', 'value')
     ]
)
def update_figure(infection_cost, infection_chance_per_1000, er_no_picc_cost, picc_placement_cost):
    return create_figure(infection_cost, picc_placement_cost, er_no_picc_cost, infection_chance_per_1000)

# show values of sliders 
@app.callback(
    Output('slider-output-container', 'children'),
    [Input('infection-cost-slider', 'value')])
def update_slider_output(value):
    return f'Infection Cost: {value}'

@app.callback(
    Output('chance-slider-output-container', 'children'),
    [Input('infection-chance-slider', 'value')])
def update_slider_output(value):
    return f'Infection Chance {value}/1000 catheter days'


@app.callback(
    Output('er-no-picc-slider-output-container', 'children'),
    [Input('er-no-picc-slider', 'value')])
def update_slider_output(value):
    return f'ER Without PICC Cost: {value}'


@app.callback(
    Output('picc-placement-cost-slider-output-container', 'children'),
    [Input('picc-placement-cost-slider', 'value')])
def update_slider_output(value):
    return f'PICC placment cost {value}'


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
