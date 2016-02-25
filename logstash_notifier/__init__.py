#!/usr/bin/env python
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
A module for dispatching Supervisor PROCESS_STATE events to a Syslog instance
"""

import argparse
import logging
import os
import signal
import sys
import warnings

import logstash


def get_headers(line):
    """
    Parse Supervisor message headers.
    """
    return dict([x.split(':') for x in line.split()])


def eventdata(payload):
    """
    Parse a Supervisor event.
    """
    if '\n' in payload:
        headerinfo, data = payload.split('\n', 1)
    else:
        headerinfo = payload
        data = ''
    headers = get_headers(headerinfo)
    return headers, data


def send_ready(stdout):
    """
    Sends the READY signal to supervisor
    """
    stdout.write('READY\n')
    stdout.flush()


def send_ok(stdout):
    """
    Sends an ack to supervisor
    """
    stdout.write('RESULT 2\nOK')
    stdout.flush()


def supervisor_events(stdin, stdout, *events):
    """
    Runs forever to receive supervisor events
    """
    while True:
        send_ready(stdout)

        line = stdin.readline()
        headers = get_headers(line)

        payload = stdin.read(int(headers['len']))
        event_body, event_data = eventdata(payload)

        if headers['eventname'] not in events:
            send_ok(stdout)
            continue

        if event_body['processname'] == 'logstash-notifier':
            send_ok(stdout)
            continue

        yield headers, event_body, event_data

        send_ok(stdout)


def get_value_from_input(text):
    """
    Parses the input from the command line to work out if we've been given the
    name of an environment variable to include or a keyval of arbitrary data to
    include instead
    """
    values = {}
    if '=' in text:
        key, val = text.split('=', 1)
        values[key] = val
    else:
        if text in os.environ:
            values[text] = os.getenv(text)
    return values


def application(include=None):
    """
    Main application loop.
    """
    env = os.environ

    try:
        host = env['LOGSTASH_SERVER']
        port = int(env['LOGSTASH_PORT'])
        socket_type = env['LOGSTASH_PROTO']
    except KeyError:
        sys.exit("LOGSTASH_SERVER, LOGSTASH_PORT and LOGSTASH_PROTO are "
                 "required.")

    events = ['BACKOFF', 'FATAL', 'EXITED', 'STOPPED', 'STARTING', 'RUNNING']
    events = ['PROCESS_STATE_' + state for state in events]

    logstash_handler = None
    if socket_type == 'udp':
        logstash_handler = logstash.UDPLogstashHandler
    elif socket_type == 'tcp':
        logstash_handler = logstash.TCPLogstashHandler
    else:
        raise RuntimeError('Unknown protocol defined: %r' % socket_type)

    logger = logging.getLogger('supervisor')
    logger.addHandler(logstash_handler(host, port, version=1))
    logger.setLevel(logging.INFO)

    for headers, event_body, _ in supervisor_events(
            sys.stdin, sys.stdout, *events):
        extra = event_body.copy()
        extra['eventname'] = headers['eventname']

        if include is not None:
            user_data = {}
            for variable in include:
                user_data.update(get_value_from_input(variable))

            if len(user_data) > 0:
                extra['user_data'] = user_data

        logger.info(
            '%s %s', headers['eventname'], event_body['processname'],
            extra=extra,
        )


def run_with_coverage():  # pragma: no cover
    """
    Invoked when `-c|--coverage` is used on the command line
    """
    try:
        import coverage
    except ImportError:
        warnings.warn(
            'Coverage data will not be generated because coverage is not '
            'installed. Please run `pip install coverage` and try again.'
        )
        return

    coverage.process_startup()
    # need to register a shutdown handler for SIGTERM since it won't run the
    # atexit functions required by coverage
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))


def main():  # pragma: no cover
    """
    Main entry point
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--include',
        nargs='*', default=list(),
        help='include named environment variables and/or arbitrary metadata '
             'keyvals in messages')
    parser.add_argument(
        '-c', '--coverage',
        action='store_true', default=False,
        help='enables coverage when running tests'
    )
    args = parser.parse_args()
    if args.coverage:
        run_with_coverage()

    application(include=args.include)


if __name__ == '__main__':  # pragma: no cover
    main()
