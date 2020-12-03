# !/usr/bin/python3
# Determines the gains of splitting on a word to determine which author wrote
# which book. To be used by id3
import os
import math

# a list containing all of the author-book text files to be used by the program
files = []

# number of authors, gotta change it if I try to do more authors
nauths = 2
# all the books broken up into paragraphs, 0 for Austen, 1 for Shelly
all_books_pars = [[], []]
# used keep track of the gains for each word
all_words_gain = []
# all the words used by either author
all_words = set()
# used as a lower cut off point for total number of uses. Will implement an
# upper threshold if I have time.
threshold = 10
# number of words to split on
nwords = 300


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
    # oof! This function is rough, but I'm guessing everyone's is.
    # It reads in the file as a list of lines then goes through each line,
    # building paragraphs and removing punctuation as it goes. When the end of
    # a paragraph is reached, the paragraph is added to the corresponding
    # author's index of all_books_par

    # find which author we are working with
    auth = get_author(fname)

    # read in the file as lines
    f = open(fname, mode='r')
    book = f.readlines()
    f.close()

    # each index of book_pars is list of the words in the paragraph. The index
    # is the number of the paragraph with the first index being the name of the
    # author and the book
    book_pars = [fname]

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
            all_words.add(w_cleaned)

    if auth == 'austen':
        all_books_pars[0].append(book_pars)
    else:
        all_books_pars[1].append(book_pars)


def calc_U(pr):
    # calculates the entropy for the group passed to it.
    if pr[0] == 0 or pr[1] == 0:
        # if a perfect split, then 0 indicates that.
        return 0
    return -(pr[0] * math.log2(pr[0]) + pr[1] * math.log2(pr[1]))


def find_gain():
    # as the name implies, it finds the gain of splitting on each word according
    # to the number of paragraphs by each author contain the word.

    # total number of paragraphs each author has. index 0 = austen, 1 = shelly
    npars = [0, 0]

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
    all_U = -(pr1 * math.log2(pr1) + pr0 * math.log2(pr0))

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
            # splits the paragraphs into the occurrences of present and not
            # present for each word for each author
            for book in all_books_pars[auth]:
                for par in book:
                    if word in par:
                        pos_counts[auth] += 1
                    else:
                        neg_counts[auth] += 1

        # total_pos is the total positive, the number of paragraphs from each
        # author containing the word being checked.
        total_pos = sum(pos_counts)
        # total_neg is the total negative, the number of paragraphs from each
        # author not containing the word being checked.
        total_neg = sum(neg_counts)
        total_occur = total_pos + total_neg
        # proportion positive, [Austen, Shelly]
        prpos = [0, 0]
        # proportion negative, [Austen, Shelly]
        prneg = [0, 0]
        if total_pos < threshold:
            # the least used words are thrown out. Don't want to divide on a
            # typo, a word with internal punctuation removed incorrectly, some
            # weird random word (I don't know, some authors are weird people,
            # we don't want to split on elvish from Tolkien, right?) and because
            # I set the default gain of each word to be -1, all words whose gain
            # has been calculated will be higher.
            continue

        for i in range(nauths):
            # finds the proportions of the usage of a word by authors,
            # 0 austen, 1 shelly
            prpos[i] = pos_counts[i] / total_pos
            prneg[i] = neg_counts[i] / total_neg

        # pos_U is the entropy for paragraphs having the word in it
        pos_U = calc_U(prpos)
        # neg_U is the entropy for paragraphs not having the word in it
        neg_U = calc_U(prneg)

        # prime_U is the of total entropy weighted to the totals.
        prime_U = (total_pos/total_occur) * pos_U + (total_neg/total_occur) * neg_U

        # add the calculated gain for a word
        all_words_gain.append((word, all_U - prime_U))


def output():
    # Hopefully obviously outputs the paragraph/word info, the first index being
    # the author-book.paragraph number of that book followed by the author
    # number, 0 for austen, 1 for shelly, then whether each of the 300 words
    # with the best gain is present in that paragraph

    # sort the words/gain key value by the gain. The highest gain will be first.
    all_words_gain.sort(key=lambda x: x[1], reverse=True)
    # simple list building to take the top 300 words by gain
    splitting_words = [x[0] for x in all_words_gain[:nwords]]
    # open a file to write to
    fout = open("par_words.CSV", "w")

    for auth in range(nauths):
        # writes to the file, the first index, then the author code, then the
        # words' presence, 0 for austen 1 for shelly; 0 for not present
        # 1 for present
        for book in range(len(all_books_pars[auth])):
            title = all_books_pars[auth][book][0][:-4]
            for par in range(len(all_books_pars[auth][book])):
                fout.write(title + '.' + str(par))
                if title[0] == 'a':
                    fout.write(',0')
                else:
                    fout.write(',1')
                for word in splitting_words:
                    if word not in all_books_pars[auth][book][par]:
                        fout.write(',0')
                    else:
                        fout.write(',1')
                fout.write("\n")

    fout.close()


def main():
    get_files()
    files.sort()
    for fname in files:
        process(fname)

    find_gain()
    output()


if __name__ == '__main__':
    main()
