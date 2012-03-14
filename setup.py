from distutils.core import setup

readme = open('README.rst')

setup(
    name='geoloqi-python',
    version='1.0.1',
    description='A powerful platform for mobile location, messaging and analytics.',
    long_description=readme.read(),
    author='Tristan Waddington',
    author_email='tristan.waddington@gmail.com',
    url='https://github.com/twaddington/geoloqi-python',
    packages=['geoloqi',],
    package_data={'': ['README.rst']},
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
