# -*- coding: utf-8 -*-
import os

from setuptools import find_packages
from setuptools import setup


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='edc-sync',
    version='0.2.26',
    author=u'Erik van Widenfelt',
    author_email='ew2789@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/clinicedc/edc-sync',
    license='GPL license, see LICENSE',
    description='Sync models instances between client and server.',
    long_description=README,
    zip_safe=False,
    keywords='django data synchronization offline',
    install_requires=[
        'djangorestframework',
        'django-js-reverse',
        'django-cors-headers',
        'requests',
        'Faker',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Security :: Cryptography',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
