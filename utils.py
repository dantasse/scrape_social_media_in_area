#!/usr/bin/env python

# Utilities for working with Twitter.

import csv, collections, datetime, pytz, ppygis

month_map = {'Jan': 1, 'Feb': 2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 
    'Aug':8,  'Sep': 9, 'Oct':10, 'Nov': 11, 'Dec': 12}
# Special case date parsing. All our dates are like this:
# Wed Jan 22 23:19:19 +0000 2014
# 012345678901234567890123456789
# so let's just parse them like that. 
def parse_date(d):
    return datetime.datetime(int(d[26:30]), month_map[d[4:7]], int(d[8:10]),\
        int(d[11:13]), int(d[14:16]), int(d[17:19]), 0, pytz.timezone('UTC')) # 0=usec

CITY_LOCATIONS = {
    'pgh':  { 'locations': '-80.2,40.241667,-79.8,40.641667' },
    'pgh_all':  { 'locations': '-80.2,40.241667,-79.8,40.641667' },
    'sf':   { 'locations': '-122.5950,37.565,-122.295,37.865' },
    'ny':   { 'locations': '-74.03095193,40.6815699768,-73.9130315074,40.8343765254' },
    'houston': { 'locations': '-95.592778, 29.550556, -95.138056, 29.958333' },
    'detroit': { 'locations': '-83.2458, 42.1314, -82.8458, 42.5314' },
    'chicago': { 'locations': '-87.9847, 41.6369, -87.5186, 42.0369' },
    'cleveland': { 'locations': '-81.9697, 41.1822, -81.4697, 41.5822' },
    'seattle': { 'locations': '-122.5331, 47.4097, -121.9331, 47.8097' },
    'miami': { 'locations': '-80.4241, 25.5877, -80.0641, 26.2877' },
    'london': { 'locations': '-0.4275, 51.3072, 0.2525, 51.7072' },
    'minneapolis': { 'locations': '-93.465, 44.7778, -93.065, 45.1778' },
    'austin': {'locations': '-97.95, 30.05, -97.55, 30.45'},
    'sanantonio': {'locations': '-98.7, 29.21667, -98.3, 29.61667'},
    'dallas': {'locations': '-96.996667, 32.575833, -96.596667, 32.975833'},
    'whitehouse': {'locations': '-77.038, 38.8965, -77.035, 38.8985'},
    'oakland': {'locations': '-122.35, 37.708, -122.18, 37.85'},
}

# Argument: a tweet JSON object and a table string name to insert into.
# Returns: a string starting with "INSERT..." that you can run to insert this
# tweet into a Postgres database.
def tweet_to_insert_string(tweet, table, psql_cursor):
    if tweet['coordinates'] is not None:
        lat = tweet['coordinates']['coordinates'][1]
        lon = tweet['coordinates']['coordinates'][0]
    else:
        lat = lon = 0
    coordinates = ppygis.Point(lon, lat, srid=4326)
    created_at = parse_date(tweet['created_at'])
    hstore_user = make_hstore(tweet['user'])
    hstore_place = make_hstore(tweet['place'])
    hstore_entities = make_hstore(tweet['entities'])

    # Sometimes there's no lang, or filter_level. Not sure why. Fix it I guess?
    if 'filter_level' not in tweet:
        tweet['filter_level'] = ''
    if 'lang' not in tweet:
        tweet['lang'] = ''

    insert_str = psql_cursor.mogrify("INSERT INTO " + table + "(contributors, " +
            "coordinates, created_at, entities, favorite_count, filter_level, " +
            "lang, id, id_str, in_reply_to_screen_name, in_reply_to_status_id, " +
            "in_reply_to_status_id_str, in_reply_to_user_id, in_reply_to_user_id_str, " +
            "place, retweet_count, source, twitter_user, text, user_screen_name) " +
            "VALUES (" + ','.join(['%s' for key in twitter_data_types]) + ")",
        (tweet['contributors'], coordinates, created_at, hstore_entities, tweet['favorite_count'],
        tweet['filter_level'], tweet['lang'], tweet['id'], tweet['id_str'],
        tweet['in_reply_to_screen_name'], tweet['in_reply_to_status_id'],
        tweet['in_reply_to_status_id_str'], tweet['in_reply_to_user_id'],
        tweet['in_reply_to_user_id_str'], hstore_place, tweet['retweet_count'],
        tweet['source'], hstore_user, tweet['text'],
        tweet['user']['screen_name']))
    return insert_str

