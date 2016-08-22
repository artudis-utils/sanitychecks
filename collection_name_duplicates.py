#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import click
import collections
import csv
import os
import Levenshtein

Collection = collections.namedtuple('Collection', 'name, link')

@click.command()
@click.argument('filename', nargs=1, type=click.File('r'))
def check_names(filename):
    """Process an artudis Collection json file. 
       Check for collections with duplicate names."""

    collections = []     
    processed = set([])

    for line in filename:
        json_collection = json.loads(line)
	collection = Collection(json_collection["name"], "https://carleton.artudis.com/col/{}/".format(json_collection["__id__"])) 
        collections.append(collection)  

    csv_filename = "{}_{}.csv".format(os.path.splitext(filename.name)[0], 'potential_duplicates')
    with open(csv_filename, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['name1', 'link1', 'name2', 'link2', 'ratio'])

        for collection1 in collections:
            for collection2 in collections:
                if collection1.link != collection2.link:
                    link_pair = tuple(sorted([collection1.link, collection2.link]))
                    if link_pair not in processed:
                        name_ratio = Levenshtein.ratio(collection1.name, collection2.name)
                        if name_ratio > 0.8:
                            click.echo("{}, {}, {}".format(collection1, collection2, name_ratio))
                            csvwriter.writerow([collection1.name.encode('utf-8'), collection1.link, 
                                                collection2.name.encode('utf-8'), collection2.link, 
                                                name_ratio])
                    processed.add(link_pair)

    click.echo("Saved to {}".format(csv_filename))

if __name__ == '__main__':
    check_names()
