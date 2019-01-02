#!/bin/bash

# Copyright 2015 Google Inc. All rights reserved.
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


#docker build -t gcr.io/rtp-gcp-poc/locust-kafka:latest .
#docker run -d --name locust -e LOCUST_MODE=standalone -e SCENARIO_FILE=/locust-tasks/locustfile.py -e KAFKA_BROKERS=35.239.216.32:9092 -p 8089:8089 gcr.io/rtp-gcp-poc/locust-kafka:latest


LOCUST="/usr/local/bin/locust"
LOCUS_OPTS="-f $SCENARIO_FILE --host=$TARGET_HOST"
#LOCUS_OPTS="-f /locust-tasks/locustfile.py --host=$TARGET_HOST"
LOCUST_MODE=${LOCUST_MODE:-standalone}

if [[ "$LOCUST_MODE" = "master" ]]; then
    LOCUS_OPTS="$LOCUS_OPTS --master"
elif [[ "$LOCUST_MODE" = "worker" ]]; then
    LOCUS_OPTS="$LOCUS_OPTS --slave --master-host=$LOCUST_MASTER"
fi

echo "=> Starting locust"
echo "$LOCUST $LOCUS_OPTS"

$LOCUST $LOCUS_OPTS