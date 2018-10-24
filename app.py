## Importing Libraries 
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import sqlite3
from textblob import TextBlob
from unidecode import unidecode
import time
from guess_language import guess_language

#consumer key, consumer secret, access token, access secret.

ckey='your_twitter_consumer_key'
csecret='your_twitter_consumer_secret'
atoken='your_twitter_access_token'
asecret='your_twitter_access_secret'

conn = sqlite3.connect('bitcoin.db')
c = conn.cursor()

def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL)")
    conn.commit()

create_table()

class listener(StreamListener):

    def on_data(self, data):
        try:
            data = json.loads(data)
            tweet = unidecode(data['text'])
            time_ms = data['timestamp_ms']
            analysis = TextBlob(tweet)
            sentiment = analysis.sentiment.polarity
            print(time_ms, tweet, sentiment)
            if sentiment != 0.0 and guess_language(tweet) == 'en':
                c.execute("INSERT INTO sentiment (unix, tweet, sentiment) VALUES (?, ?, ?)",
                      (time_ms, tweet, sentiment))
                conn.commit()

        except KeyError as e:
            print(str(e))
        return(True)

    def on_error(self, status):
        print(status)


while True:
    try:
        auth = OAuthHandler(ckey, csecret)
        auth.set_access_token(atoken, asecret)
        twitterStream = Stream(auth, listener())
        twitterStream.filter(track=["bitcoin"])
    except Exception as e:
        print(str(e))
        time.sleep(5)

# Importing Libraries

import dash
from dash.dependencies import Input, Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import sqlite3
import pandas as pd

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
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 50000", conn ,params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace=True)
        df['date'] = pd.to_datetime(df['unix'], unit='ms') + pd.Timedelta('05:30:00')
        df.set_index('date', inplace=True)

        max_, min_ = 1.0, -1.0
        df['sentiment_smoothed'] = round((((df['sentiment'] - min_) * (100)) / (max_ - min_)))
        df = df.resample('30T').mean()

        df.dropna(inplace=True)

        X = df.index
        Y = df.sentiment_smoothed.values

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
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')
if __name__ == '__main__':
    app.run_server(debug=False, port=8000)
    
