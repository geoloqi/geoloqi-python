Geoloqi is a powerful platform for real-time location, messaging, and
analytics. For more information visit `Geoloqi.com`_.

Features
========

- Full test suite!

Requirements
============

- Mock (for tests)

Getting Started
===============
You can install the library directly from `PyPi`_ with pip.

::

    $ pip install geoloqi-python

You can create a config file that holds your client credentials. If you do
so you won't have to provide them when instantiating a new Geoloqi object.
The config file can be in the current user's home directory as ``.geoloqi``
or in the system ``/etc/geoloqi/geoloqi.config``.

The configuration file should have the following format:

::

    [Credentials]
    user_access_token = <your_user_access_token>
    application_access_key = <client_api_key>
    application_secret_key = <client_api_secret>

You must provide either your user access token or your application's access key
and secret. Either can be obtained from the Geoloqi `developers site`_.

Examples
========
Create a geotrigger:

::

    >>> from geoloqi.geoloqi import Geoloqi
    >>> g = Geoloqi(access_token="<your_application_access_token>")
    >>> g.post('trigger/create', {'place_name': "Powell's Books", "type": "message", "latitude": 45.523334, "longitude": -122.681612, "radius": 150, "text": "Welcome to Powell's Books!"})

Create a new sharing link:

::

    >>> from geoloqi.geoloqi import Geoloqi
    >>> g = Geoloqi(access_token="<your_application_access_token>")
    >>> g.post('link/create', {'minutes': 180,})

..

    Note: If you have created a config file with your Geoloqi credentials
    your access token may be omitted in the examples above.

Documentation
=============
Full documentation is available on `Read the Docs`_.

Contributing
============
Please fork the project on `GitHub`_ and send us a pull request! If you have
a problem, please file an issue and we'll respond as soon as we can.

There are many other ways to `get support`_ from the Geoloqi `developers site`_.

Testing
-------
Before you submitting a patch or a pull request please make sure
you've written a test and run the full test suite.

::

    $ python geoloqi/tests.py

..

    Note: You must create a config file containing your Geoloqi credentials
    before you are able to run tests!

License
=======
See the LICENSE file.

.. _Geoloqi.com: https://www.geoloqi.com/
.. _PyPi: http://pypi.python.org/pypi/geoloqi-python/
.. _get support: https://developers.geoloqi.com/support/
.. _developers site: https://developers.geoloqi.com/
.. _Read the Docs: http://readthedocs.org/docs/geoloqi-python/en/latest/
.. _GitHub: https://github.com/geoloqi/geoloqi-python/
