### distributed load-testing using kubernetes and locust

This tutorial describes how to distributed load-testing kafka with kubernetes and locust


##### set your shell to GCP #####

    gcloud auth login
    gcloud config set region us-central1
    gcloud config set zone us-central1-a
    


##### create kafka in GCP #####

create kafka from GCP deployment manager, select Kafka Certified by Bitnami

open kafka for outside connections: https://stackoverflow.com/questions/32811824/not-able-to-connect-to-kafka-server-on-google-compute-engine-from-local-machine

Open firewall rule for kafka

##### build the new image and submit to GCP #####

    docker build -t gcr.io/rtp-gcp-poc/locust-kafka:latest .
    gcloud builds submit --tag gcr.io/rtp-gcp-poc/locust-kafka:latest .

##### Create GKE cluster #####

    gcloud container clusters create locust-kafka --zone us-central1-a

    gcloud container clusters get-credentials  locust-test --zone us-central1-a --project rtp-gcp-poc

##### deploy locust using k8s #####

    kubectl create -f ./

##### open logs of the worker #####

    kubectl get pods
    kubectl logs -f locust-worker-jdf8d

##### Testing #####

    kubectl get svc

login to external ip of locust master and start the test

##### Check that messages are arriving #####

    kafka-console-consumer --bootstrap-server 35.239.216.32:9092 --topic test --from-beginning


##### Cleanup #####

delete the cluster you have created
delete the kafka from the deployment manager


