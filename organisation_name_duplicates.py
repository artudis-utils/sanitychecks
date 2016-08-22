#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import click
import collections
import csv
import os
import Levenshtein

Organisation = collections.namedtuple('Organisation', 'name, link')

@click.command()
@click.argument('filename', nargs=1, type=click.File('r'))
def check_names(filename):
    """Process an artudis Organisation json file. 
       Check for organisations with duplicate names."""

    organisations = []     
    processed = set([])

    for line in filename:
        json_organisation = json.loads(line)
	organisation = Organisation(json_organisation["name"], "https://carleton.artudis.com/org/{}/".format(json_organisation["__id__"])) 
        organisations.append(organisation)  

    csv_filename = "{}_{}.csv".format(os.path.splitext(filename.name)[0], 'potential_duplicates')
    with open(csv_filename, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['name1', 'link1', 'name2', 'link2', 'ratio'])

        for organisation1 in organisations:
            for organisation2 in organisations:
                if organisation1.link != organisation2.link:
                    link_pair = tuple(sorted([organisation1.link, organisation2.link]))
                    if link_pair not in processed:
                        name_ratio = Levenshtein.ratio(organisation1.name, organisation2.name)
                        if name_ratio > 0.8:
                            click.echo("{}, {}, {}".format(organisation1, organisation2, name_ratio))
                            csvwriter.writerow([organisation1.name.encode('utf-8'), organisation1.link, 
                                                organisation2.name.encode('utf-8'), organisation2.link, 
                                                name_ratio])
                    processed.add(link_pair)

    click.echo("Saved to {}".format(csv_filename))

if __name__ == '__main__':
    check_names()
