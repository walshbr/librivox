#!/usr/bin/env python3


"""usage: compare_terms.py TERM1 TERM2

Writes out a CSV file listing the frequencies of these terms by month.
"""


import nltk
import csv
from collections import Counter
import sys
import sqlite3
import dateutil.parser
from contextlib import closing


DB_FILE = 'librivox.db'


def get_postings(c):
    c.execute('SELECT posted, text FROM postings ORDER BY posted;')
    return [
        (dateutil.parser.parse(posted), text)
        for (posted, text) in c.fetchall()
    ]


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) == 0 or '-h' in argv or '--help' in argv:
        print(__doc__)
        sys.exit()
    term0, term1 = argv

    index = {}
    with closing(sqlite3.connect(DB_FILE)) as cxn:
        with closing(cxn.cursor()) as c:
            for (posted, text) in get_postings(c):
                freqs = Counter(
                    token.lower() for token in nltk.word_tokenize(text)
                    )
                # normalized_freqs = (freqs / len(nltk.word_tokenize(text)))
                key = (posted.year, posted.month)
                if key not in index:
                    index[key] = Counter()
                index[key].update(freqs)

    groups = list(index.items())
    groups.sort()
    writer = csv.writer(sys.stdout)
    writer.writerow(('year-month', term0, term1))
    writer.writerows(
        ('{}-{}'.format(*date), freqs[term0]/len(list(freqs.elements())),
            freqs[term1]/len(list(freqs.elements())))
        for (date, freqs) in groups
    )


if __name__ == '__main__':
    main()
