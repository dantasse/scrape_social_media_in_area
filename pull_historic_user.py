#!/usr/bin/env python

# Gets data from the twitter API in a given region.

import argparse, random, ConfigParser, os, time, datetime, pytz, traceback, json
import psycopg2, psycopg2.extensions, psycopg2.extras, ast, time, utils, httplib
from collections import defaultdict
import sys
from twython import Twython
import twython.exceptions

config = ConfigParser.ConfigParser()
config.read('config.txt')

OAUTH_KEYS = [{'consumer_key': config.get('twitter-' + str(i), 'consumer_key'),
              'consumer_secret': config.get('twitter-' + str(i), 'consumer_secret'),
              'access_token_key': config.get('twitter-' + str(i), 'access_token_key'),
              'access_token_secret': config.get('twitter-' + str(i), 'access_token_secret')}
             for i in range(int(config.get('num_twitter_credentials', 'num')))]

def connect_to_twitter(oauth_keys):
    connected = False;
    twitter = {}
    while not connected:
        try:
            keys_to_use_index = random.randint(0, len(oauth_keys)-1)
            keys_to_use = oauth_keys[keys_to_use_index]
            twitter = Twython(keys_to_use['consumer_key'], keys_to_use['consumer_secret'],
                          keys_to_use['access_token_key'], keys_to_use['access_token_secret'])
            twitter.verify_credentials()
        except:
            print "couldn't authenticate"
            sys.exit(0)
        
        else:
            connected = True
    return twitter


def save_to_postgres(tweet, table, connection, cursor):
    if 'coordinates' not in tweet or tweet['coordinates'] == None or 'coordinates' not in tweet['coordinates']:
        tweet['coordinates'] = {'coordinates': [-999, -999]}
    insert_str = utils.tweet_to_insert_string(tweet, table, cursor)
    try:
        cursor.execute(insert_str)
        connection.commit()
   
    except Exception as e:
        print "Error running this command: %s" % insert_str
        traceback.print_exc()
        traceback.print_stack()
        connection.rollback() # just ignore the error
        # because, whatever, we miss one tweet

def get_min_id(screen_name, table, connection, cursor):
    # SELECT id FROM pgh311 WHERE user_screen_name == pgh311 ORDER BY id ASC

    cursor.execute("SELECT id FROM "+str(table)+" WHERE user_screen_name LIKE '"+str(screen_name)+"' ORDER BY id ASC")
    results = cursor.fetchone()   
    if(results and results[0]):
        return results[0] - 1
    else:
        return False

def checkIfAlreadyHaveTweet(cursor, table, id):
    #SELECT count(*) FROM pgh311 WHERE id = 577870288752283649
    cursor.execute("SELECT count(*) FROM "+ table +" WHERE id = "+str(id)+"")
    results = cursor.fetchone()
    if(results[0] and results[0] > 0):
        return True
    else:
        return False
    
def saveSectionOfTweets(twython, screen_name, table, conn, cursor, include_replies=False):
    min_id_of_currently_saved_tweets =  get_min_id(screen_name, table, conn, cursor)
    if min_id_of_currently_saved_tweets:
        tweets = twython.get_user_timeline(screen_name=args.screen_name, count=200, max_id=min_id_of_currently_saved_tweets)
    else: 
        tweets = twython.get_user_timeline(screen_name=args.screen_name, count=200)
    
    
    if(len(tweets) == 0):
        return False
    for tweet in tweets:
        print 'saving tweet: ' + tweet['text']
        save_to_postgres(tweet, table, conn, cursor)
        if(include_replies and tweet['in_reply_to_status_id_str'] and not checkIfAlreadyHaveTweet(cursor, table, tweet['in_reply_to_status_id_str'])):
           replyTweet = getTweetBasedOnId(twython, tweet['in_reply_to_status_id_str'])
           if(replyTweet):
                print 'saving reply: ' + str(replyTweet['text'].encode('utf-16'))
                save_to_postgres(replyTweet, table, conn, cursor)
    return True

def getTweetBasedOnId(twython_conn, id):
    def tryTweet():
        try:
            tweet = twython_conn.show_status(id=id)
        except twython.TwythonRateLimitError:
            return "rate"
        except twython.TwythonError:
            return "pass"
        return tweet
            
    foundTweet = False
    tweet = {}
    while(not foundTweet):
        print "trying to get tweet"
        returnVal = tryTweet()
        if(returnVal is "pass"):
            print "Something else went wrong. Continuing on"
            tweet = {}
            foundTweet = True
        elif(returnVal is "rate"):
            print "over rate limit. Waiting for a few minutes"
            time.sleep(60*5)
            foundTweet = False
        else:
            print "Found tweet"
            time.sleep(1)
            tweet = returnVal
            foundTweet = True
    return tweet
   
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--screen_name', required=True)
    parser.add_argument('--include_responses', default='false')
    parser.add_argument('--table', required=True)
    parser.add_argument('--max_requests', default='10')
    args = parser.parse_args()

    psql_conn = psycopg2.connect("dbname='tweet'")
    psql_cursor = psql_conn.cursor()
    psql_table = args.table
    psycopg2.extras.register_hstore(psql_conn)
    twython_connection = connect_to_twitter(OAUTH_KEYS)
    
    moreTweetsToFind = True
    
    while(moreTweetsToFind):
        moreTweetsToFind = saveSectionOfTweets(twython_connection, args.screen_name, args.table, psql_conn, psql_cursor, True)
        
   
