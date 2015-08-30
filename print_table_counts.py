#!/usr/bin/env python

# Outputs a one-row count of approx how many things are in the DB, just like 
# the old monitoring on MongoDB used to.

import psycopg2, datetime

psql_conn = psycopg2.connect("dbname='tweet'")
pg_cur = psql_conn.cursor()

pg_cur.execute("SELECT relname,n_live_tup FROM pg_stat_user_tables;");
relnames_counts = {k: v for (k, v) in pg_cur.fetchall()}
relnames_in_order = ['tweet_pgh','tweet_sf','tweet_ny','tweet_houston','tweet_cleveland','tweet_seattle','tweet_miami','tweet_detroit','tweet_chicago','tweet_london','tweet_minneapolis','tweet_austin', 'tweet_dallas', 'tweet_sanantonio', 'instagram_pgh']

#Thu Jan 23 2014 00:00:00 GMT+0000 (UTC)
date = datetime.datetime.now().strftime('%a %b %d %Y %X GMT+0000 (UTC)')

row = ','.join([date] + [str(relnames_counts[r]) for r in relnames_in_order if r in relnames_in_order])
print row
