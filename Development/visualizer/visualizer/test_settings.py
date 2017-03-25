from visualizer.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_VERBOSE = True
TEST_OUTPUT_DESCRIPTIONS = True
TEST_OUTPUT_DIR = 'junit'
