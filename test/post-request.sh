#!/bin/bash -eux

IMPLEMENTATIONID=${1}
DESCRIPTION=${2}
PASSPHRASE=${3}
SERVER=${4:-http://localhost:8000}

curl -vvv -X POST -F "implementationId=${IMPLEMENTATIONID}" \
             -F "description=${DESCRIPTION}" \
             -F "passphrase=${PASSPHRASE}" \
             ${SERVER}/tools/implementationid
