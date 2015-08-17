#!/usr/bin/env python

# Every so often (TBD), takes a food, messes its name up, grabs an image of
# that food, and makes a meme with the misspelled word, posts it to Twitter.

import argparse, random, ConfigParser, os, time, datetime
from collections import defaultdict
from twython import TwythonStreamer
import twython.exceptions

config = ConfigParser.ConfigParser()
config.read('config.txt')

OAUTH_KEYS = [{'consumer_key': config.get('twitter-' + str(i), 'consumer_key'),
              'consumer_secret': config.get('twitter-' + str(i), 'consumer_secret'),
              'access_token_key': config.get('twitter-' + str(i), 'access_token_key'),
              'access_token_secret': config.get('twitter-' + str(i), 'access_token_secret')}
             for i in range(int(config.get('num_twitter_credentials', 'num')))]

CITY_LOCATIONS = {
    'pgh':  { 'locations': '-80.2,40.241667,-79.8,40.641667' },
    'sf':   { 'locations': '-122.5950,37.565,-122.295,37.865' },
    'ny':   { 'locations': '-74.03095193,40.6815699768,-73.9130315074,40.8343765254' },
    'houston': { 'locations': '-95.592778, 29.550556, -95.138056, 29.958333' },
    'detroit': { 'locations': '-83.2458, 42.1314, -82.8458, 42.5314' },
    'chicago': { 'locations': '-87.9847, 41.6369, -87.5847, 42.0369' },
    'cleveland': { 'locations': '-81.9697, 41.1822, -81.4697, 41.5822' },
    'seattle': { 'locations': '-122.5331, 47.4097, -121.9331, 47.8097' },
    'miami': { 'locations': '-80.4241, 25.5877, -80.0641, 26.2877' },
    'london': { 'locations': '-0.4275, 51.3072, 0.2525, 51.7072' },
    'minneapolis': { 'locations': '-93.465, 44.7778, -93.065, 45.1778' },
    'austin': {'locations': '-97.95, 30.05, -97.55, 30.45'},
    'sanantonio': {'locations': '-98.7, 29.21667, -98.3, 29.61667'},
    'dallas': {'locations': '-96.996667, 32.575833, -96.596667, 32.975833'},
    'whitehouse': {'locations': '-77.038, 38.8965, -77.035, 38.8985'},
}

class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            print data['text'].encode('utf-8')

    def on_error(self, status_code, data):
        print status_code

def post_tweet(image, fud):
    # TODO update this to use upload_media and then a separate post instead.
    twitter.update_status_with_media(media=image_io, status='')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--foods_file', default='foods.txt')
    args = parser.parse_args()

 
    keys = OAUTH_KEYS[0]
    # twitter = Twython(keys['consumer_key'], keys['consumer_secret'],
    #     keys['access_token_key'], keys['access_token_secret'])
    # twitter.verify_credentials()

    stream = MyStreamer(keys['consumer_key'], keys['consumer_secret'],
        keys['access_token_key'], keys['access_token_secret'])
    stream.statuses.filter(locations=[-122.75,36.8,-121.75,37.8])
