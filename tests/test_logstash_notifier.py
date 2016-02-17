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

"""
Test logstash_notifier
"""

import json
import os
import subprocess
import threading
from time import sleep
from unittest import TestCase

from six.moves import socketserver


def strip_volatile(message):
    """
    Strip volatile parts (PID, datetime, host) from a logging message.
    """
    volatile = [
        '@timestamp',
        'host',
        'pid',
        'tries',
        'stack_info'
    ]
    message_dict = json.loads(message)
    for key in volatile:
        if key in message_dict:
            message_dict.pop(key)

    return message_dict


def record(eventname, from_state):
    """
    Returns a pre-formatted log line to save on the boilerplate
    """
    return {
        '@version': '1',
        'eventname': eventname,
        'from_state': from_state,
        'groupname': 'messages',
        'level': 'INFO',
        'logger_name': 'supervisor',
        'message': '%s messages' % eventname,
        'path': './logstash_notifier/__init__.py',
        'processname': 'messages',
        'tags': [],
        'type': 'logstash'
    }


class SupervisorLoggingTestCase(TestCase):

    """
    Test logging.
    """

    maxDiff = None

    def test_logging(self):
        """
        Test logging.
        """

        messages = []

        class LogstashHandler(socketserver.BaseRequestHandler):

            """
            Save received messages.
            """

            def handle(self):
                messages.append(self.request[0].strip().decode())

        logstash_server = socketserver.UDPServer(('0.0.0.0', 0), LogstashHandler)
        try:
            threading.Thread(target=logstash_server.serve_forever).start()

            env = os.environ.copy()
            env['LOGSTASH_SERVER'] = logstash_server.server_address[0]
            env['LOGSTASH_PORT'] = str(logstash_server.server_address[1])
            env['LOGSTASH_PROTO'] = 'udp'

            working_directory = os.path.dirname(__file__)

            conf = os.path.join(working_directory, 'supervisord.conf')
            supervisor = subprocess.Popen(
                ['supervisord', '-c', conf],
                env=env,
                cwd=os.path.dirname(working_directory),
            )

            try:
                sleep(3)

                subprocess.call(['supervisorctl', 'stop', 'messages'])
                # we've stopped a process so should get the first message
                # where it started, then a stopped message
                # thus: STOPPED->STARTING->STOPPING
                messages_stop = [
                    record('PROCESS_STATE_STARTING', 'STOPPED'),
                    record('PROCESS_STATE_RUNNING', 'STARTING'),
                    record('PROCESS_STATE_STOPPED', 'STOPPING'),
                ]
                self.assertEqual(
                    list(map(strip_volatile, messages)), messages_stop)
                messages = []

                subprocess.call(['supervisorctl', 'start', 'messages'])
                sleep(3)
                messages_start = [
                    record('PROCESS_STATE_STARTING', 'STOPPED'),
                    record('PROCESS_STATE_RUNNING', 'STARTING'),
                ]

                self.assertEqual(
                    list(map(strip_volatile, messages)), messages_start)
                messages = []

                subprocess.call(['supervisorctl', 'restart', 'messages'])
                sleep(3)
                messages_restarting = [
                    record('PROCESS_STATE_STOPPED', 'STOPPING'),
                    record('PROCESS_STATE_STARTING', 'STOPPED'),
                    record('PROCESS_STATE_RUNNING', 'STARTING'),
                ]
                self.assertEqual(
                    list(map(strip_volatile, messages)), messages_restarting)
            finally:
                supervisor.terminate()

        finally:
            logstash_server.shutdown()
