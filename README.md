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

### Set your shell to GCP ###

    gcloud auth login
    gcloud config set region us-central1
    gcloud config set zone us-central1-a

### Create kafka in GCP ###

Create kafka from [GCP Cloud Deployment Manager](https://console.cloud.google.com/marketplace/details/bitnami-launchpad/kafka), select Kafka Certified by Bitnami


### Configure kafka ###
Open kafka for advertised listeners:
You must access to the cloud compute VM instance through SSH, then edit the kafka configuration file.

    gcloud compute --project <PROJECT_ID> ssh --zone "us-central1-a" <KAFKA_VM_NAME>

    sudo vim /opt/bitnami/kafka/config/server.properties

Uncomment the line # advertised.listeners=PLAINTEXT://:9092 and replace with       

    advertised.listeners=PLAINTEXT://[instance_public_id_address]:9092

As a last step restart the kafka service

    sudo /opt/bitnami/ctlscript.sh restart
    

### Build the new image and submit to GCP ###

    cd docker-image
    docker build -t gcr.io/<PROJECT_ID>/locust-kafka-client:latest .
    gcloud builds submit --tag gcr.io/<PROJECT_ID>/locust-kafka-client:latest .

### Create GKE cluster ###

    gcloud container clusters create locust-cluster --zone us-central1-a

    gcloud container clusters get-credentials  locust-cluster --zone us-central1-a --project <PROJECT_ID>


### Deploy locust using k8s ###

    cd kubernetes-config
    kubectl create -f ./


### Open logs of the worker ###

    kubectl get pods
    kubectl logs -f locust-worker-<GENERATED_ID>


### Testing ###

    kubectl get svc

Login to external ip of locust master and start the test


### Check that messages are arriving ###

    kafka-console-consumer --bootstrap-server <KAFKA_VM_EXTERNAL_IP>:9092 --topic test --from-beginning


### Cleanup ###

Delete the cluster you have created:

    gcloud container clusters create locust-cluster --zone us-central1-a
    
Delete the kafka server from [GCP Cloud Deployment Manager](https://console.cloud.google.com/dm/deployments)

Delete the locust-kafka-client docker image from  [GCP Container Registry](https://console.cloud.google.com/gcr/images/)
