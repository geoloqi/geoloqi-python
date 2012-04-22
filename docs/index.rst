.. Geoloqi documentation master file, created by
   sphinx-quickstart on Mon Mar 12 17:51:40 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome
=======

Geoloqi is a powerful platform for real-time location, messaging, and
analytics. For more information visit `Geoloqi.com`_.

.. toctree::
   :maxdepth: 2

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

For more detailed information please see the :doc:`geoloqi` method documentation.

Examples
========
Get the active user's profile info:

::

    >>> from geoloqi.geoloqi import Geoloqi
    >>> g = Geoloqi(access_token="<your_user_access_token>")
    >>> g.get('account/profile')

Create a new sharing link:

::

    >>> from geoloqi.geoloqi import Geoloqi
    >>> g = Geoloqi(access_token="<your_user_access_token>")
    >>> g.post('link/create', {'minutes': 180,})

..

    Note: If you have created a config file with your Geoloqi credentials
    your access token may be omitted in the examples above.

Contributing
============
Please fork the project on `GitHub`_ and send us a pull request! If you have
a problem, please file an issue and we'll respond as soon as we can.

There are many other ways to `get support`_ from the Geoloqi `developers site`_.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Geoloqi.com: https://www.geoloqi.com/
.. _PyPi: http://pypi.python.org/pypi/geoloqi-python/
.. _get support: https://developers.geoloqi.com/support/
.. _developers site: https://developers.geoloqi.com/
.. _GitHub: https://github.com/geoloqi/geoloqi-python/
