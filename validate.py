## Script to validate schemata for integrations
## Author: Alex Kindel
## Date: 9 December 2015

import csv
import sys

ALLOWED_TYPES = ['text', 'category', 'date', 'link', 'multiple', 'default']

has_default = False

check = sys.argv[1]
with open(check, 'rU') as f:
    schema = csv.reader(f)
    for line in schema:
        # Update global schema constraints
        has_default = (line[1] == line[2] == 'default')

        # Check per-line constraints
        try:
            assert len(line) == 4
        except AssertionError:
            print "Line has a blank cell: %s" % repr(line)
        try:
            assert line[2] in ALLOWED_TYPES
        except AssertionError:
            print "Not a valid type: '%s'" % line[2]
            print "Valid types are: %s" % repr(ALLOWED_TYPES)

    # Check global constraints
    try:
        assert has_default
    except AssertionError:
        print "One or more pieces are missing."
