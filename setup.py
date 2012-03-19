from distutils.core import setup

# Get the version number
execfile('geoloqi/version.py')

readme = open('README.rst')

setup(
    name='geoloqi-python',
    version=__version__,
    description='A powerful platform for mobile location, messaging and analytics.',
    long_description=readme.read(),
    author='Tristan Waddington',
    author_email='tristan.waddington@gmail.com',
    url='https://github.com/twaddington/geoloqi-python',
    packages=['geoloqi',],
    classifiers=[
        'Development Status :: 4 - Beta', # 4 Beta, 5 Production/Stable
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
