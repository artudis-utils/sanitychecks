#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import click
import collections
import csv
import os
import Levenshtein

Person = collections.namedtuple('Person', 'familyname, givenname, link')

@click.command()
@click.argument('filename', nargs=1, type=click.File('r'))
def check_names(filename):
    """Process an artudis Person json file. 
       Check for people with duplicate names."""

    people = []     
    processed = set([])

    for line in filename:
        json_person = json.loads(line)
        person = Person(json_person["family_name"], json_person["given_name"], "https://carleton.artudis.com/ppl/{}/".format(json_person["__id__"])) 
        people.append(person)  
        if person.familyname == "Smy":
            click.echo("Got smy")

    csv_filename = "{}_{}.csv".format(os.path.splitext(filename.name)[0], 'potential_duplicates')
    with open(csv_filename, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['familyname1', 'givenname1', 'link1', 'familyname2', 'givenname2', 'link2', 'ratiofamilyname', 'ratiogivenname'])

        for person1 in people:
            for person2 in people:
                if person1.link != person2.link:
                    link_pair = tuple(sorted([person1.link, person2.link]))
                    click.echo(link_pair)
                    if link_pair not in processed:
                        familyname_ratio = Levenshtein.ratio(person1.familyname, person2.familyname)
                        givenname_ratio = Levenshtein.ratio(person1.givenname, person2.givenname)
                        click.echo(familyname_ratio)
                        click.echo(givenname_ratio)
                        if familyname_ratio > 0.7 and givenname_ratio > 0.3:
                            click.echo("{}, {}, {} {}".format(person1, person2, familyname_ratio, givenname_ratio))
                            csvwriter.writerow([person1.familyname.encode('utf-8'), person1.givenname.encode('utf-8'), person1.link, 
                                                person2.familyname.encode('utf-8'), person2.givenname.encode('utf-8'), person2.link, 
                                                familyname_ratio, givenname_ratio])
                    processed.add(link_pair)

    click.echo("Saved to {}".format(csv_filename))

if __name__ == '__main__':
    check_names()
