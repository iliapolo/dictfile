fileconfig
==========

## A short story

A while back i was given a task to deploy a bunch of software components onto an amazon EC2 instance:

- Graphite + Grafana
- Elasticsearch + Logstash + Kibana (ELK)
- Nagios
- ...
- ...

Immediately i thought to myself: "Hey, no sweat, im sure DockerHub has containers for all these guys!".

This means all i will have to do is write a *docker-compose* file that defines all of them. A quick lookup at the
DockerHub registery revieled that even though containers existed for most of these components, they were not exactly
what i needed. They were either hardcoding some configuration (for example elasticsearch port), or bringing in
extra components that i just did not need (for example StatsD with the graphite container).

This meant that i had to start writing my own docker files, and configure each component to my needs. And let me tell
you, there was a lot of configuration to do:

- Retention policies for graphite storage (carbon.conf)
- Elasticsearch port (elasticsearch.yml)
- Grafana datasources and security (config.js)
- Logstash filters (logstash.conf)
- Nagios checks (nagios.cfg)
- ...
- ...

Effectively, this meant that i had to manipulate a lot of different configuration files from within the Dockerfile.
So, i did what every programmer would do:

1.  Bang my head against the table for a while.
2.  Freshen up on my 'sed' skills.

After a couple of hours, and with very little hair left, i thought to myself: "Man, wouldn't it be great if every onc
of these software components would provide a simply CLI for configurating the damn thing?!"
Imagine that in order to configure the elasticsearch port, all you had to do was:

`$ elasticsearch config port=9201`