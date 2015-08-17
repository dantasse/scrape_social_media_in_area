#!/usr/bin/env python

# Every so often (TBD), takes a food, messes its name up, grabs an image of
# that food, and makes a meme with the misspelled word, posts it to Twitter.

import argparse, random, ConfigParser, os, time, datetime
from collections import defaultdict
from twython import Twython
import twython.exceptions

config = ConfigParser.ConfigParser()
config.read('config.txt')
POST_URL = 'https://api.twitter.com/1.1/statuses/update.json'
OAUTH_KEYS = [{'consumer_key': config.get('twitter-' + str(i), 'consumer_key'),
              'consumer_secret': config.get('twitter-' + str(i), 'consumer_secret'),
              'access_token_key': config.get('twitter-' + str(i), 'access_token_key'),
              'access_token_secret': config.get('twitter-' + str(i), 'access_token_secret')}
             for i in range(int(config.get('num_twitter_credentials', 'num')))]


def post_tweet(image, fud):
    # TODO update this to use upload_media and then a separate post instead.
    twitter.update_status_with_media(media=image_io, status='')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--foods_file', default='foods.txt')
    args = parser.parse_args()

 
    keys = OAUTH_KEYS[0]
    twitter = Twython(keys['consumer_key'], keys['consumer_secret'],
        keys['access_token_key'], keys['access_token_secret'])


