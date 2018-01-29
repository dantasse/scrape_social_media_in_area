# Geotagged Tweets

This archive includes public geotagged tweets (and a few Instagram posts) around 15 cities for most of 2014-2017.

This data should be found on s3 [here](https://s3.console.aws.amazon.com/s3/buckets/dantasse-tweets/?region=us-west-1&tab=overview).

Included are:

- coordinate-geotagged tweets from:
  - Pittsburgh, starting on 2014-01-22
  - San Francisco and New York, starting on 2014-06-13
  - Houston, Cleveland, Seattle, Miami, Detroit, Chicago, and London (England), starting on 2015-03-18
  - San Antonio, Austin, and Dallas, starting on 2015-06-15
  - A few in Oakland and around the White House, collected on a whim
- all geotagged (including placetagged) tweets from Pittsburgh, starting on 2017-06-22.
- instagrams from Pittsburgh (more details below)

By "coordinate-geotagged" we mean points that users have attached their precise lat-lon coordinates to, like (40.441667, -80.00000). The one Pittsburgh data set that has "all geotagged tweets", we are including also "placetagged" tweets (such as those tagged with "Pittsburgh" or "PNC Park"). See [our 2017 ICWSM paper](https://www.dantasse.com/docs/state_of_the_geotags_icwsm2017.pdf) for more discussion of coordinate-geotagging vs. placetagging.

All cities' tweets end on 2017-11-15.

## Where and how much data
Number of tweets:

- Austin: 1.6M
- Chicago: 8.2M
- Cleveland: 3.6M
- Dallas: 2.4M
- Detroit: 3.8M
- Houston: 7.1M
- London: 16.1M
- Minneapolis: 2.0M
- Miami: 9.5M
- New York: 14.3M
- Oakland: 0.2M
- Pittsburgh: 4.9M
- San Antonio: 1.2M
- Seattle: 3.8M
- San Francisco: 6.8M
- the White House: 41K

The location of each tweet is "near" the city, where we somewhat arbitrarily defined "near" as "within a box approximately 0.2 degrees latitude and longitude around the Wikipedia center of the city (expanding the box a bit in cases where that would exclude some of the city)." So if you want, you could probably filter these to be actually within the city limits if you got a shapefile/GeoJSON of the city limits. We haven't done that yet.

And we only centered on Manhattan in New York. I know, I know, sorry to the other four boroughs!

## Format of each file
Each tweet file is stored as (cityname).json.gz. Pittsburgh is stored as "pgh", San Francisco and New York as "sf" and "ny", respectively. We have no good justification for this.

When you unzip the .json.gz (via `gunzip city.json.gz`), you'll get a .json file. The ".json" extension is a bit of a lie; they're actually files where each line is a json object, but the file overall isn't valid json. Sorry about this too.

## Format of each tweet
Tweets are mostly stored [as they came out of the Twitter API](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object), but with some modifications for our ease of use. These modifications:

- `favorited` and `retweeted` have been removed, as it only makes sense if you're issuing the query as a logged-in user, which we aren't
- `geo` is skipped as it's deprecated (replaced by `place`)
- `truncated` is also skipped because of deprecation
- `user` is renamed to `twitter_user`
- an extra field, `user_screen_name`, was added; `tweet['user_screen_name']` is the same as `tweet['twitter_user']['screen_name']`. I don't have a reason for this that still makes sense either.
- `coordinates` is stored as a PostGIS format, maybe Well-Known Binary, but don't quote me on that. The coordinates are also stored in the `st_asgeojson` field (as strings that can be parsed as GeoJSON objects) so you don't have to install PostGIS in order to read them.

The tweets were gathered using [`scrape_social_media_in_area`](https://github.com/CMUChimpsLab/scrape_social_media_in_area), so feel free to check up on that if you need to get into details (specifically [`tweet_to_insert_string`](https://github.com/CMUChimpsLab/scrape_social_media_in_area/blob/master/utils.py#L40) will be a useful function).

## Format of the Instagrams
`instas.json.gz` has some Instagram posts from around Pittsburgh for about two years, from about 2014-01-24 to 2016-06-01. (in June 2016, Instagram's API changed such that you can no longer just crawl it.)

The format of this file is basically a tab-separated variable. It's nominally a SQL file, but if you try to just run it, it will probably fail because I think the Well-Known Binary representing the coordinates of each post (the long 0101011010124024AE39ADD... string at the end of each line) got corrupted somehow.

My recommendation to you is to just treat this file as a TSV file and parse it manually to get what you can out of it. Sorry again!

## Who are we
- Dan Tasse, who completed his Ph.D. in Human-Computer Interaction at Carnegie Mellon thanks to this data, in 2017. Contact me with any questions or anything about this: dan.tasse@gmail.com
- Jason Hong, professor of HCI at CMU and Dan's advisor. I'd say contact him if you're interested in working on this kind of thing, but he's not doing this so much anymore; more about privacy and security. (But he's awesome and his lab is always full of great people, so do work with them!)
- So many other collaborators and research assistants! Notably Alex Sciuto, Zichen Liu, Andy Dong Hyun Choi, Jennifer Chou, Hong Bin Shim, Emily Su, Joshua Herman, Jinny Hyun Ji Kim, Eva Peng, and Sriram Venkiteshwaran.

## Citation
If you find these useful in an academic or otherwise work, you can cite us! (No worries either way, I won't be terribly fussed if you don't.) These were collected in service of a couple works, but here's probably the best one to cite.

### Bibtex:

```
@inproceedings{tasse2017state,
  title={State of the Geotags: Motivations and Recent Changes.},
  author={Tasse, Dan and Liu, Zichen and Sciuto, Alex and Hong, Jason I},
  booktitle={Proceedings of the 11th International AAAI Conference on Web and Social Media (ICWSM-17)},
  pages={250--259},
  year={2017}
}
```

### Easier to read:

Tasse, D., Liu, Z., Sciuto, A., and Hong, J.I. State of the Geotags: Motivations and Recent Changes. Proceedings of the 11th International AAAI Conference on Web and Social Media (ICWSM-17), 2017.

### Link to the paper:
[`https://www.dantasse.com/docs/state_of_the_geotags_icwsm2017.pdf`](https://www.dantasse.com/docs/state_of_the_geotags_icwsm2017.pdf)
