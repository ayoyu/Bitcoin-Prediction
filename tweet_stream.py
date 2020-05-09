from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import sqlite3
from textblob import TextBlob
from unidecode import unidecode
import time
#from guess_language import guess_language
import yaml
from langdetect import detect
import logging


logging.basicConfig(
		filename='errors.log',
        format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
        level=logging.ERROR,
        datefmt="%H:%M:%S",
)
# Create a logger object.
logger = logging.getLogger(__file__.split('.')[0])
logging.getLogger("chardet.charsetprober").disabled = True

conn = sqlite3.connect('bitcoin.db')
c = conn.cursor()


def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL)")
    conn.commit()


class listener(StreamListener):

    def on_data(self, data):
        try:
            data = json.loads(data)
            tweet = unidecode(data['text'])
            time_ms = data['timestamp_ms']
            analysis = TextBlob(tweet)
            sentiment = analysis.sentiment.polarity
            if sentiment != 0.0 and detect(tweet) == 'en':
                c.execute("INSERT INTO sentiment (unix, tweet, sentiment) VALUES (?, ?, ?)",
                      (time_ms, tweet, sentiment))
                conn.commit()

        except Exception as e:
            logger.error(str(e))
            return False
        return True


    def on_error(self, status):
        logger.error(str(status))


if __name__ == "__main__": 
    create_table()
    with open('./.twitter_credentials.yaml') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    credentials_data = data['TwitterCredentials']
    while True:
        try:
            auth = OAuthHandler(
                credentials_data['Consumer']['consumer_key'],
                credentials_data['Consumer']['consumer_secret']
            )
            auth.set_access_token(
                credentials_data['Access']['access_token'],
                credentials_data['Access']['access_secret']
            )
            twitterStream = Stream(auth, listener())
            twitterStream.filter(track=["bitcoin"])
        except Exception as e:
            logger.error(str(e))
            time.sleep(5)