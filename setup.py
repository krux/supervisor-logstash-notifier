"""
Setup script.
"""

from setuptools import setup, find_packages

with open('requirements.txt') as requirements:
    setup(
        name='supervisord-syslog-notifier',
        version='0.0.1',
        description='Stream supervisord events to a logstash/syslog instance',
        author='Dohop hf.',
        author_email='devs@infoxchange.net.au',
        url='https://github.com/dohop/supervisord-syslog-notifier',
        license='Apache 2.0',
        long_description=open('README.md').read(),

        packages=find_packages(exclude=['tests']),
        package_data={
            'forklift': [
                'README.md',
                'requirements.txt',
                'test_requirements.txt',
            ],
        },
        entry_points={
            'console_scripts': [
                'supervisord_syslog_notifier = supervisord_syslog_notifier:main',
            ],
        },

        install_requires=requirements.read().splitlines()
    )