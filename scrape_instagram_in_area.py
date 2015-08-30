#!/usr/bin/env python

# Instagram scraper
# Tries to get all the photos/videos in the Pittsburgh area.
# TODO: generalize this to take an arbitrary area

import requests, json, time, sys, ConfigParser, traceback
import utwils, psycopg2, psycopg2.extensions, psycopg2.extras

# coordinates in Twitter scraper: lower left (40.241667, -80.2),
# upper right (40.641667, -79.8)

# these are a bunch of points that form a hexagon that covers most of where
# people live around Pittsburgh. Roughly corresponds to the .2 degrees lat and
# long around Pittsburgh. made kinda ad hoc with:
# http://www.freemaptools.com/radius-around-point.htm
points = [\
(40.44276659332212,-80.01205444335938),\
(40.32011119146361,-80.11590957641602),\
(40.421860362045166,-79.85309600830078),\
(40.487692978918865,-79.90116119384766),\
(40.48821520200259,-80.0137710571289),\
(40.484037303554615,-80.12020111083984),\
(40.53258931069557,-80.1229476928711),\
(40.53832969648848,-80.0137710571289),\
(40.53415491923227,-79.90596771240234),\
(40.44485685896176,-80.06732940673828),\
(40.457397087754444,-80.17341613769531),\
(40.386304853509046,-80.1229476928711),\
(40.38839687388361,-80.01514434814453),\
(40.382643661497255,-79.90802764892578),\
(40.32351403031128,-79.96639251708984),\
(40.324037528756165,-80.07007598876953),\
(40.44485685896176,-80.12260437011719),\
(40.44276659332212,-79.90562438964844),\
(40.50440210202652,-79.95780944824219),\
(40.506490449822046,-80.06904602050781),\
(40.50753459933616,-79.84794616699219),\
(40.43649540640561,-79.79850769042969),\
(40.37688995771412,-79.85618591308594),\
(40.37793612222415,-79.96055603027344),\
(40.383166701110994,-80.06767272949219),\
(40.318278822577945,-80.01960754394531),\
(40.317231732315236,-79.90837097167969),\
(40.567024247788396,-80.01411437988281),\
(40.56598102500835,-79.90562438964844),\
(40.575369444618396,-80.11573791503906),\
(40.50335790374529,-80.17341613769531),\
(40.43858586704328,-80.22834777832031),\
(40.3810745182893,-80.16654968261719),\
(40.32011119146361,-80.11590957641602)]

config = ConfigParser.ConfigParser()
config.read('config.txt')

# don't check in the client_secret
payload = {'client_id': config.get('instagram', 'client_id'),
        'client_secret': config.get('instagram', 'client_secret'),
        'object': 'geography',
        'aspect': 'media',
        'radius': '5000'}

# set up the Postgres connection.
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
psql_conn = psycopg2.connect("dbname='tweet'")
psycopg2.extras.register_hstore(psql_conn)
pg_cur = psql_conn.cursor()

curr_point_num = 0
# ID of each photo/video we've seen already.
media_seen = []

timestamp = time.time()
# errFile = open('instagram_error_%d.log'%(timestamp), 'w')
# outFile = open('instagram_output_%d.log'%(timestamp), 'w')
# sys.stdout = outFile
# sys.stderr = errFile
    

# iterate through all the points, querying them in order.
while True:
    try:
        # set latitude and longitude of query for current point
        curr_point = points[curr_point_num]
        payload['lat'] = str(curr_point[0])
        payload['lng'] = str(curr_point[1])
        # only take the last 30 min.
        payload['min_timestamp'] = int(time.time() - 18000)
        
        # print "Searching around: %s, %s since %s" % (payload['lat'], payload['lng'], payload['min_timestamp'])
        r = requests.get('https://api.instagram.com/v1/media/search', params=payload)
        if r.status_code != 200:
            time.sleep(5)
            print 'Request not OK. Code: %d. Reason: %s' % (r.status_code, r.text)
            continue

        print 'For point %s, %s, this many photos: %d' % (payload['lat'], payload['lng'], len(r.json()['data']))
        for media in r.json()['data']:
            id = media['id']
            if id not in media_seen:
                # Rename id to _id b/c that's what load_instagrams_into_postgres takes
                media['_id'] = id
                del media['id']
                insert_str = utwils.instagram_to_insert_string(media, 'instagram_pgh')
                try:
                    pg_cur.execute(insert_str)
                    psql_conn.commit()
                except Exception as e:
                    print "Error running this command: %s" % insert_str
                    traceback.print_exc()
                    traceback.print_stack()
                    psql_conn.commit()

                media_seen.append(id)
        time.sleep(5)
        # one request every 5 sec = ~720/hr, well under 5000 rate limit
        # and if we have 34 points, that means each one gets polled every ~170 sec
        # (~3 min) so there's still no way we'll miss any media.
        curr_point_num = (curr_point_num + 1) % len(points)
    except Exception as e:
        print e
        time.sleep(5)
    except:
        print "some other error!"
        time.sleep(5)
