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
            # clear the messages from when supervisor started the script
            self.clear_message_buffer()

            try:
                subprocess.call(['supervisorctl', 'stop', 'messages'])
                sleep(3)
                expected = [
                    record('PROCESS_STATE_STOPPED', 'STOPPING'),
                ]
                self.assertEqual(self.messages(clear_buffer=True), expected)

                subprocess.call(['supervisorctl', 'start', 'messages'])
                sleep(3)
                expected = [
                    record('PROCESS_STATE_STARTING', 'STOPPED'),
                    record('PROCESS_STATE_RUNNING', 'STARTING'),
                ]

                self.assertEqual(self.messages(clear_buffer=True), expected)

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


class SupervisorEnvironmentLoggingTestCase(BaseSupervisorTestCase):
    """
    Test case for logging extra environment variables
    """

    def _test_environment_logging(self, include=None):
        """
        test logging of env variables
        """
        logstash = self.run_logstash()
        try:
            environment = {
                'LOGSTASH_SERVER': logstash.server_address[0],
                'LOGSTASH_PORT': str(logstash.server_address[1]),
                'LOGSTASH_PROTO': 'udp'
            }
            if include is not None:
                environment.update(include)

            self.run_supervisor(environment, 'supervisord_env_logging.conf')
            sleep(3)
            self.clear_message_buffer()

            try:
                subprocess.call(['supervisorctl', 'stop', 'messages'])
                sleep(3)

                received = self.messages(clear_buffer=True)
                # should only have the 'stopping' message
                self.assertTrue(len(received) == 1)
                message = received[0]

                yield message
            finally:
                self.shutdown_supervisor()
        finally:
            self.shutdown_logstash()

    def test_not_present(self):
        """
        If the logger is configured to add two environment variables, FRUITS
        and VEGETABLES, but neither is set, we shouldn't get anything extra
        """
        for message in self._test_environment_logging({}):
            # should have no additional added values since we asked for an
            # empty dict to be added
            self.assertTrue('env_vars' not in message)

    def test_only_one_value_set(self):
        """
        If only one of them is set, we should only see that one in the logged
        message
        """
        env = {
            'FRUITS': 'pineapple,raspberry,kiwi'
        }
        for message in self._test_environment_logging(env):
            self.assertTrue('env_vars' in message)
            self.assertDictContainsSubset(env, message['env_vars'])

    def test_both_values_set(self):
        """
        If both of them is set, we should get both returned in the logged
        message
        """
        env = {
            'FRUITS': 'pineapple,raspberry,kiwi',
            'VEGETABLES': 'sweet potato,leek,mushroom'
        }
        for message in self._test_environment_logging(env):
            self.assertTrue('env_vars' in message)
            self.assertDictContainsSubset(env, message['env_vars'])
