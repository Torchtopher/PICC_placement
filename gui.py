import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np
from main_multi import *

# Initialize the Dash app
app = dash.Dash(__name__)

# Function to translate solutions to human-readable form
def translate_solution(sol):
    res = "Cycle "
    for i in sol:
        res += f"{CHEMO_DAYS.index(i)}, "
    return res[:-2]


# Function to create the bar chart based on infection cost
def create_figure(infection_cost):
    data = find_optimal_solution(infection_cost=infection_cost)
    data.sort(key=lambda x: x[1])
    annotation = [x[0] for x in data]  # Annotations for each bar
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
        title=f'Cost of Different PICC Removal Times (Infection Cost: {infection_cost})',
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
        html.Label('Infection Cost:'),
    dcc.Slider(
        id='infection-cost-slider',
        min=int(PICC_PLACEMENT_COST * 100 / 10),
        max=PICC_PLACEMENT_COST * 100 * 5,
        step=PICC_PLACEMENT_COST * 2,
        value=PICC_PLACEMENT_COST * 100,  # Default value       \
        marks={i: str(i) for i in range(int(PICC_PLACEMENT_COST * 100 / 10), PICC_PLACEMENT_COST * 100 * 10, PICC_PLACEMENT_COST * 100 )},
        dots=False
        ),
        html.Div(id='slider-output-container')  # To show current slider value if needed
    ])
])

# Callback to update the figure based on the slider value
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('infection-cost-slider', 'value')]
)
def update_figure(infection_cost):
    return create_figure(infection_cost)

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
