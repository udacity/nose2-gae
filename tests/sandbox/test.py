import unittest


@unittest.skip('Sandbox not implemented')
class TestSandbox(unittest.TestCase):
    def test_import(self):
        # this should work
        import webapp2

    def test_restricted_import(self):
        def do_import():
            import webtest
        self.assertRaises(BaseException, do_import)

    def test_write_disallowed(self):
        def do_write():
            with open('temp.py', 'a') as f:
                f.write('# deleteme')
        self.assertRaises(BaseException, do_import)

    def test_read_not_allowed_from_staticfiles(self):
        def do_read():
            with open('static.txt', 'r') as f:
                f.readlines()
        self.assertRaises(BaseException, do_import)

    def test_read_not_allowed_from_skipped_files(self):
        def do_read():
            with open('skip.txt', 'r') as f:
                f.readlines()
        self.assertRaises(BaseException, do_import)

    def test_read_allowed(self):
        def do_read():
            with open(__file__, 'r') as f:
                f.readlines()
        do_read()

