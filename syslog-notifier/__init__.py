#!/usr/bin/env python

import logging
import os
import re
import sys
import socket
import time
from supervisor import childutils
from logging.handlers import SysLogHandler


class PalletFormatter(logging.Formatter):
	"""
	A formatter for the Pallet environment.
	"""

	HOSTNAME = re.sub(r':\d+$', '', os.getenv('SITE_DOMAIN', socket.gethostname()))
	FORMAT = '%(asctime)s {hostname} %(name)s[%(process)d]: %(message)s'.format(hostname=HOSTNAME)
	DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

	converter = time.gmtime

	def __init__(self):
		super(PalletFormatter, self).__init__(fmt=self.FORMAT, datefmt=self.DATE_FORMAT)

	def formatTime(self, record, datefmt=None):
		"""
		Format time, including milliseconds.
		"""

		formatted = super(PalletFormatter, self).formatTime(
			record, datefmt=datefmt)
		return formatted + '.%03dZ' % record.msecs

	def format(self, record):
		# strip newlines
		message = super(PalletFormatter, self).format(record)
		message = message.replace('\n', ' ')
		message += '\n'
		return message


def supervisor_events(stdin, stdout, *events):
	while True:
		childutils.listener.ready()

		headers, payload = childutils.listener.wait(stdin, stdout)
		event_headers, event_data = childutils.eventdata(payload+'\n')
		
		if headers['eventname'] not in events:
			childutils.listener.ok(stdout)
			continue

		yield event_headers, event_data

		childutils.listener.ok(stdout)


def main():
	"""
	Main application loop.
	"""
	try:
		host = os.getenv('SYSLOG_SERVER')
		port = int(os.getenv('SYSLOG_PORT'))
		socket_type = socket.SOCK_DGRAM if os.getenv('SYSLOG_PROTO') == 'udp' else socket.SOCK_STREAM
	except KeyError:
		sys.exit("SYSLOG_SERVER, SYSLOG_PORT and SYSLOG_PROTO are required.")

	events = ['BACKOFF', 'FATAL', 'EXITED', 'STOPPED', 'STARTING', 'RUNNING']
	events = ['PROCESS_STATE_'+state for state in events]
	handler = SysLogHandler(address=(host, port), socktype=socket_type, *events)

	for event_headers, event_data in supervisor_events(sys.stdin, sys.stdout):
		event = logging.LogRecord(
			name=event_headers['processname'],
			level=logging.INFO,
			pathname=None,
			lineno=0,
			msg=event_data,
			args=(),
			exc_info=None,
		)
		event.process = int(event_headers['pid'])
		handler.handle(event)

if __name__ == '__main__':
	main()