#!/usr/bin/env python

# Just create the database and tables that we need to collect twitter data.
# Before doing this you have to:
#   create the database (CREATE DATABASE tweet)
#   run CREATE EXTENSION hstore; in the database.
#   run CREATE EXTENSION postgis; too.

import argparse, psycopg2, psycopg2.extensions, psycopg2.extras, ppygis
import utils

def create_tweet_table(table_name, pg_cur, psql_conn):
    pg_cur.execute("DROP TABLE IF EXISTS " + table_name + ";")
    psql_conn.commit()
    create_table_str = "create table " + table_name + "("
    for key, value in sorted(utils.twitter_data_types.iteritems()):
        if key not in ['coordinates']: # create that coords column separately.
            create_table_str += key + ' ' + value + ', '
    create_table_str = create_table_str[:-2] + ");"

    pg_cur.execute(create_table_str)
    psql_conn.commit()
    pg_cur.execute("select addgeometrycolumn('" + table_name + "', 'coordinates', 4326, 'point', 2)")
    psql_conn.commit()

def create_instagram_table(table_name, pg_cur, psql_conn):
    pg_cur.execute("DROP TABLE IF EXISTS " + table_name + ";")
    psql_conn.commit()
    create_table_str = "create table " + table_name + "("
    for key, value in sorted(utils.instagram_data_types.iteritems()):
        if key not in ['coordinates']: # create that coords column separately.
            create_table_str += key + ' ' + value + ', '
    create_table_str = create_table_str[:-2] + ");"

    pg_cur.execute(create_table_str)
    psql_conn.commit()
    pg_cur.execute("select addgeometrycolumn('" + table_name + "', 'coordinates', 4326, 'point', 2)")
    psql_conn.commit()

# Creates an index on the |coordinates| field. Also, if the table name starts
# with 'tweet_', creates an index on the user_screen_name field.
def create_indices(table_name, pg_cur, psql_conn):
    vacuum_str = 'VACUUM ANALYZE %s;' % table_name
    psql_conn.set_isolation_level(0) # so we can VACUUM outside a transaction
    if table_name.startswith('tweet_'):
        create_index_str = 'CREATE INDEX %s_user_screen_name_match ON %s USING HASH(user_screen_name);' % (table_name, table_name)
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

    TWEET_TABLE_NAMES = ['tweet_' + city for city in utils.CITY_LOCATIONS.keys()]
    IG_TABLE_NAMES = ['instagram_pgh'] # TODO update if we get more cities

    if args.create_all:
        print "About to dump and recreate all tables: %s. Enter to continue, Ctrl-C to quit." % str(TWEET_TABLE_NAMES + IG_TABLE_NAMES)
        raw_input()
        print "Are you sure? I mean, seriously, you're about to DROP ALL THE TABLES. I mean, you'll lose all the data that's in there. You better be pretty sure. Type 'Yes I am sure' here to continue."
        text = raw_input()
        if text != 'Yes I am sure':
            print "Ok, seems like you\'re not sure. Doing nothing. Whew! Disaster averted."
            exit(0)
        for table_name in TWEET_TABLE_NAMES:
            print "Creating: " + str(table_name)
            create_tweet_table(table_name, pg_cur, psql_conn)
            print "Done creating table, now creating indices"
            create_indices(table_name, pg_cur, psql_conn)
            print "Done creating indices"
        for table_name in INSTAGRAM_TABLE_NAMES:
            print "Creating: " + str(table_name)
            create_instagram_table(table_name, pg_cur, psql_conn)
            print "Done creating table, now creating indices"
            create_indices(table_name, pg_cur, psql_conn)
            print "Done creating indices"

    elif args.table_name:
        print "About to dump and recreate %s. Enter to continue, Ctrl-C to quit." % args.table_name
        raw_input()
        print "Creating: " + str(args.table_name)
        if args.table_name.startswith('tweet_'):
            create_tweet_table(args.table_name, pg_cur, psql_conn)
        elif args.table_name.startswith('instagram_'):
            create_instagram_table(args.table_name, pg_cur, psql_conn)
        else:
            print "We can only create tweet or instagram tables now. Doing nothing."
            exit(1)
        print "Done creating table, now creating indices"
        create_indices(args.table_name, pg_cur, psql_conn)
        print "Done creating indices"
    else:
        print "No options selected, doing nothing. Try --create_all or --table_name"
