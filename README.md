# Distributed load testing of Apache Kafka using kubernetes and locust #

This tutorial describes how to distributed load-testing kafka with kubernetes and locust


## Testing locally ##
Deploy kafka using docker-compose:

    git clone git@github.com:wurstmeister/kafka-docker.git
    docker-compose -f docker-compose-single-broker.yml up
Test kafka runs properly:
    
    kafka-console-producer --broker-list 192.168.99.100:9092 --topic test
    kafka-console-consumer --bootstrap-server 192.168.99.100:9092 --topic test --from-beginning

Export your kafka broker before running locust:

    export KAFKA_BROKERS=192.168.99.100:9092
Run locust:

    locust -f locust-tasks/locustfile.py

## Testing in GCP with K8s ##

### Create kafka in GCP ###

create kafka from GCP deployment manager, select Kafka Certified by Bitnami


### Configure kafka ###
Open kafka for advertised listeners:
You must access to the cloud compute VM instance through SSH, then edit the kafka configuration file.

    sudo vim /opt/bitnami/kafka/config/server.properties

Uncomment the line # advertised.listeners=PLAINTEXT://:9092 and replace with       

    advertised.listeners=PLAINTEXT://[instance_public_id_address]:9092

As a last step restart the kafka service

    sudo /opt/bitnami/ctlscript.sh restart


### Set your shell to GCP ###

    gcloud auth login
    gcloud config set region us-central1
    gcloud config set zone us-central1-a
    

### Build the new image and submit to GCP ###

    cd docker-image
    docker build -t gcr.io/rtp-gcp-poc/locust-kafka:latest .
    gcloud builds submit --tag gcr.io/rtp-gcp-poc/locust-kafka:latest .

### Create GKE cluster ###

    gcloud container clusters create locust-kafka --zone us-central1-a

    gcloud container clusters get-credentials  locust-test --zone us-central1-a --project rtp-gcp-poc


### Deploy locust using k8s ###

    cd kubernetes-config
    kubectl create -f ./


### Open logs of the worker ###

    kubectl get pods
    kubectl logs -f locust-worker-jdf8d


### Testing ###

    kubectl get svc

Login to external ip of locust master and start the test


### Check that messages are arriving ###

    kafka-console-consumer --bootstrap-server 35.239.216.32:9092 --topic test --from-beginning


### Cleanup ###

Delete the cluster you have created:

    gcloud container clusters create locust-kafka --zone us-central1-a
    
Delete the kafka from the deployment manager


