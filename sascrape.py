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

from scrape import *

def forumfrompost(r):
    pass

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] > stats"
    parser = OptionParser(usage=usage)
    parser.add_option('-u', '--username', default='')
    parser.add_option('-p', '--password', default='')
    parser.add_option('-g', '--guest', default=False, action='store_true',
            help='Do not log in and scrape anonymously')
    parser.add_option('-n', '--page-number', default=1, type='int')

    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.print_help()
        return 2

    duration_regex = re.compile('\d+ (day|year|month|week|hour)s?', re.IGNORECASE)

    # do stuff
    if not options.guest:
        creds = {'username': options.username if options.username else raw_input('username: '),
                 'password': options.password if options.password else getpass('password: ')}

        login = s.go('http://forums.somethingawful.com/account.php?action=loginform')
        userpage = s.submit(login.first('form', class_='login_form'), paramdict=creds)

    lepers = s.go('http://forums.somethingawful.com/banlist.php?pagenumber=%d'
            % options.page_number)

    # always skip the first row (just header)
    for row in lepers.first('table', class_='standard full').all('tr')[1:]:

        thread_anchor = row.first('td').first('a')
        bantype, date, username, reason, requestedby, approvedby = \
                [x.text for x in row.all('td')]

        try:
            duration = re.search(duration_regex, reason).group(0)
        except AttributeError:
            sys.stderr.write('No duration! "%s"\n' % reason)
            duration = 'NA'

        print('%s\t%s\t%s\t%s' % (username, bantype, duration, thread_anchor['href']))

if __name__ == '__main__':
    sys.exit(main())
