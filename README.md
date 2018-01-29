# `scrape_social_media_in_area`

Tools to get tweets in a city and save them to PostgreSQL.

`s3_readme.md`: Info about how to find the data we collected from this project. It's stored as gzipped json files in a public bucket on s3.

`scrape_tweets_in_area.py`: the main thing. Run this with --city=(city name)
and it'll listen to the Twitter streaming endpoint for a small bounding box
around that city (defined beforehand).

`scrape_instagram_in_area.py`: the same, but for instagram. But limited to
Pittsburgh, so far. EDIT: as of September 2016, this won't work; they shut down the bit of the API we were using to grab instagram photos.

`notify_if_broken.py`: sends an email if no data has been added to each table in
the database in 24 hours. (run via cron.)

`print_table_counts.py`: prints out how many items are in each table. (run via
cron to make a log of sorts.)

`create_tables.py`: if you're starting on a new computer, this can help you
set up the database. Some basic instructions included in the top comments in
this file too.

`utils.py`: common functions used in more than one of the above files.

`crontab`: my crontab on Domo (our EC2 machine) that runs a couple of the above
daily.
