import sys, os
from collections import defaultdict

files = []
authors = []
all_words = []
all_histo = {}
by_book = {}


def author_name(f):
    i = 0
    while f[i] != '-':
        i += 1
    return i


def get_names():
    for f in os.listdir():
        if f[-4:] == '.txt' and '-' in f:
            files.append(f)
            author = f[:author_name(f)]
            if author not in authors:
                authors.append(author)

def is_word(w):
    return ''.join([c.lower() for c in w if c.lower() >= 'a' and c.lower() <= 'z'])


def process(fname):
    f = open(fname, mode='r')
    book = f.readlines()
    f.close()

    sing_book_histo = {}
    ps = []
    p = []
    for bi in range(len(book)):
        if book[bi] == '\n':
            ps.append(p)
            p = []
            continue

        line_garb = book[bi].strip().split()
        line = []

        for w in line_garb:
            actual_w = is_word(w)

            if actual_w and len(actual_w) > 1:
                line.append(actual_w)

                if actual_w not in all_words:
                    all_words.append(actual_w)

                if actual_w not in all_histo:
                    all_histo[actual_w] = 1
                else:
                    all_histo[actual_w] += 1

                if actual_w not in sing_book_histo:
                    sing_book_histo[actual_w] = 1
                else:
                    sing_book_histo[actual_w] += 1

        p = p + line

    ps.append(p)
    by_book[fname] = sing_book_histo


def main():
    get_names()

    for fname in files:
    #fname = 'austen-northanger-abbey.txt'
        process(fname)
    print(len(all_words))
    print(sum(all_histo.values()))

if __name__ == '__main__':
    main()
