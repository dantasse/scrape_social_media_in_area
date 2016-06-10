#!/usr/bin/env python

# Emails us if we haven't received any Tweets, Instagrams, or Flickrs in a day.
# Email addresses (from and to) given in config.txt.

import smtplib, json, ConfigParser, psycopg2

config = ConfigParser.ConfigParser()
config.read('config.txt')

FROM_EMAIL = config.get('error_handling', 'email')
TO_EMAILS = config.get('error_handling_to_addr', 'email').split(',')
PSWD = config.get('error_handling', 'password')

COUNT_FILENAME = 'data_counts.json'

psql_conn = psycopg2.connect("dbname='tweet'")
pg_cur = psql_conn.cursor()

# COLLECTIONS: db -> collection list
COLLECTIONS = {
    'tweet' : [ 'tweet_pgh',
                'tweet_sf', 
                'tweet_ny',
                'tweet_houston',
                'tweet_detroit',
                'tweet_chicago',
                'tweet_cleveland',
                'tweet_seattle',
                'tweet_miami',
                'tweet_london',
                'tweet_minneapolis',
                'tweet_austin',
                'tweet_sanantonio',
                'tweet_dallas'], #TODO put the foursquares back in?
                # 'foursquare_pgh',
                # 'foursquare_ny',
                # 'foursquare_sf',
                # 'foursquare_houston',
                # 'foursquare_detroit',
                # 'foursquare_chicago',
                # 'foursquare_cleveland',
                # 'foursquare_seattle',
                # 'foursquare_miami',
                # 'foursquare_london' ],
    'instagram' : [ 'instagram_pgh' ],
    'flickr' : [ 'flickr_pgh' ]
}

# This actually sends an email.
def email_error(data_name, prev_count, current_count):
    s = smtplib.SMTP('smtp.gmail.com', 587)  
    s.ehlo()
    s.starttls()
    s.ehlo
    s.login(FROM_EMAIL, PSWD)

    headers = ["from: " + FROM_EMAIL,
               "subject: Error: stopped collecting " + data_name + " data",
               "to: " + ', '.join(TO_EMAILS),
               "mime-version: 1.0",
               "content-type: text/html"]
    headers = "\r\n".join(headers)
    body = "Data collection seems to be not working. \r\n\r\n" \
           + "Data: " + data_name + "\r\n\r\n" \
           + "Previous count: " + str(prev_count) + "\r\n\r\n" \
           + "Current count: " + str(current_count)

    s.sendmail(FROM_EMAIL, TO_EMAILS, headers + "\r\n\r\n" + body)
    s.quit()
    return

# Returns true iff the count from this column is the same as the last time
# we ran this script.
def data_not_updated(data_name):
    return prev_counts.get(data_name) \
        and current_counts.get(data_name) \
        and prev_counts.get(data_name) >= current_counts.get(data_name)

if __name__ == '__main__':

    current_counts = {}
    for db in ['tweet'] # formerly instagram and flickr too
        cols = COLLECTIONS[db]
        for col in cols:
            # print "Counting table: " + str(col)
            pg_cur.execute("SELECT COUNT(*) FROM " + col + ";")
            # ^^ This is bad, don't combine strings like this. In this case I
            # know it's safe because I created |col|.
            current_counts[col] = pg_cur.fetchone()[0]

    # if file does not exist, make one.
    try:
        f = open(COUNT_FILENAME, 'r')
        prev_counts = json.load(f)
        f.close()
    except:
        prev_counts = {}
        for db in COLLECTIONS:
            cols = COLLECTIONS[db]
            for col in cols:
                prev_counts[col] = 0

        f = open(COUNT_FILENAME, 'w')
        f.write(json.dumps(prev_counts))
        f.close()

    # print "Previous Counts: %s" % str(prev_counts)
    # print "Current Counts: %s" % str(current_counts)
    # Check each collection, send an email if it's not updated.
    for db in ['tweet', 'instagram']: # TODO add flickr
        cols = COLLECTIONS[db]
        for col in cols:
            if data_not_updated(col):
                email_error(col, prev_counts[col], current_counts[col])
                del current_counts[col]

    with open(COUNT_FILENAME, 'w') as f:
        # update only the counts that increased
        for k in prev_counts:
            if k in current_counts:
                prev_counts[k] = current_counts[k]
        for k in current_counts:
            if k not in prev_counts:
                prev_counts[k] = current_counts[k]
        f.write(json.dumps(prev_counts))

