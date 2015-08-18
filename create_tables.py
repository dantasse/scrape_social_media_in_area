#!/usr/bin/env python

# Just create the database and tables that we need to collect twitter data.
# Before doing this you have to:
#   create the database (CREATE DATABASE tweet)
#   run CREATE EXTENSION hstore; in the database.
#   run CREATE EXTENSION postgis; too.

import argparse, psycopg2, psycopg2.extensions, psycopg2.extras, ppygis

# Map of field name -> postgres datatype. Contains everything we want to save.
# TODO: if you change this, also change the tweet_to_insert_string method in
# scrape_twitter_in_area.py.
data_types = {
    'contributors': 'text', # TODO does this work?
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

def create_table(table_name, pg_cur, psql_conn):
    pg_cur.execute("DROP TABLE IF EXISTS " + table_name + ";")
    psql_conn.commit()
    create_table_str = "create table " + table_name + "("
    for key, value in sorted(data_types.iteritems()):
        if key not in ['coordinates']: # create that coords column separately.
            create_table_str += key + ' ' + value + ', '
    create_table_str = create_table_str[:-2] + ");"

    pg_cur.execute(create_table_str)
    psql_conn.commit()
    pg_cur.execute("select addgeometrycolumn('" + table_name + "', 'coordinates', 4326, 'point', 2)")
    psql_conn.commit()

def create_indices(table_name, pg_cur, psql_conn):
    create_index_str = 'CREATE INDEX %s_user_screen_name_match ON %s USING HASH(user_screen_name);' % (table_name, table_name)
    vacuum_str = 'VACUUM ANALYZE %s;' % table_name
    psql_conn.set_isolation_level(0) # so we can VACUUM outside a transaction
    pg_cur.execute(create_index_str)
    pg_cur.execute(vacuum_str)
    coordinates_geo_index_str = 'CREATE INDEX %s_coordinates_geo ON %s USING GIST(coordinates);' % (table_name, table_name)
    pg_cur.execute(coordinates_geo_index_str)
    pg_cur.execute(vacuum_str)
    psql_conn.set_isolation_level(1)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--create_all', action='store_true')
    parser.add_argument('--table_name')
    parser.add_argument('--db_name', default='tweet')
    args = parser.parse_args()

    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
    psql_conn = psycopg2.connect("dbname='%s'" % args.db_name)
    psycopg2.extras.register_hstore(psql_conn)
    pg_cur = psql_conn.cursor()

    TABLE_NAMES=['tweet_austin', 'tweet_chicago', 'tweet_cleveland',
        'tweet_dallas', 'tweet_detroit', 'tweet_houston', 'tweet_london',
        'tweet_miami', 'tweet_minneapolis', 'tweet_ny', 'tweet_pgh',
        'tweet_sanantonio', 'tweet_seattle', 'tweet_sf', 'tweet_whitehouse']

    if args.create_all:
        print "About to dump and recreate all tables: %s. Enter to continue, Ctrl-C to quit." % str(TABLE_NAMES)
        raw_input()
        print "Are you sure? I mean, seriously, you're about to DROP ALL THE TABLES. I mean, you'll lose all the data that's in there. You better be pretty sure. Type 'Yes I am sure' here to continue."
        text = raw_input()
        if text != 'Yes I am sure':
            print "Ok, seems like you\'re not sure. Doing nothing. Whew! Disaster averted."
            exit(0)
        for table_name in TABLE_NAMES:
            create_table(table_name, pg_cur, psql_conn)
            print "Done creating table, now creating indices"
            create_indices(table_name, pg_cur, psql_conn)
            print "Done creating indices"

    elif args.table_name:
        print "About to dump and recreate %s. Enter to continue, Ctrl-C to quit." % args.table_name
        raw_input()
        create_table(args.table_name, pg_cur, psql_conn)
        print "Done creating table, now creating indices"
        create_indices(args.table_name, pg_cur, psql_conn)
        print "Done creating indices"
    else:
        print "No options selected, doing nothing."
