import dash
from dash.dependencies import Input, Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import sqlite3
import pandas as pd
import subprocess


app = dash.Dash(__name__)
app.title='Bitcoin Sentiments'

app_colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
}

app.layout = html.Div(
    [   html.Div(className='container', children=[html.H1('Live Twitter Sentiment of Bitcoins', style={'color':"#CECECE", 'padding':'10px', 'word-spacing':'1em'}),
                                                  dcc.Input(id='sentiment_term', value='bitcoin', type='text', style={'color':'black' ,'margin':'10px'}),
                                                  ]),
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1*1000
        ),
    ], style={'backgroundColor': app_colors['background']},
)

@app.callback(Output('live-graph', 'figure'),
              [Input(component_id='sentiment_term', component_property='value')],
              events=[Event('graph-update', 'interval')])
def update_graph_scatter(sentiment_term):
    try:
        conn = sqlite3.connect('bitcoin.db')
        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 50000",
        conn, params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace=True)
        df['date'] = pd.to_datetime(df['unix'], unit='ms') + pd.Timedelta('05:30:00')
        df.set_index('date', inplace=True)
        df = df.resample('1T').mean()
        df.dropna(inplace=True)

        X = df.index
        Y = df.sentiment.values

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Scatter',
                mode= 'lines+markers'
                )

        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[min(Y),max(Y)]),
                                                    font={'color':app_colors['text']},
                                                    plot_bgcolor = app_colors['background'],
                                                    paper_bgcolor = app_colors['background'],
                                                   )}

    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    app.run_server(debug=True, port=8000)