"""
Setup script.
"""

from setuptools import setup

with open('requirements.txt') as requirements:
    setup(
        name='supervisord-syslog-notifier',
        version='0.0.1',
        description='Stream supervisord events to a logstash/syslog instance',
        author='Dohop hf.',
        author_email='info@dohop.com',
        url='https://github.com/dohop/supervisord-syslog-notifier',
        license='Apache 2.0',
        long_description=open('README.md').read(),
        entry_points={
            'console_scripts': [
                'supervisord_syslog_notifier = supervisord_syslog_notifier:main',
            ],
        },

        install_requires=requirements.read().splitlines()
    )