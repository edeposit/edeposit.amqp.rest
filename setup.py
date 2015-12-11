#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from setuptools import setup, find_packages
from docs import getVersion


# Variables ===================================================================
changelog = open('CHANGELOG.rst').read()
long_description = "\n\n".join([
    open('README.rst').read(),
    changelog
])


# Actual setup definition =====================================================
setup(
    name='edeposit.amqp.rest',
    version=getVersion(changelog),
    description="REST API to access Edeposit website.",
    long_description=long_description,
    url='https://github.com/edeposit/edeposit.amqp.rest/',

    author='Edeposit team',
    author_email='edeposit@email.cz',

    classifiers=[
        "Development Status :: 3 - Alpha",
        'Intended Audience :: Developers',

        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",

        "License :: OSI Approved :: MIT License",
    ],
    license='MIT',

    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['edeposit', 'edeposit.amqp'],

    scripts=[
        'bin/edeposit_rest_runzeo.py',
        'bin/edeposit_rest_webserver.py',
    ],

    zip_safe=False,
    include_package_data=True,
    install_requires=open("requirements.txt").read().splitlines(),

    test_suite='py.test',
    tests_require=["pytest"],
    extras_require={
        "test": [
            "pytest",
        ],
        "docs": [
            "sphinx",
            "sphinxcontrib-napoleon",
        ]
    },
)
