import os, math

# a list containing all of the author-book text files to be used by the program
files = []

all_books_count = {}
# contains a count of which words are used how many times by each author
auth_counts = {}

all_books_pars = [[],[]]
all_words_gain = {}


def get_files():
    # gets all the filenames of text files to be considered.
    for f in os.listdir():
        if f[-4:] == '.txt' and '-' in f:
            files.append(f)

def get_author(fname):
    # takes the file name and returns the author name from it
    i = 0
    while fname[i] != '-':
        i += 1
    return fname[:i]

def alphas(w):
    # cleans a dirty word. Makes it so every word is all lower cased and no
    # punctuation is present in any of the lists.
    return ''.join([c.lower() for c in w if c.lower() >= 'a' and c.lower() <= 'z'])


def process(fname):

    # find which author we are working with and adds it to the auth_counts
    # dictionary if it's not already in it
    auth = get_author(fname)
    if auth not in auth_counts:
        auth_counts[auth] = {}

    # read in the file as lines
    f = open(fname, mode='r')
    book = f.readlines()
    f.close()

    # each index of book_pars is list of the words in the paragraph. The index
    # is the number of the paragraph with the first index being the name of the
    # author and the book
    book_pars = [fname]

    # TODO delete?
    book_count = {}

    # p will be the set of words present in a given paragraph. These counts will
    # be stored in book_pars
    p = set()

    for i in range(len(book)):
        # book has each index as a line from the book. This for loop determines
        # which words are in each paragraph for each book while also tabulating
        # the counts for each word and stores the results by author.
        # I know, I know, one thing at a time.

        if book[i] == '\n':
            # if an entire line is only a newline, then it is the end of a
            # paragraph, time to start the process over again.
            book_pars.append(p)
            p = set()
            continue

        # each index of book is a line from the book. This splits the line into
        # a list of words.
        line = book[i].split()

        for w_dirty in line:
            # for all the words of the line, get only the lower cased version
            # without any punctuation
            w_cleaned = alphas(w_dirty)

            if len(w_cleaned) <= 1:
                # don't include single letter words
                continue

            # adds the cleaned up word to the set of paragraphs. If it is
            # already in there, it does nothing.
            p.add(w_cleaned)
            # adds the cleaned up words to the set of all words whose gain will
            # be calculated later.
            all_words_gain[w_cleaned] = 0

    if auth == 'austen':
        all_books_pars[0].append(book_pars)
    else:
        all_books_pars[1].append(book_pars)


def find_gain():

    # list of all the words
    all_words = all_words_gain.keys()
    # number of authors
    nauths = len(all_books_pars)
    # total number of paragraphs each author has. index 0 = austen, 1 = shelly
    npars = [0,0]

    for i in range(nauths):
        # sums the total number of paragraphs from each author and stores the
        # totals in that author's index. The '- 1' accounts for the first index
        # containing the author's name and book title
        for b in all_books_pars[i]:
            npars[i] += len(b) - 1

    # pr0 is the probability that any one paragraph is written by austen
    pr0 = npars[0] / sum(npars)
    # pr1 is the probability that any one paragraph is written by shelly
    pr1 = npars[1] / sum(npars)
    # all_U is a measure of the entropy for the entire system
    all_U = -(pr0 * math.log2(pr0) + pr1 * math.log2(pr1))

    for word in all_words:
        # for every word from all the books scanned in, and for every paragraph
        # for each author, the amount of information gained from splitting
        # on that word is calculated
        # pos_counts is the number of paragraphs of each author that contains
        # the word being checked
        pos_counts = [0, 0]
        # pos_counts is the number of paragraphs of each author that doesn't
        # contain the word being checked
        neg_counts = [0, 0]
        for auth in range(nauths):
            for book in all_books_pars[auth]:
                for par in book:
                    if word in par:
                        pos_counts[auth] += 1
                    else:
                        neg_counts[auth] += 1

        # totalp is the total positive, the number of paragraphs from each
        # author containing the word being checked.
        totalp = sum(pos_counts)
        # totaln is the total negative, the number of paragraphs from each
        # author not containing the word being checked.
        totaln = sum(neg_counts)
        # proportion positive
        prp = [0,0]
        # proportion negative
        prn = [0,0]


        for i in range(nauths):
            prp[i] = pos_counts[i] / totalp
            prn[i] = neg_counts[i] / totaln



def main():
    get_files()
    files.sort()

    for fname in files:
        process(fname)

    find_gain()

if __name__ == '__main__':
    main()

# example of psam:
#