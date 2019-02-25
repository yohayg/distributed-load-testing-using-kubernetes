# Distributed load testing of postgres using kubernetes and locust #

This tutorial describes how to distributed load testing postgres with kubernetes and locust


Prerequisites:

* [Docker](https://download.docker.com/mac/stable/Docker.dmg)
* python 2.7, pip
* virtualenv ```pip install virtualenv```
* psql ```brew install postgres```
* kubectl ```brew install kubernetes-cli```
* [gcloud](https://cloud.google.com/sdk/docs/quickstart-macos) 

## Setup ##

    virtualenv -p /usr/bin/python2.7 venv
    source venv/bin/activate
    

## Testing locally ##

Run postgres using docker:
Create docker machine:

    docker-machine create --driver virtualbox default
    eval $(docker-machine env default)
    
Check the IP (It should be: 192.168.99.100)

    docker-machine ip default
    docker run -d -p 5432:5432 --name my-postgres -e POSTGRES_PASSWORD=mysecretpassword postgres
    
Check that python is able to connect to postgres

    virtualenv -p /usr/bin/python2.7 venv
    source venv/bin/activate
    pip install -r requirements.txt
    python postgres_test.py
    
Check that there are rows in postgres table:

    psql -h 192.168.99.100 -U postgres

And run 

    psql> select count(*) from films;

### Testing locally using python ###

Export your postgres before running locust:

    export POSTGRES_CONNECTION_STRING=postgres://postgres:mysecretpassword@192.168.99.100:5432/postgres
Run locust:

    locust -f docker-image/locust-tasks/postgres_locustfile.py

Open your browser at [locust](http://localhost:8089/)


Check that the films table is increasing

    psql> select count(*) from films;

When done clean your python env:
    
    deactivate
    rm -Rf ~/.virtualenvs/distributed-load-testing-using-kubernetes

### Testing locally using docker ###

Open new command shell (otherwise the locust will start on docker-machine default with port 192.168.99.100)

    cd docker-image
    docker build -t gcr.io/<PROJECT_ID>/locust-postgres-client:latest .
    docker run --rm  -e  LOCUST_MODE=standalone -e LOCUST_FILE=/locust-tasks/postgres_locustfile.py -e POSTGRES_CONNECTION_STRING=postgres://postgres:mysecretpassword@192.168.99.100:5432/postgres  -p 8089:8089 gcr.io/<PROJECT_ID>/locust-postgres-client
 
Open your browser at [locust docker-machine](http://192.168.99.100:8089/) or [locust localhost](http://localhost:8089/)

When done clean your docker env:

    docker kill $(docker ps | grep locust | awk '{print $1;}') && docker rm $(docker ps -a | grep locust | awk '{print $1;}')
    docker images -a |  grep locust | awk '{print $3}' | xargs docker rmi -f

## Testing in GCP with K8s ##

### Set your shell to GCP ###

    gcloud auth login
    gcloud config set project <PROJECT_ID>
    gcloud config set region us-central1
    gcloud config set zone us-central1-a

### Create postgres in GCP ###

Deploy postgres from [GCP Cloud SQL](https://console.cloud.google.com/sql)


### Configure postgres for accessing from ANY IP ###

Go to your postgres connections tab and add network: 0.0.0.0/0

Test that postgres runs properly:
    
    psql -h POSTGRES_EXTERAL_IP -U postgres
    

Create the test table:

    CREATE TABLE public.films
    (
        title text COLLATE pg_catalog."default",
        director text COLLATE pg_catalog."default",
        year text COLLATE pg_catalog."default"
    )
    WITH (
        OIDS = FALSE
    )
    TABLESPACE pg_default;
    
    ALTER TABLE public.films
        OWNER to postgres;


### Build the new image and submit to GCP ###

    cd docker-image
    docker build -t gcr.io/<PROJECT_ID>/locust-postgres-client:latest .
    gcloud builds submit --tag gcr.io/<PROJECT_ID>/locust-postgres-client:latest .

### Create GKE cluster ###

    gcloud container clusters create locust-cluster --zone us-central1-a

    gcloud container clusters get-credentials  locust-cluster --zone us-central1-a --project <PROJECT_ID>


### Deploy locust using k8s ###

    cd kubernetes-config-postgres
    
Set the postgres external IP:
Open kubernetes-config-postgres/locust-worker-controller.yaml and replace POSTGRES_EXTERNAL_IP with the postgres external IP address.

Deploy the environment:
    
    kubectl create -f ./


### Open logs of the worker ###

    kubectl get pods
    kubectl logs -f locust-worker-<GENERATED_ID>


### Testing ###

    kubectl get svc locust-master

Login to external ip of locust master and start the test


### Check that messages are arriving ###

    psql -h POSTGRES_EXTERAL_IP -U postgres

    psql>select count(*) from films;


### Deploying new code to GCP ###

Roll out new image:

        docker build -t gcr.io/rtp-gcp-poc/locust-postgres-client:latest .
        gcloud builds submit --tag gcr.io/rtp-gcp-poc/locust-postgres-client:latest .
        kubectl rolling-update locust-worker --image gcr.io/rtp-gcp-poc/locust-postgres-client:latest --image-pull-policy Always
        kubectl rolling-update locust-master --image gcr.io/rtp-gcp-poc/locust-postgres-client:latest --image-pull-policy Always

Go to locust UI, Stop existing test and run it again.


### Scaling workers ###

    kubectl scale --replicas=20 replicationcontrollers locust-worker

### Cleanup ###
    
Delete the cluster you have created:

    gcloud container clusters delete locust-cluster --zone us-central1-a
    
Delete the postgres server from [GCP Cloud SQL](https://console.cloud.google.com/sql)

Delete the locust-postgres-client docker image from  [GCP Container Registry](https://console.cloud.google.com/gcr/images/)
