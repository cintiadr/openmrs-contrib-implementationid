# Implementation ID

<https://wiki.openmrs.org/x/wREz>

This application is used to generate an ImplementationId.

The code already existed; it was just migrated to Flask and dockerised to be deployed in Jetstream.


## Implementation details

It's an unauthenticated POST request. It does require `implementationId`, `description` and `passphrase`.
`implementationId` shouldn't have `^` or `|` chars (no idea why).

  - If any of the fields is incorrect or missing, it will return code `400`.
  - If `implementationId` doesn't exist on the database, it creates and returns code `200`.
  - If `implementationId` already exists and passphrase matches, it returns code `200`.
  - If `implementationId` already exists and passphrase doesn't match, it will return an `403` error.

  A log is created for all cases.


## Running locally

Make sure to install docker and docker-compose locally.
```
$ docker-compose build

# Starting database and application in docker
$ docker-compose up -d

# to test application
$ curl localhost:8000/ping

# to power off and delete data
$ docker-compose down -v
```
