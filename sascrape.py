#!/usr/bin/env python
#
# Scrape SA.
#
# TODO:
# * make login work
# * parse forum name from post
# * find and follow "next" button
#

import sys
from optparse import OptionParser
import re
import time
import random

from scrape import *

def forumfrompost(row):
    """Given a row from the Leper's Colony return string representing the forums
    and subforums for the given thread."""
    try:
        thread_anchor = row.first('td').first('a')
        thread = s.follow(thread_anchor.content, row)
        breadcrumb_anchors = thread.first('div', class_='breadcrumbs').all('a')
        s.back()
        return ' > '.join([x.text for x in breadcrumb_anchors])
    except ScrapeError:
        return 'Must login to get forum! (%s)' % s.url

def randsleep(n):
    time.sleep(random.random() * n)

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] > stats 2> log"
    parser = OptionParser(usage=usage)
    parser.add_option('-u', '--username', default='')
    parser.add_option('-p', '--password', default='')
    parser.add_option('-g', '--guest', default=False, action='store_true',
            help='Do not log in and scrape anonymously')
    parser.add_option('-n', '--page-number', default=1, type='int')
    parser.add_option('-d', '--num-pages-to-parse', default=1, type='int')
    parser.add_option('-r', '--row-sleep-time', default=2, type='int')
    parser.add_option('-t', '--page-sleep-time', default=5, type='int')

    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.print_help()
        return 2

    duration_regex = re.compile('\d+ (day|year|month|week|hour)s?', re.IGNORECASE)

    # do stuff
    if not options.guest:
        params = {'username': options.username if options.username else raw_input('username: '),
                 'password': options.password if options.password else getpass('password: '),
                 'action': 'login',
                 'next': '/'}

        login = s.go('http://forums.somethingawful.com/account.php?action=loginform')
        userpage = s.submit(login.first('form', class_='login_form'), paramdict=params)

    for pagenum in range(options.page_number, options.page_number + options.num_pages_to_parse):
        lepers = s.go('http://forums.somethingawful.com/banlist.php?pagenumber=%d'
                % pagenum)

        sys.stderr.write('Begin parsing #%d\n' % pagenum)

        # always skip the first row (just header)
        for row in lepers.first('table', class_='standard full').all('tr')[1:]:

            bantype, date, username, reason, requestedby, approvedby = \
                    [x.text for x in row.all('td')]

            try:
                duration = re.search(duration_regex, reason).group(0)
            except AttributeError:
                sys.stderr.write('No duration! "%s"\n' % reason)
                duration = 'NA'

            print('%s\t%s\t%s\t%s' % (username, bantype, duration, forumfrompost(row)))
            randsleep(options.row_sleep_time)

        sys.stderr.write('Finished parsing #%d\n' % pagenum)
        randsleep(options.page_sleep_time)

if __name__ == '__main__':
    sys.exit(main())
