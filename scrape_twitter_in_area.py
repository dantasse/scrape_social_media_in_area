#!/usr/bin/env python

# Gets data from the twitter API in a given region.

import argparse, random, ConfigParser, os, time, datetime, pytz, traceback, json
import psycopg2, psycopg2.extensions, psycopg2.extras, ast, time, utwils
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

class MyStreamer(TwythonStreamer):
    psql_connection = None
    psql_cursor = None
    psql_table = None
    city_name = ''
    oauth_keys = {}
 
    # c = consumer, at = access_token
    def __init__(self, oauth_keys, psql_conn, city_name):
        self.oauth_keys = oauth_keys
        self.psql_connection = psql_conn
        self.city_name = city_name

        keys_to_use_index = random.randint(0, len(oauth_keys)-1)
        print "Connecting with keys: " + str(keys_to_use_index)
        keys_to_use = oauth_keys[keys_to_use_index]
        TwythonStreamer.__init__(self,
            keys_to_use['consumer_key'], keys_to_use['consumer_secret'],
            keys_to_use['access_token_key'], keys_to_use['access_token_secret'])
        
        self.psql_cursor = self.psql_connection.cursor()
        self.psql_table = 'tweet_' + city_name
        psycopg2.extras.register_hstore(self.psql_connection)
        self.min_lon, self.min_lat, self.max_lon, self.max_lat =\
            [float(s.strip()) for s in utwils.CITY_LOCATIONS[city_name]['locations'].split(',')]

    def on_success(self, data):
        str_data = str(data)
        message = ast.literal_eval(str_data)
        if message.get('limit'):
            log('Rate limiting caused us to miss %s tweets' % (message['limit'].get('track')))
        elif message.get('disconnect'):
            raise Exception('Got disconnect: %s' % message['disconnect'].get('reason'))
        elif message.get('warning'):
            log('Got warning: %s' % message['warning'].get('message'))
        elif message['coordinates'] == None:
            pass # message with no actual coordinates, just a bounding box
        else:
            # Check to make sure the point is actually in the bbox.
            lon = message['coordinates']['coordinates'][0]
            lat = message['coordinates']['coordinates'][1]
            if lon >= self.min_lon and lon <= self.max_lon and \
                    lat >= self.min_lat and lat <= self.max_lat:
                self.save_to_postgres(dict(message))
                print 'Got tweet: %s' % message.get('text').encode('utf-8')
                # TODO save foursquare data to its own table
                # self.save_foursquare_data_if_present(message)


    def on_error(self, status_code, data):
        print "Error: " + str(status_code)
        print data
        if status_code == 420: # "Enhance your calm" aka rate-limit
            print "Rate limit, will try again."
            time.sleep(3)
        self.disconnect() 

    # Given a tweet from the Twitter API, saves it to Postgres DB table |table|.
    def save_to_postgres(self, tweet):
        insert_str = utwils.tweet_to_insert_string(tweet, self.psql_table, self.psql_cursor)
        try:
            self.psql_cursor.execute(insert_str)
            self.psql_connection.commit()
       
        except Exception as e:
            print "Error running this command: %s" % insert_str
            traceback.print_exc()
            traceback.print_stack()
            self.psql_connection.rollback() # just ignore the error
            # because, whatever, we miss one tweet

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', required=True, choices=utwils.CITY_LOCATIONS.keys())
    args = parser.parse_args()

    psql_conn = psycopg2.connect("dbname='tweet'")

    sleep_time = 0
    while True:
        stream = MyStreamer(OAUTH_KEYS, psql_conn, args.city)
        stream.statuses.filter(locations=utwils.CITY_LOCATIONS[args.city]['locations'])
        print "Sleeping for %d seconds." % sleep_time
        time.sleep(sleep_time)
        sleep_time += 1
