import plotly.graph_objs as go

x = ['Product A', 'Product B', 'Product C']
y1 = [20, 14, 23]
y2 = [12, 18, 29]

xcoord = [0,1,2]

# annotations1 = [dict(
#             x=xi-0.2,
#             y=yi,
#             text=str(yi),
#             xanchor='auto',
#             yanchor='bottom',
#             showarrow=False,
#         ) for xi, yi in zip(xcoord, y1)]

# annotations2 = [dict(
#             x=xi+0.2,
#             y=yi,
#             text=str(yi),
#             xanchor='auto',
#             yanchor='bottom',
#             showarrow=False,
#         ) for xi, yi in zip(xcoord, y2)]

# annotations = annotations1 + annotations2

trace1 = go.Bar(
    x=x,
    y=y1,
    text=str(y1),
    textposition='auto',
    name='SF Zoo'
)
trace2 = go.Bar(
    x=x,
    y=y2,
    text=str(y2),
    textposition='auto',
    name='LA Zoo'
)
data = [trace1, trace2]
layout = go.Layout(
    barmode='group',
    # annotations=annotations
)
fig = go.Figure(data=data, layout=layout)
fig.show()