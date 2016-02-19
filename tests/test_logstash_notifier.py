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

import subprocess
from time import sleep

from .utilities import BaseSupervisorTestCase, record


class SupervisorLoggingTestCase(BaseSupervisorTestCase):
    """
    Test logging.
    """
    def test_logging(self):
        """
        Test logging.
        """
        logstash = self.run_logstash()
        try:
            environment = {
                'LOGSTASH_SERVER': logstash.server_address[0],
                'LOGSTASH_PORT': str(logstash.server_address[1]),
                'LOGSTASH_PROTO': 'udp'
            }

            self.run_supervisor(environment, 'supervisord.conf')
            sleep(3)

            try:
                subprocess.call(['supervisorctl', 'stop', 'messages'])
                # we've stopped a process so should get the first message
                # where it started, then a stopped message
                # thus: STOPPED->STARTING->STOPPING
                expected = [
                    record('PROCESS_STATE_STARTING', 'STOPPED'),
                    record('PROCESS_STATE_RUNNING', 'STARTING'),
                    record('PROCESS_STATE_STOPPED', 'STOPPING'),
                ]
                self.assertEqual(self.messages(clear_buffer=True), expected)
                self.clear_message_buffer()

                subprocess.call(['supervisorctl', 'start', 'messages'])
                sleep(3)
                expected = [
                    record('PROCESS_STATE_STARTING', 'STOPPED'),
                    record('PROCESS_STATE_RUNNING', 'STARTING'),
                ]

                self.assertEqual(self.messages(clear_buffer=True), expected)
                self.clear_message_buffer()

                subprocess.call(['supervisorctl', 'restart', 'messages'])
                sleep(3)
                expected = [
                    record('PROCESS_STATE_STOPPED', 'STOPPING'),
                    record('PROCESS_STATE_STARTING', 'STOPPED'),
                    record('PROCESS_STATE_RUNNING', 'STARTING'),
                ]
                self.assertEqual(self.messages(clear_buffer=True), expected)
            finally:
                self.shutdown_supervisor()
        finally:
            self.shutdown_logstash()
