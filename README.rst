|Build Status|

This is a port of the
`Supervisor-logging <https://github.com/infoxchange/supervisor-logging>`__
project. Rather than capture loglines, as Supervisor-logging does it's
intended to capture the
`PROCESS_STATE <http://supervisord.org/events.html#event-listeners-and-event-notifications>`__
events that Supervisor emits.

supervisor-logstash-notifier
============================

A `supervisor <http://supervisord.org/>`__ plugin to stream events to a
Logstash instance.

Installation
------------

Python 2.7 or Python 3.2+ is required.

::

    pip install supervisor-logstash-notifier

Note that Supervisor itself does not yet work on Python 3, though it can
be installed in a separate environment (because
supervisor-logstash-notifier is a separate process).

Usage
-----

The Logstash instance to send the events to is configured with the
environment variables:

-  ``LOGSTASH_SERVER``
-  ``LOGSTASH_PORT``
-  ``LOGSTASH_PROTO``

Add the plugin as an event listener:

::

    [eventlistener:logging]
    command = logstash_notifier
    events = PROCESS_STATE

If you don't wish to define the environment variables for the entire
shell, you can pass them in via Supervisor's configuration:

::

    [eventlistener:logging]
    environment=LOGSTASH_SERVER="127.0.0.1",LOGSTASH_PORT="12202",LOGSTASH_PROTO="tcp"
    command=logstash_notifier
    events=PROCESS_STATE

Advanced Usage
--------------

It is also possible to include environment variables in the event messages, 
by specifying the name of the environment variables to include:

::

    [eventlistener:logging]
    command=export IPV4=`ec2metadata --local-ipv4`; logstash_notifier --include IPV4
    events=PROCESS_STATE

Running with Logstash
---------------------

Logstash can be simply configured to receive events:

::

    input {
        tcp {
            port => 12201
            codec => json
        }
    }

    output {
        stdout {
            codec => rubydebug
        }
    }

.. |Build Status| image:: https://travis-ci.org/dohop/supervisor-logstash-notifier.svg?branch=master
   :target: https://travis-ci.org/dohop/supervisor-logstash-notifier
