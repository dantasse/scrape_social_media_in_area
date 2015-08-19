# scrape_twitter_in_area

Tools to get tweets in a city and save them to PostgreSQL.

scrape_tweets_in_area.py: the main thing. Run this with --city=(city name)
and it'll listen to the Twitter streaming endpoint for a small bounding box
around that city (defined beforehand).

create_tables.py: if you're starting on a new computer, this can help you
set up the database. Some basic instructions included in the top comments in
this file too.

utwils.py: common functions used in more than one of the above files.

