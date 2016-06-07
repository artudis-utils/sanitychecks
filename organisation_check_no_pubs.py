#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import click
import os
import collections
import csv

Org = collections.namedtuple('Org', 'name, link')

@click.command()
@click.option('--orgs', required=True, show_default=True, 
                             type=click.File('r', encoding='utf-8'), 
                             help="Organisation export JSON file from Artudis.")
@click.option('--pubs', show_default=True, required=True,
                             type=click.File('r', encoding='utf-8'), 
                             help="Pubs export JSON file from Artudis.")
def check_empty_orgs(orgs, pubs):
    """Process a artudis organisations and pubs json files. 
         Find orgs with no pubs."""

    orgs_with_pubs_ids = set([])
    orgs_no_pubs = []

    for line in pubs:
        json_pub = json.loads(line)
        for affiliation in json_pub['affiliation']:
            if affiliation['organisation'] != None:
                org_id = int(affiliation['organisation'].split(":")[1])
                recurse_add_orgs(orgs_with_pubs_ids, orgs, org_id)
                
    orgs.seek(0)

    for line in orgs:
        json_org = json.loads(line)
        if int(json_org["__id__"]) not in orgs_with_pubs_ids:
            org = Org(json_org["name"], "https://carleton.artudis.com/org/{}/".format(json_org["__id__"])) 
            orgs_no_pubs.append(org)

    click.echo("Number of orgs without publications: {}".format(len(orgs_no_pubs)))
    save_to_csv(orgs_no_pubs, orgs, "without_pubs")

def recurse_add_orgs(set_of_visited, orgsfile, orgid):
    set_of_visited.add(orgid)
    orgsfile.seek(0)
    recurseme=[]
    for line in orgsfile:
        json_org = json.loads(line)
        if int(json_org['__id__']) == orgid:
            for relation in json_org['relation']:
                if relation['organisation'] != None and relation['role'] == u'partOf':
                    recurseme.append(int(relation['organisation'].split(":")[1]))
    for possibleorgid in recurseme:
        if possibleorgid not in set_of_visited:
            recurse_add_orgs(set_of_visited, orgsfile, possibleorgid)

def save_to_csv(listoforgs, filename, name):
        csv_filename = "{}_{}.csv".format(os.path.splitext(filename.name)[0], name)
        with open(csv_filename, 'wb') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['name', 'link'])
                for org in listoforgs:
                        csvwriter.writerow([org.name.encode('utf-8'), org.link.encode('utf-8')])
        click.echo("Saved to {}".format(csv_filename))

if __name__ == '__main__':
        check_empty_orgs()
