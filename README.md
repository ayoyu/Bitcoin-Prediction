# Bitcoin Twitter Sentiment Analysis Tweepy

**To test the application make sure to have Python3.x installed and a developer twitter account**

## Instructions

#### Create a developer twitter account

- https://developer.twitter.com/en

#### Create a virtualenv

```
$ virtualenv -p python3.6 myenv
$ source myenv/bin/activate
(myenv)$ pip install -r requirements.txt
```
#### Set your twitter credentials

- you need to modify the yaml file ```.twitter_credentials.yaml``` with your own credentials

```
TwitterCredentials:

    Consumer:
        consumer_key: 'your_consumer_key'
        consumer_secret: 'your_consumer_secret'
    
    Access:
        access_token: 'your_access_token'
        access_secret: 'your_access_secret'
```
#### Stream tweets & run the web server

- stream tweets:
```
(myenv)$ python tweet_stream.py &
```
- run the web server:
```
(myenv)$ python app.py
```