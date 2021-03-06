# Natural Language Toolkit: Unit Tests
#
# Copyright (C) 2001 University of Pennsylvania
# Author: Edward Loper <edloper@gradient.cis.upenn.edu>
# URL: <http://nltk.sf.net>
# For license information, see LICENSE.TXT
#
# $Id: __init__.py,v 1.1.1.2 2004/09/29 21:58:13 adastra Exp $

"""
Unit tests for the NLTK modules.  These tests are intented to ensure
that changes that we make to NLTK's code don't accidentally introduce
bugs.

Each module in this package tests a specific aspect of NLTK.  Modules
are typically named for the module or class that they test (e.g.,
L{nltk.test.token} performs tests on the L{nltk.token} module).

This package can be run as a script from the command line, with the
following syntax::

    python nltk/test/__init__.py -v nltk/test/*.py

This command is called by the \"C{test}\" target in the NLTK Makefile.
"""

import sys, os, os.path, unittest, trace, StringIO, re

#######################################################################
# Test runner
#######################################################################

def testsuite():
    testsuites = []
    
    path = os.path.split(__file__)[0]
    for file in os.listdir(path):
        if not file.endswith('.py'): continue
        if file.startswith('__init__'): continue
        try: exec('import nltk.test.%s as m' % file[:-3])
        except: print 'Error importing %s' % file
        # Add unittest tests.
        if hasattr(m, 'testsuite'):
            testsuites.append(m.testsuite())

    return unittest.TestSuite(testsuites)

def test(verbosity=0):
    """
    Run unit tests for the NLP toolkit; print results to stdout/stderr.
    """
    # Ensure that the type safety level is set to full.
    import nltk.chktype
    nltk.chktype.type_safety_level(1000)
    
    global success
    runner = unittest.TextTestRunner(verbosity=verbosity)
    success = runner.run(testsuite()).wasSuccessful()

def test_coverage(verbosity, coverdir):
    tracer = trace.Trace(ignoredirs=[sys.prefix, sys.exec_prefix,],
                         trace=0, count=1)

    # This is something of a hack, so trace.Trace can get at test().
    import __main__
    __main__.test = test
    
    tracer.run('test(%d)' % verbosity)
    r = tracer.results()

    print 'Writing coverage results...'
    sys.stdout = StringIO.StringIO()
    r.write_results(show_missing=True, summary=True,
                    coverdir=coverdir)

    # Hack the summary output to look nicer.
    summary = sys.stdout.getvalue()
    sys.stdout = sys.__stdout__
    pp_summary(summary)

def pp_summary(summary):
    lines = []
    def subfunc(m):
        numlines = int(m.group(1))
        percent = int(m.group(2))
        module_name = os.path.abspath(m.group(3))
        module_name = module_name.replace('\\', '/')
        module_name = re.sub('.*/nltk/', 'nltk.', module_name)
        module_name = module_name.replace('/__init__.py', '')
        module_name = module_name.replace('/','.')
        module_name = module_name.replace('.py', '')
        if module_name.startswith('nltk.test'): return ''
        lines.append([percent, numlines, module_name])
    re.sub(' +(\S+) +(\S+)% +\S+ +\((\S*nltk\S+)\)\n', subfunc, summary)
    lines.sort()
    print
    print 'Coverage  Lines  Module'
    print '------------------------------------'
    for percent, numlines, module_name in lines:
        print '%5s%%   %5s   %s' % (percent, numlines, module_name)

def usage(name):
    print """
    Usage: %s [-v] [-c] coverdir
    """ % name
    return 0

def cli():
    """
    The command line interface for the NLP test suite.  Usage::

        python nltk/test/__init__.py [-v] [-c] 
    """
    verbosity = 0
    coverage = False
    coverdir = None

    for arg in sys.argv[1:]:
        if arg[:1] == '-':
            if arg[1:].lower() in ('v', 'verbose'):
                verbosity += 1
            elif arg[1:].lower() in ('c', 'coverage'):
                coverage = True
            else:
                sys.exit(usage(sys.argv[0]))
        else:
            if coverdir: sys.exit(usage(sys.argv[0]))
            coverdir = arg
    if coverage:
        test_coverage(verbosity, coverdir)
    else:
        test(verbosity)

    global success
    try: return success
    except: return -1

if __name__ == '__main__':
    cli()

