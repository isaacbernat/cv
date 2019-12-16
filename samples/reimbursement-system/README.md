Developer work test
===================

This readme:

* Provides the received instructions.
* Describes how to get the project up and running.
* Explains assumptions/decisions that shaped the project.
* Outlines improvements and further work that could be done.

Instructions
------------
### General Guidelines

You are free to solve the problems in any way you like within the
constraints listed. Where specifications are insufficient you should
document your assumptions.

Try to time box your work to a maximum of 8 h. Prioritize good code
over more features! Document in your readme what you left out (e.g.
authentication or logging).

The solution should run on Python, and any third party libraries used
should be listed (with fixed version) in a requirements file. It
should be possible to easily set up the environment using the
requirements file.

You are encouraged to discuss your solution with us, do not hesitate
to contact us at any stage of your work - from planning to final
implementation.

### Assignment

Using Django or Flask (or another web app framework agreed upon), build
a backend with an HTTP API that mimics a minimal system for handling
reimbursements in health care.

If you use a database, SQLite is strongly preferred. Any other choice
must be agreed upon. This makes the evaluation easier for us.

API requirements:

1. It should be possible for a care giver to register healthcare
   events (including <event type, timestamp, care giver>). Each event
   type corresponds to a fixed sum of money to be reimbursed to the
   care giver.

2. It should be possible to fetch a report with reimbursements summed
   by month, per care giver. Further, it should be possible to select
   what time period and which care givers the report covers.

The application should be designed to be able to handle at least five
years of data and millions of registered healthcare events.

### Evaluation

In our evaluation we will look at:

* How you design the API
* How you test your code
* How you handle errors
* Usage of relevant third party libraries
* Performance

You'll have the opportunity to discuss you're solution in detail with
us at the follow-up meeting.

### The Solution

The solution (or questions) should be sent to dev@COMPANY.com before the
agreed deadline.

Running the app
---------------
### Setup

