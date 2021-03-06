#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A tool to help keep .mailmap and AUTHORS up-to-date.
"""
# TODO:
# - Check doc/src/aboutus.rst
# - Make it easier to update .mailmap or AUTHORS with the correct entries.

import os
import sys

from fabric.api import local, env
from fabric.colors import yellow, blue, green
from fabric.utils import error

mailmap_update_path = os.path.abspath(__file__)
mailmap_update_dir = os.path.dirname(mailmap_update_path)
sympy_top = os.path.split(mailmap_update_dir)[0]
sympy_dir = os.path.join(sympy_top, 'sympy')

if os.path.isdir(sympy_dir):
    sys.path.insert(0, sympy_top)

from sympy.utilities.misc import filldedent

try:
    # Only works in newer versions of fabric
    env.colorize_errors = True
except AttributeError:
    pass

git_command = 'git log --format="%aN <%aE>" | sort -u'

git_people = unicode(local(git_command, capture=True), 'utf-8').strip().split("\n")

with open(os.path.realpath(os.path.join(__file__, os.path.pardir,
    os.path.pardir, "AUTHORS"))) as fd:
    AUTHORS = unicode(fd.read(), 'utf-8')

firstauthor = u"Ondřej Čertík"

authors = AUTHORS[AUTHORS.find(firstauthor):].strip().split('\n')

# People who don't want to be listed in AUTHORS
authors_skip = ["Kirill Smelkov <kirr@landau.phys.spbu.ru>"]

predate_git = 0

exit1 = False

print blue(filldedent("""Read the text at the top of AUTHORS and the text at
the top of .mailmap for information on how to fix the below errors.  If
someone is missing from AUTHORS, add them where they would have been if they
were added after their first pull request was merged ( checkout the merge
commit from the first pull request and see who is at the end of the AUTHORS
file at that commit."""))

print
print yellow("People who are in AUTHORS but not in git:")
print

for name in sorted(set(authors) - set(git_people)):
    if name.startswith("*"):
        # People who are in AUTHORS but predate git
        predate_git += 1
        continue
    exit1 = True
    print name

print
print yellow("People who are in git but not in AUTHORS:")
print

for name in sorted(set(git_people) - set(authors) - set(authors_skip)):
    exit1 = True
    print name

# + 1 because the last newline is stripped by strip()
authors_count = AUTHORS[AUTHORS.find(firstauthor):].strip().count("\n") + 1
adjusted_authors_count = (
    authors_count
    - predate_git
    + len(authors_skip)
    )
git_count = len(git_people)

print
print yellow("There are {git_count} people in git, and {adjusted_authors_count} "
    "(adjusted) people from AUTHORS".format(git_count=git_count,
    adjusted_authors_count=adjusted_authors_count))

if git_count != adjusted_authors_count:
    error("These two numbers are not the same!")
else:
    print
    print green(filldedent("""Congratulations. The AUTHORS and .mailmap files
appear to be up to date. You should now verify that doc/src/aboutus has %s
people.""" % authors_count))

if exit1:
    sys.exit(1)
