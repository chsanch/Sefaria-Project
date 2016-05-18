# -*- coding: utf-8 -*-

"""
The text of different editions of the Mishnah can have significant differences. In addition, the Wikisource
 edition of the Mishnah originally hosted on Sefaria seems to be very inaccurate, and was ultimately replaced
 by the Vilna edition of the Mishna. The goal of this module is to assess the differences between the two
 versions and ultimately align and correct all commentaries so that they match the Vilna edition.
"""

import os
import sys
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print p
sys.path.insert(0, p)
from sefaria.local_settings import *
os.environ['DJANGO_SETTINGS_MODULE'] = 'sefaria.settings'
from sefaria.model import *

tractates = library.get_indexes_in_category('Mishnah')

"""
Phase I: The goal of these functions is to roughly compare the two versions and to find "suspicious" sections
and to gain a better understanding of the differences between them.
"""


def get_relevant_books():
    """
    As not all tractates have had the Vilna edition uploaded yet, get those tractates for which the version has
    been uploaded.
    :return: List of tractates for which the Vilna edition has been uploaded.
    """

    relevant = []

    for book in tractates:

        ref = Ref(book)
        for version in ref.version_list():
            if version['versionTitle'] == 'Vilna Mishna':
                relevant.append(book)
                break
    return relevant


def compare_number_of_mishnayot(chapter, allowed=0):
    """
    Compares number of mishnayot between two versions.
    :param chapter: Tuple, each value is a list of Mishnayot from each version.
    :param allowed: Allowed difference between number of Mishnayot.
    :return: True or False
    """

    if abs(chapter[0].verse_count() - chapter[1].verse_count()) > allowed:
        return False
    else:
        return True


def compare_number_of_words(mishnah, allowed=0):
    """
    Compares number of words in a mishna from two parallel versions
    :param mishnah: Tuple with each value containing a string of text from each version from one mishnah
    :param allowed: Allowed difference between both versions before test returns false
    :return: boolean
    """

    if abs(mishnah[0].word_count() - mishnah[1].word_count()) > allowed:
        return False
    else:
        return True


def run(outfile):

    outfile.write(u'Tractate,Chapter,Mishnah Count,Word Count\n')
    books = get_relevant_books()
    for book in books:
        chapters = Ref(book).all_subrefs()

        for chap_ind, chapter in enumerate(chapters):
            outfile.write(u'{},{},'.format(book, chap_ind+1))
            v1 = TextChunk(chapter, 'he', 'Vilna Mishna')
            v2 = TextChunk(chapter, 'he', 'Wikisource Mishnah')

            if compare_number_of_mishnayot((v1, v2)):
                outfile.write(u'Passed,')
            else:
                outfile.write(u'Failed,')

            word_count = []

            for m_index, mishna in enumerate(chapter.all_subrefs()):
                v1 = TextChunk(mishna, 'he', 'Vilna Mishna')
                v2 = TextChunk(mishna, 'he', 'Wikisource Mishnah')
                if not compare_number_of_words((v1, v2)):
                    word_count.append(m_index+1)

            outfile.write(u'{}\n'.format(u' '.join(word_count)))