1. Fork/Clone/Download this repo.
2. Install [docker compose](https://docs.docker.com/compose/install/)
3. Copy and paste in a terminal:

```sh
# Build the images
docker-compose build
# Run the containers (in the background)
docker-compose up -d
# Create database
docker-compose run events-service python manage.py recreate_db
# Run tests
docker-compose run events-service python manage.py test
# List running containers basic information
docker ps
```

### Try it live!
The last command (`docker ps`) should show something similar to this:
```
CONTAINER ID        IMAGE                     COMMAND                  CREATED             STATUS                   PORTS                    NAMES
4653150545b5        test_nginx            "nginx -g 'daemon ..."   14 minutes ago      Up 7 minutes             0.0.0.0:80->80/tcp       nginx
229c163964b6        test_events-service   "/bin/sh -c 'pytho..."   14 minutes ago      Up 7 minutes             0.0.0.0:5001->5000/tcp   events-service
84017cfb532b        test_events-db        "docker-entrypoint..."   15 minutes ago      Up 8 minutes (healthy)   0.0.0.0:5435->5432/tcp   events-db
```

The events-service address should be shown. It may be opened in a web browser.
It can also be "curled" from a terminal. You may try
`curl http://0.0.0.0:5001/ping` to ensure it respons "pong" with success status.

### More handy docker-compose commands
In addition to those from setup. You may skip this section if already familiar.
```sh
# Stop the containers
docker-compose stop

# Bring down the containers:
docker-compose down

# Force a build
docker-compose build --no-cache

# Delete all containers
docker rm $(docker ps -a -q)

# Delete all images
docker rmi $(docker images -q)

# Check logs
docker-compose logs <service-name>
```

Implementation details
----------------------
This section explains the reasoning behind assumptions that were made.
It also tells how decisions were made to align with the evaluated aspects.

### Data model
The data model (`project/api/models.py`) consists of the following entities.

#### Event
This entity conforms to all requirements as specified in the instructions
*register healthcare events (including <event type, timestamp, care giver>)*
and a few more.
- **id**: an autoincrementing integer. Chosen for simplicity. A UUID could be
a good choice for performance/security/etc (more details in further sections)
- **type_id**: a foreign key to the Event Type it belongs to.
- **caregiver_id**: we assume 1 and only 1 per event.
- **start_time**: timestamp which states when the event took place.
- **reimbursed**: determines if the event has been reimbursed to the caregiver.
- **created_at**: when the event was introduced in the DB. Useful for auditing.

#### Event type
- **id**: same reasoning as above.
- **name**: an alternative id (is unique). Human readable.
- **amount_in_cents**: an integer. We consider only significant figures and
treat them as integers to avoid precision errors associated with other number
representations. Especially important for accounting audits.
- **currency**: for simplicity only SEK are allowed.

I personally think **amount** should belong to the Event not to the Event Type
entity. This is because the cost for an Event Type may change at some point in
time and there would not be any way to reflect this in a report (e.g. a law is
passed saying "x-rays must be recalibrated between each use". This turns a 5
minute process into a 30 minute one. This would increase the Event Type cost.
Of course past x-ray Events should use the previous standard cost).

I implemented it this way because I inferred this is what it was expected from
the instructions *Each event type corresponds to a fixed sum of money*.

#### Caregivers
An entity could be created to represent caregivers/personnel. In a microservice
architecture this warrants a service of its own, since it is decoupled enough
from Type/Event Type to share it with them. Due to time limitations it has not
been implemented.

### Endpoints
Here is a succint definition of the existing endpoints (`project/api/views.py`).
There are no endpoints to update created resources (PUT verb). They could be
trivially implemented if needed. Not having them saved development time.

Additional filters for endpoints to get all events could be implemented the same
way it is done for `/events/report`. Pagination could also be useful if the list
of Events in the system is in the order or millions.

#### Permissions
Since no authentication has been implemented (due to time restrictions) all
endpoints may be called by anyone. For this system to be production-ready, some
restrictions should be enforced. Depending on the role/permissions associated
with each user, actions could be restricted and data partially filtered.

Examples follow:
- Managers calling the report endpoint should not get information regarding
personnel outside their responsibilities (e.g. employees at other hospitals).
- Deletion endpoints should be more restricted than creation.
- Creation endpoints should be more restricted than read.
- Reimburse endpoint should only be callable by people on accounting department.

#### Event
- **/events** `GET`: returns all events in the system.
- **/events** `POST`: creates an event. Returns *event_id* of created event.
- **/events/<event_id>** `GET`: gets the event with given *event_id*.
- **/events/<event_id>** `DELETE`: removes event with *event_id* from the system.

#### Event type
- **/events/types** `GET`: returns all event types in the system.
- **/events/types** `POST`: creates an event type. Returns *id* of created type.
- **/events/types/<etype_id>** `GET`: gets the event type with given *etype_id*.
- **/events/types/<etype_id>** `DELETE`: removes event type with *etype_id*.

#### Other
- **/ping** `GET`: responds if the system is up. It does not use DB nor it does
any other kind of health/load check, but is useful to measure latency.
- **/events/<event_id>/reimburse** `POST`: marks event with *event_id* as
reimbursed.
- **/events/report** `GET`: outputs a report of events which consists of summed
amounts in SEK by `year>month>caregiver id`. They are further grouped by
reimbursion state. Example output format of report field follows:
```python
    report = {
        '2017': {
            'Jan': {
                caregiver_id1: {
                    'non-reimbursed SEK': 500,
                    'reimbursed SEK': 2500,
                }
                caregiver_id2: {
                    'reimbursed SEK': 1000,
                }
                caregiver_id3: {
                    'reimbursed SEK': 2500,
                }
            }
            'Feb': {
                caregiver_id1: {
                    'non-reimbursed SEK': 1500,
                }
                caregiver_id3: {
                    'reimbursed SEK': 3000,
                    'non-reimbursed SEK': 1000,
                }
            }
        }
    }
```
- **/events/report** `POST`: same as previous endpoint but accepts a POST
payload which contain filters. Example below:
```python
  {
    'caregiver_ids': [3,4,5],  # includes only events for selected caregivers
    'min_time': '2017-10-28T23:28:23.456701',  # only events started after
    'max_time': '2017-10-28T23:28:23.456701',  # only events started before
  }
```
#### Technical details
For this project to scale to millions of users, a few changes should be applied.
Some issues specific to concrete endpoints are listed here. On the performance
section ahead, more abstract advice with a wider scope is also given.
##### /events (POST)

###### caregiver_id
This project lacks verification for this field. It should be checked that this
id is valid, that this caregiver can perform an Event of that Event Type, that
the authed user has permissions to create an Event for that given caregiver, etc.

In a microservice architecture this may require calls to several other services
(e.g. personnel service). These multiple calls could make this endpoint slow.
A strategy could be to cache that information or store it in memory. I could
imagine a user at the end of the day entering all the Events he/she was involved
in. This way only the first call would need to fetch most of the previous
information.

As always when there are caches, relatively short expiry times, ways to flush
specific keys (e.g. calling an endpoint), etc. are encouraged to keep the data
true to the original source. Changes should not be very frequent for caregiver
information relevant to Events, but should be kept in mind.

###### start_time
A rule should be placed so older events (e.g. >12h) may not be entered. At
least, not with the normal usage of this endpoint (or without special admin
privileges). Main reasons are:
- Prevents tampering of old records. Willingly or not, the longer it takes to
introduce the data the less reliable it becomes (details are forgotten, paper
notes get lost, etc.)
- Keeps the system more complete. Users have a strong incentive to fill the data
within the alloted maximum time. Reports generated, can be ensured to be more
accurate, at least for periods older than the rule/limit. That also makes the DB
a more valuable data source.
- Allows for pre-computing, caching, intermediate results, etc. If introduction
of old Events (or data) is rare, old data can be stored in read-only replicas.
A smaller database with just today's data can be merged with the historical
read-only DB in nightly batches, etc. This can achieve important performance
increases.

###### reimbursed
An Event is always created with `reimbursed=False`, no matter what parameter
values are submitted. This is because reimbursing an Event is very different
from creating one. There should be a separate traceability for how this is done.
It should probably be done by different users as well.

Maybe it would be a good idea to return an error when this is submitted (as well
as with id or non-valid parameters that will be ignored). It would be trivial to
change this behaviour.

##### /events/report
###### caching
This operation could become slow for DBs with many entries. Caching some partial
aggregations seems a reasonable approach. Data is grouped by month and year. For
historic data, the results should not change, as introducing old data in this
system should not be the norm. Maybe only the latest month should be recomputed.

Furthermore, the `generated_at` field returned could show the end user how old
is the cached data obtained. If deemed too old, it could be flushed and
recomputed again.
###### POST vs GET
There is a GET version of this endpoint, since this is the one it makes most
sense according to RESTful principles. Nevertheless, filterable options include
an arbitrarily long list of caregiver_ids. It can be problematic to have long
URLs. Therefore, the parameters are passed via POST instead of URL query strings
parameters. Since POST payload is used for caregiver_ids, it is used by the
other filtering options as well.

### What has been left out?
Because of time constraints for this assignment, elements essential to a
production-ready project of these characteristics had to be left out. Apart from
more extensive testing or potential performance improvements (which are covered
in the following section), what is especially missing is logging, monitoring,
authentication or instructions on deployment. I wanted to remark these omissions
as intended, and not as an oversight. They could be addressed with further alloted
development time. I assumed the other implemented parts to be more relevant from
your standpoint.

### Evaluation
#### API design
The API is desgined following [REST principles](https://en.wikipedia.org/wiki/Representational_state_transfer#Applied_to_web_services).

##### Versioning
Any API should be designed to support versioning from the start. This is
especially true when old clients are expected to be outside our control (i.e.
unable to force those clients to update, but they still must be supported).
There are many different valid approaches with their own pros and cons. I would
use a query parameter (e.g. http://domain/url?version=1.0) to "force" a specific
version of a resource to be served. Omission would default to the latest version.
I would also include a field in the response indicating which version of the
resource is being returned (and maybe which is the latest available, so the
receiver may choose to update to a newer one if available).

Of course, I value consistency over small implementation details. I would
consider how the other services in the environment implement versioning and
adjust accordingly.

#### Code testing
I think TDD is a nice practise. Code coverage metrics are also useful.
My opinion on the topic is not set in stone, but one should never mistake
a 100% path coverage with bug-free code.
My own approach is to add tests for each non-trivial functionality which cover:
 - Simple base cases.
 - Complex cases using as many different options as possible/reasonable.
 - Corner cases and likely exploits that come to mind.

Balance between adding more tests to increase confidence in the code and
time/effort spent in other parts of the software development process must be reached.

#### Error handling
Incorrect error handling may pose serious security risks. When an error occurs,
no more information than needed should be provided to the end user. Revealing too
much could be used in exploits.

An error may be caused by non-malicious usage. When this is predictably the case,
the user ought to be informed. To avoid more frustration, the user should be
offered help/details to fulfill his/her goals with descriptive messages.
Nevertheless, this should not conflict with previous paragraph.

When an error occurs, as much information as possible on the state should be
gathered and logged. This aids in debugging the system, finding the cause, etc.
Logs should be monitored. Abnormal errors should trigger alarms to whomever
is responsible for the security. Repeated errors in a short time period, sharing
the same IP, parameters or overly similar patterns should be carefully analysed and
automatic temporary rate limiting could be enforced to prevent further damage.
When the situation is manually addressed, the limiting could be lifted. These
are valid signs of suspicion of an attack.

#### Usage of relevant third parties
##### Git
A solid version control system. The most widely used according to Stack Overflow.
##### Python 3
It is suggested that Python is used in the description. The choice was easy.
(you also mentioned Go as a possibility in a previous conversation).
The choice of Python3 over Python2 seems obvious for a new project. Some reasons:
* Python3's is more consistent with The Zen of Python (PEP 20) than Python2.
    *There should be one-- and preferably only one --obvious way to do it* and
    *Special cases aren't special enough to break the rules* comes to mind.
    * py2 `print` vs py3 `print()`.
    * all "strings" are unicode in python3.
    * py2 `range` and `xrange`.
* [Most major libraries](http://py3readiness.org/) are already ported to Python3.
* Python 2.7 End Of Life is coming...
##### Flask
Flask is suggested in the assigment. Is more straightforward than Django here.
##### Docker
A few benfits which justify Docker over other solutions here.
- It is easy to set the environment up (a suggested General guideline).
- Containers are lighter than full-fledged VMs (also valid performance point).
- Makes orchestration of different microservices and integration testing easy.
- Scalable (the assignment talks about processing millions of entries).
- Avoids the "Works on my machine" syndrome.
##### PostgreSQL
It is a sound and time-tested DBMS (not a critical element for this assignment).
##### SQLAlchemy
One of the most relied on Python ORMs. Here basically used to sanitise inputs.
##### Gunicorn
The number of workers or threads per instance should be tunned up for performance.

##### testdriven.io
This project uses a subset of [testdriven.io](https://testdriven.io/) (Part 1).
The main reasons behind it are:
* It uses *Python3*, *Flask*, *Docker Compose*, *PostgreSQL*, *SQLAlchemy*.
They form coherent stack and align well with project requirements (see above).
* The project structure is sound, it defines different environments for test,
production and development, the files are neatly organised.
* The documentation is clear and modular.
* Reusing such a skeleton makes sense for an assignment of this scope. It saves
development time and avoids the notorious "reinventing the wheel" anti-pattern.
* Other Parts of testdriven.io are not used because it is well beyond
what is expected here (even if it showcases React also used at COMPANY or other
technologies required for the assignment to be production-ready like auth)

#### Performance
##### Disclaimer
I believe optimisation should be purposeful (not just for optimisation sake).
There is a famous saying "Premature optimization is the root of all evil".
I interpret this as a call for prudence. Improvements in performance are often
gained at the cost of increased complexity. In these cases, a cost-benefit
analysis may be called for. Not only the current implementation time/resources
are needed for any optimisation. Maintainability may be seriously compromised.
This might affect the project success and development pace in the long run.

Furthermore, within the [Kano model](https://en.wikipedia.org/wiki/Kano_model)
theory, performance could be considered a *Must-be* quality. A given user
expects an API call to be responded in 100 ms. A 1000 ms delay may be
unacceptable for that user. A 10 ms or a 1ms delay will not make a difference.
If the user can not notice it, optimising beyond 100 ms is wasteful. A real case
would involve analysing all users within a wide range of percentiles (e.g. 90).
Then ensuring they are within the limits that would be considered "good enough".

Having said so, I believe this is not an excuse to write bad code. I just want
to remark that when it comes to optimistation there is no "silver bullet".
There are many different valid strategies to apply, but the first one should be
to set up a benchmark (which is the acceptable response time/memory usage/etc.).
Then look for bottlenecks and start working on those. A few ideas come to mind:

##### Approach
When performance is crucial, some values should be set to ensure product quality
meets the user expected standards. From now on, we assume total correctness.
Here is a list of possible approaches that could be useful:
1. If there already is a service up and running, we could set up a replica using
the new software which receives a copy of all the calls that are made to the
production environment. Assuming current usage is representative of expected usage.
2. If that is not possible, in a micro-service architecture we could replace one
single instance of a service with the new version and monitor it closely. The
overall performance effect should be minimal (considering we have many instances)
3. If that is not possible, a staging environment resembling the production one
as close as possible, could be fed with calls simulating expected usage.

##### Examples
Depending on where the bottleneck is found a few strategies could be applied:
###### Machine scaling
- Horizontal scaling (increase the number of instances serving petitions) with a
loadbalancer distributing the calls.
- Vertical scaling (having faster and more powerful machines).

###### Serving incoming petitions
- Locate machines closer to where calls are being made may reduce response time.
- Use a CDN to host all static files (e.g. CSS).
- Use Round-robin DNS to distribute petitions among the different load-balancers.
- Implement a queue that takes all petitions from load balancers. If there is a
 peak it should prevent petitions from getting lost.
- Rate limit petitions per hour/minute per IP to prevent abuse and affect other
users.

###### Analysis/profiling
- Apply machine learning to load/usage/etc. to prevent (or at least forecast)
usage spikes, know the regions traffic comes from, etc.
- Do the same with errors, abnormal usage, data queries, endpoints called, etc.
- Profile the application usage and optimise (or port to faster compiled languages
like C or Go) the most critical paths/microservices.
- Consider the use of specialised hardware (e.g. GPUs) is applicable.
- Finetune Gunicorn number of workers or threads per docker instance.
- Find out when docker/machine performance start to deteriorate (e.g. memory
leaks, allocated resources that garbage collector fails to free, etc.) Restart
them frequently, before that happens (e.g. every day). With many instances per
service, restarting 1 by 1 should not affect overall performance.
- Try possible exploits (e.g. sending large payloads on POST endpoints) and
make the system resilient to them.

###### Database
- precompute queries (ETL/OLAP)
- cache
- shard
- read replicas
- split/specialise DBs
- connection pools
- benchmark different DBMS
- autoincremental vs UUIDs (may be computed on client, unique among tables...)
- prepared statements
- profile the DB
- review query plans for most common/expensive queries
- etc.