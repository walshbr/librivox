import geograpy
import os
from nltk import FreqDist
import multiprocessing as mp
import codecs
from collections import Counter


def yield_corpus_filenames(corpus="corpus"):
    """given a function and a corpus directory, apply that function to all things in that directory"""
    if os.path.isdir(corpus):
        corpus_dir = corpus
        corpus = [
            os.path.join(corpus_dir, fn) for fn in os.listdir(corpus_dir)
        ]
    for fn in corpus:
        yield fn


def flatten(nested_list):
    """Takes in a nested list of lists and flattens them out"""
    return [item for sublist in nested_list for item in sublist]


def unpack_fd(fd):
    """Takes in a frequency distribution and returns a list of those items, unpacked all in one flat list."""
    unpacked = []
    for (item, num) in fd:
        if num == 1:
            unpacked.append(item)
        if num < 1:
            while num != 0:
                unpacked.append(item)
    return unpacked


def read_file(filename):
    """Read a file and return its contents."""
    with codecs.open(filename, encoding='utf8') as f:
        return f.read()


def name_reg(text):
    """Return a triplet of recognized entities."""
    countries = Counter()
    regions = Counter()
    cities = Counter()

    if text:
        places = geograpy.get_place_context(text=text)
        if places.country_mentions:
            countries.update(unpack_fd(places.country_mentions))
        if places.region_mentions:
            regions.update(unpack_fd(places.region_mentions))
        if places.city_mentions:
            cities.update(unpack_fd(places.city_mentions))

    return (countries, regions, cities)


def main():
    file_texts = (
        read_file(filename) for filename in yield_corpus_filenames("sample")
        )

    # reading out place names
    countries = Counter()
    regions = Counter()
    cities = Counter()
    counter = 0

    pool = mp.Pool()
    counts = pool.map(name_reg, file_texts)
    for (co, rg, ci) in counts:
        countries += co
        regions += rg
        cities += ci
        counter += 1

    with open('results.txt', 'w') as fout:
        fout.write("\ncount = {}\n".format(counter))
        fout.write('\n=======================countries:\n')
        fout.write(str(countries.most_common()))
        fout.write('\n=======================regions:\n')
        fout.write(str(regions.most_common()))
        fout.write('\n=======================cities:\n')
        fout.write(str(cities.most_common()))


if __name__ == '__main__':
    main()