# Map of field name -> postgres datatype. Contains everything we want to save.
# TODO: if you change this, also change the tweet_to_insert_string method below.
twitter_data_types = {
    'contributors': 'text',
    'coordinates': 'Point',
    'created_at': 'timestamp',
    'entities': 'hstore', 
    'favorite_count': 'integer',
    # |favorited| only makes sense if there's an authenticated user.
    'filter_level': 'text',
    # geo skipped, b/c it's deprecated
    'lang': 'text',
    'id': 'bigint primary key',
    'id_str': 'text',
    'in_reply_to_screen_name': 'text',
    'in_reply_to_status_id': 'bigint',
    'in_reply_to_status_id_str': 'text',
    'in_reply_to_user_id': 'bigint',
    'in_reply_to_user_id_str': 'text',
    'place': 'hstore',
    'retweet_count': 'integer',
    # |retweeted| only make sense if there's an authenticated user.
    'source': 'text',
    'text': 'text NOT NULL',
    # |truncated| is obsolete; Twitter now rejects long tweets instead of truncating.
    'twitter_user': 'hstore', # was |user| in Twitter API.
    'user_screen_name': 'text NOT NULL', # added this
}

# Argument: a python dictionary. Returns: the same thing with all keys and
# values as strings, so we can make a postgres hstore with them.
def make_hstore(py_dict):
    if not py_dict:
        py_dict={}
    return {unicode(k): unicode(v) for k, v in py_dict.iteritems()}


# Map of field name -> postgres datatype. Contains everything we want to save.
# TODO: if you change this, also change the instagram_to_insert_string method below.
instagram_data_types = {
    # |attribution| dropped
    'caption_from_username': 'text',
    'caption_id': 'bigint',
    'caption_text': 'text', # ignoring the rest of the caption
    'comments_count': 'integer', # ignoring the contents of the comments
    'created_time': 'timestamp',
    'filter': 'text',
    'id': 'text primary key', # copied from mongo instagram
    'image_standard_res_url': 'text', # ignoring the rest of the image
    'likes_count': 'integer', # ignoring who the likes are from
    'link': 'text',
    'location': 'Point',
    'tags': 'text[]', # hashtags.
    'type': 'text',
    'instagram_user': 'hstore', # was |user| in Instagram API.
    'user_username': 'text NOT NULL', # added this, redundant with instagram_user
    'user_id': 'bigint', # added this, redundant with instagram_user
    # ignoring users_in_photo
}


# Argument: an instagram JSON object and a collection string name to insert into.
# Returns: a string starting with "INSERT..." that you can run to insert this
# instagram into a Postgres database.
def instagram_to_insert_string(instagram, collection, psql_cursor):
    if instagram['caption'] != None:
        caption_from_username = instagram['caption']['from']['username']
        caption_id = int(instagram['caption']['id'])
        caption_text = instagram['caption']['text']
    else:
        caption_from_username = caption_id = caption_text = None
    comments_count = instagram['comments']['count']
    created_time = datetime.datetime.fromtimestamp(int(instagram['created_time']))

    filter = instagram['filter']
    id = instagram['_id']
    image_standard_res_url = instagram['images']['standard_resolution']['url']
    likes_count = instagram['likes']['count']
    link = instagram['link']

    lat = float(instagram['location']['latitude'])
    lon = float(instagram['location']['longitude'])
    location = ppygis.Point(lon, lat, srid=4326)

    tags = instagram['tags']
    type = instagram['type']
    instagram_user = make_hstore(instagram['user'])
    user_username = instagram['user']['username']
    user_id = int(instagram['user']['id'])

    insert_str = psql_cursor.mogrify("INSERT INTO " + collection + "(caption_from_username," +
            "caption_id, caption_text, comments_count, created_time, filter, id," +
            "image_standard_res_url, likes_count, link, location, tags, type," +
            "instagram_user, user_username, user_id) " +
            "VALUES (" + ','.join(['%s' for key in instagram_data_types]) + ")", 
        (caption_from_username, caption_id, caption_text, comments_count,
        created_time, filter, id, image_standard_res_url, likes_count, link,
        location, tags, type, instagram_user, user_username, user_id))
    return insert_str

