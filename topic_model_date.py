"""Given a topic model composition document and an associated
database, run over that document to associate dates with topics.
then produce a csv that can be graphed."""


import csv

import datetime
from contextlib import closing
import re
import sqlite3

from collections import Counter
import dateutil.parser

"""TODO: Speed up. Normalize for document frequency."""

TOPIC_COMPOSITION_FILE = 'librivox_composition.txt'
# TOPIC_COMPOSITION_FILE = 'librivox_composition_test.txt'
DB_FILE = 'librivox.db'


def read_database():
    """Reads in tab delimeted file and stores it as a list."""
    with open(TOPIC_COMPOSITION_FILE) as f:
        reader = csv.reader(f, delimiter="\t")
        # cleans off the header first line. returns it as a list.
        return list(reader)[1:]


def load_url_index():
    """given a line of the topic model document, replace
    the url with the posted date."""
    cxn = sqlite3.connect(DB_FILE)
    with closing(cxn.cursor()) as c:
        urls = c.execute("""SELECT u.url, p.posted
                         FROM urls u, postings p
                         WHERE u.id=p.url_id;""")
        return dict(
            (re.sub(r'[^\w\.]', '', url), posted)
            for (url, posted) in urls
        )


def prep_dict(d):
    """Takes in a tuple of a date and a list of proportions. Combines them
    into a new flat dict."""
    new_dict = {}
    new_dict["year-month"] = str(list(d[0])[0]) + '-' + str(list(d[0])[1])
    flat_dict = dict(d[1].items())
    for key, value in flat_dict.items():
        new_dict[key] = value
    return new_dict


def main():
    """""Main stuff of the program."""
    content = read_database()
    # next line should probably be refactored - right now it's going into
    # every line of content twice. should probably be included instead as
    # part of the loop below. Also needs to scaled for document length.
    url_index = load_url_index()
    index = {}
    for line in content:
        line[1] = url_index[line[1]]
        # TODO: need to process it a little so that it's in better shape for
        # the ingestion into the counter. maybe put the things in a hash so
        # that the topics are keys for the percentages which are the values?
        # Then maybe a counter would take it up.
        key = (dateutil.parser.parse(line[1]).year,
               dateutil.parser.parse(line[1]).month)
        i = iter(line[2:-1])
        # produces a hash of the line with the id and blank space removed.
        b = dict(zip(i, i))
        for item in b:
            b[item] = float(b[item])
        freqs = Counter(b)
        if key not in index:
            index[key] = Counter()
        index[key].update(freqs)
    index = list(index.items())
    index = [prep_dict(item) for item in index]
    with open('results.csv', 'w') as csvfile:
        fieldnames = ['year-month', '0', '1', '2', '3', '4', '5', '6', '7',
                      '8', '9', '10', '11', '12', '13', '14', '15', '16',
                      '17', '18', '19']
        writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=fieldnames)
        writer.writeheader()
        for row in index:
            writer.writerow(row)

if __name__ == '__main__':
    main()
