# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import glob
import io
import os
import re

import setuptools


def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()


setuptools.setup(
    name='datamonitor',
    version='0.0.5.post4',
    license='MIT',
    description='Python utility to monitor metadata KPI',
    long_description_content_type='text/x-rst',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='Denis Arnaud',
    author_email='denis.arnaud_fedora@m4x.org',
    url='https://github.com/infra-helpers/induction-monitoring/python',
    packages=setuptools.find_packages(),
    py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob.glob('datamonitor/*.py')],
    include_package_data=True,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    project_urls={
        'Documentation': 'https://datamonitoring.readthedocs.io/en/latest/',
        'Changelog': 'https://datamonitoring.readthedocs.io/en/latest/changelog.html',
        'Issue Tracker': 'https://github.com/infra-helpers/induction-monitoring/issues',
    },
    keywords=[
        'data', 'monitoring', 'data-monitoring', 'quality', 'quality-assurance',
        'qa', 'kpi', 'metric', 'sensor'
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    install_requires=[
        'elasticsearch',
        'elasticmock',
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    entry_points={
        'console_scripts': [
            'datamonitor = datamonitor.cli:main',
        ]
    },
)
