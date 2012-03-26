import json
import os
import sys
import urllib
import urllib2

from ConfigParser import ConfigParser, NoOptionError
from version import __version__
from urllib2 import HTTPError, URLError

API_VERSION = 1
API_URL_BASE_TEMPLATE = 'https://api.geoloqi.com/%d/%s'


class Geoloqi:
    """
    A simple interface wrapper for the Geoloqi API.
    """
    config = None
    api_key = None
    api_secret = None
    access_token = None
    session = None

    def __init__(self, api_key=None, api_secret=None, access_token=None):
        """
        Initializes a new instance of the Geoloqi API wrapper.
        
        Application credentials can be provided as kwargs or in a config
        file. Clients *must* provide either a user access_token or an
        application api_key and api_secret. Application credentials can be
        obtained from the Geoloqi developer site.

        Credentials can be provided in a config file in the user's home
        directory named `.geoloqi` or in the system directory
        `/etc/geoloqi/geoloqi.cfg`. In either case, config files should
        use the following format.

        ::

            [Credentials]
            user_access_token = <your_user_access_token>
            application_access_key = <client_api_key>
            application_secret_key = <client_api_secret>

        If both a user access_token *and* a set of client application
        credentials are provided, the user access token will be used.

        Args:
            api_key: Your application's Geoloqi API key.
            api_secret: Your application's Geoloqi API secret.
            access_token: Your personal user access token.

        Raises:
            ValueError: If the proper client credentials were not provided.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token

        # Parse any config files
        self.config = ConfigParser()
        self.config.read(['/etc/geoloqi/geoloqi.cfg', os.path.expanduser('~/.geoloqi')])

        if not self.api_key:
            try:
                self.api_key = self.config.get('Credentials', 'application_access_key')
            except NoOptionError:
                pass
        if not self.api_secret:
            try:
                self.api_secret = self.config.get('Credentials', 'application_secret_key')
            except NoOptionError:
                pass
        if not self.access_token:
            try:
                self.access_token = self.config.get('Credentials', 'user_access_token')
            except NoOptionError:
                pass

        # Determine if Credentials exist
        if not self.access_token and not (self.api_key and self.api_secret):
            raise ValueError('Missing application credentials or a valid user access token!')

        # Create our session
        self.session = Session(self.api_key, self.api_secret, self.access_token)

    def get(self, path, args={}, headers={}):
        """
        Make a GET request to the Geoloqi API server.

        Args:
            path: Path to the resource being requested (example: 'account/profile')
            args: An optional dictonary of GET arguments.
            headers: An optional dictonary of extra headers to send with the request.

        Returns:
            The JSON response as a dictionary.
        """
        return self.session.get(path, args, headers)

    def post(self, path, data={}, headers={}):
        """
        Make a POST request to the Geoloqi API server.

        Args:
            path: Path to the resource being requested (example: 'account/profile')
            data: An optional dictonary to be sent to the server as a POST.
            headers: An optional dictonary of extra headers to send with the request.

        Returns:
            The JSON response as a dictionary.
        """
        return self.session.post(path, data, headers)

    def run(self, path, data=None, headers={}):
        """
        Make a request to the Geoloqi API server.

        Args:
            path: Path to the resource being requested (example: 'account/profile')
            data: An optional dictonary to be sent to the server as a POST.
            headers: An optional dictonary of extra headers to send with the request.

        Returns:
            The JSON response as a dictionary.
        """
        return self.session.run(path, data, headers)


class Session:
    """
    This class represents a session with the Geoloqi API.
    """
    api_key = None
    api_secret = None
    access_token = None
    auth = None

    retry_attempt = 0

    def __init__(self, api_key=None, api_secret=None, access_token=None):
        """
        Create a new Geoloqi API session.

        Args:
            api_key: Your application's Geoloqi API key.
            api_secret: Your application's Geoloqi API secret.
            access_token: Your personal user access token.

        Raises:
            ValueError: If the proper client credentials were not provided.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token

        # Verify the Session has the needed Credentials
        if not self.access_token and not (self.api_key and self.api_secret):
            raise ValueError('A Session requires a set of application credentials'\
                    + ' or a valid user access token!')

        # Get an access token
        if not self.access_token:
            self.get_access_token()

    def get(self, path, args={}, headers={}):
        """
        Make a GET request to the Geoloqi API server.

        Args:
            path: Path to the resource being requested (example: 'account/profile')
            args: An optional dictonary of GET arguments.
            headers: An optional dictonary of extra headers to send with the request.

        Returns:
            The JSON response as a dictionary.
        """
        if len(args) > 0:
            path = "%s?%s" % (path, urllib.urlencode(args))

        return self.run(path, None, headers)

    def post(self, path, data={}, headers={}):
        """
        Make a POST request to the Geoloqi API server.

        Args:
            path: Path to the resource being requested (example: 'account/profile')
            data: An optional dictonary to be sent to the server as a POST.
            headers: An optional dictonary of extra headers to send with the request.

        Returns:
            The JSON response as a dictionary.
        """
        headers.update({
            'Content-Type': 'application/json',
        })

        return self.run(path, data, headers)

    def run(self, path, data=None, headers={}):
        """
        Make a request to the Geoloqi API server.

        Args:
            path: Path to the resource being requested (example: 'account/profile')
            data: An optional dictonary to be sent to the server as a POST.
            headers: An optional dictonary of extra headers to send with the request.

        Returns:
            The JSON response as a dictionary.
        """
        # Update the request headers
        headers.update({
            'User-Agent': self.get_user_agent_string(),
        })

        # Authorize the request
        if self.access_token:
            headers.update({'Authorization': 'OAuth %s' % self.access_token,})

        # Execute request
        f = self.execute(path, data, headers)
        raw = f.read()

        # Parse response
        response = json.loads(raw)
        if response.has_key('error'):
            error = response.get('error')

            if error == 'expired_token':
                # Our access token has expired
                if self.retry_attempt < 1:
                    self.renew_access_token()

                    # Retry the request
                    self.retry_attempt += 1
                    return self.run(path, data, headers)
                else:
                    # TODO: Failed to refresh the access token!
                    pass
            else:
                # TODO: Throw or log the error?
                pass

        # Reset our retry counter
        self.retry_attempt = 0

        return response

    def execute(self, path, data=None, headers={}):
        """
        Makes a low-level request to the Geoloqi API server. Does no
        processing of the response.

        Args:
            path: Path to the resource being requested (example: 'account/profile')
            data: An optional dictonary to be sent to the server as a POST.
            headers: An optional dictonary of extra headers to send with the request.

        Returns:
            A file like object returned from `urllib2.urlopen`.
        """
        if data is not None:
            data = json.dumps(data)

        request = urllib2.Request(API_URL_BASE_TEMPLATE % (API_VERSION, path),
                data, headers=headers)

        # Execute the request
        try:
            return urllib2.urlopen(request)
        except (HTTPError, URLError), e:
            return e

    def establish(self, data):
        """
        Used to retrieve the access token from the Geoloqi OAuth2 server. This
        is used internally and you shouldn't need to call it manually.

        Args:
            data: A dictionary of data to be included with the request. You should
                  include the OAuth2 'grant_type' and other data like your
                  refresh token.

        Returns:
            None
        """
        data.update({
            'client_id': self.api_key,
            'client_secret': self.api_secret,
        })

        self.auth = self.post('oauth/token', data)
        self.access_token = self.auth.get('access_token')

    def renew_access_token(self):
        """
        Renew the access token using the stored refresh token. This method is
        called automatically when the server returns an expired_token response,
        so you shouldn't need to call it manually.

        Returns:
            None
        """
        self.establish({
            'grant_type': 'refresh_token',
            'refresh_token': self.auth.get('refresh_token'),
        })

    def get_access_token(self):
        """
        Retrieve an access token for this session. This token is used in
        the same manner as the user access token, it simply allows the
        application to make requests on the behalf of itself instead of a
        user within the app.

        This call makes a request to the API server once for each instantiation
        of the object, then cache the result on the object.

        Returns:
            The current access token as a String.
        """
        if not self.access_token:
            self.establish({
                'grant_type': 'client_credentials',
            })
        return self.access_token

    def get_user_agent_string(self):
        """
        Retrieve a 'User-Agent' string to be used when making API requests.

        Returns:
            The 'User-Agent' string.
        """
        return 'geoloqi-python %s' % __version__


if __name__ == "__main__":
    # TODO: Write a `main` method that enables simple command-line
    #       access to the Geoloqi API.
    sys.exit()
