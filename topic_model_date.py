"""Given a topic model composition document and an associated
database, run over that document to associate dates with topics.
then produce a csv that can be graphed."""

import csv

from contextlib import closing
import sqlite3
import sys

from collections import Counter
import dateutil.parser

# TOPIC_COMPOSITION_FILE = 'librivox_composition.txt'
TOPIC_COMPOSITION_FILE = 'librivox_composition_test.txt'
DB_FILE = 'librivox.db'


def read_database():
    """Reads in tab delimeted file and stores it as a list."""
    with open(TOPIC_COMPOSITION_FILE) as f:
        reader = csv.reader(f, delimiter="\t")
        # cleans off the header first line. returns it as a list.
        return list(reader)[1:]


def fetch_date(given_url):
    """Given the url of a post, fetch its posted date_time"""
    cxn = sqlite3.connect(DB_FILE)
    with closing(cxn.cursor()) as c:
        # take url and pull out url id
        given_url_id = c.execute("""
            SELECT id FROM urls WHERE replace(
            replace(replace(replace(replace(
            url,'&' ,''),'=' ,''),'/', ''), ':', ''), '?', '') = ?;
            """, [given_url]).fetchone()[0]
        # take url id, find the associated post, and
        # pull out a posted date_time
        posted_date_time = c.execute('SELECT posted FROM postings WHERE url_id = ?;', [given_url_id]).fetchone()[0]
    return posted_date_time


def replace_urls_with_date(content):
    """given a line of the topic model document, replace the url with the posted date."""
    for line in content:
        line[1] = fetch_date(line[1])
    return content

def compile_topic_proportions(content):
    """Takes a content and returns compiles all the topic proportions of date and month."""
    index = {}
    for line in content:
        # TODO: need to process it a little so that it's in better shape for the ingestion into the counter. maybe put the things in a hash so that the topics are keys for the percentages which are the values? Then maybe a counter would take it up.
        key = (dateutil.parser.parse(line[1]).year, dateutil.parser.parse(line[1]).month)
        i = iter(line[2:-1])
        #produces a hash of the line with the id and blank space removed.
        b = dict(zip(i, i))
        for key in b:
            b[key] = float(b[key])
        freqs = Counter(b)
        if key not in index:
            index[key] = Counter()
        index[key].update(freqs)
    return index


def main():
    """""Main stuff of the program."""
    content = read_database()
    content = replace_urls_with_date(content)
    # compile_topic_proportions(content)
    index = {}
    for line in content:
        # TODO: need to process it a little so that it's in better shape for the ingestion into the counter. maybe put the things in a hash so that the topics are keys for the percentages which are the values? Then maybe a counter would take it up.
        key = (dateutil.parser.parse(line[1]).year, dateutil.parser.parse(line[1]).month)
        i = iter(line[2:-1])
        #produces a hash of the line with the id and blank space removed.
        b = dict(zip(i, i))
        for item in b:
            b[item] = float(b[item])
        freqs = Counter(b)
        if key not in index:
            index[key] = Counter()
        index[key].update(freqs)
    groups = list(index.items())
    groups.sort()
    # figure out how to splat the keys and values pieces into the csv
    writer = csv.writer(sys.stdout)
    writer.writerow(('year-month', ','.join(map(str, groups[0][1].keys()))))
    writer.writerows(
        (('{}-{}').format(*date), ','.join(map(str, proportions.values()))) for (date, proportions) in groups
    )
if __name__ == '__main__':
    main()
