This is a port of the [Supervisor-logging](https://github.com/infoxchange/supervisor-logging) project. Rather than capture loglines, as Supervisor-logging does it's intended to capture the [`PROCESS_STATE`](http://supervisord.org/events.html#event-listeners-and-event-notifications) events that Supervisor emits.

# NOTE: this project is a work in progress.

supervisord-syslog-notifier
===========================

A [supervisor]( http://supervisord.org/) plugin to stream events to an external Syslog instance (for example, Logstash).

Installation
------------

Python 2.7 or Python 3.2+ is required.

```
pip install supervisord-syslog-notifier
```

Note that supervisor itself does not yet work on Python 3, though it can be
installed in a separate environment (because supervisor-logging is a separate
process).

Usage
-----

The Syslog instance to send the events to is configured with the environment
variables:

* `SYSLOG_SERVER`
* `SYSLOG_PORT`
* `SYSLOG_PROTO`

Add the plugin as an event listener:

```
[eventlistener:logging]
command = supervisor_syslog_notifier
events = PROCESS_STATE
```

Enable the log events in your program:

```
[program:yourprogram]
stdout_events_enabled = true
stderr_events_enabled = true
```
