import unittest

from google.appengine.ext import db

import nose2gae


class Person(db.Model):
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    city = db.TextProperty()
    birth_year = db.IntegerProperty()
    height = db.IntegerProperty()


class TestIndexes(unittest.TestCase):
    def setUp(self):
        Person(last_name='Smith', height=10, city='FizzBuzz').put()

    def testIndexed(self):
        q = Person.all()
        q.filter('last_name =', 'Smith')
        q.filter('height <=', 11)
        q.order('-height')
        self.assertEquals(1, len(list(q.run())))

    def testNonIndexed(self):
        q = Person.all()
        q.filter('city =', 'FizzBuzz')
        q.filter('height <=', 11)
        q.order('-height')
        self.assertRaises(BaseException, lambda l: list(l), q.run())

    @nose2gae.indexesOptional
    def testNonIndexedAnnotated(self):
        q = Person.all()
        q.filter('city =', 'FizzBuzz')
        q.filter('height <=', 11)
        q.order('-height')
        # won't raise an exception but alsow won't reeturn the correct answer
        list(q.run())
