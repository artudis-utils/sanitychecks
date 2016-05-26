#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import click
import collections
import csv
import os

Org = collections.namedtuple('Org', 'name, link')

@click.command()
@click.argument('filename', nargs=1, type=click.File('r'))
def check_orgs(filename):
    """Process an artudis organisations json file. 
       Check for orgs without descriptions, homepages, or relations."""

    without_descriptions = []
    without_home_pages = []
    without_relation = []
  
    for line in filename:
        json_org = json.loads(line)
        org = Org(json_org["name"], "https://carleton.artudis.com/org/{}/".format(json_org["__id__"])) 
        without_descriptions.append(org)
        if json_org['description'] != []:
            for description in json_org['description']:
                if description['type'] == u"description" and len(description['value']) > 1:
                    without_descriptions.pop()
                    break

        without_home_pages.append(org)
        if json_org['contact'] != []:
            for info in json_org['contact']:
                if u"website" in info and info['website'] != u"":
                    without_home_pages.pop()
                    break

        without_relation.append(org)
        if json_org['relation'] != []:
            without_relation.pop()

 
    click.echo("Number of orgs without descriptions: {}".format(len(without_descriptions)))
    save_to_csv(without_descriptions, filename, "without_descriptions")    

    click.echo("Number of orgs without home pages: {}".format(len(without_home_pages)))
    save_to_csv(without_home_pages, filename, "without_home_pages")

    click.echo("Number of orgs without relations: {}".format(len(without_relation)))
    save_to_csv(without_relation, filename, "without_relation")


def save_to_csv(listoforgs, filename, name):

    csv_filename = "{}_{}.csv".format(os.path.splitext(filename.name)[0], name)
    with open(csv_filename, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['name', 'link'])
        for org in listoforgs:
            csvwriter.writerow([org.name.encode('utf-8'), org.link.encode('utf-8')])
    click.echo("Saved to {}".format(csv_filename))

if __name__ == '__main__':
    check_orgs()
