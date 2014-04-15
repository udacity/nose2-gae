"""
Runs the unittests inside of the Google App Engine development server sandbox.

This is the unofficial descendant of the [NoseGAE plugin](https://github.com/Trii/NoseGAE) rewritten
to work with nose2.
"""
import inspect
import os
import sys
import time

from nose2 import events


# nose2 doesn't do multithreading (yet) so this is safe
_GAE_TESTBED = None

def getGaeTestbed():
    return _GAE_TESTBED


_NO_INDEX_CHECK_NEEDED = set()

def indexesOptional(f):
    """Decorate test methods with this if you don't require strict index checking"""
    stack = inspect.stack()
    _NO_INDEX_CHECK_NEEDED.add('%s.%s.%s' % (f.__module__, stack[1][3], f.__name__))
    del stack
    return f


class Nose2GAE(events.Plugin):
    configSection = 'nose2-gae'
    commandLineSwitch = (None, 'with-gae', 'Run tests inside the Google Appengine sandbox')

    def __init__(self):
        self._gae_path = os.path.abspath(
            self.config.as_str('lib-root', '/usr/local/google_appengine'))
        appserver_py = os.path.join(self._gae_path, 'dev_appserver.py')
        if not os.path.isfile(appserver_py):
            raise ValueError(
                'Invalid path for the Google Appengine SDK - %s not found' % appserver_py)

        self._gae_app_path = os.path.abspath(self.config.as_str(
            'application', self.session.topLevelDir or self.session.startDir))
        if not os.path.isfile(os.path.join(self._gae_app_path, 'app.yaml')):
            raise ValueError('app.yaml not found in %s' % self._gae_app_path)

        self._gae_stubs_to_enable = self.config.as_list(
            'stubs',
            ['app_identity', 'blobstore', 'capability', 'channel', 'datastore_v3', 'files',
                'images', 'logservice', 'mail', 'memcache', 'taskqueue', 'urlfetch', 'user', 'xmpp',
                'search', 'modules'
            ]
        )
        if self.config.as_bool('skip-image-stub', False):
            self._gae_stubs_to_enable = [s for s in self._gae_stubs_to_enable if s != 'images']

        self._gae_datastore_consistency_policy = self.config.as_str(
            'datastore-consistency-policy')
        self._gae_datastore_require_indexes = self.config.as_bool('datastore-require-indexes', True)

        self._gae_testbed_env = {}
        for env in self.config.as_list('testbed-env', []):
            k, v = env.split('=', 1)
            self._gae_testbed_env[k] = eval(v)

        # TODO
        self._gae_disable_sandbox = self.config.as_bool('without-sandbox', False)

        self._gae_testbed_inited = False

    def createTests(self, event):
        self._startGaeTestbed()

    def registerInSubprocess(self, event):
        event.pluginClasses.append(self.__class__)

    def startSubprocess(self, event):
        self._startGaeTestbed()

    def startTest(self, event):
        self._startGaeTestbed(indexes_optional=event.test.id() in _NO_INDEX_CHECK_NEEDED)
        # this is normally done by the sandbox
        self._original_dir = os.path.abspath(os.getcwd())
        os.chdir(self._gae_app_path)

    def testOutcome(self, event):
        self._stopGaeTestbed()
        os.chdir(self._original_dir)
        self._original_dir = None

    def _initGaeTestbed(self):
        # we want to put GAE sys path right at the front, not at the second place as GAE SDK does
        # to prevent system-local imports if the test is not run in an isolated virtualenv (as it
        # should!)
        original_sys_paths = list(sys.path)
        sys.path.insert(0, self._gae_path)
        import dev_appserver
        dev_appserver.fix_sys_path()
        new_sys_paths = [p for p in sys.path if p not in original_sys_paths]
        sys.path = [self._gae_app_path] + new_sys_paths + original_sys_paths

        # set time to UTC, as it is on GAE
        os.environ['TZ'] = 'UTC'
        time.tzset()

        from google.appengine.ext import testbed
        self._testbed_module = testbed

        from google.appengine.datastore import datastore_stub_util
        self._datastore_stub_util_module = datastore_stub_util

    def _startGaeTestbed(self, indexes_optional=False):
        if not self._gae_testbed_inited:
            self._initGaeTestbed()
            self._gae_testbed_inited = True

        global _GAE_TESTBED
        if _GAE_TESTBED:
            return
        _GAE_TESTBED = self._testbed_module.Testbed()
        _GAE_TESTBED.setup_env(**self._gae_testbed_env)
        _GAE_TESTBED.activate()

        special_stubs = set(['taskqueue', 'datastore_v3']) # these require special initialization
        for stub_name in self._gae_stubs_to_enable:
            if stub_name in special_stubs:
                continue
            getattr(_GAE_TESTBED, 'init_%s_stub' % stub_name)()

        consistency_policy = None
        if self._gae_datastore_consistency_policy:
            consistency_policy = eval(
                'self._datastore_stub_util_module.%s' % self._gae_datastore_consistency_policy)
        require_indexes = self._gae_datastore_require_indexes and not indexes_optional
        _GAE_TESTBED.init_datastore_v3_stub(
            consistency_policy=consistency_policy, require_indexes=require_indexes,
            use_sqlite=True, root_path=self._gae_app_path if require_indexes else None)

        _GAE_TESTBED.init_taskqueue_stub(root_path=self._gae_app_path)

    def _stopGaeTestbed(self):
        global _GAE_TESTBED
        _GAE_TESTBED.deactivate()
        _GAE_TESTBED = None
