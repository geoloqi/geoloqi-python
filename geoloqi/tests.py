"""
Tests for the geoloqi module.
"""
import json
import unittest

from unittest import TestCase
from urllib2 import HTTPError

from geoloqi import Geoloqi, Session


class GeoloqiTest(TestCase):
    geoloqi = Geoloqi()

    def test_init(self):
        # Verify that we have valid credentials
        self.assertFalse(not self.geoloqi.access_token and \
                not (self.geoloqi.api_key and self.geoloqi.api_secret))

    def test_get(self):
        # Verify that an invalid request returns a dict
        r = self.geoloqi.get('foo/bar')
        self.assertTrue(r.has_key('error'))

        # Verify that a simple request is successful
        r = self.geoloqi.get('layer/list')
        self.assertTrue(r.has_key('layers'))

    def test_post(self):
        # Verify that an invalid request returns a dict
        r = self.geoloqi.post('foo/bar')
        self.assertTrue(r.has_key('error'))

        # Verify that a simple request is successful
        r = self.geoloqi.post('link/create', {'minutes': 1})
        self.assertTrue(r.has_key('link'))

    def test_run(self):
        # Verify that an invalid request returns a dict
        r = self.geoloqi.run('foo/bar')
        self.assertTrue(r.has_key('error'))

        # Verify that a simple request is successful
        r = self.geoloqi.post('layer/list')
        self.assertTrue(r.has_key('layers'))


class SessionTest(TestCase):
    session = Geoloqi().session

    def test_init(self):
        # Verify that we have valid credentials
        self.assertFalse(not self.session.access_token and \
                not (self.session.api_key and self.session.api_secret))

    def test_get(self):
        # Verify that an invalid request returns a dict
        r = self.session.get('foo/bar')
        self.assertTrue(r.has_key('error'))

        # Verify that a simple request is successful
        r = self.session.get('layer/list')
        self.assertTrue(r.has_key('layers'))

    def test_post(self):
        # Verify that an invalid request returns a dict
        r = self.session.post('foo/bar')
        self.assertTrue(r.has_key('error'))

        # Verify that a simple request is successful
        r = self.session.post('link/create', {'minutes': 1})
        self.assertTrue(r.has_key('link'))

        # Verify that another request is successful
        r = self.session.post('link/expire', {'token': r.get('token')})
        self.assertEqual(r.get('result'), 'ok')

    def test_run(self):
        # Verify that an invalid request returns a dict
        r = self.session.run('foo/bar')
        self.assertTrue(r.has_key('error'))

        # Verify that a simple request is successful
        r = self.session.run('layer/list')
        self.assertTrue(r.has_key('layers'))

    def test_execute(self):
        # Verify that an invalid request returns an error
        r = self.session.execute('foo/bar')
        self.assertEqual(type(r), HTTPError) 
        self.assertTrue(json.loads(r.read()).has_key('error'))

        # Verify that execute requests are not pre-processed or authorized
        r = self.session.execute('layer/list')
        self.assertEqual(r.code, 400)

    def test_establish(self):
        # TODO: Test this method!
        pass

    def test_renew_access_token(self):
        # TODO: Test this method!
        pass

    def get_access_token(self):
        self.assertEqual(self.session.access_token,
                self.session.get_access_token())


if __name__ == '__main__':
    unittest.main()
