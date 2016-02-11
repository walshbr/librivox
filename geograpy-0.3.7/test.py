import geograpy
import os
from nltk import FreqDist


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


file_names = list(yield_corpus_filenames("sample"))

# reading out place names
countries = []
regions = []
cities = []
counter = 0

for fn in file_names:
    test_data = []
    with open(fn) as fin:
        data = fin.read()
    # print(data)
    test_data.append(data)
    if test_data[0] != '':
        places = geograpy.get_place_context(text=unicode(data, "utf-8"))
        # print(places)
        if places.country_mentions:
            countries.append(places.country_mentions)
            print(places.country_mentions)
        if places.region_mentions:
            regions.append(places.region_mentions)
            print(places.region_mentions)
        if places.city_mentions:
            cities.append(places.city_mentions)
            print(places.city_mentions)
    print(counter)
    counter += 1

countries = FreqDist(unpack_fd(flatten(countries)))
regions = FreqDist(unpack_fd(flatten(regions)))
cities = FreqDist(unpack_fd(flatten(cities)))

with open('results.txt', 'w') as fout:
    fout.write('\n=======================countries:\n')
    fout.write(str(countries.items()))
    fout.write('\n=======================regions:\n')
    fout.write(str(regions.items()))
    fout.write('\n=======================cities:\n')
    fout.write(str(cities.items()))
