# Distributed load testing of Apache Kafka using kubernetes and locust #

This tutorial describes how to distributed load testing kafka with kubernetes and locust


Prerequisites:

* [Docker](https://download.docker.com/mac/stable/Docker.dmg)
* python 2.7, pip, virtualenv
* kafka-client ```brew install kafka```

## Setup ##

    mkvirtualenv -p /usr/bin/python2.7 distributed-load-testing-using-kubernetes
    

## Testing locally ##

Create docker machine:

    docker-machine create --driver virtualbox default
    eval $(docker-machine env default)
    
Check the IP (It should be: 192.168.99.100)

    docker-machine ip default
    
Deploy kafka using docker-compose:

    git clone git@github.com:wurstmeister/kafka-docker.git

If your docker machine IP was not 192.168.99.100 then you will need to change it in the yml and then follow this IP 
with the rest of the tutorial
    
    docker-compose -f docker-compose-single-broker.yml up

Test that kafka runs properly:
    
    kafka-console-producer --broker-list 192.168.99.100:9092 --topic test
    kafka-console-consumer --bootstrap-server 192.168.99.100:9092 --topic test --from-beginning

### Testing locally using python ###

Export your kafka broker before running locust:

    export KAFKA_BROKERS=192.168.99.100:9092
Run locust:

    mkvirtualenv -p /usr/bin/python2.7 distributed-load-testing-using-kubernetes
    pip install -r requirements.txt
    locust -f docker-image/locust-tasks/locustfile.py

Open your browser at [locust](http://localhost:8089/)

When done clean your python env:
    
    deactivate
    rm -Rf ~/.virtualenvs/distributed-load-testing-using-kubernetes

### Testing locally using docker ###

Open new command shell (otherwise the locust will start on docker-machine default with port 192.168.99.100)

    cd docker-image
    docker build -t gcr.io/<PROJECT_ID>/locust-kafka-client:latest .
    docker run -d --name locust -e LOCUST_MODE=standalone -e SCENARIO_FILE=/locust-tasks/locustfile.py -e KAFKA_BROKERS=192.168.99.100:9092 -p 8089:8089 gcr.io/<PROJECT_ID>/locust-kafka-client:latest
 
Open your browser at [locust docker-machine](http://192.168.99.100:8089/) or [locust localhost](http://localhost:8089/)

When done clean your docker env:

    docker kill $(docker ps | grep locust | awk '{print $1;}') && docker rm $(docker ps -a | grep locust | awk '{print $1;}')
    docker images -a |  grep locust | awk '{print $3}' | xargs docker rmi -f

## Testing in GCP with K8s ##

### Set your shell to GCP ###

    gcloud auth login
    gcloud config set region us-central1
    gcloud config set zone us-central1-a

### Create kafka in GCP ###

Delpoy kafka from [GCP Cloud Deployment Manager](https://console.cloud.google.com/marketplace/details/click-to-deploy-images/kafka)


### Configure kafka ###

Add new firewall rule tag:

    gcloud compute firewall-rules create kafka-locust --allow tcp:9092 --target-tags kafka-locust
    
Assign the rule to the Kafka instance:

    gcloud compute instances add-tags <KAFKA_VM_NAME> --tags kafka-locust --zone us-central1-a
 
Open kafka for advertised listeners:
You must access to the cloud compute VM instance through SSH, then edit the kafka configuration file.

    gcloud compute --project <PROJECT_ID> ssh --zone "us-central1-a" <KAFKA_VM_NAME>

    sudo vim /opt/kafka/config/server.properties

Uncomment the line # advertised.listeners=PLAINTEXT://:9092 and replace with       

    advertised.listeners=PLAINTEXT://[instance_public_id_address]:9092

As a last step restart the kafka service

    sudo systemctl restart kafka
    

### Build the new image and submit to GCP ###

    cd docker-image
    docker build -t gcr.io/<PROJECT_ID>/locust-kafka-client:latest .
    gcloud builds submit --tag gcr.io/<PROJECT_ID>/locust-kafka-client:latest .

### Create GKE cluster ###

    gcloud container clusters create locust-cluster --zone us-central1-a

    gcloud container clusters get-credentials  locust-cluster --zone us-central1-a --project <PROJECT_ID>


### Deploy locust using k8s ###

    cd kubernetes-config
    
Set the Kafka external IP:
Open kubernetes-config/locust-worker-controller.yaml and replace KAFKA_EXTERNAL_IP with the Kafka external IP address.

Deploy the environment:
    
    kubectl create -f ./


### Open logs of the worker ###

    kubectl get pods
    kubectl logs -f locust-worker-<GENERATED_ID>


### Testing ###

    kubectl get svc locust-master

Login to external ip of locust master and start the test


### Check that messages are arriving ###

    kafka-console-consumer --bootstrap-server <KAFKA_VM_EXTERNAL_IP>:9092 --topic test --from-beginning


### Deploying new code to GCP ###

You will need to delete the topic since it contains old messages (Optional)

    kafka-topics --zookeeper <KAFKA_VM_EXTERNAL_IP>:2181 --delete --topic test

Roll out new image:

        docker build -t gcr.io/rtp-gcp-poc/locust-kafka-client:latest .
        gcloud builds submit --tag gcr.io/rtp-gcp-poc/locust-kafka-client:latest .
        kubectl rolling-update locust-worker --image gcr.io/rtp-gcp-poc/locust-kafka-client:latest --image-pull-policy Always
        kubectl rolling-update locust-master --image gcr.io/rtp-gcp-poc/locust-kafka-client:latest --image-pull-policy Always

Go to locust UI, Stop existing test and run it again.

### Cleanup ###

Delete the firewall rule:

    gcloud compute firewall-rules delete kafka-locust
    
Delete the cluster you have created:

    gcloud container clusters delete locust-cluster --zone us-central1-a
    
Delete the kafka server from [GCP Cloud Deployment Manager](https://console.cloud.google.com/dm/deployments)

Delete the locust-kafka-client docker image from  [GCP Container Registry](https://console.cloud.google.com/gcr/images/)
