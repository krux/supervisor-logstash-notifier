#
# Copyright 2016 Dohop hf.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from setuptools import setup

with open('requirements.txt') as requirements:
	setup(
		name='supervisord-syslog-notifier',
		version='0.0.1',
		packages=['syslog_notifier'],
		url='https://github.com/dohop/supervisord-syslog-notifier',
		license='Apache 2.0',
		author='alexander',
		author_email='alexander@dohop.com',
		description='Stream supervisord events to a logstash/syslog instance',
		long_description=open('README.md').read(),
		entry_points={
			'console_scripts': [
				'syslog_notifier = syslog_notifier:main'
			]
		},
		install_requires=requirements.read().splitlines(),
	)
