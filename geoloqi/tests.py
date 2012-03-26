"""
Tests for the geoloqi module.
"""
import json
import unittest
import urllib2

from mock import Mock, patch
from unittest import TestCase
from urllib2 import HTTPError, URLError

from geoloqi import Geoloqi, Session
from version import __version__


class GeoloqiTest(TestCase):
    @patch.object(Session, 'post')
    def setUp(self, mock_post):
        # Mock out Session.post to return a fake access_token.
        auth = {'access_token': 33187}
        mock_post.return_value = auth

        self.geoloqi = Geoloqi()

    def test_init(self):
        # Verify that we have valid credentials
        self.assertFalse(not self.geoloqi.access_token and \
                not (self.geoloqi.api_key and self.geoloqi.api_secret))

    @patch.object(Session, 'get')
    def test_get(self, mock_get):
        self.geoloqi.get('foo/bar')
        mock_get.assert_called_with('foo/bar', None, None)

        data = {'one': 1}
        headers = {'two': 2}
        self.geoloqi.get('foo/bar', data, headers)
        mock_get.assert_called_with('foo/bar', data, headers)

    @patch.object(Session, 'post')
    def test_post(self, mock_post):
        self.geoloqi.post('foo/bar')
        mock_post.assert_called_with('foo/bar', None, None)

        data = {'one': 1}
        headers = {'two': 2}
        self.geoloqi.post('foo/bar', data, headers)
        mock_post.assert_called_with('foo/bar', data, headers)

    @patch.object(Session, 'run')
    def test_run(self, mock_run):
        self.geoloqi.run('foo/bar')
        mock_run.assert_called_with('foo/bar', None, None)

        data = {'one': 1}
        headers = {'two': 2}
        self.geoloqi.run('foo/bar', data, headers)
        mock_run.assert_called_with('foo/bar', data, headers)


class SessionTest(TestCase):
    @patch.object(Session, 'post')
    def setUp(self, mock_post):
        # Mock out Session.post to return a fake access_token.
        auth = {'access_token': 33187}
        mock_post.return_value = auth

        self.session = Geoloqi().session

    def test_init(self):
        # Verify that we have valid credentials
        self.assertFalse(not self.session.access_token and \
                not (self.session.api_key and self.session.api_secret))

    @patch.object(Session, 'run')
    def test_get(self, mock_run):
        self.session.get('foo/bar')
        mock_run.assert_called_with('foo/bar', None, None)

        args = {'one': 1}
        headers = {'two': 2}
        self.session.get('foo/bar', args, headers)
        mock_run.assert_called_with('foo/bar?one=1', None, headers)

    @patch.object(Session, 'run')
    def test_post(self, mock_run):
        h = {
            'Content-Type': 'application/json',
        }

        mock = self.session.post('foo/bar')
        mock_run.assert_called_with('foo/bar', None, h)

        data = {'one': 1}
        headers = {'two': 2}
        headers.update(h)
        self.session.post('foo/bar', data, headers)
        mock_run.assert_called_with('foo/bar', data, headers)

    @patch.object(Session, 'execute')
    def test_run(self, mock_execute):
        # Ensure execute returns a sensible result
        result = Mock()
        result.read = Mock(return_value=json.dumps({'result': 'ok'}))
        mock_execute.return_value = result

        # Invoke run
        self.session.run('foo/bar')
        self.assertTrue(mock_execute.called)

        # Sanity check
        self.assertTrue(self.session.access_token is not None)

        # Verify call args
        args = mock_execute.call_args[0]
        self.assertEqual(args[0], 'foo/bar')
        self.assertEqual(args[1], None)
        self.assertTrue(args[2].has_key('User-Agent'))
        self.assertTrue(args[2].has_key('Authorization'))

        # Invoke run
        data = {'one': 1}
        headers = {'two': 2}
        self.session.run('foo/bar', data, headers)
        self.assertTrue(mock_execute.called)

        args = mock_execute.call_args[0]
        self.assertEqual(args[0], 'foo/bar')
        self.assertEqual(args[1], data)
        self.assertTrue(args[2].has_key('two'))

        # Unset asset_token and verify that the 'Authorization'
        # header is not added to the request.
        self.session.access_token = None
        self.session.auth = None

        self.session.run('foo/bar')
        self.assertTrue(mock_execute.called)

        args = mock_execute.call_args[0]
        self.assertFalse(args[2].has_key('Authorization'))

        # Verify that the run method will retry if execute returns
        # an expired_token response.
        result.read = Mock(return_value=json.dumps({'error': 'expired_token'}))
        mock_execute.return_value = result

        with patch.object(Session, 'renew_access_token') as mock_renew_access_token:
            self.session.run('foo/bar')
            self.assertTrue(mock_renew_access_token.called)

    @patch.object(urllib2, 'urlopen')
    def test_execute(self, mock_urlopen):
        # Test a basic request
        self.session.execute('foo/bar')
        self.assertTrue(mock_urlopen.called)

        request = mock_urlopen.call_args[0][0]
        self.assertEqual(request.get_full_url(),
                'https://api.geoloqi.com/1/foo/bar')
        self.assertEqual(request.data, None)
        self.assertEqual(request.headers, {})

        # Test a request with data and headers
        data = {'one': 1}
        headers = {'Timezone': 2}
        self.session.execute('foo/bar', data, headers)
        self.assertTrue(mock_urlopen.called)

        request = mock_urlopen.call_args[0][0]
        self.assertEqual(request.get_full_url(),
                'https://api.geoloqi.com/1/foo/bar')
        self.assertEqual(json.loads(request.data), data)
        self.assertEqual(request.headers, headers)

        # Ensure exceptions are caught and returned
        mock_urlopen.side_effect = HTTPError(request.get_full_url(),
                400, "", request.headers, None)

        e = self.session.execute('foo/bar')
        self.assertTrue(mock_urlopen.called)
        self.assertEqual(type(e), HTTPError)

        mock_urlopen.side_effect = URLError("")

        e = self.session.execute('foo/bar')
        self.assertTrue(mock_urlopen.called)
        self.assertEqual(type(e), URLError)

    @patch.object(Session, 'post')
    def test_establish(self, mock_post):
        auth = {'access_token': 33187}
        mock_post.return_value = auth

        self.session.establish({})

        # Assert that establish called post with the expected arguments
        mock_post.assert_called_with('oauth/token', {
            'client_id': self.session.api_key,
            'client_secret': self.session.api_secret,
        })

        # Ensure establish sets the access token correctly
        self.assertEqual(auth, self.session.auth)
        self.assertEqual(auth['access_token'], self.session.access_token)

    @patch.object(Session, 'establish')
    def test_renew_access_token(self, mock_establish):
        self.session.renew_access_token()

        # Assert that our mock method was called as expected
        mock_establish.assert_called_with({
            'grant_type': 'refresh_token',
            'refresh_token': self.session.auth.get('refresh_token'),
        })

    @patch.object(Session, 'establish')
    def test_get_access_token(self, mock_establish):
        self.assertEqual(self.session.access_token,
                self.session.get_access_token())

        # Verify that get_access_token calls establish if the
        # session has no access token.
        self.session.access_token = None
        self.session.get_access_token()
        mock_establish.assert_called_with({
            'grant_type': 'client_credentials',
        })
        self.assertEqual(self.session.access_token,
                self.session.get_access_token())

    def test_get_user_agent_string(self):
        ua = self.session.get_user_agent_string()

        self.assertTrue("geoloqi-python" in ua)
        self.assertTrue(__version__ in ua)


if __name__ == '__main__':
    unittest.main()
