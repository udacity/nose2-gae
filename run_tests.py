#!/usr/bin/env python
import os
from os import path

test_dir = path.abspath(path.join(path.dirname(__file__), 'tests'))

for testcase in os.listdir(test_dir):
    testcase_dir = path.join(test_dir, testcase)
    if not path.isdir(testcase_dir): continue
    os.chdir(testcase_dir)
    config_file = 'nose2.cfg' if path.isfile('nose2.cfg') else '../nose2.cfg'
    result = os.system('nose2 --config %s' % config_file)
    assert result == 0, 'Test %s failed with exitcode %d' % (testcase, result)

