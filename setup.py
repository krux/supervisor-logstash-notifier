from setuptools import setup

setup(
	name='supervisord-syslog-notifier',
	version='0.0.1',
	packages=['syslog_notifier'],
	url='https://github.com/dohop/supervisord-syslog-notifier',
	license='Apache 2.0',
	author='alexander',
	author_email='alexander@dohop.com',
	description='Stream supervisord events to a logstash/syslog instance',
	entry_points={
		'console_scripts': [
			'syslog_notifier = syslog_notifier:main'
		]
	},
)
