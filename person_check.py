#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import click
import collections
import csv
import os

Person = collections.namedtuple('Person', 'familyname, givenname, link')

@click.command()
@click.argument('filename', nargs=1, type=click.File('r'))
def check_people(filename):
    """Process an artudis Person json file. 
       Check for people without work url, identifiers, work affiliation, name variant."""

    without_work_url = []
    without_identifiers = []  
    without_work_affiliation = []
    without_name_variant = []
    with_duplicate_identifiers = []

    for line in filename:
        json_person = json.loads(line)
        person = Person(json_person["family_name"], json_person["given_name"], "https://carleton.artudis.com/ppl/{}/".format(json_person["__id__"])) 
        
        without_work_url.append(person)
        if json_person['contact'] != []:
            for contact in json_person['contact']:
                if contact['role'] == u"work" and isinstance(contact['website'], basestring) and len(contact['website']) > 1:
                    without_work_url.pop()
                    break

        without_identifiers.append(person)
        if json_person['identifier'] != []:
            without_identifiers.pop()

        without_work_affiliation.append(person)
        if json_person['affiliation'] != []:
            for affiliation in json_person['affiliation']:
                if affiliation['role'] == u"workRelation":
                    without_work_affiliation.pop()
                    break

        without_name_variant.append(person)
        if json_person['name_info'] != []:
            for name_info in json_person['name_info']:
                if name_info['type'] == u"alternative":
                    without_name_variant.pop()
                    break
      
        with_duplicate_identifiers.append(person)
        if json_person['identifier'] != []:
            c = collections.Counter([x['scheme'] for x in json_person['identifier']])
            if all(count == 1 for count in c.itervalues()):
                with_duplicate_identifiers.pop()
            

    click.echo("Number of people without work urls: {}".format(len(without_work_url)))
    save_to_csv(without_work_url, filename, "without_work_url")    

    click.echo("Number of people without identifiers: {}".format(len(without_identifiers)))
    save_to_csv(without_identifiers, filename, "without_identifiers")

    click.echo("Number of people without work affiliations: {}".format(len(without_work_affiliation)))
    save_to_csv(without_work_affiliation, filename, "without_work_affiliation")

    click.echo("Number of people without name variants: {}".format(len(without_name_variant)))
    save_to_csv(without_name_variant, filename, "without_name_variant")

    click.echo("Number of people with duplicate identifiers: {}".format(len(with_duplicate_identifiers)))
    save_to_csv(with_duplicate_identifiers, filename, "with_duplicate_identifiers")


def save_to_csv(listofpeople, filename, name):

    csv_filename = "{}_{}.csv".format(os.path.splitext(filename.name)[0], name)
    with open(csv_filename, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['familyname', 'givenname', 'link'])
        for person in listofpeople:
            csvwriter.writerow([person.familyname.encode('utf-8'), person.givenname.encode('utf-8'), person.link.encode('utf-8')])
    click.echo("Saved to {}".format(csv_filename))

if __name__ == '__main__':
    check_people()
